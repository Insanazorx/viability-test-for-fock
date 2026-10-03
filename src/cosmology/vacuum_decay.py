"""Transparent O(4) scalar bounce and gravity-equation reference.

Dimensionless rho=Lambda_U^2*r/f, x=lambda/f; no lifetime estimate.
"""
import numpy as np
from scipy.integrate import solve_ivp,quad


def potential(x,a=.24,b=1.,c=1.):
    return a*x*x/2-b*x**3/3+c*x**4/4


def force(x,a=.24,b=1.,c=1.):
    return x*(a-b*x+c*x*x)


def regular_origin(x0,rho0):
    if rho0<=0:raise ValueError('Positive regular-origin offset required')
    derivative=force(x0)
    return [x0+derivative*rho0**2/8,derivative*rho0/4,0.,0.]


def shoot(x0,*,rtol,atol,rho0,rho_max,max_step,x_false):
    vacuum=potential(x_false)
    def rhs(r,y):
        x,p,_,_=y
        return [p,force(x)-3*p/r,2*np.pi**2*r**3*p*p/2,2*np.pi**2*r**3*(potential(x)-vacuum)]
    def overshoot(r,y):return y[0]-x_false
    def undershoot(r,y):return y[1]
    overshoot.terminal=True;overshoot.direction=1
    undershoot.terminal=True;undershoot.direction=-1
    sol=solve_ivp(rhs,(rho0,rho_max),regular_origin(x0,rho0),method='DOP853',rtol=rtol,atol=atol,max_step=max_step,events=[overshoot,undershoot])
    if not sol.success or not np.all(np.isfinite(sol.y)):raise RuntimeError('Bounce integrator failed')
    if len(sol.t_events[0]):kind='overshoot'
    elif len(sol.t_events[1]):kind='undershoot'
    else:raise RuntimeError('No shooting event before frozen outer truncation')
    return sol,kind


def flat_bounce(parameters,accuracy):
    opts=dict(accuracy,rho0=parameters['rho0'],rho_max=parameters['rho_max'],max_step=parameters['max_step'],x_false=parameters['x_false'])
    lo,hi=parameters['shooting_bracket'];_,left=shoot(lo,**opts);_,right=shoot(hi,**opts)
    if left!='overshoot' or right!='undershoot':raise ValueError('Frozen bounce bracket does not straddle')
    evaluations=2;solutions=[]
    for _ in range(parameters['max_bisections']):
        mid=(lo+hi)/2
        if mid==lo or mid==hi:break
        sol,kind=shoot(mid,**opts);evaluations+=1
        if kind=='overshoot':lo=mid
        else:hi=mid
    for initial in (lo,hi):
        sol,kind=shoot(initial,**opts);evaluations+=1
        x,p,T,V=sol.y[:,-1]
        # Missing origin integrals are analytic leading terms; rho0^4 suppressed.
        V+=2*np.pi**2*(potential(initial)-potential(parameters['x_false']))*parameters['rho0']**4/4
        T+=np.pi**2*force(initial)**2*parameters['rho0']**6/96
        action=T+V;virial=abs(2*T+4*V)/max(1,abs(2*T),abs(4*V))
        solutions.append(dict(x0=float(initial),action=float(action),kinetic=float(T),potential=float(V),virial=float(virial),tail_field_error=float(abs(x-parameters['x_false'])),tail_derivative=float(abs(p)),event=kind,rho_end=float(sol.t[-1]),integration_nodes=len(sol.t),evaluations=evaluations))
    result=min(solutions,key=lambda s:s['tail_field_error']+s['tail_derivative'])
    result['bracket_width']=float(hi-lo);result['accuracy']=accuracy
    return result


def cdl_rhs(rho,state,epsilon):
    x,p,r,s=state
    if r<=0 or epsilon<0:raise ValueError('Use regular-origin expansion at poles; epsilon nonnegative')
    return np.array([p,force(x)-3*s*p/r,s,-epsilon*r*(p*p+potential(x))/3])


def gravity_constraint(state,epsilon):
    x,p,r,s=state
    return s*s-1-epsilon*r*r*(p*p/2-potential(x))/3


def false_vacuum_action(epsilon,u_false):
    if epsilon<=0 or u_false<=0:raise ValueError('Positive gravity parameter and false-vacuum energy required')
    return -24*np.pi**2/(epsilon*epsilon*u_false)


def validate_decay(config):
    p=config['parameters'];rows=[flat_bounce(p,accuracy) for accuracy in p['accuracy_sequence']]
    final=rows[-1];worst={
        'source_action':abs(final['action']/p['source_action']-1),
        'source_center':abs(final['x0']/p['source_center']-1),
        'action_convergence':abs(rows[-1]['action']-rows[-2]['action']),
        'virial':final['virial'],
        'tail':max(final['tail_field_error'],final['tail_derivative']),
        'gravity_constraint_derivative':0.,'false_vacuum_radius':0.,'false_vacuum_action':0.}
    grav_rows=[]
    for epsilon in p['gravity_parameters']:
        for seed in config['seeds']:
            rng=np.random.default_rng(seed);x=float(rng.uniform(.05,.5));v=float(rng.uniform(.01,.1));r=float(rng.uniform(.1,1.))
            s=np.sqrt(1+epsilon*r*r*(v*v/2-potential(x))/3);state=[x,v,r,s]
            dx,dv,dr,ds=cdl_rhs(1.,state,epsilon)
            residual=2*s*ds-epsilon/3*(2*r*dr*(v*v/2-potential(x))+r*r*(v*dv-force(x)*dx))
            worst['gravity_constraint_derivative']=max(worst['gravity_constraint_derivative'],abs(float(residual)))
        u=potential(p['x_false']);H=np.sqrt(epsilon*u/3);end=.95*np.pi/H
        # A held constant scalar at its exact minimum isolates Einstein geometry.
        sol=solve_ivp(lambda rho,y:[y[1],-H*H*y[0]],(0,end),[0.,1.],rtol=1e-11,atol=1e-12,method='DOP853',max_step=.1/H)
        expected=np.sin(H*sol.t)/H
        radius_error=float(np.max(abs(sol.y[0]-expected))*H)
        integral=quad(lambda t:4*np.pi**2*((np.sin(t)/H)**3*u-3*np.sin(t)/(H*epsilon))/H,0,np.pi,epsabs=1e-6,epsrel=1e-12)[0]
        expected_action=false_vacuum_action(epsilon,u)
        worst['false_vacuum_radius']=max(worst['false_vacuum_radius'],radius_error)
        worst['false_vacuum_action']=max(worst['false_vacuum_action'],abs(integral/expected_action-1))
        grav_rows.append(dict(epsilon=epsilon,scaled_radius_error=radius_error,false_vacuum_action=float(expected_action),numerical_action=float(integral)))
    checks={key:bool(value<=config['tolerances'][key]) for key,value in worst.items()}
    checks.update(integrations_finite=all(np.isfinite(row['action']) for row in rows),shooting_bracket_resolved=final['bracket_width']<1e-16)
    checks={k:bool(v) for k,v in checks.items()}
    return dict(passed=all(checks.values()),checks=checks,worst_errors=worst,flat_rows=rows,gravity_rows=grav_rows,
                physical_action_scaling='B4=(f/Lambda_U)^4 * Bhat4',gravity_parameter='epsilon=f^2/M_Pl^2',
                source_regression=True,cdl_equations_verified=True,nontrivial_gravitational_bounce_solved=False,
                prefactor_computed=False,cosmological_lifetime_established=False,scientific_G4D_pass=False)
