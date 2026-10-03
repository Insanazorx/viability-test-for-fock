"""Bounded CUDA LBFGS/AL solve using the existing validated mathematical core."""
from __future__ import annotations

import time

from .solver_checkpoint import restore_rng


class EvaluationBudgetExceeded(RuntimeError):
    pass


def solve_cuda(objective, initial, settings, *, resume=None, checkpoint=None, progress=None):
    import torch
    if objective.ops.name != 'torch' or initial.device.type != 'cuda' or initial.dtype != torch.float64:
        raise ValueError('Production requires actual float64 CUDA tensors')
    raw = objective.chart.pack(initial)
    multiplier = 0.
    history = []
    first_outer = 0
    if resume:
        state = resume['state']
        raw = state['raw'].to(device=initial.device, dtype=initial.dtype)
        multiplier = state['multiplier']
        history = state['history']
        first_outer = state['next_outer']
        if first_outer != len(history) or not 0 <= first_outer <= settings['outer_updates']:
            raise ValueError('Invalid AL resume boundary')
        objective.chart.unpack(raw)
        restore_rng(resume['rng'])
    latest = None
    if checkpoint and not resume:
        latest = checkpoint({'raw': raw, 'multiplier': multiplier, 'next_outer': 0,
                             'history': [], 'optimizer': {}, 'complete': False})
    for outer in range(first_outer, settings['outer_updates']):
        started = time.perf_counter()
        parameter = torch.nn.Parameter(raw.detach().clone())
        optimizer = torch.optim.LBFGS(
            [parameter], max_iter=settings['maxiter'], max_eval=settings['maxfun'],
            tolerance_grad=settings['gtol'], tolerance_change=settings['ftol'],
            history_size=settings['history_size'], line_search_fn='strong_wolfe')
        evaluations = 0
        last_finite = raw.detach().clone()
        best_value = float('inf')
        budget_exceeded = False

        def closure():
            nonlocal evaluations, last_finite, best_value
            if evaluations >= settings['maxfun']:
                raise EvaluationBudgetExceeded('Declared function-evaluation limit reached in line search')
            with torch.no_grad():
                value, gradient = objective.value_gradient(parameter, multiplier, settings['penalty'])
                if not torch.isfinite(value) or not torch.isfinite(gradient).all():
                    raise FloatingPointError('Nonfinite augmented objective or gradient')
                evaluations += 1
                parameter.grad = gradient.detach().clone()
                if float(value) < best_value:
                    best_value = float(value)
                    last_finite = parameter.detach().clone()
            return value

        with torch.no_grad():
            initial_value = float(objective.value_gradient(raw, multiplier, settings['penalty'])[0])
        try:
            optimizer.step(closure)
        except EvaluationBudgetExceeded:
            # The interrupted Wolfe trial is not an accepted optimizer iterate.
            # Keep the best evaluated finite field, label the capped solve explicitly.
            budget_exceeded = True
            with torch.no_grad():
                parameter.copy_(last_finite)
        with torch.no_grad():
            field, _ = objective.chart.unpack(parameter)
            metrics = objective.metrics(field)
            final_value, final_gradient = objective.value_gradient(parameter, multiplier, settings['penalty'])
        inner = optimizer.state.get(parameter, {})
        next_multiplier = multiplier + settings['penalty'] * metrics['charge_error']
        row = {'outer': outer, 'initial_augmented': initial_value, 'final_augmented': float(final_value),
               'multiplier_before': multiplier, 'multiplier_after': next_multiplier,
               'penalty': settings['penalty'], 'iterations': int(inner.get('n_iter', 0)),
               'evaluations': evaluations, 'max_chart_gradient': float(final_gradient.abs().max()),
               'evaluation_budget_exceeded': budget_exceeded,
               'inner_converged_by_gradient': bool(final_gradient.abs().max() <= settings['gtol']),
               'wall_time_seconds': time.perf_counter()-started, **metrics}
        history.append(row)
        multiplier = next_multiplier
        raw = objective.chart.pack(field)
        if checkpoint:
            latest = checkpoint({'raw': raw, 'multiplier': multiplier, 'next_outer': outer+1,
                                 'history': history, 'optimizer': optimizer.state_dict(),
                                 'complete': outer+1 == settings['outer_updates']})
        if progress:
            progress(row)
    with torch.no_grad():
        field, _ = objective.chart.unpack(raw)
        metrics = objective.metrics(field)
    return {'field': field, 'history': history, 'multiplier': multiplier, 'metrics': metrics,
            'latest_checkpoint': latest, 'resume_boundary': 'completed AL outer update; inner restart on interruption'}
