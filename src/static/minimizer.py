"""Reduced Eq. 70 solver: explicit sphere chart, fixed boundary and AL ledger.

NumPy/SciPy is the small-grid reference. The Torch adapter uses strong-Wolfe
LBFGS and the identical explicit derivatives; CUDA execution is a later gate.
"""
from __future__ import annotations

import math
import numpy as np

from .hopf import HopfInvariant


def tangent(vector, field, ops):
    return vector-ops.sum(vector*field,-1)[...,None]*field


class SphereChart:
    def __init__(self, engine):
        self.engine=engine;self.ops=engine.ops
        self.mask=np.ones(engine.grid.shape,dtype=bool)
        for axis in range(3):
            for face in (0,-1):
                index=[slice(None)]*3;index[axis]=face;self.mask[tuple(index)]=False
        self.template=np.zeros((*engine.grid.shape,3));self.template[...,2]=-1

    def mask_like(self, like):
        return self.ops.as_like(self.mask,like)>0

    def pack(self, field):
        self.engine.check(field)
        mask=self.mask_like(field)
        vacuum=self.ops.as_like(self.template,field)
        if self.ops.any(abs(field[~mask]-vacuum[~mask])>1e-12):
            raise ValueError('Initial field must have the fixed south-pole boundary')
        if self.ops.any(abs(self.ops.sum(field*field,-1)-1)>1e-12):
            raise ValueError('Initial field must be explicitly unit normalized')
        value=field[mask]
        return value.copy() if self.ops.name=='numpy' else value.clone()

    def unpack(self, raw):
        self.ops.check(raw,(3,))
        if tuple(raw.shape)!=(int(self.mask.sum()),3):
            raise ValueError('Exactly three raw coordinates per interior site required')
        norms=self.ops.sqrt(self.ops.sum(raw*raw,-1))
        if self.ops.any(norms<1e-12):
            raise ValueError('Sphere chart crossed its singular origin')
        template=self.ops.as_like(self.template,raw)
        field=template.copy() if self.ops.name=='numpy' else template.clone()
        field[self.mask_like(field)]=raw/norms[...,None]
        return field,norms

    def pullback(self, raw, gradient):
        field,norms=self.unpack(raw)
        return tangent(gradient,field,self.ops)[self.mask_like(field)]/norms[...,None]


class AugmentedHopfObjective:
    def __init__(self, engine, target=-1.):
        if not math.isfinite(target):
            raise ValueError('Finite explicit charge target required')
        self.engine=engine;self.ops=engine.ops;self.hopf=HopfInvariant(engine)
        self.chart=SphereChart(engine);self.target=target

    def value_gradient(self, raw, multiplier, penalty):
        if not math.isfinite(multiplier) or not math.isfinite(penalty) or penalty<=0:
            raise ValueError('Finite multiplier and positive penalty required')
        field,_=self.chart.unpack(raw)
        e2,e4=self.engine.energy(field);q=self.hopf.evaluate(field)['charge']
        error=q-self.target;coefficient=multiplier+penalty*error
        value=e2+e4+multiplier*error+0.5*penalty*error*error
        gradient=self.engine.energy_gradient(field)+coefficient*self.hopf.charge_gradient(field)
        return value,self.chart.pullback(raw,gradient)

    def metrics(self, field):
        mask=self.chart.mask_like(field)
        ge=tangent(self.engine.energy_gradient(field),field,self.ops)[mask]
        gq=tangent(self.hopf.charge_gradient(field),field,self.ops)[mask]
        qnorm2=self.ops.sum(gq*gq,tuple(range(gq.ndim)))
        active=float(qnorm2)>1e-30
        alpha=self.ops.sum(ge*gq,tuple(range(ge.ndim)))/qnorm2 if active else 0.
        residual=(ge-alpha*gq)/self.engine.grid.cell_volume
        e2,e4=self.engine.energy(field);q=self.hopf.evaluate(field)['charge']
        return dict(energy=float(e2+e4),energy2=float(e2),energy4=float(e4),charge=float(q),
                    charge_error=float(q-self.target),charge_gradient_rank=int(active),alpha=float(alpha),
                    constrained_rms=float(self.ops.sqrt(self.ops.sum(residual*residual,
                        tuple(range(residual.ndim)))/residual.numel())) if self.ops.name=='torch' else float(np.sqrt(np.mean(residual**2))),
                    virial=float((e2-e4)/(e2+e4)) if float(e2+e4)>0 else 0.)


def minimize_cpu(objective, initial, *, penalty=2e4, outer_updates=4,
                 maxiter=120,maxfun=180,gtol=1e-10,ftol=1e-14):
    from scipy.optimize import minimize
    if objective.ops.name!='numpy':
        raise ValueError('The CPU adapter requires the NumPy backend')
    raw=objective.chart.pack(initial);multiplier=0.;history=[]
    for outer in range(outer_updates):
        shape=raw.shape
        def oracle(flat):
            value,gradient=objective.value_gradient(flat.reshape(shape),multiplier,penalty)
            return float(value),gradient.reshape(-1)
        start_value=oracle(raw.reshape(-1))[0]
        result=minimize(oracle,raw.reshape(-1),jac=True,method='L-BFGS-B',
                        options=dict(maxiter=maxiter,maxfun=maxfun,gtol=gtol,ftol=ftol,maxls=40))
        field,_=objective.chart.unpack(result.x.reshape(shape))
        metrics=objective.metrics(field);next_multiplier=multiplier+penalty*metrics['charge_error']
        history.append(dict(outer=outer,initial_augmented=start_value,final_augmented=float(result.fun),
                            multiplier_before=multiplier,multiplier_after=next_multiplier,
                            penalty=penalty,inner_success=bool(result.success),inner_message=str(result.message),
                            iterations=int(result.nit),evaluations=int(result.nfev),**metrics))
        multiplier=next_multiplier;raw=objective.chart.pack(field)
    return dict(field=field,history=history,multiplier=multiplier,metrics=objective.metrics(field),
                adapter='SciPy L-BFGS-B unbounded sphere chart; separate equivalence needed for source production')


def minimize_cuda(objective, initial, *, penalty=2e4,outer_updates=4,
                  maxiter=120,maxfun=180,gtol=1e-10,ftol=1e-14):
    import torch
    if objective.ops.name!='torch' or initial.device.type!='cuda':
        raise ValueError('CUDA adapter requires actual CUDA tensors')
    raw=objective.chart.pack(initial);multiplier=0.;history=[]
    for outer in range(outer_updates):
        parameter=torch.nn.Parameter(raw.detach().clone())
        optimizer=torch.optim.LBFGS([parameter],max_iter=maxiter,max_eval=maxfun,
                    tolerance_grad=gtol,tolerance_change=ftol,history_size=100,line_search_fn='strong_wolfe')
        evaluations=0
        def closure():
            nonlocal evaluations
            with torch.no_grad():
                value,gradient=objective.value_gradient(parameter,multiplier,penalty)
                parameter.grad=gradient.detach().clone();evaluations+=1
            return value
        optimizer.step(closure)
        with torch.no_grad():
            field,_=objective.chart.unpack(parameter);metrics=objective.metrics(field)
        next_multiplier=multiplier+penalty*metrics['charge_error']
        history.append(dict(outer=outer,multiplier_before=multiplier,multiplier_after=next_multiplier,
                            penalty=penalty,evaluations=evaluations,**metrics))
        multiplier=next_multiplier;raw=objective.chart.pack(field)
    return dict(field=field,history=history,multiplier=multiplier,metrics=objective.metrics(field),
                adapter='CUDA Torch LBFGS strong_wolfe; actual device validation required')
