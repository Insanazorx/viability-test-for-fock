"""Constant-background scalar one-loop EFT diagnostics, MSbar.

No matter/derivative/curvature matching or physical viability claim.
"""
import numpy as np
from core.scalar_potential import ScalarPotential


def scalar_loop(mass2,scale):
    y=np.asarray(mass2,dtype=np.float64)
    if not np.isfinite(scale) or scale<=0 or not np.all(np.isfinite(y)):
        raise ValueError('Finite mass spectrum and positive renormalization scale required')
    if np.any(y<0):
        raise ValueError('Negative squared mass: unstable real-potential domain; no abs prescription')
    positive=y[y>0];value=np.sum(positive**2*(np.log(positive/scale**2)-1.5))/(64*np.pi**2)
    pole=np.sum(y*y)/(64*np.pi**2)
    return dict(value=float(value),counterterm_pole_coefficient=float(pole),
                d_dlog_scale=float(-2*pole),zero_modes=int(np.sum(y==0)))


def threshold_curvature(theory,scale):
    return -theory.kappa*theory.m_chi2/(16*np.pi**2)*(np.log(theory.m_chi2/scale**2)-1)


def scalar_loop_derivatives(y,dy,ddy,scale):
    if y<=0:
        raise ValueError('Positive scalar squared mass required')
    logarithm=np.log(y/scale**2)
    return (y*dy*(logarithm-1)/(32*np.pi**2),
            (dy*dy*logarithm+y*ddy*(logarithm-1))/(32*np.pi**2))


