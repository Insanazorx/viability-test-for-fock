"""Identified source-sequence acceptance and CUDA optimizer/restart checks."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from core.backends import TorchBackend
from static.spectral import PeriodicGrid, SpectralEnergy
from static.hopf_initial import compact_hopf
from static.minimizer import AugmentedHopfObjective
from static.production import solve_cuda
from static.solver_checkpoint import load_checkpoint, save_checkpoint


def code_digest(root):
    paths = sorted((root/'src').rglob('*.py')) + [root/'scripts/run.py', root/'scripts/configuration.py']
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.relative_to(root).as_posix().encode()+b'\0'+path.read_bytes()+b'\0')
    return digest.hexdigest()


def row_checks(metrics, reference, tolerances, history, unit_error, boundary_error):
    return {
        'finite': all(np.isfinite(metrics[key]) for key in ('energy','charge','constrained_rms','virial')),
        'energy_relative': abs(metrics['energy']-reference['energy'])/reference['energy'] <= tolerances['energy_relative'],
        'unit_charge': abs(abs(metrics['charge'])-1) <= tolerances['unit_charge'],
        'charge_sign': metrics['charge'] < 0,
        'constrained_rms': metrics['constrained_rms'] <= tolerances['constrained_rms'],
        'unit_error': unit_error <= tolerances['unit_error'],
        'boundary_error': boundary_error <= tolerances['boundary_error'],
        'iteration_budget': all(row['iterations'] <= 120 for row in history),
        'evaluation_budget': all(row['evaluations'] <= 180 for row in history),
        'outer_updates': len(history) == 4,
    }


def oracle_comparison(objective, field, multiplier, penalty):
    import torch
    cpu=AugmentedHopfObjective(SpectralEnergy(objective.engine.grid),objective.target)
    host=field.detach().cpu().numpy()
    raw=objective.chart.pack(field).detach().requires_grad_(True)
    value,gradient=objective.value_gradient(raw,multiplier,penalty)
    expected,host_gradient=cpu.value_gradient(cpu.chart.pack(host),multiplier,penalty)
    automatic,=torch.autograd.grad(value,raw)
    return {'backend':max(abs(float(value.detach())-float(expected))/max(1,abs(float(expected))),
                          float(np.max(abs(gradient.detach().cpu().numpy()-host_gradient)))/max(1,float(np.max(abs(host_gradient))))),
            'autograd':float((automatic-gradient).detach().abs().max())/max(1,float(gradient.detach().abs().max())),
            'cpu_metrics':cpu.metrics(host)}


def engineering_checks(root, run_id, identity, tolerances):
    import torch
    errors = {'backend': 0., 'autograd': 0., 'resume': 0.}
    grid = PeriodicGrid.paper(5,4.)
    cpu = SpectralEnergy(grid)
    gpu = SpectralEnergy(grid,TorchBackend())
    field = compact_hopf(grid)['field']
    x = torch.tensor(field,device='cuda',dtype=torch.float64)
    cpu_objective = AugmentedHopfObjective(cpu)
    gpu_objective = AugmentedHopfObjective(gpu)
    raw = gpu_objective.chart.pack(x).requires_grad_(True)
    value, gradient = gpu_objective.value_gradient(raw,.7,200.)
    vcpu, gcpu = cpu_objective.value_gradient(cpu_objective.chart.pack(field),.7,200.)
    errors['backend'] = max(abs(float(value.detach())-float(vcpu))/max(1,abs(float(vcpu))),
                            float(np.max(abs(gradient.detach().cpu().numpy()-gcpu)))/max(1,float(np.max(abs(gcpu)))))
    automatic, = torch.autograd.grad(value,raw)
    errors['autograd'] = float((automatic-gradient).detach().abs().max())/max(1,float(gradient.detach().abs().max()))
    grid = PeriodicGrid.paper(7,4.)
    engine = SpectralEnergy(grid,TorchBackend())
    objective = AugmentedHopfObjective(engine,0.)
    xyz = grid.numpy_coordinates()
    envelope = np.prod([np.cos(np.pi*x/8)**2 for x in xyz],axis=0)
    initial = np.stack([.01*envelope*np.sin(xyz[0]),.01*envelope*np.cos(xyz[1]),-np.ones(grid.shape)],axis=-1)
    initial /= np.linalg.norm(initial,axis=-1,keepdims=True)
    initial[~objective.chart.mask] = objective.chart.template[~objective.chart.mask]
    initial = torch.tensor(initial,device='cuda',dtype=torch.float64)
    settings = {'penalty':20000., 'outer_updates':2, 'maxiter':8, 'maxfun':30,
                'gtol':1e-9, 'ftol':1e-14, 'history_size':5}
    snapshot = root/'checkpoints'/f'{run_id}__smoke_outer1.h5'
    smoke_identity = dict(identity,grid_index=-1,size=7,half_box=4.,scope='engineering vacuum smoke')
    def save(state):
        if state['next_outer']==1:
            save_checkpoint(snapshot,state,smoke_identity)
    uninterrupted = solve_cuda(objective,initial,settings,checkpoint=save)
    resumed = solve_cuda(objective,initial,settings,resume=load_checkpoint(snapshot,smoke_identity))
    errors['resume'] = float((uninterrupted['field']-resumed['field']).abs().max())
    return {'passed':all(error <= tolerances[key] for key,error in errors.items()),
            'errors':errors, 'checks':{key:error <= tolerances[key] for key,error in errors.items()},
            'vacuum_initial_energy':float(sum(engine.energy(initial))),
            'vacuum_final':uninterrupted['metrics'], 'restart_checkpoint':snapshot.relative_to(root).as_posix(),
            'scope':'small CUDA derivative/host-reference and AL-boundary restart test; not a soliton'}


def validate_stationary(config, root, run_id, config_hash, git_commit, resume_path=None):
    import torch
    p = config['parameters']; tolerances = config['tolerances']
    torch.cuda.reset_peak_memory_stats()
    identity = {'task':config['task'],'config_sha256':config_hash,'code_sha256':code_digest(root)}
    resume = load_checkpoint(resume_path,identity) if resume_path else None
    engineering = engineering_checks(root,run_id,identity,tolerances)
    if not engineering['passed']:
        return {'passed':False,'engineering':engineering,'rows':[],
                'reason':'CUDA optimizer/restart engineering check failed',
                'peak_vram_gb':torch.cuda.max_memory_allocated()/1e9}
    rows = resume['state'].get('completed_rows',[]) if resume else []
    first_grid = resume['identity']['grid_index'] if resume else 0
    if not 0 <= first_grid < len(p['sequence']) or len(rows) != first_grid:
        raise ValueError('Invalid source-sequence checkpoint prefix')
    final_checkpoint = None
    for index in range(first_grid,len(p['sequence'])):
        reference = p['sequence'][index]
        n, half_box = reference['size'], reference['half_box']
        grid = PeriodicGrid.paper(n,half_box)
        engine = SpectralEnergy(grid,TorchBackend())
        objective = AugmentedHopfObjective(engine,p['target_charge'])
        initial = compact_hopf(grid,p['profile_scale'],p['profile_radius'])['field']
        initial = torch.tensor(initial,device='cuda',dtype=torch.float64)
        grid_identity = dict(identity,run_id=run_id,git_commit=git_commit,grid_index=index,size=n,
                             half_box=half_box,fft_period=list(grid.box),scope='source stationary sequence')
        if resume and index == first_grid:
            origin = resume['identity']
            if any(origin.get(key) != grid_identity[key] for key in ('grid_index','size','half_box','scope')):
                raise ValueError('Checkpoint source grid mismatch')
        completed_prefix = list(rows)
        def save(state):
            checkpoint_field,_=objective.chart.unpack(state['raw'])
            checkpoint_metrics=objective.metrics(checkpoint_field)
            norm_error=float((torch.sum(checkpoint_field*checkpoint_field,dim=-1)-1).abs().max())
            state = dict(state,completed_rows=completed_prefix,field=checkpoint_field,
                         stationary=False,metrics=checkpoint_metrics)
            path = root/'checkpoints'/f'{run_id}__N{n}__outer{state["next_outer"]}.h5'
            save_checkpoint(path,state,grid_identity)
            return path.relative_to(root).as_posix()
        def progress(row):
            print(json.dumps({'grid':n,'half_box':half_box,**row}),flush=True)
        initial_metrics = objective.metrics(initial)
        solution = solve_cuda(objective,initial,p['solver'],resume=resume if index==first_grid else None,
                              checkpoint=save,progress=progress)
        field = solution['field']
        unit_error = float((torch.sum(field*field,dim=-1)-1).abs().max())
        mask = objective.chart.mask_like(field)
        template = objective.ops.as_like(objective.chart.template,field)
        boundary_error = float((field[~mask]-template[~mask]).abs().max())
        metrics = solution['metrics']
        checks = row_checks(metrics,reference,tolerances,solution['history'],unit_error,boundary_error)
        diagnostics=oracle_comparison(objective,field,solution['multiplier'],p['solver']['penalty'])
        checks.update({key+'_final':diagnostics[key] <= tolerances[key] for key in ('backend','autograd')})
        output_checkpoint=solution['latest_checkpoint'] or str(Path(resume_path).relative_to(root))
        if all(checks.values()):
            candidate=load_checkpoint(root/output_checkpoint,identity)
            accepted_path=root/'checkpoints'/f'{run_id}__N{n}__accepted.h5'
            save_checkpoint(accepted_path,dict(candidate['state'],stationary=True,acceptance=checks),grid_identity)
            output_checkpoint=accepted_path.relative_to(root).as_posix()
        row = {'size':n,'half_box':half_box,'spacing':list(grid.spacing),'fft_period':list(grid.box),
               'initial':initial_metrics,'reference':reference,'final':metrics,
               'relative_energy_error':abs(metrics['energy']-reference['energy'])/reference['energy'],
               'unit_error':unit_error,'boundary_error':boundary_error,
               'history':solution['history'],'checks':checks,'passed':all(checks.values()),
               'final_oracle_diagnostics':diagnostics,'checkpoint_path':output_checkpoint}
        final_checkpoint = row['checkpoint_path']
        rows.append(row)
        print(json.dumps({'grid':n,'accepted':row['passed'],'checks':checks}),flush=True)
        if not row['passed'] and p['stop_on_failed_grid']:
            break
        resume = None
    all_rows = len(rows)==len(p['sequence']) and all(row['passed'] for row in rows)
    virial_improved = all_rows and abs(rows[-1]['final']['virial']) < abs(rows[-2]['final']['virial'])
    return {'passed':bool(engineering['passed'] and all_rows and virial_improved),
            'engineering':engineering,'rows':rows,'source_sequence_complete':all_rows,
            'virial_box_trend':bool(virial_improved),'final_checkpoint':final_checkpoint,
            'not_run_grids':[r['size'] for r in p['sequence'][len(rows):]],
            'source_initializer_available':False,'initializer_equivalence':'UNRESOLVED - independent map',
            'hessian_computed':False,'resume_boundary':'completed AL outer update',
            'peak_vram_gb':torch.cuda.max_memory_allocated()/1e9}
