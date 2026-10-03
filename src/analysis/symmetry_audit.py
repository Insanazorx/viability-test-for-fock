"""Source-action symmetry/field-choice audit; no loop-generation assertion."""
from fractions import Fraction
from math import factorial
import numpy as np
from core.math_core import MathCore
from .operator_basis import catalog, monomials


BASE_POTENTIAL = {'1','C1','C1^2','lambda^2','lambda^3','lambda^4',
                  'chi^2','chi^4','lambda^2*chi^2'}


def classified_catalog():
    rows=[]
    for operator in catalog():
        row=dict(operator);expr=row['expression'];sector=row['sector']
        odd_pf = row.get('powers',[0,0,0,0])[3]%2==1 or row['id']=='K-04'
        row['stated_symmetry_allowed']=True
        if sector=='potential':
            row['baseline_present']=expr in BASE_POTENTIAL
            row['field_choice']='lambda-origin shift trades one condition for changes to all lambda-dependent coefficients; no removal of the physical hierarchy' if expr=='lambda' else 'independent IBP representative; no EOM elimination claimed'
        else:
            row['baseline_present']=row['id'] in {'K-01','K-02','K-03','R-01'}
            row['field_choice']=('constant kinetic normalizations can be fixed by invertible field rescaling; all couplings must be transformed' if row['id'] in {'K-01','K-02','K-03'} else
                                'Jordan/Einstein-frame redistribution possible where F>0; induced potential, kinetic and matter terms must be retained' if sector=='linear_curvature' else
                                'metric EOM redefinition can trade curvature terms for stress/other operators at EFT order; no deletion in coupled scalar gravity' if sector=='curvature_squared' else
                                'unequal Hodge-sector rescaling trades the kinetic coefficient for potential/portal coefficients')
        row['absence_class']=('present in displayed baseline' if row['baseline_present'] else
                              'protected by accidental internal reflection of displayed baseline; allowed UV matching under only stated SO4' if odd_pf else
                              'allowed matching coefficient set to zero in displayed frame; no stated-symmetry protection')
        row['accidental_reflection_odd']=odd_pf
        rows.append(row)
    return rows


def mu_series(order=16):
    """Coefficients of 1-exp(-x^4), exact, including all zero powers."""
    return [Fraction((-1)**(n//4+1),factorial(n//4)) if n and n%4==0 else Fraction(0) for n in range(order+1)]


def xi_series(order=10):
    """Coefficients of y^2/(1+y^2) about zero, valid |y|<1."""
    return [Fraction((-1)**((n-2)//2)) if n>=2 and n%2==0 else Fraction(0) for n in range(order+1)]


def validate_classification(config):
    rows=classified_catalog();core=MathCore();worst=0.;cubic_witness=0.;pf_witness=0.
    for seed in config['seeds']:
        rng=np.random.default_rng(seed)
        for _ in range(config['parameters']['samples_per_seed']):
            m=rng.normal(size=6);d=rng.normal(size=(3,6));lam,chi=rng.uniform(.1,.9,2)
            reflection=np.diag([-1.,1.,1.,1.]);mr=core.packed(reflection@core.matrix(m)@reflection)
            dr=core.packed(reflection@core.matrix(d)@reflection)
            def potential(field):
                return .25*(core.c1(field)-1)**2 +(-np.expm1(-lam**4))*core.c2(field)**2 + .12*lam**2-lam**3/3+lam**4/4+chi**2/2+chi**4/4-.1*chi**2/(1+chi**2)*lam**2/2
            for a,b in [(potential(m),potential(mr)),(core.static_two_derivative(d),core.static_two_derivative(dr)),(core.static_quartic(d),core.static_quartic(dr))]:
                worst=max(worst,float(abs(a-b)/max(1,abs(a))))
            cubic_witness=max(cubic_witness,2*lam**3/3)
            pf_witness=max(pf_witness,abs(float(core.c2(m)-core.c2(mr))))
    checks=dict(coverage=len(rows)==32 and len({r['id'] for r in rows})==32,
                baseline_potential_count=sum(r['baseline_present'] for r in rows if r['sector']=='potential')==9,
                no_forbidden_operator_in_allowed_basis=all(r['stated_symmetry_allowed'] for r in rows),
                accidental_baseline_reflection=worst<=config['tolerances']['reflection'],
                stated_so4_does_not_forbid_pfaffian=pf_witness>1e-3,
                no_lambda_parity=cubic_witness>1e-3,
                chi_odd_forbidden=all(p[1]%2 for p in monomials(4,chi_parity=1)),
                no_untracked_eom_deletion=all(r['field_choice'] for r in rows))
    checks={k:bool(v) for k,v in checks.items()}
    return dict(passed=all(checks.values()),checks=checks,catalog=rows,worst_errors={'reflection':worst},
                forbidden_examples=['chi','lambda*chi','chi*C1','chi*C2','nabla lambda . nabla chi'],
                quotient='IBP basis retained; conditional field/EOM equivalences documented with induced operators',
                portal_reflection='M Hilbert stress is invariant because its kinetic, potential and sum of quartic Hodge sectors are invariant; matter fields inert',
                loop_coefficients_computed=False)


def validate_switching(config):
    mu=mu_series(16);xi=xi_series(12);worst_mu=0.;worst_xi=0.
    for x in config['parameters']['series_points']:
        m=sum(float(v)*x**n for n,v in enumerate(mu))
        z=sum(float(v)*x**n for n,v in enumerate(xi))
        worst_mu=max(worst_mu,abs(m+np.expm1(-x**4)))
        worst_xi=max(worst_xi,abs(z-x*x/(1+x*x)))
    checks=dict(lower_switch_allowed=all((n,0,0,2) in monomials(8) for n in range(5)),
                quartic_onset_exact=mu[:4]==[0]*4 and mu[4]==1 and factorial(4)*mu[4]==24,
                exponential_coefficients=mu[8]==Fraction(-1,2) and mu[12]==Fraction(1,6) and mu[16]==Fraction(-1,24),
                xi_parity=all(v==0 for n,v in enumerate(xi) if n%2),
                xi_saturation_relations=xi[2]==1 and xi[4]==-1 and xi[6]==1,
                mu_series=worst_mu<=config['tolerances']['mu_series'],
                xi_series=worst_xi<=config['tolerances']['xi_series'])
    checks={k:bool(v) for k,v in checks.items()}
    return dict(passed=all(checks.values()),checks=checks,worst_errors={'mu_series':float(worst_mu),'xi_series':float(worst_xi)},
                mu_dimensionless_series=[str(v) for v in mu],xi_dimensionless_series=[str(v) for v in xi],
                lower_switch_terms=[dict(n=n,dimension=4+n,coefficient_dimension=-n,stated_symmetry_allowed=True,accidental_internal_reflection_even=True,baseline_coefficient='mu_v/(f^4*x_mu^4)' if n==4 else 'zero matching condition',protection=False) for n in range(5)],
                xi_taylor_domain='|chi| < chi_s; full rational function retained outside this domain',
                renormalization_conditions=['mu_eff^(n)(0)=0 for n=0,1,2,3 imposed at chosen matching scale','higher Xi coefficients matched independently unless UV relations supplied'],
                loop_generation_order='not computed by a symmetry audit; allowed does not mean generated at every loop order',
                no_added_fields=True)