def validate_radiative(config):
    p=config['parameters'];theory=ScalarPotential(**p['coefficients']);worst={k:0. for k in config['tolerances']};rows=[]
    for seed in config['seeds']:
        rng=np.random.default_rng(seed)
        fields=np.r_[rng.normal(size=6)*.25,rng.uniform(.05,.8),rng.uniform(-.4,.4)]
        _,g,h,_=theory.evaluate(fields);v=rng.normal(size=8);v/=np.linalg.norm(v)
        diffs=[]
        for step in p['difference_steps']:
            vp,gp,_,_=theory.evaluate(fields+step*v);vm,gm,_,_=theory.evaluate(fields-step*v)
            eg=abs((vp-vm)/(2*step)-np.dot(g,v))/max(1,abs(np.dot(g,v)))
            eh=np.linalg.norm((gp-gm)/(2*step)-h@v)/max(1,np.linalg.norm(h@v))
            diffs.append(dict(step=step,gradient=float(eg),hessian=float(eh)))
        worst['potential_gradient']=max(worst['potential_gradient'],diffs[-1]['gradient'])
        worst['potential_hessian']=max(worst['potential_hessian'],diffs[-1]['hessian'])
        worst['hessian_symmetry']=max(worst['hessian_symmetry'],float(np.max(abs(h-h.T))))
        rows.append(dict(seed=seed,derivative_sequence=diffs))
    xv=(theory.b+np.sqrt(theory.b**2-4*theory.a*theory.c))/(2*theory.c)
    vacuum=np.r_[theory.sigma0,np.zeros(5),xv*theory.f,0.]
    V,g,h,canonical=theory.evaluate(vacuum);spectrum=np.linalg.eigvalsh(canonical)
    # Analytic exact zeros at the Fock vacuum, not an arbitrary eigenvalue clamp.
    expected=np.sort(np.r_[np.zeros(4),2*theory.alpha*theory.sigma0**2/theory.z_m,2*theory.mu(vacuum[6])[0]*theory.sigma0**2/theory.z_m,theory.u(vacuum[6])[2],theory.m_chi2-theory.kappa*vacuum[6]**2])
    worst['vacuum_spectrum']=float(np.max(abs(spectrum-expected)))
    scales=[]
    for scale in p['renormalization_scales']:
        loop=scalar_loop(expected,scale)
        delta=p['scale_difference_step'];plus=scalar_loop(expected,scale*np.exp(delta));minus=scalar_loop(expected,scale*np.exp(-delta))
        worst['scale_derivative']=max(worst['scale_derivative'],abs((plus['value']-minus['value'])/(2*delta)-loop['d_dlog_scale']))
        curvature=threshold_curvature(theory,scale)
        def chi_value(lam):return scalar_loop([theory.m_chi2-theory.kappa*lam*lam],scale)['value']
        step=p['curvature_difference_step'];finite=(chi_value(step)-2*chi_value(0.)+chi_value(-step))/step**2
        worst['threshold_curvature']=max(worst['threshold_curvature'],abs(finite-curvature))
        y,dy,ddy=theory.u(vacuum[6])[2:];tadpole,mass=scalar_loop_derivatives(y,dy,ddy,scale)
        def scalar_value(lam):return scalar_loop([theory.u(lam)[2]],scale)['value']
        step=p['curvature_difference_step'];lam=vacuum[6]
        finite_tad=(scalar_value(lam+step)-scalar_value(lam-step))/(2*step)
        finite_mass=(scalar_value(lam+step)-2*scalar_value(lam)+scalar_value(lam-step))/step**2
        worst['scalar_derivatives']=max(worst['scalar_derivatives'],abs(finite_tad-tadpole),abs(finite_mass-mass))
        scales.append(dict(scale=scale,**loop,chi_threshold_delta_lambda_mass2=float(curvature),scalar_tadpole=float(tadpole),scalar_delta_lambda_mass2=float(mass),
                           illustrative_vacuum_cancellation_ratio=float(abs(loop['value'])/V),physical_tuning_measure=False))
    negative_rejected=False
    # UV pole is polynomial in the Hessian even on off-shell unstable backgrounds.
    # Equal C1, different C2 isolates the lower switching counterterm.
    base=np.r_[np.sqrt(.5),np.zeros(5),0.,0.]
    pf=base.copy();pf[0]=pf[5]=.5
    def trace_difference(lam):
        a=base.copy();b=pf.copy();a[6]=b[6]=lam
        ha=theory.evaluate(a)[3];hb=theory.evaluate(b)[3]
        return float(np.sum(hb*hb)-np.sum(ha*ha))
    delta=p['switch_difference_step']
    observed=(trace_difference(delta)+trace_difference(-delta)-2*trace_difference(0.))/(2*delta**2*.25**2)
    expected_switch=24*theory.mu_v/(theory.f*theory.x_mu)**4*theory.u(0.)[2]
    worst['lower_switch_counterterm']=abs(observed-expected_switch)/max(1,abs(expected_switch))
    try:scalar_loop([-1.],1.)
    except ValueError:negative_rejected=True
    checks={key:bool(value<=config['tolerances'][key]) for key,value in worst.items()}
    checks.update(negative_mass_rejected=negative_rejected,four_tangent_zeros=int(np.sum(expected==0))==4,
                  stable_test_vacuum=bool(np.all(expected>=0) and np.linalg.norm(g)<1e-12),
                  chi_linear_mixing_absent=bool(np.max(abs(h[7,:7]))==0))
    return dict(passed=all(checks.values()),checks=checks,worst_errors=worst,derivative_rows=rows,
                canonical_vacuum_mass2=expected.tolist(),vacuum_energy=V,scale_rows=scales,
                lower_switch_uv_pole=dict(trace_mass4_lambda2_C2_squared=float(observed),analytic=float(expected_switch),backgrounds='equal C1; different C2; off-shell pole only, no unstable finite real potential'),
                renormalization_conditions=['V_eff(lambda_v)=specified vacuum density','V_eff_prime(lambda_v)=0','V_eff_second(lambda_v)=specified curvature','mu_eff^(n)(0)=specified matching for n=0..3','Xi higher coefficients and kinetic/curvature/portal coefficients matched separately'],
                switching_one_loop_result='A lambda determinant expanded at small lambda contains 12*mu4*lambda^2*C2^2 times m_lambda^2*(log(m_lambda^2/Q^2)-1)/(32*pi^2). Lower quadratic onset is generally present; constant/linear terms are not asserted from this diagram.',
                wilsonian_sensitivity='Delta lambda mass2 from chi tadpole = -kappa*[Lambda_cut^2-m_chi^2*log(1+Lambda_cut^2/m_chi^2)]/(16*pi^2); cutoff/matching are unknown physical inputs, distinct from MSbar.',
                missing_inputs=['concrete L_m','physical f,Lambda_U,sigma0,m_chi,portal Lambda','UV cutoff/matching coefficients','retained soliton/production parameter region'],
                matter_portal_matching_complete=False,curvature_derivative_matching_complete=False,
                parameters_are_illustrative=True,physical_viability='PARTIAL / UNRESOLVED')
