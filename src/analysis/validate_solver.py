"""Identified small-grid solver/HVP/independent-DFT engineering validation."""
import numpy as np

from static.spectral import PeriodicGrid,SpectralEnergy
from static.hopf import HopfInvariant
from static.hopf_initial import compact_hopf
from static.minimizer import AugmentedHopfObjective,minimize_cpu
from hessian.reduced import energy_hvp,charge_hvp,TangentChargeHessian
from .direct_reference import direct_observables


def validate_solver(config):
    p=config['parameters'];t=config['tolerances'];rows=[];smokes=[]
    worst={key:0. for key in t}
    for seed in config['seeds']:
        rng=np.random.default_rng(seed)
        grid=PeriodicGrid.paper(p['oracle_grid'],p['half_box']);engine=SpectralEnergy(grid)
        field=compact_hopf(grid)['field'];direction=rng.normal(size=field.shape)
        direction/=np.linalg.norm(direction);other=rng.normal(size=field.shape);other/=np.linalg.norm(other)
        hopf=HopfInvariant(engine);direct=direct_observables(field,grid.spacing[0])
        e=sum(engine.energy(field));q=hopf.evaluate(field)['charge']
        worst['direct_energy']=max(worst['direct_energy'],abs(e-direct['energy'])/max(1,abs(e)))
        worst['direct_charge']=max(worst['direct_charge'],abs(q-direct['charge']))
        derivative_rows=[]
        for label,gradient,hvp in (('energy',engine.energy_gradient,energy_hvp),('charge',hopf.charge_gradient,charge_hvp)):
            expected=np.sum(gradient(field)*direction);hv=hvp(engine,field,direction)
            symmetry=abs(np.sum(other*hv)-np.sum(direction*hvp(engine,field,other)))
            worst['hvp_symmetry']=max(worst['hvp_symmetry'],symmetry)
            for step in p['difference_steps']:
                reference=(direct_observables(field+step*direction,grid.spacing[0])[label]-
                           direct_observables(field-step*direction,grid.spacing[0])[label])/(2*step)
                finite=(gradient(field+step*direction)-gradient(field-step*direction))/(2*step)
                derivative_rows.append(dict(quantity=label,step=step,directional_error=float(abs(reference-expected)/max(1,abs(expected))),
                                             hvp_relative=float(np.linalg.norm(finite-hv)/max(1,np.linalg.norm(hv)))))
                if step==p['difference_steps'][-1]:
                    worst['direct_directional']=max(worst['direct_directional'],abs(reference-expected)/max(1,abs(expected)))
                    worst['hvp_difference']=max(worst['hvp_difference'],np.linalg.norm(finite-hv)/max(1,np.linalg.norm(hv)))
        objective=AugmentedHopfObjective(engine)
        raw=objective.chart.pack(field);v=rng.normal(size=raw.shape);v/=np.linalg.norm(v)
        value,g=objective.value_gradient(raw,0.7,200.)
        step=p['difference_steps'][-1]
        finite=(objective.value_gradient(raw+step*v,0.7,200.)[0]-objective.value_gradient(raw-step*v,0.7,200.)[0])/(2*step)
        worst['chart_gradient']=max(worst['chart_gradient'],abs(finite-np.sum(g*v))/max(1,abs(finite)))
        hessian=TangentChargeHessian(engine,field,alpha=0.3)
        u=rng.normal(size=(*grid.shape,2));v2=rng.normal(size=u.shape)
        hu=hessian.apply(u);hv2=hessian.apply(v2)
        error=abs(np.sum(u*hv2)-np.sum(v2*hu))/max(1,abs(np.sum(u*hv2)),abs(np.sum(v2*hu)))
        worst['projected_symmetry']=max(worst['projected_symmetry'],error)
        projected=hessian.project(u)
        worst['charge_projection']=max(worst['charge_projection'],abs(np.sum(projected*hessian.q))/max(1,np.linalg.norm(projected)*np.linalg.norm(hessian.q)))
        # Independently differentiate the retracted two-coordinate gradient.
        direction2=hessian.to_field(u);nplus=field+step*direction2;nminus=field-step*direction2
        nplus/=np.linalg.norm(nplus,axis=-1,keepdims=True);nminus/=np.linalg.norm(nminus,axis=-1,keepdims=True)
        def chart_gradient(n,sign):
            ambient=engine.energy_gradient(n)-0.3*hopf.charge_gradient(n)
            norm=np.linalg.norm(field+sign*step*direction2,axis=-1,keepdims=True)
            physical=(ambient-n*np.sum(ambient*n,axis=-1,keepdims=True))/norm
            return hessian.to_coefficients(physical)*hessian.mask[...,None]
        finite=(chart_gradient(nplus,1)-chart_gradient(nminus,-1))/(2*step)
        expected=hessian.apply(u,charge_project=False)
        worst['retracted_hvp']=max(worst['retracted_hvp'],np.linalg.norm(finite-expected)/max(1,np.linalg.norm(expected)))
        rows.append(dict(seed=seed,grid=list(grid.shape),raw_charge=float(q),direct=direct,derivative_checks=derivative_rows,
                         charge_resolved_as_unit=False,stationary=False))
        grid=PeriodicGrid.paper(p['smoke_grid'],p['half_box']);engine=SpectralEnergy(grid)
        xyz=grid.numpy_coordinates();envelope=np.prod([np.cos(np.pi*x/(2*p['half_box']))**2 for x in xyz],axis=0)
        initial=np.stack([p['smoke_amplitude']*envelope*np.sin(xyz[0]),p['smoke_amplitude']*envelope*np.cos(xyz[1]),-np.ones(grid.shape)],axis=-1)
        initial/=np.linalg.norm(initial,axis=-1,keepdims=True)
        objective=AugmentedHopfObjective(engine,target=0.);initial[~objective.chart.mask]=objective.chart.template[~objective.chart.mask]
        initial_energy=sum(engine.energy(initial))
        result=minimize_cpu(objective,initial,penalty=p['penalty'],outer_updates=p['outer_updates'],
                            maxiter=p['maxiter'],maxfun=p['maxfun'],gtol=p['gtol'],ftol=p['ftol'])
        final=result['field'];metrics=result['metrics']
        worst['smoke_residual']=max(worst['smoke_residual'],metrics['constrained_rms'])
        worst['smoke_energy_fraction']=max(worst['smoke_energy_fraction'],metrics['energy']/initial_energy)
        worst['unit_error']=max(worst['unit_error'],np.max(abs(np.sum(final*final,axis=-1)-1)))
        worst['boundary_error']=max(worst['boundary_error'],np.max(abs(final[~objective.chart.mask]-objective.chart.template[~objective.chart.mask])))
        worst['multiplier_update']=max(worst['multiplier_update'],max(abs(row['multiplier_after']-row['multiplier_before']-p['penalty']*row['charge_error']) for row in result['history']))
        smokes.append(dict(seed=seed,initial_energy=float(initial_energy),**metrics,history=result['history'],target_charge=0.))
    checks={key:float(error)<=t[key] for key,error in worst.items()}
    return dict(passed=all(checks.values()),checks=checks,worst_errors={k:float(v) for k,v in worst.items()},
                oracle_rows=rows,vacuum_smokes=smokes,cuda_executed=False,published_stationary_sequence_reproduced=False,
                physical_spectrum_computed=False,dense_hessian_allocated=False,
                source_production_defaults=dict(outer_updates=4,penalty=2e4,maxiter=120,maxfun=180,gtol=1e-10,ftol=1e-14))
