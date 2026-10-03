"""Small-grid unit Hopf/closure tests with independent continuum references."""
from __future__ import annotations

import math
from pathlib import Path
import numpy as np

from core.backends import NumpyBackend,TorchBackend
from static.spectral import PeriodicGrid,SpectralEnergy
from static.hopf import HopfInvariant
from static.hopf_initial import compact_hopf,continuum_degree


def validate_hopf(config,checkpoint_path=None,run_id=None,config_sha256=None):
    cuda=config['machine']=='RTX5070'
    if cuda:
        import torch
        if not torch.cuda.is_available():
            raise ValueError('Actual CUDA is required')
        torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats()
    backend=TorchBackend('cuda') if cuda else NumpyBackend()
    p=config['parameters'];radius=p['profile_radius'];scale=p['profile_scale'];half_box=p['half_box']

    def tensor(value):
        return torch.as_tensor(value,dtype=torch.float64,device='cuda') if cuda else value

    def array(value):
        return value.detach().cpu().numpy() if cuda and torch.is_tensor(value) else np.asarray(value)

    def scalar(value):
        return float(array(value))

    def normalized(a,b):
        return float(np.max(abs(array(a)-np.asarray(b)))/max(1.,float(np.max(abs(b)))))

    def evaluate(hopf,n):
        result=hopf.evaluate(tensor(n))
        return scalar(result['charge']),{key:scalar(v) for key,v in result['diagnostics'].items()}

    continuum=continuum_degree(scale,radius)
    rows=[]
    worst={'unit_error':0.,'boundary_error':0.,'gauge_relative':0.,'fourier_difference':0.,
           'analytic_density_identity':0.,'helical_inverse':0.,'reflection_sign':0.,'antipodal_invariance':0.,
           'trivial_charge':0.,'gradient_directional':0.,'continuum_degree_error':abs(continuum['degree']+1)}
    if cuda:
        worst.update(backend=0.,autograd=0.)
    for size in p['resolution_sequence']:
        grid=PeriodicGrid.paper(size,half_box)
        engine=SpectralEnergy(grid,backend);hopf=HopfInvariant(engine)
        data=compact_hopf(grid,scale,radius)
        n=data['field'];charge,diagnostics=evaluate(hopf,n)
        b_exact=engine.core.magnetic_field(engine.core.field_strength(tensor(n),tensor(data['derivatives'])))
        analytic_charge=scalar(engine.core.hopf_functional(tensor(data['analytic_potential']),b_exact,grid.cell_volume))
        degree=float(grid.cell_volume*np.sum(data['degree_density']))
        density=array(engine.ops.sum(tensor(data['analytic_potential'])*b_exact,-1))/(16*math.pi**2)
        worst['analytic_density_identity']=max(worst['analytic_density_identity'],normalized(density,data['degree_density']))
        worst['unit_error']=max(worst['unit_error'],float(np.max(abs(np.sum(n*n,-1)-1))))
        for i in range(3):
            for end in (0,-1):
                worst['boundary_error']=max(worst['boundary_error'],float(np.max(abs(np.take(n,end,axis=i)-[0,0,-1]))))
        worst['gauge_relative']=max(worst['gauge_relative'],diagnostics['gauge_relative'])
        worst['fourier_difference']=max(worst['fourier_difference'],diagnostics['fourier_charge_difference'])
        rows.append({'grid':[size]*3,'half_box':half_box,'spacing':grid.spacing[0],'fft_period':grid.box[0],
                     'charge':charge,'charge_error':abs(charge+1),'analytic_berry_charge':analytic_charge,
                     'analytic_s3_degree':degree,'diagnostics':diagnostics})
        if cuda:
            reference=HopfInvariant(SpectralEnergy(grid)).evaluate(n)
            worst['backend']=max(worst['backend'],normalized(charge,reference['charge']))

    # The last data/grid are the baseline saved for a later solver, not a stationary field.
    grid=PeriodicGrid.paper(p['resolution_sequence'][-1],half_box)
    engine=SpectralEnergy(grid,backend);hopf=HopfInvariant(engine)
    data=compact_hopf(grid,scale,radius);n=data['field']
    deformation_rows=[]
    closure_rows=[rows[-1]['diagnostics']]
    for seed in config['seeds']:
        rng=np.random.default_rng(seed)
        coordinates=grid.numpy_coordinates()
        raw=np.stack([sum(coefficient*np.sin(math.pi*x/half_box) for coefficient,x in zip(rng.normal(size=3),coordinates))
                      for _ in range(3)],axis=-1)*data['bump'][...,None]
        tangent=raw-n*np.sum(n*raw,axis=-1,keepdims=True)
        shifted=n+p['deformation_amplitude']*tangent
        shifted/=np.linalg.norm(shifted,axis=-1,keepdims=True)
        charge,diagnostics=evaluate(hopf,shifted)
        closure_rows.append(diagnostics)
        deformation_rows.append({'seed':seed,'charge':charge,'difference_from_baseline':abs(charge-rows[-1]['charge']),
                                 'max_tangent_step':float(np.max(np.linalg.norm(p['deformation_amplitude']*tangent,axis=-1))),
                                 'diagnostics':diagnostics})
    warped_coordinates=[x+amplitude*np.sin(math.pi*x/half_box) for x,amplitude in zip(grid.numpy_coordinates(),p['coordinate_deformation'])]
    warped=compact_hopf(grid,scale,radius,warped_coordinates)['field']
    warped_charge,warped_diagnostics=evaluate(hopf,warped)
    closure_rows.append(warped_diagnostics)
    deformation_rows.append({'kind':'orientation-preserving coordinate deformation','charge':warped_charge,
                             'difference_from_baseline':abs(warped_charge-rows[-1]['charge']),'diagnostics':warped_diagnostics})
    reflected,_=evaluate(hopf,np.flip(n,axis=0).copy())
    antipodal,_=evaluate(hopf,-n)
    worst['reflection_sign']=abs(reflected+rows[-1]['charge'])
    worst['antipodal_invariance']=abs(antipodal-rows[-1]['charge'])
    theta=.3*data['bump']
    trivial=np.stack([np.sin(theta),theta*0,-np.cos(theta)],axis=-1)
    vacuum=n*0;vacuum[...,2]=-1
    worst['trivial_charge']=max(abs(evaluate(hopf,trivial)[0]),abs(evaluate(hopf,vacuum)[0]))

    _,_,z=grid.numpy_coordinates();k=2*math.pi/grid.box[2]
    a=np.stack([np.cos(k*z),np.sin(k*z),z*0],axis=-1)
    helical=hopf.from_magnetic(tensor(-k*a))
    expected=-k*grid.volume/(16*math.pi**2)
    worst['helical_inverse']=max(normalized(helical['potential'],a),normalized(helical['charge'],expected))
    # Off-S2 dense polynomial variation gives a nonzero independent gradient check.
    small=PeriodicGrid.paper(9,half_box);small_hopf=HopfInvariant(SpectralEnergy(small,backend))
    gradient_rows=[]
    for seed in config['seeds']:
        rng=np.random.default_rng(seed);field=rng.normal(size=(*small.shape,3))*.2
        direction=rng.normal(size=field.shape)*.03
        grad=small_hopf.charge_gradient(tensor(field));analytic=float(np.sum(array(grad)*direction))
        steps=[]
        for step in p['gradient_steps']:
            plus=scalar(small_hopf.evaluate(tensor(field+step*direction),require_unit=False)['charge'])
            minus=scalar(small_hopf.evaluate(tensor(field-step*direction),require_unit=False)['charge'])
            fd=(plus-minus)/(2*step)
            steps.append({'step':step,'analytic':analytic,'central_difference':fd,'normalized_error':abs(fd-analytic)/max(1,abs(analytic))})
        worst['gradient_directional']=max(worst['gradient_directional'],steps[-1]['normalized_error'])
        gradient_rows.append({'seed':seed,'steps':steps})
        if cuda:
            leaf=tensor(field).detach().clone().requires_grad_(True)
            autodiff=torch.autograd.grad(small_hopf.evaluate(leaf,require_unit=False)['charge'],leaf)[0]
            worst['autograd']=max(worst['autograd'],normalized(grad,array(autodiff)))
            worst['backend']=max(worst['backend'],normalized(grad,HopfInvariant(SpectralEnergy(small)).charge_gradient(field)))
    worst.update(unit_charge=rows[-1]['charge_error'],charge_refinement=abs(rows[-1]['charge']-rows[-2]['charge']),
                 analytic_charge=abs(rows[-1]['analytic_berry_charge']+1),
                 smooth_deformation=max(abs(row['charge']+1) for row in deformation_rows),
                 deformation_drift=max(row['difference_from_baseline'] for row in deformation_rows),
                 curl_relative=max(row['curl_relative'] for row in closure_rows),
                 divergence_relative=max(row['divergence_relative'] for row in closure_rows),
                 harmonic_fraction=max(row['harmonic_fraction'] for row in closure_rows))
    checks={key:worst[key]<=limit for key,limit in config['tolerances'].items()}
    improvement=rows[0]['charge_error']/max(rows[-1]['charge_error'],1e-30)
    checks.update(charge_refines=improvement>=p['minimum_charge_improvement'],
                  coordinate_map_orientation=all(abs(amplitude)*math.pi/half_box<1 for amplitude in p['coordinate_deformation']),
                  continuum_quadrature_controlled=continuum['quadrature_error_estimate']<=1e-10)
    result={'passed':all(checks.values()),'checks':checks,'worst_errors':worst,'resolution_sequence':rows,
            'deformations':deformation_rows,'reflected_charge':reflected,'antipodal_charge':antipodal,
            'continuum_reference':continuum,'charge_improvement':improvement,'gradient_checks':gradient_rows,
            'initializer':'independently derived compact unit-Hopf map; no archived paper initializer available',
            'cuda_verified':cuda,'stationary_solution_evaluated':False}
    if checkpoint_path:
        import h5py
        path=Path(checkpoint_path)
        path.parent.mkdir(parents=True,exist_ok=True)
        with h5py.File(path,'x') as stream:
            stream.create_dataset('n',data=n,compression='gzip',shuffle=True)
            stream.attrs.update(run_id=run_id,config_sha256=config_sha256,initializer=result['initializer'],
                                charge=rows[-1]['charge'],half_box=half_box,spacing=grid.spacing[0],
                                fft_period=grid.box[0],profile_scale=scale,profile_radius=radius,stationary=False)
        path.chmod(0o444)
    if cuda:
        torch.cuda.synchronize();result['peak_vram_gb']=torch.cuda.max_memory_allocated()/1e9
    return result
