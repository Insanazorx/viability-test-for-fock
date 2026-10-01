"""Independent contractions and directional checks for the MACM6 math core."""
from __future__ import annotations

from itertools import permutations
import math
import numpy as np

from core.math_core import MathCore, SPATIAL_PAIRS

EPSILON4 = np.zeros((4, 4, 4, 4), dtype=np.float64)
for permutation in permutations(range(4)):
    inversions = sum(permutation[i] > permutation[j] for i in range(4) for j in range(i + 1, 4))
    EPSILON4[permutation] = (-1.0) ** inversions


def matrix_reference(field):
    """Independent component construction, Appendix A.1."""
    value = np.zeros(field.shape[:-1] + (4, 4), dtype=np.float64)
    for k, (a, b) in enumerate(((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))):
        value[..., a, b], value[..., b, a] = field[..., k], -field[..., k]
    return value


def error(actual, expected, scale=None):
    actual, expected = np.asarray(actual), np.asarray(expected)
    if not np.isfinite(actual).all() or not np.isfinite(expected).all():
        return math.inf
    denominator = np.maximum(1.0, np.abs(expected) if scale is None else np.asarray(scale))
    return float(np.max(np.abs(actual - expected) / denominator))


def reduced_directional(n, dn, vn, vd):
    result = float(np.sum(dn * vd))
    for i, j in SPATIAL_PAIRS:
        cross = np.cross(dn[i], dn[j])
        f = float(n @ cross)
        df = float(vn @ cross + n @ (np.cross(vd[i], dn[j]) + np.cross(dn[i], vd[j])))
        result += f * df
    return result


def physical_directional(dm, vm, sigma0, z_m, zeta):
    result = float(z_m * np.sum(dm * vm))
    for sign in (1.0, -1.0):
        l, a = dm[:, [3, 1, 0]].copy(), dm[:, [2, 4, 5]]
        vl, va = vm[:, [3, 1, 0]].copy(), vm[:, [2, 4, 5]]
        l[:, 1] *= -1
        vl[:, 1] *= -1
        u, vu = (l + sign * a) / math.sqrt(2), (vl + sign * va) / math.sqrt(2)
        for i, j in SPATIAL_PAIRS:
            area = np.cross(u[i], u[j])
            variation = np.cross(vu[i], u[j]) + np.cross(u[i], vu[j])
            result += zeta / (4 * sigma0 ** 4) * float(area @ variation)
    return result


