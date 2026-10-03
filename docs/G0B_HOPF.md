# G0B-T02 CPU Hopf reference contract

The supplied `yayınlanan.pdf`, SHA256
`09111940dc2575283d8db69ee65785d2b85beb3864e416e63c7538e91c70c312`, defines
F_ij, B and Q_H in Eqs. (31), (67)-(68), PDF pp. 4 and 8. Spatial
epsilon123=+1 and Q_H=(16 pi^2)^-1 integral A.B. The active unit sector has
Q_H approximately -1 and N_plus=-Q_H. PDF p. 9, section 7.1, specifies a
degree-one compactified initial map and south-pole boundary (0,0,-1), but
does not give an analytic initial profile or its scale. It refers to a
reproducibility archive on p. 17; no such archive is present in this workspace.
Pages 8 and 9 were visually inspected. The initializer below is an independent
realization of the specified unit sector, not an archived paper checkpoint.

## Paper grid

`PeriodicGrid.paper(N,L)` samples both physical endpoints +/-L with
h=2L/(N-1). The full-grid FFT frequencies have period N h, rather than 2L.
Constant boundary values make the periodic extension continuous. Integration
uses h^3 over all N^3 nodes, matching the declared collocation convention.
Odd grids 17^3,25^3,33^3,49^3 at L=4 are small MACM6 reference validations.
The 49^3 fixture resolves a known analytic map; this is not a minimization or
production lattice campaign. G0B-T01's earlier endpoint-excluded manufactured
fixtures and frozen configs remain unchanged.

## Coulomb inversion and certification boundary

For k != 0, Ahat=i(k x Bhat)/k^2, and the zero harmonic modes have Ahat=0.
Orthonormal forward/inverse transforms preserve Parseval. This sign follows
from Bhat=i k x Ahat and k.Ahat=0; no sign is fitted to a computed charge.
Q is checked against its independent Fourier inner product.

The inverse reconstructs only the transverse, nonharmonic part of B. The
original B is retained and the following diagnostics are reported:

- relative norm of curl(A)-B;
- norm of div(B)/(k_box norm(B)), with k_box=2pi/min(FFT periods);
- norm of div(A)/(k_box norm(A));
- fraction of B in harmonic Fourier modes;
- physical/Fourier helicity difference.

All norms are discrete L2 norms; the common cell volume cancels in ratios.
Zero-field denominators use 1 to avoid undefined 0/0. The operator returns
diagnostics, not a claim of quantized topology for arbitrary B. A constant
flux or longitudinal B is explicitly detected by tests. Aliasing/closure can
be poor on coarse initial maps; acceptance requires the finest baseline and
deformed maps to pass the predeclared closure/flux thresholds as well as
charge convergence. There is no hidden smoothing, renormalization to unity,
transverse replacement of the original B or charge-penalty adjustment.

## Independent compact unit map and sign proof

For s=r^2<R^2, choose g=a exp[-s/(R^2-s)]; for r>=R choose g=0.
Its profile is f=2 atan(g/r), with f(0)=pi, f(R)=0. It is smooth at the
origin and flat at the support edge. The unit quaternion is

    q0=(s-g^2)/(s+g^2), (q1,q2,q3)=2g(x,y,z)/(s+g^2).
    z1=q0+i q3, z2=q1+i q2.
    n=-(2 Re(z1 conj(z2)),2 Im(z1 conj(z2)),|z1|^2-|z2|^2).

The final minus sign gives n_infinity=(0,0,-1). With epsilon0123=+1 the
quaternion winding is -1 because f decreases from pi to zero. Its magnitude
is one, and the source's active-sector convention gives N_plus=+1.
An independent radial SciPy quadrature evaluates
`degree=(2/pi) integral sin(f)^2 f'(r) dr=-1`.
Analytic spatial quaternion derivatives also give the S3 winding density.
For this target convention the Berry potential is

    A_i=2[q0 d_i q3-q3 d_i q0+q1 d_i q2-q2 d_i q1].

With analytic n derivatives its helicity density equals the quaternion
winding density pointwise. This independently fixes the sign and 16 pi^2
normalization before FFT charge evaluation. The Coulomb potential can differ
from this Berry potential by a gauge gradient; their helicities converge.
The chosen a=1.2 and R=3.4 are fixture parameters, not source-fitted physical
couplings or a claim about the stationary soliton radius.

## Topology/gradient checks and artifact

Three explicitly seeded smooth tangent deformations are retracted onto S2.
The path `normalize(n+t v)` is nonsingular because n.v=0. A coordinate
deformation x_j -> x_j+epsilon_j sin(pi x_j/L) has positive diagonal Jacobian
when |epsilon_j| pi/L<1. All preserve the compact boundary and expected charge.
Spatial reflection must flip Q; target antipodal reflection must preserve Q.
A smooth great-circle map and the vacuum must have Q=0.

The same discrete helicity has an analytic node gradient: curl inverse is
self-adjoint, so delta Q=(8 pi^2)^-1 integral A.delta B. Mapping coefficients
to (F12,F13,F23) gives (A3,-A2,A1); the skew-adjoint derivative supplies the
flux divergence. Central differences of the off-S2 polynomial verify this
gradient on three independent seeds. The CUDA mirror also compares autograd
when it actually runs; MACM6 does not certify CUDA.

The finest initial field is saved under checkpoints/<run-id>__initial.h5.
It is ignored by Git and referenced by path plus SHA256 in the sealed result
and report. It contains n and exact config/run/profile/grid provenance, and
is labeled stationary=false. Hash verification is required before completion.
Reproduce it from its frozen config and code if it is not copied to RTX5070.
This substep does not reproduce stationary Table 2 energies or a Hessian.
G0B-T03 remains assigned to RTX5070 first; the user has explicitly deferred it.
