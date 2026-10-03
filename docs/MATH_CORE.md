# G0A-T02 mathematical core contract

Source: `yayınlanan.pdf`, I. C. Peker, Nuclear Physics B 1031 (2026) 117639,
DOI `10.1016/j.nuclphysb.2026.117639`. Exact file SHA256:
`09111940dc2575283d8db69ee65785d2b85beb3864e416e63c7538e91c70c312`.
Bibliographic identity is recorded in `config/benchmark/publication.source.yaml`.
Appendix A (PDF pp. 17-18) and the energy definitions (p. 8) were visually
inspected against the extracted text. Equations below are source definitions
or explicit algebraic consequences, not additional EFT operators.

## Representation and orientation

Internal indices a,b=1,...,4 use the Euclidean metric and epsilon1234=+1.
The independent array is `m=(M12,M13,M14,M23,M24,M34)` with channels last.
`MathCore.matrix` restores M_ba=-M_ab and a zero diagonal. From Eq. (4)/A.1,

    L=(M23,-M13,M12), A=(M14,M24,M34).
    C1=sum_c m_c^2 = L.L + A.A = Tr(M M^T)/2.
    C2=Pf(M)=M12 M34 - M13 M24 + M14 M23 = L.A.
    star(m)=(M34,-M24,M23,M14,-M13,M12).
    M_plus/minus=(M +/- star(M))/2.

The isometric dual triplets used in Eq. (30)/(64) are

    u_plus=(L+A)/sqrt(2), u_minus=(L-A)/sqrt(2).
    rho_plus^2 + rho_minus^2=C1.
    (rho_plus^2 - rho_minus^2)/2=C2.

This basis choice fixes both triplet orientations; full bivector projections
and their triplets are different representations of the same sectors.
On the Fock vacuum, `u_s=sigma0/sqrt(2) n_s`, with unit n_s. The lift enforces
unit vectors; extraction returns directions and radii separately. A vanishing
sector raises an error rather than assigning a fictitious topology.

## Quadratic STF channel and Appendix A

    K=M M^T, Q=K-(C1/2) I4.
    Q is symmetric and trace-free.
    Q^2=(C1^2-4 C2^2) I4/4.
    Tr(Q^2)=C1^2-4 C2^2.
    det(M)=C2^2, 2 abs(C2)<=C1.

SO(4) acts as `M -> R M R^T`; Q transforms in the same way and both invariants
are preserved. An orientation-reversing O(4) reflection flips Pf(M).
No spacetime/internal index identification is made.

## Static terms and reduction

The provided gradients are independent data. No spatial derivative
discretization or Fourier inversion is selected by this API.

For `dM` of shape `(...,3,6)`, Eq. (20) gives

    e2_full = Z_M/2 sum_{i,c} d_i m_c^2.

For the dual triplet gradients `du_s`, minus the static Lagrangian (30) gives

    e4_full = zeta/(16 sigma0^4) sum_s [(Tr G_s)^2-Tr(G_s^2)]
            = zeta/(8 sigma0^4) sum_s sum_{i<j} |du_s_i x du_s_j|^2,
    (G_s)_ij=du_s_i.du_s_j.

The implementation uses the cross-product form to avoid subtracting nearly
equal Gram contractions. On fixed-radius tangent data,

    e2_full = Z_M sigma0^2/4 sum_s sum_i |d_i n_s|^2,
    e4_full = zeta/32 sum_s sum_{i<j} F_s,ij^2,
    F_ij=n.(d_i n x d_j n).

These are physical coefficients before rescaling. The distinct dimensionless
Eq. (65) is implemented without changing its coefficients:

    e2_reduced = 1/2 sum_i |d_i n|^2,
    e4_reduced = 1/2 sum_{i<j} F_ij^2.

For one sector, writing a=Z_M sigma0^2/4, b=zeta/32, the positive rescaling
`x=sqrt(b/a) y` and `E_full=2 sqrt(a b) E_65` maps the two expressions. The
order-one factors are consistent with the scaling estimates in Eq. (66).
The polynomial reduced energy is defined off S2 for differentiation; imposing
unit fields/tangent variations is the caller's responsibility.

## Hopf functional boundary

Spatial epsilon123=+1; F is stored as `(F12,F13,F23)`.

    B=(F23,-F13,F12).
    Q_H=(1/(16 pi^2)) integral A.B d^3x.
    N_plus=-Q_H for the paper's initial-map orientation.

`hopf_functional` implements only this uniform-cell integral. It does not
construct A, certify charge quantization, or reconstruct a map from a lattice.
G0B-T01 selects spectral derivatives and G0B-T02 validates Fourier inversion
and the unit map. No unit Hopf charge has been reproduced in G0A-T02.

## Backend and validation boundary

`MathCore(NumpyBackend())` is the independent MACM6 float64 reference.
`MathCore(TorchBackend("cuda"))` uses tensor operations preserving dtype/device
and autograd; its actual CUDA comparison is required on RTX5070. CPU Torch
is available as an optional backend, but is not a substitute for CUDA checks.
Public input checks reject wrong channels, non-floating/non-finite arrays,
and undefined reduced directions. Validation is small pointwise sampling,
not a 3-D minimization, full six-component soliton scan, or viability result.
