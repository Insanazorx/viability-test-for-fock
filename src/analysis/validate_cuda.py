"""RTX5070 float64 mirror; callable only with real available CUDA hardware."""
from __future__ import annotations

import math
import numpy as np

from core.backends import TorchBackend
from core.math_core import MathCore
from .validate_core import error, physical_directional, reduced_directional


def validate_cuda(config):
    import torch
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is unavailable; do not substitute MPS or CPU")
    device = torch.device("cuda")
    torch.cuda.reset_peak_memory_stats(device)
    reference = MathCore()
    mirror = MathCore(TorchBackend("cuda"))
    count = config["parameters"]["samples_per_seed"]
    comparisons, gradients = [], []
    for seed in config["seeds"]:
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        rng = np.random.default_rng(seed)
        m = rng.normal(size=(count,6))
        dm = rng.normal(size=(count,3,6))
        n = rng.normal(size=(count,3))
        n /= np.linalg.norm(n,axis=-1,keepdims=True)
        dn = rng.normal(size=(count,3,3))
        dn -= np.sum(dn*n[:,None,:],axis=-1,keepdims=True)*n[:,None,:]
        tensor = lambda value: torch.tensor(value,dtype=torch.float64,device=device)
        tm, tdm, tn, tdn = map(tensor,(m,dm,n,dn))
        pairs = [
            (mirror.matrix(tm),reference.matrix(m)), (mirror.c1(tm),reference.c1(m)),
            (mirror.c2(tm),reference.c2(m)), (mirror.hodge(tm),reference.hodge(m)),
            (mirror.stf(tm),reference.stf(m)),
            (mirror.static_two_derivative(tdm),reference.static_two_derivative(dm)),
            (mirror.static_quartic(tdm),reference.static_quartic(dm)),
            (mirror.field_strength(tn,tdn),reference.field_strength(n,dn)),
        ]
        for cuda_value,cpu_value in pairs:
            comparisons.append(error(cuda_value.detach().cpu().numpy(),cpu_value))
        for cuda_values,cpu_values in (
            (mirror.projections(tm),reference.projections(m)),
            (mirror.dual_vectors(tm),reference.dual_vectors(m)),
            (mirror.reduced_fields(tm),reference.reduced_fields(m)),
            (mirror.reduced_energy(tn,tdn),reference.reduced_energy(n,dn)),
        ):
            comparisons.extend(error(c.detach().cpu().numpy(),r) for c,r in zip(cuda_values,cpu_values))
        comparisons.append(error(mirror.packed(mirror.matrix(tm)).detach().cpu().numpy(),m))
        comparisons.append(error(mirror.lift_reduced(tn,tn).detach().cpu().numpy(),reference.lift_reduced(n,n)))
        strength = mirror.field_strength(tn,tdn)
        comparisons.append(error(mirror.magnetic_field(strength).detach().cpu().numpy(),
                                 reference.magnetic_field(reference.field_strength(n,dn))))
        av,bv = rng.normal(size=(2,count,3))
        comparisons.append(error(mirror.hopf_functional(tensor(av),tensor(bv),0.125).detach().cpu().numpy(),
                                 reference.hopf_functional(av,bv,0.125)))
        # CUDA autograd versus independently differentiated CPU contractions.
        x,v = rng.normal(size=(2,6))
        tx = tensor(x).requires_grad_(True)
        c1g = torch.autograd.grad(mirror.c1(tx),tx)[0]
        c2g = torch.autograd.grad(mirror.c2(tx),tx)[0]
        gradients.extend([error(c1g.detach().cpu().numpy(),2*x),
                          error(c2g.detach().cpu().numpy(),np.array([x[5],-x[4],x[3],x[2],-x[1],x[0]]))])
        nd,vdn = rng.normal(size=(2,3))
        nd /= np.linalg.norm(nd)
        dd,vdd = rng.normal(size=(2,3,3))
        tnd,tdd = tensor(nd).requires_grad_(True),tensor(dd).requires_grad_(True)
        gnd,gdd = torch.autograd.grad(sum(mirror.reduced_energy(tnd,tdd)),(tnd,tdd))
        observed = float(torch.sum(gnd*tensor(vdn))+torch.sum(gdd*tensor(vdd)))
        gradients.append(error(observed,reduced_directional(nd,dd,vdn,vdd)))
        dd,vdd = rng.normal(size=(2,3,6))
        tdd = tensor(dd).requires_grad_(True)
        gd = torch.autograd.grad(mirror.static_two_derivative(tdd,0.9)+mirror.static_quartic(tdd,1.7,2.3),tdd)[0]
        gradients.append(error(float(torch.sum(gd*tensor(vdd))),physical_directional(dd,vdd,1.7,0.9,2.3)))
        ta,tb = tensor(av).requires_grad_(True),tensor(bv).requires_grad_(True)
        ga,gb = torch.autograd.grad(mirror.hopf_functional(ta,tb,0.125),(ta,tb))
        factor=0.125/(16*math.pi**2)
        gradients.extend([error(ga.detach().cpu().numpy(),factor*bv),error(gb.detach().cpu().numpy(),factor*av)])
    torch.cuda.synchronize(device)
    errors={"backend_normalized":max(comparisons),"autograd_normalized":max(gradients)}
    return {"passed":all(math.isfinite(errors[k]) and errors[k]<=v for k,v in config["tolerances"].items()),
            "worst_errors":errors,"samples_checked":count*len(config["seeds"]),
            "numpy_version":np.__version__,"pytorch_version":torch.__version__,
            "cuda_runtime":torch.version.cuda,"cuda_device_name":torch.cuda.get_device_name(device),
            "peak_vram_gb":torch.cuda.max_memory_allocated(device)/1e9,
            "cuda_verified":True,"hopf_unit_charge_reproduced":False,"dtype":"float64"}
