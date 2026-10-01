# G0B-T01 reduced spectral energy contract

Source: user-supplied `yayınlanan.pdf`, PDF p. 8, Eqs. (64)-(68), with
SHA256 `09111940dc2575283d8db69ee65785d2b85beb3864e416e63c7538e91c70c312`.
The complete relevant page was visually inspected. Eq. (65) defines one
dimensionless S2 sector:

    E2 = (1/2) integral sum_i |d_i n|^2 d^3x
    E4 = (1/2) integral sum_{i<j} [n.(d_i n x d_j n)]^2 d^3x.

`src/static/spectral.py` uses the existing mathematical core with these
unchanged coefficients. This substep implements energy/derivatives on
manufactured fields; the charge inversion, initial map, minimizer, stationary
tables and Hessian remain later substeps.

## Grid and Fourier conventions

`PeriodicGrid((Nx,Ny,Nz),(Lx,Ly,Lz))` samples
`x_j=-Lj/2+q Lj/Nj`, q=0,...,Nj-1. There is no duplicated endpoint.
The integration cell volume is `product(Lj/Nj)`, independent of array shape.
Fields are channels-last `(Nx,Ny,Nz,3)`; gradients have shape
`(Nx,Ny,Nz,spatial_axis,component)`.

FFTs operate on all three spatial axes with orthonormal transforms. For each
axis, `D_j=FFT^-1 (i k_j FFT)` with `k_j=2 pi mode_j/Lj`. No MPS,
spatial-domain cut, hidden tangent projection or two-thirds filter is used.
Nonlinear products and quadrature are evaluated on the full collocation
grid. They can alias on insufficiently resolved data; convergence must be
measured. This discretization is not yet certified against published
stationary energies, which requires G0B-T03.

On odd grids all modes use the ordinary FFT frequency ordering. On even
grids the first-derivative Nyquist multiplier is explicitly zero: a real
alternating sampled cosine does not determine its continuum sine derivative.
This preserves a real, skew-adjoint derivative. Nyquist modes are unresolved
for physical-gradient inference; they must not be used as proof of a stable
configuration. The production sequence in this contract uses odd grids.
The independent centered finite-difference reference uses periodic rolls.

## Energy and analytic discrete gradient

The physical energy entry rejects nonunit n. The off-S2 polynomial extension
is explicit (`require_unit=False`) for differentiation checks. `energy_gradient`
returns the Euclidean node gradient, including the cell-volume factor. If
`F_ij=n.(D_i n x D_j n)`, its analytic derivative uses:

    local = sum_{i<j} F_ij (D_i n x D_j n)
    flux_i = D_i n + sum_{j>i} F_ij (D_j n x n)
                        + sum_{j<i} F_ji (n x D_j n)
    dE/dn = cell_volume [local - sum_i D_i flux_i].

This follows from discrete skew-adjointness and differentiates the exact
collocation energy. Tangent projection and charge constraints are not applied
inside it. The future minimizer can project explicitly. NumPy and Torch/CUDA
share the definitions; CUDA FFT/autograd acceptance must execute on RTX5070.

## Predeclared acceptance fixtures

MACM6 uses float64 on 9^3,13^3,17^3,25^3,33^3 manufactured fields and an
even 16^3 Nyquist check. These are small reference validations, not a 3-D
minimization campaign. The anisotropic box is `(2 pi,3 pi,4 pi)`.

For `n=(sin(kx)cos(ell y),sin(kx)sin(ell y),cos(kx))`, with
`k=2 pi/Lx`, `ell=2 pi/Ly`, exact integrals are
`E2=V(k^2+ell^2/2)/2` and `E4=V k^2 ell^2/4`.
All its component modes lie below every fixture's Nyquist limit.
The nonbandlimited scalar `exp(0.6 cos(kx)+0.4 sin(ell y)+0.3 cos(mz))`
tests actual spectral convergence against analytic derivatives. Its three
channels are `(f,0.3f,-0.2f)`; it is a derivative fixture, not an S2 state.

Parseval and derivative skew-adjointness are checked independently. Constant
vacuum has zero energy. A smooth periodic bump with angle
`theta=0.55 product_j [(1+cos(2 pi xj/Lj))/2]^4` approaches the same vacuum
on every face; field/gradient face errors are recorded. It has no certified
Hopf charge. Rotation and grid-translation energy invariance, three seeded
tangent central-difference checks and an independent second-order finite
difference sequence complete MACM6 acceptance. Thresholds are frozen in
`config/benchmark/g0b_t01_macm6.json.yaml` before the identified run.

## Machine prerequisites and GPU deferral

The user explicitly requested continuing MACM6 preparation while deferring
RTX5070. MACM6 G0B-T01 therefore requires the passing **MACM6 responsibility**
of G0A-T02 and the whole G0A-T03 task. The full prerequisite list remains in
state; its machine-specific decomposition and reason are explicit.
RTX5070 G0B-T01 still requires **the whole G0A-T02 and G0A-T03 tasks** and
the preceding MACM6 G0B-T01 report. Whole G0B-T01 stays RUNNING until both
machines pass; G0B/G1 completion is not implied by CPU fixtures.

Deferred machines are excluded from the active action. Resume RTX5070 only
when the user requests it, using `ctl.py resume-machine --machine RTX5070
--reason 'User requested RTX5070 continuation'`; it returns first to the
unfinished G0A-T02 CUDA mirror. CLOUD remains paused and remote runners off.