def evaluate_seed(core, config, seed):
    parameters = config["parameters"]
    rng = np.random.default_rng(seed)
    count = parameters["samples_per_seed"]
    field = rng.normal(size=(count, 6)).astype(np.float64)
    # Exercise a six-order amplitude range with scale-aware identity residuals.
    field *= np.power(10.0, rng.uniform(-3, 3, size=(count, 1)))
    matrix = matrix_reference(field)
    l = np.stack((field[:, 3], -field[:, 1], field[:, 0]), axis=-1)
    a = field[:, [2, 4, 5]]
    c1 = np.sum(l*l + a*a, axis=-1)
    c2 = np.sum(l*a, axis=-1)
    epsilon_pf = np.einsum("abcd,nab,ncd->n", EPSILON4, matrix, matrix) / 8.0
    gram = matrix @ matrix.transpose(0, 2, 1)
    q_ref = gram - 0.25 * np.trace(gram, axis1=-2, axis2=-1)[:, None, None] * np.eye(4)
    q = core.stf(field)
    q_squared = q @ q
    gap = c1*c1 - 4*c2*c2
    star_ref = 0.5*np.einsum("abcd,ncd->nab", EPSILON4, matrix)
    plus, minus = core.projections(field)
    uplus, uminus = core.dual_vectors(field)
    rp, rm = np.sum(uplus*uplus, -1), np.sum(uminus*uminus, -1)
    residuals = [
        error(core.matrix(field), matrix), error(core.packed(matrix), field),
        error(core.c1(field), c1, c1), error(core.c2(field), c2, c1),
        error(core.c2(field), epsilon_pf, c1),
        error(np.linalg.det(matrix), c2*c2, c1*c1),
        error(np.trace(gram, axis1=-2, axis2=-1), 2*c1, 2*c1),
        error(q, q_ref, c1[:,None,None]),
        error(q_squared, gap[:,None,None]*np.eye(4)/4, (c1*c1)[:,None,None]),
        error(np.trace(q_squared, axis1=-2, axis2=-1), gap, c1*c1),
        error(np.trace(q, axis1=-2, axis2=-1), np.zeros(count), c1),
        error(core.matrix(core.hodge(field)), star_ref),
        error(core.hodge(core.hodge(field)), field),
        error(core.hodge(plus), plus), error(core.hodge(minus), -minus),
        error(np.sum(plus*minus, -1), np.zeros(count), c1),
        error(rp+rm, c1, c1), error((rp-rm)/2, c2, c1),
        error(core.from_dual_vectors(uplus, uminus), field),
    ]
    inequality = float(np.max(np.maximum(2*np.abs(c2)-c1, 0) / np.maximum(1, c1)))
    rotation_errors=[]
    for i in range(parameters["rotations_per_seed"]):
        rotation, _ = np.linalg.qr(rng.normal(size=(4,4)))
        if np.linalg.det(rotation) < 0:
            rotation[:, -1] *= -1
        original = field[i]
        transformed_matrix = rotation @ matrix[i] @ rotation.T
        transformed = core.packed(transformed_matrix)
        rotation_errors.extend([
            error(core.c1(transformed), c1[i], c1[i]),
            error(core.c2(transformed), c2[i], c1[i]),
            error(core.stf(transformed), rotation@q[i]@rotation.T, c1[i]),
            error(core.matrix(core.hodge(transformed)), rotation@star_ref[i]@rotation.T,
                  math.sqrt(c1[i])),
        ])
        dm = rng.normal(size=(3,6))
        rotated_dm = core.packed(rotation @ matrix_reference(dm) @ rotation.T)
        rotation_errors.append(error(core.static_quartic(rotated_dm), core.static_quartic(dm)))
    reflection = np.diag([-1.0,1.0,1.0,1.0])
    reflected = core.packed(reflection @ matrix @ reflection)
    rotation_errors.append(error(core.c2(reflected), -c2, c1))
    nplus, nminus = rng.normal(size=(2,count,3))
    nplus /= np.linalg.norm(nplus, axis=-1, keepdims=True)
    nminus /= np.linalg.norm(nminus, axis=-1, keepdims=True)
    sigma0, z_m, zeta = 1.7, 0.9, 2.3
    lifted = core.lift_reduced(nplus, nminus, sigma0)
    np_out, nm_out, rplus, rminus = core.reduced_fields(lifted)
    dnp, dnm = rng.normal(size=(2,count,3,3))
    dnp -= np.sum(dnp*nplus[:,None,:], axis=-1, keepdims=True)*nplus[:,None,:]
    dnm -= np.sum(dnm*nminus[:,None,:], axis=-1, keepdims=True)*nminus[:,None,:]
    dm = core.from_dual_vectors(sigma0/math.sqrt(2)*dnp, sigma0/math.sqrt(2)*dnm)
    fp, fm = core.field_strength(nplus, dnp), core.field_strength(nminus, dnm)
    expected2 = z_m*sigma0**2/4 * np.sum(dnp*dnp+dnm*dnm, axis=(-2,-1))
    expected4 = zeta/32 * np.sum(fp*fp+fm*fm, axis=-1)
    reduction_errors = [
        error(core.c1(lifted), np.full(count,sigma0**2)), error(core.c2(lifted), np.zeros(count)),
        error(np_out,nplus), error(nm_out,nminus),
        error(rplus, np.full(count,sigma0/math.sqrt(2))),
        error(rminus,np.full(count,sigma0/math.sqrt(2))),
        error(core.static_two_derivative(dm,z_m), expected2),
        error(core.static_quartic(dm,sigma0,zeta), expected4),
    ]
    # Isolated exactly known geometry catches F/B orientation and the Eq. 65 half factors.
    n = np.array([0.,0.,1.])
    dn = np.array([[2.,0.,0.],[0.,3.,0.],[0.,0.,0.]])
    f = core.field_strength(n,dn)
    e2,e4 = core.reduced_energy(n,dn)
    reduction_errors.extend([error(f,np.array([6.,0.,0.])), error(e2,6.5), error(e4,18.),
                             error(core.magnetic_field(f),np.array([0.,0.,6.]))])
    # Analytic directional derivatives use independent formulas, not autodiff of this code.
    x, v = rng.normal(size=(2,6))
    mx, mv = matrix_reference(x), matrix_reference(v)
    dq = mv@mx.T + mx@mv.T - np.dot(x,v)*np.eye(4)
    c1_derivative = 2*float(np.dot(x,v))
    pf_gradient = np.array([x[5],-x[4],x[3],x[2],-x[1],x[0]])
    c2_derivative = float(pf_gradient@v)
    n, vn = rng.normal(size=(2,3))
    n /= np.linalg.norm(n)
    dn, vd = rng.normal(size=(2,3,3))
    dn -= np.sum(dn*n,axis=-1,keepdims=True)*n
    reduced_derivative = reduced_directional(n,dn,vn,vd)
    dm, vm = rng.normal(size=(2,3,6))
    physical_derivative = physical_directional(dm,vm,sigma0,z_m,zeta)
    av, bv, da, db = rng.normal(size=(4,8,3))
    cell_volume = 0.125
    hopf_derivative = cell_volume/(16*math.pi**2)*float(np.sum(da*bv+av*db))
    gradient_steps=[]
    for step in parameters["gradient_step_sizes"]:
        def central(function):
            return (function(step)-function(-step))/(2*step)
        errors = [
            error(central(lambda h: core.c1(x+h*v)), c1_derivative),
            error(central(lambda h: core.c2(x+h*v)), c2_derivative),
            error(central(lambda h: core.stf(x+h*v)), dq),
            error(central(lambda h: sum(core.reduced_energy(n+h*vn,dn+h*vd))), reduced_derivative),
            error(central(lambda h: core.static_two_derivative(dm+h*vm,z_m)
                          + core.static_quartic(dm+h*vm,sigma0,zeta)), physical_derivative),
            error(central(lambda h: core.hopf_functional(av+h*da,bv+h*db,cell_volume)), hopf_derivative),
        ]
        gradient_steps.append({"step": step, "maximum_normalized_error": max(errors),
                               "reduced_energy_error": errors[3], "physical_energy_error": errors[4]})
    return {"identity_normalized": max(residuals+[inequality]),
            "rotation_normalized": max(rotation_errors),
            "reduction_normalized": max(reduction_errors),
            "gradient_normalized": gradient_steps[-1]["maximum_normalized_error"],
            "gradient_steps": gradient_steps}


def validate_core(config):
    core = MathCore()
    by_seed = {str(seed): evaluate_seed(core, config, seed) for seed in config["seeds"]}
    summary = {key: max(value[key] for value in by_seed.values()) for key in config["tolerances"]}
    passed = all(math.isfinite(summary[key]) and summary[key] <= tolerance
                 for key, tolerance in config["tolerances"].items())
    return {"passed": passed, "worst_errors": summary, "by_seed": by_seed,
            "samples_checked": config["parameters"]["samples_per_seed"]*len(config["seeds"]),
            "so4_rotations_checked": config["parameters"]["rotations_per_seed"]*len(config["seeds"]),
            "dtype": "float64", "numpy_version": np.__version__,
            "hopf_unit_charge_reproduced": False, "cuda_verified": False}
