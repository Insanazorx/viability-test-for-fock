import numpy as np
from static.spectral import PeriodicGrid
from static.full_field import SixComponentStatic


def validate_full_static(config):
    p=config['parameters'];grid=PeriodicGrid.paper(config['grid'][0],p['half_box'])
    theory=SixComponentStatic(grid,**p['coefficients']);core=theory.core
    worst={key:0. for key in config['tolerances']};rows=[]
    for seed in config['seeds']:
        rng=np.random.default_rng(seed);field=rng.normal(size=(*grid.shape,6))*.3
        u=rng.normal(size=field.shape);u/=np.linalg.norm(u);v=rng.normal(size=field.shape);v/=np.linalg.norm(v)
        gradient=theory.energy_gradient(field);hv=theory.hvp(field,v)
        symmetric=abs(np.sum(u*hv)-np.sum(v*theory.hvp(field,u)))
        worst['hvp_symmetry']=max(worst['hvp_symmetry'],symmetric/max(1,abs(np.sum(u*hv))))
        differences=[]
        for step in p['difference_steps']:
            finite=(sum(theory.energy(field+step*v).values())-sum(theory.energy(field-step*v).values()))/(2*step)
            gv=(theory.energy_gradient(field+step*v)-theory.energy_gradient(field-step*v))/(2*step)
            error=abs(finite-np.sum(gradient*v))/max(1,abs(finite))
            herror=np.linalg.norm(gv-hv)/max(1,np.linalg.norm(hv))
            differences.append(dict(step=step,gradient_error=float(error),hvp_error=float(herror)))
            if step==p['difference_steps'][-1]:
                worst['gradient']=max(worst['gradient'],error);worst['hvp_difference']=max(worst['hvp_difference'],herror)
        rotation,_=np.linalg.qr(rng.normal(size=(4,4)));rotation[:,0]*=np.linalg.det(rotation)
        rotated=core.packed(rotation@core.matrix(field)@rotation.T)
        original=sum(theory.energy(field).values());new=sum(theory.energy(rotated).values())
        worst['so4_energy']=max(worst['so4_energy'],abs(new-original)/max(1,abs(original)))
        nplus=rng.normal(size=(32,3));nplus/=np.linalg.norm(nplus,axis=-1,keepdims=True)
        nminus=rng.normal(size=(32,3));nminus/=np.linalg.norm(nminus,axis=-1,keepdims=True)
        dplus=rng.normal(size=(32,3,3));dminus=rng.normal(size=dplus.shape)
        dplus-=np.sum(dplus*nplus[:,None,:],axis=-1,keepdims=True)*nplus[:,None,:]
        dminus-=np.sum(dminus*nminus[:,None,:],axis=-1,keepdims=True)*nminus[:,None,:]
        sigma=theory.sigma0;length=np.sqrt(theory.zeta/(8*theory.z_m*sigma*sigma))
        prefactor=theory.z_m*sigma*sigma*length/2
        lifted=core.lift_reduced(nplus,nminus,sigma0=sigma)
        dM=core.from_dual_vectors(sigma/np.sqrt(2)*dplus/length,sigma/np.sqrt(2)*dminus/length)
        expected=sum(sum(core.reduced_energy(n,d)) for n,d in ((nplus,dplus),(nminus,dminus)))
        actual=length**3*(core.static_two_derivative(dM,theory.z_m)+core.static_quartic(dM,sigma,theory.zeta))/prefactor
        worst['heavy_reduction']=max(worst['heavy_reduction'],np.max(abs(actual-expected)/np.maximum(1,abs(expected))))
        worst['fock_potential']=max(worst['fock_potential'],float(np.max(theory.potential(lifted))))
        vacuum=np.zeros(6);vacuum[0]=sigma
        radial=vacuum/sigma;pf=core.hodge(radial)
        radial_h=theory.potential_hvp(vacuum,radial)/theory.z_m
        pf_h=theory.potential_hvp(vacuum,pf)/theory.z_m
        mass_error=max(np.max(abs(radial_h-2*theory.alpha*sigma*sigma/theory.z_m*radial)),np.max(abs(pf_h-2*theory.mu*sigma*sigma/theory.z_m*pf)))
        worst['normal_masses']=max(worst['normal_masses'],mass_error)
        rows.append(dict(seed=seed,energy_decomposition={k:float(v) for k,v in theory.energy(field).items()},differences=differences,
                         reduced_length=float(length),reduced_energy_prefactor=float(prefactor)))
    checks={key:float(value)<=config['tolerances'][key] for key,value in worst.items()}
    return dict(passed=all(checks.values()),checks=checks,worst_errors={k:float(v) for k,v in worst.items()},rows=rows,
                coefficients=p['coefficients'],cuda_executed=False,stationary_solution=False,finite_stiffness_branch_passed=False,
                scalar_background='fixed final lambda encoded by positive mu; chi=0; additive scalar vacuum energy subtracted',
                dense_lattice_hessian_allocated=False)
