"""Manufactured-field validation; no Hopf charge or soliton solve is claimed."""
from __future__ import annotations

import math
import numpy as np

from core.backends import NumpyBackend, TorchBackend
from static.spectral import PeriodicGrid, SpectralEnergy, centered_reference_gradient


def unit_two_angle(grid):
    x, y, z = grid.numpy_coordinates()
    k, ell = 2*math.pi/grid.box[0], 2*math.pi/grid.box[1]
    theta, phi = k*x, ell*y
    n = np.stack((np.sin(theta)*np.cos(phi), np.sin(theta)*np.sin(phi), np.cos(theta)), axis=-1)
    dtheta = np.stack((np.cos(theta)*np.cos(phi), np.cos(theta)*np.sin(phi), -np.sin(theta)), axis=-1)
    dphi = np.stack((-np.sin(theta)*np.sin(phi), np.sin(theta)*np.cos(phi), z*0), axis=-1)
    derivatives = np.stack((k*dtheta, ell*dphi, n*0), axis=-2)
    return n, derivatives, grid.volume/2*(k*k+ell*ell/2), grid.volume/4*k*k*ell*ell


def smooth_periodic(grid):
    coordinates = grid.numpy_coordinates()
    k = [2*math.pi/v for v in grid.box]
    a, b, c = [frequency*x for frequency, x in zip(k, coordinates)]
    scalar = np.exp(0.6*np.cos(a)+0.4*np.sin(b)+0.3*np.cos(c))
    field = np.stack((scalar, scalar*0.3, scalar*-0.2), axis=-1)
    derivatives = np.stack((-0.6*k[0]*np.sin(a)*scalar,
                            0.4*k[1]*np.cos(b)*scalar,
                           -0.3*k[2]*np.sin(c)*scalar), axis=-1)
    return field, derivatives[..., :, None]*np.array([1., 0.3, -0.2])


def localized_vacuum(grid):
    coordinates = grid.numpy_coordinates()
    phases = [2*math.pi*x/length for x, length in zip(coordinates, grid.box)]
    weights = [(1+np.cos(phase))/2 for phase in phases]
    theta = 0.55*math.prod(weight**4 for weight in weights)
    phi = phases[1]
    n = np.stack((np.sin(theta)*np.cos(phi), np.sin(theta)*np.sin(phi), np.cos(theta)), axis=-1)
    return n


def seeded_field(grid, seed):
    rng = np.random.default_rng(seed)
    coordinates = grid.numpy_coordinates()
    phases = [2*math.pi*x/length for x, length in zip(coordinates, grid.box)]
    components = []
    for c in range(3):
        coefficients = rng.normal(size=6)
        value = sum(coefficients[i]*np.sin(phases[i])+coefficients[i+3]*np.cos(phases[i])
                    for i in range(3))*0.08
        components.append(value+(1 if c == 2 else 0))
    field = np.stack(components, axis=-1)
    return field/np.linalg.norm(field, axis=-1, keepdims=True), rng


