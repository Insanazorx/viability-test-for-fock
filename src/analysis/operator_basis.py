"""G4A-T01: exact low-dimension dark/metric operator enumeration.

IBP quotient only, not an EOM quotient. Higher-order source operators are
catalogued separately; this is not a complete dimension-eight/ten basis.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import product

GENERATORS = ('lambda', 'chi', 'C1', 'C2')
DIMENSIONS = (1, 1, 2, 2)


def monomials(max_dimension, chi_parity=0):
    if type(max_dimension) is not int or not 0 <= max_dimension <= 8:
        raise ValueError('An integer dimension from zero to eight is required')
    if type(chi_parity) is not int or chi_parity not in (0, 1):
        raise ValueError('chi parity must be zero or one')
    powers = product(*(range(max_dimension // d + 1) for d in DIMENSIONS))
    return sorted((p for p in powers if p[1] % 2 == chi_parity and
                   sum(a*d for a,d in zip(p,DIMENSIONS)) <= max_dimension),
                  key=lambda p:(sum(a*d for a,d in zip(p,DIMENSIONS)),p))


def name(powers):
    terms = [g if p == 1 else f'{g}^{p}' for g,p in zip(GENERATORS,powers) if p]
    return '*'.join(terms) or '1'


def record(identifier, expression, dimension, sector, **extra):
    return dict(id=identifier, expression=expression, dimension=dimension,
                coefficient_dimension=4-dimension, sector=sector, **extra)


def catalog():
    potential = [record(f'V-{i:02d}',name(p),sum(a*d for a,d in zip(p,DIMENSIONS)),
                        'potential',powers=list(p)) for i,p in enumerate(monomials(4),1)]
    curvature = [record(f'R-{i:02d}','R' if name(p)=='1' else f'R*{name(p)}',
                        2+sum(a*d for a,d in zip(p,DIMENSIONS)),
                        'linear_curvature',powers=list(p)) for i,p in enumerate(monomials(2),1)]
    kinetic = [record('K-01','(nabla lambda)^2',4,'kinetic'),
               record('K-02','(nabla chi)^2',4,'kinetic'),
               record('K-03','1/2 nabla M_ab nabla M_ab',4,'kinetic'),
               record('K-04','1/2 nabla M_ab nabla (*M)_ab',4,'kinetic')]
    gravity = [record('G-01','R^2',4,'curvature_squared'),
               record('G-02','R_munu R^munu',4,'curvature_squared')]
    return potential+curvature+kinetic+gravity


def boundary_catalog():
    return [
        {'expression':'E4 = Riemann^2 - 4 Ricci^2 + R^2',
         'status':'constant-coefficient Euler density; topological in four dimensions'},
        {'expression':'Riemann dual(Riemann)',
         'status':'constant-coefficient Pontryagin density; topological in four dimensions'},
        {'expression':'Box R', 'status':'total divergence'},
        *[{'expression':f'Box {value}','status':'total divergence'}
          for value in ('lambda','lambda^2','chi^2','C1','C2')],
    ]


def source_extensions():
    return [
        {'expression':'L4[M]', 'source':'Eq. (30), PDF p. 5',
         'numerator_dimension':8,'coefficient_dimension':-4,
         'scope':'displayed first-derivative quartic only; not the entire d=8 basis'},
        {'expression':'lambda^4 C2^2', 'source':'Eq. (22), Taylor onset',
         'numerator_dimension':8,'coefficient_dimension':-4,
         'scope':'mu_v/(f^4 x_mu^4) times this monomial'},
        {'expression':'lambda^8 C2^2', 'source':'Eq. (22), second Taylor term',
         'numerator_dimension':12,'coefficient_dimension':-8,
         'scope':'-mu_v/(2 f^8 x_mu^8) times this monomial; full exponential retained in baseline'},
        {'expression':'chi^4 lambda^2', 'source':'Eqs. (21)-(22), Xi expansion',
         'numerator_dimension':6,'coefficient_dimension':-2,
         'scope':'+kappa/(2 chi_s^2) times this monomial; expansion requires |chi|<chi_s'},
        {'expression':'chi^2 S:T_m', 'source':'Eq. (20), defined Hilbert STF composite',
         'numerator_dimension':10,'coefficient_dimension':-6,
         'scope':'S includes coefficients; expanding its L4 part gives bare d=14 divided by sigma0^4 Lambda^6'},
    ]


def hilbert_coefficients(max_dimension):
    """Independent series of 1/((1-t)(1-t^2)^3), without tuple filtering."""
    coefficients = [1]+[0]*max_dimension
    for weight in (1,2,2,2):
        for degree in range(weight,max_dimension+1):
            coefficients[degree] += coefficients[degree-weight]
    return coefficients


def exact_rank(rows):
    """Exact rational rank; no conditioning-dependent rank declaration."""
    matrix = [[Fraction(value) for value in row] for row in rows]
    pivot = 0
    for column in range(len(matrix[0])):
        found = next((j for j in range(pivot,len(matrix)) if matrix[j][column]),None)
        if found is None:
            continue
        matrix[pivot],matrix[found] = matrix[found],matrix[pivot]
        factor=matrix[pivot][column]
        matrix[pivot]=[value/factor for value in matrix[pivot]]
        for j in range(pivot+1,len(matrix)):
            if matrix[j][column]:
                factor=matrix[j][column]
                matrix[j]=[a-factor*b for a,b in zip(matrix[j],matrix[pivot])]
        pivot += 1
        if pivot == len(matrix):
            break
    return pivot


def matter_interface(matter_dimension):
    """Scalar-singlet O_m decorations only; full matter basis needs L_m.

    The stated chi -> -chi transformation leaves the other fields inert.
    Matter operators with Lorentz/internal indices need their own contractions.
    No particular visible-sector field content or coefficient is inserted.
    """
    if type(matter_dimension) is not int or not 0 <= matter_dimension <= 4:
        raise ValueError('Scalar matter dimension must be an integer <=4')
    return [name(p) for p in monomials(4-matter_dimension)]
