# G0B-T03 RTX5070 production contract

## Source and immutable targets

The supplied PDF (SHA256 in publication.source.yaml), p. 9, Table 2 and
sections 7.1-7.2, was extracted and visually inspected on RTX5070. Eq. 65,
full-grid FFT, endpoint-included sampling and the fixed south-pole boundary
are unchanged. There is no dealiasing, Fourier truncation or charge rescaling.

| N | Physical L | h | Published energy | Q_H | Virial | Constrained RMS |
|---|---|---|---|---|---|---|
| 17 | 4 | 0.5 | 281.3653 | -0.999987 | -0.0820 | 1.06e-7 |
| 21 | 4 | 0.4 | 281.2711 | -0.999727 | -0.0762 | 9.41e-6 |
| 25 | 4 | 1/3 | 281.2625 | -0.999973 | -0.0758 | 4.48e-6 |
| 33 | 8 | 0.5 | 274.5448 | -0.999931 | -0.0134 | 5.08e-6 |

Four AL updates, beta=20000, Qstar=-1, strong-Wolfe Torch LBFGS, at most
120 iterations and 180 evaluations per inner solve, gradient tolerance 1e-10,
change tolerance 1e-14, history size 100. The chart normalizes every oracle
evaluation and excludes the boundary. Source FFT period is N*h, not 2L.

Acceptance is frozen before running: relative energy error <=5e-4,
abs(abs(Q_H)-1)<=5e-4, physical tangent/charge-constrained RMS <=1e-5,
finite field/observables, unit/boundary checks, all engineering checks, all
four matched rows and improved absolute virial upon box enlargement.
Each final source field is additionally checked against host NumPy and CUDA
autograd; these diagnostics discriminate implementation from stopping/basin
issues without claiming a MACM6 execution. Only a fully accepted row creates
a separate stationary=true checkpoint; restart candidates stay false.
The residual threshold brackets the largest Table 2 residual (9.41e-6);
it does not replace the tighter inner optimizer gradient tolerance.

## Initializer/optimizer equivalence boundary

The publication archive and its precise initializer/profile are absent.
Each grid starts from the independently derived compact map with scale=1.2,
radius=3.4; no energy fitting or initial-charge renormalization is performed.
This is the same validated sign/sector construction as G0B-T02, evaluated
on each source grid. It is not a published stationary checkpoint or a warm
start from an unavailable archive. Torch LBFGS is the existing library,
not a new optimizer implementation. Its stopping conditions, actual counts
and physical residual are reported separately; exhausted budgets are not
called convergence. A strict closure guard caps actual evaluations at 180;
if a Wolfe trial exhausts that budget, the best finite evaluated field is
retained, the interrupted trial is labeled and convergence is still tested.

An EQUIVALENCE.md companion is generated separately from the SUBSTEP REPORT.
Agreement or disagreement with Table 2 must be reported, not hidden by
changing published energy/charge tolerances. A failed first source row stops
the sequence for classification; later rows are NOT_RUN, never PASS.

## Checkpoint and restart contract

HDF5 checkpoints contain normalized raw chart variables, multiplier, AL
history, complete Torch optimizer state for audit, Python/NumPy/Torch/CUDA
RNG states, run/config/code/grid identities and completed prefix results.
No pickle or arbitrary checkpoint code is executed. Each checkpoint is
written to a new path; no prior checkpoint is overwritten.

Restart is supported at completed AL boundaries. The next outer update
recenters the normalized chart and initializes a fresh LBFGS, exactly as in
the uninterrupted adapter. The previous optimizer state is retained for
audit, not loaded into a differently recentered chart. An interrupted inner
solve restarts from the last completed outer checkpoint. Mid-Wolfe/inner
iteration restart is NOT claimed. Resume requires an explicit checkpoint
path and SHA256 plus an exact config/code/grid match; it is a new identified
run with the old checkpoint as a hashed input, never a mutation of old logs.

## Scope and device policy

All new runs are RTX5070 unless the user explicitly changes the preference.
Host-side NumPy comparison on this Windows machine is not MACM6 completion.
MACM6's independent report/fit responsibilities remain unmarked. CLOUD
stays paused with zero budget. This driver supplies no Hessian, full-M
stability, lifetime, production or cosmological viability result.