def validate_spectral(config):
    cuda = config['machine'] == 'RTX5070'
    if cuda:
        import torch
        if not torch.cuda.is_available():
            raise ValueError('Real CUDA is required')
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats()
    backend = TorchBackend('cuda') if cuda else NumpyBackend()

    def tensor(value):
        if cuda:
            return torch.as_tensor(value, dtype=torch.float64, device='cuda')
        return np.asarray(value, dtype=np.float64)

    def array(value):
        return value.detach().cpu().numpy() if cuda else np.asarray(value)

    def scalar(value):
        return float(array(value))

    def error(actual, expected):
        a, b = array(actual), np.asarray(expected)
        return float(np.max(abs(a-b))/max(1., float(np.max(abs(b)))))

    worst = {'bandlimited_derivative':0., 'analytic_energy':0., 'parseval':0.,
             'skew_adjoint':0., 'vacuum_energy':0., 'unit_error':0.,
             'directional_gradient':0., 'symmetry_energy':0.}
    if cuda:
        worst.update(backend=0., autograd=0.)
    rows = []
    box = tuple(config['box'])
    for size in config['parameters']['resolution_sequence']:
        grid = PeriodicGrid((size,)*3, box)
        engine = SpectralEnergy(grid, backend)
        n, exact, exact_e2, exact_e4 = unit_two_angle(grid)
        nt = tensor(n)
        derivative = engine.gradient(nt)
        e2, e4 = engine.energy(nt)
        band_error = error(derivative, exact)
        energy_error = max(error(e2,exact_e2),error(e4,exact_e4))
        rnorm, fnorm, fe2 = engine.parseval(nt)
        parseval_error = max(error(rnorm,scalar(fnorm)),error(e2,scalar(fe2)))
        analytic, exact_derivative = smooth_periodic(grid)
        smooth_error = error(engine.gradient(tensor(analytic)), exact_derivative)
        fd = centered_reference_gradient(n, grid)
        fd_error = float(np.linalg.norm(fd-exact)/np.linalg.norm(exact))
        vacuum = n*0
        vacuum[...,2] = 1
        ve2, ve4 = engine.energy(tensor(vacuum))
        worst['vacuum_energy'] = max(worst['vacuum_energy'],scalar(ve2+ve4))
        worst['unit_error'] = max(worst['unit_error'],float(np.max(abs(np.sum(n*n,-1)-1))))
        worst['bandlimited_derivative'] = max(worst['bandlimited_derivative'],band_error)
        worst['analytic_energy'] = max(worst['analytic_energy'],energy_error)
        worst['parseval'] = max(worst['parseval'],parseval_error)
        rows.append({'grid':[size]*3,'spacing':list(grid.spacing), 'energy_2':scalar(e2), 'energy_4':scalar(e4),
                     'exact_energy_2':exact_e2,'exact_energy_4':exact_e4,
                     'bandlimited_derivative_error':band_error,'analytic_energy_error':energy_error,
                     'smooth_derivative_error':smooth_error,'centered_fd_relative_error':fd_error,
                     'parseval_error':parseval_error})
        if cuda:
            cpu=SpectralEnergy(grid)
            worst['backend']=max(worst['backend'],error(derivative,cpu.gradient(n)),
                                 error(e2,float(cpu.energy(n)[0])),error(e4,float(cpu.energy(n)[1])))

    grid=PeriodicGrid(tuple(config['grid']), box)
    engine=SpectralEnergy(grid,backend)
    directions=[]
    for seed in config['seeds']:
        n,rng=seeded_field(grid,seed)
        u=rng.normal(size=n.shape)
        v=rng.normal(size=n.shape)
        nt,ut,vt=tensor(n),tensor(u),tensor(v)
        du,dv=array(engine.gradient(ut)),array(engine.gradient(vt))
        adjoint=max(abs(np.sum(u*dv[...,i,:])+np.sum(du[...,i,:]*v)) /
                    max(1.,float(np.linalg.norm(u)*np.linalg.norm(dv[...,i,:]))) for i in range(3))
        worst['skew_adjoint']=max(worst['skew_adjoint'],float(adjoint))
        grad=engine.energy_gradient(nt)
        # A smooth, tangent direction; retraction validates the S2 variation as well.
        direction=0.1*np.roll(n,1,axis=1)
        direction-=n*np.sum(n*direction,axis=-1,keepdims=True)
        directional=float(np.sum(array(grad)*direction))
        steps=[]
        for step in config['parameters']['gradient_steps']:
            estimates=[]
            for sign in (-1,1):
                shifted=n+sign*step*direction
                shifted/=np.linalg.norm(shifted,axis=-1,keepdims=True)
                estimates.append(scalar(sum(engine.energy(tensor(shifted)))))
            fd=(estimates[1]-estimates[0])/(2*step)
            residual=abs(fd-directional)/max(1.,abs(directional))
            steps.append({'step':step,'finite_difference':fd,'analytic':directional,'normalized_error':residual})
        worst['directional_gradient']=max(worst['directional_gradient'],steps[-1]['normalized_error'])
        q,_=np.linalg.qr(rng.normal(size=(3,3)))
        q[:,0]*=np.linalg.det(q)
        energy=scalar(sum(engine.energy(nt)))
        rotation=scalar(sum(engine.energy(tensor(n@q))))
        translation=scalar(sum(engine.energy(tensor(np.roll(n,(1,-2,3),axis=(0,1,2))))))
        worst['symmetry_energy']=max(worst['symmetry_energy'],abs(rotation-energy)/max(1.,energy),
                                     abs(translation-energy)/max(1.,energy))
        directions.append({'seed':seed,'gradient_steps':steps,'skew_adjoint_error':float(adjoint)})
        if cuda:
            leaf=nt.detach().clone().requires_grad_(True)
            autodiff=torch.autograd.grad(sum(engine.energy(leaf)),leaf)[0]
            worst['autograd']=max(worst['autograd'],error(grad,array(autodiff)))
            worst['backend']=max(worst['backend'],error(grad,SpectralEnergy(grid).energy_gradient(n)))

    finest=PeriodicGrid((config['parameters']['resolution_sequence'][-1],)*3,box)
    local_engine=SpectralEnergy(finest,backend)
    bump=localized_vacuum(finest)
    bump_derivatives=array(local_engine.gradient(tensor(bump)))
    face_error=0.
    face_gradient=0.
    vacuum=np.array([0.,0.,1.])
    for axis in range(3):
        for index in (0,-1):
            face_error=max(face_error,float(np.max(abs(np.take(bump,index,axis=axis)-vacuum))))
            face_gradient=max(face_gradient,float(np.max(abs(np.take(bump_derivatives,index,axis=axis)))))
    even=PeriodicGrid(tuple(config['parameters']['even_grid']),box)
    even_engine=SpectralEnergy(even,backend)
    alternating=np.broadcast_to((-1.)**np.arange(even.shape[0])[:,None,None,None],(*even.shape,3)).copy()
    nyquist_error=float(np.max(abs(array(even_engine.gradient(tensor(alternating))))))
    ev,rng=seeded_field(even,config['seeds'][0])
    eu=rng.normal(size=ev.shape)
    edv=array(even_engine.gradient(tensor(ev)))
    edu=array(even_engine.gradient(tensor(eu)))
    even_adjoint=max(abs(np.sum(eu*edv[...,i,:])+np.sum(edu[...,i,:]*ev)) /
                     max(1.,float(np.linalg.norm(eu)*np.linalg.norm(edv[...,i,:]))) for i in range(3))
    worst['skew_adjoint']=max(worst['skew_adjoint'],float(even_adjoint))
    worst.update(smooth_derivative_final=rows[-1]['smooth_derivative_error'],
                 centered_fd_final=rows[-1]['centered_fd_relative_error'],
                 vacuum_face=face_error,vacuum_face_gradient=face_gradient,nyquist_derivative=nyquist_error)
    improvement=rows[0]['smooth_derivative_error']/max(rows[-1]['smooth_derivative_error'],1e-30)
    slope=math.log(rows[-2]['centered_fd_relative_error']/rows[-1]['centered_fd_relative_error']) / math.log(rows[-1]['grid'][0]/rows[-2]['grid'][0])
    checks={key:worst[key]<=threshold for key,threshold in config['tolerances'].items()}
    checks.update(spectral_convergence=improvement>=config['parameters']['minimum_spectral_improvement'],
                  finite_difference_order=1.8<=slope<=2.2,
                  smooth_error_decreases=all(b['smooth_derivative_error']<a['smooth_derivative_error']
                                            for a,b in zip(rows,rows[1:]) if a['smooth_derivative_error']>1e-11))
    result={'passed':all(checks.values()),'checks':checks,'worst_errors':worst,
            'resolution_sequence':rows,'directional_checks':directions,
            'spectral_improvement':improvement,'centered_fd_observed_order':slope,
            'even_grid':list(even.shape),'dtype':'float64',
            'cuda_verified':cuda,'hopf_charge_evaluated':False,'stationary_solution_evaluated':False}
    if cuda:
        torch.cuda.synchronize()
        result['peak_vram_gb']=torch.cuda.max_memory_allocated()/1e9
    return result
