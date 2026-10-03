"""Independent exact counting/rank plus SO(4)/chi-parity numeric witnesses."""
from __future__ import annotations

from collections import Counter
import numpy as np

from core.math_core import MathCore
from .operator_basis import (DIMENSIONS, boundary_catalog, catalog, exact_rank,
                             hilbert_coefficients, monomials, source_extensions)


def validate_operators(config):
    basis=catalog();powers=monomials(4);core=MathCore()
    histogram=[sum(sum(a*d for a,d in zip(p,DIMENSIONS))==degree for p in powers)
               for degree in range(5)]
    exact_rows=[];worst_rotation=0.;worst_parity=0.;reflection_witness=0.
    kinetic_reflection_witness=0.
    for seed in config['seeds']:
        rng=np.random.default_rng(seed)
        for _ in range(config['parameters']['samples_per_seed']):
            # Independent canonical normal form: M12=a, M34=b.
            a,b,l,h=(int(v) for v in rng.integers(-4,5,size=4))
            values=(l,h,a*a+b*b,a*b)
            exact_rows.append([np.prod([v**p for v,p in zip(values,exponent)],dtype=object)
                               for exponent in powers])
            field=rng.normal(size=6);gradient=rng.normal(size=(4,6))
            matrix=core.matrix(field);d_matrix=core.matrix(gradient)
            orthogonal,_=np.linalg.qr(rng.normal(size=(4,4)))
            orthogonal[:,0]*=np.linalg.det(orthogonal)
            rotated=core.packed(orthogonal@matrix@orthogonal.T)
            d_rotated=core.packed(orthogonal@d_matrix@orthogonal.T)
            lam,chi=rng.uniform(-1,1,size=2)
            original=(lam,chi,core.c1(field),core.c2(field))
            transformed=(lam,chi,core.c1(rotated),core.c2(rotated))
            for exponent in powers:
                expected=float(np.prod([v**p for v,p in zip(original,exponent)]))
                observed=float(np.prod([v**p for v,p in zip(transformed,exponent)]))
                parity=float(np.prod([v**p for v,p in zip((lam,-chi,*original[2:]),exponent)]))
                worst_rotation=max(worst_rotation,abs(observed-expected)/max(1,abs(expected)))
                worst_parity=max(worst_parity,abs(parity-expected)/max(1,abs(expected)))
            metric=np.array([-1.,1.,1.,1.])[:,None]
            for other in (lambda d:d,core.hodge):
                expected=float(np.sum(metric*gradient*other(gradient)))
                observed=float(np.sum(metric*d_rotated*other(d_rotated)))
                worst_rotation=max(worst_rotation,abs(observed-expected)/max(1,abs(expected)))
            reflect=np.diag([-1.,1.,1.,1.])
            reflected=core.packed(reflect@matrix@reflect)
            reflection_witness=max(reflection_witness,abs(float(core.c2(reflected)-core.c2(field))))
            d_reflected=core.packed(reflect@d_matrix@reflect)
            kinetic_reflection_witness=max(kinetic_reflection_witness,
                abs(float(np.sum(metric*d_reflected*core.hodge(d_reflected))-
                          np.sum(metric*gradient*core.hodge(gradient)))))
    rank=exact_rank(exact_rows)
    counts=dict(Counter(row['sector'] for row in basis))
    checks={
        'hilbert_count':histogram==hilbert_coefficients(4)==[1,1,4,4,10],
        'exact_potential_rank':rank==20,
        'basis_counts':counts=={'potential':20,'linear_curvature':6,'kinetic':4,'curvature_squared':2},
        'unique_ids':len({row['id'] for row in basis})==32,
        'so4_invariance':worst_rotation<=config['tolerances']['so4_normalized'],
        'chi_parity':worst_parity<=config['tolerances']['chi_parity'],
        'internal_reflection_is_extra_symmetry':reflection_witness>1e-3 and kinetic_reflection_witness>1e-3,
        'lower_switch_terms_included':all((n,0,0,2) in monomials(8) for n in range(5)),
        'source_dimensions':all(row['numerator_dimension']+row['coefficient_dimension']==4
                                for row in source_extensions()),
    }
    return dict(passed=all(checks.values()),checks=checks,catalog=basis,
                boundary_and_topological_terms=boundary_catalog(),source_extensions=source_extensions(),
                potential_count_by_dimension=histogram,exact_potential_rank=rank,
                exact_integer_samples=len(exact_rows),sector_counts=counts,
                worst_so4_normalized=worst_rotation,worst_chi_parity=worst_parity,
                internal_reflection_witness=reflection_witness,
                internal_kinetic_reflection_witness=kinetic_reflection_witness,
                scope='d<=4 dark/metric bulk analytic basis modulo IBP; no EOM quotient; source exceptions separately catalogued',
                matter_status='L_m unspecified: formal scalar-singlet decorations documented; no concrete matter basis or portal matching computed',
                scientific_naturalness_decision=False,loop_coefficients_computed=False)
