# AGENTS.md — Fock-Selected Dark-Sector Full-Viability Program

> **Project:** Fock-selected topological dark matter + metastable dark energy  
> **Primary source:** `yayınlanan.pdf`, Nuclear Physics B 1031 (2026) 117639  
> **Purpose of this file:** single operational contract for all human/agent work across **Mac mini M6**, **RTX 5070**, and **Cloud**.  
> **Rule:** an agent must read only this file, the current `NEXT.md`, the latest `MACHINE_HANDOFF.md`, and the specific gate report(s) referenced there. Do not reload the whole project history unless a task explicitly requires it.

---

## 0. Mission, scope, and source-derived scientific targets

The published paper deliberately stops at **candidate-level** status. It establishes:

- explicit mediator-resolved covariant EFT;
- Fock/Pfaffian selection and the \(S^5 \rightarrow S^2\times S^2\) topology change;
- a topology-preserving reduced unit-Hopf stationary configuration;
- a tangent/charge-projected reduced Hessian with no resolved negative physical mode in the tested sector;
- a reduced homogeneous trigger benchmark that crosses the mediator/scalar thresholds while remaining in its stated principal-stability window;
- a metastable positive scalar branch with a flat-space bounce diagnostic;
- an illustrative reduced Newtonian-gauge closure with sub-percent growth deformation.

The paper explicitly leaves open:

1. unrestricted finite-stiffness six-component \(M_{ab}\) solitons and collisions;
2. a minimum-energy unwinding saddle;
3. strong-gradient hyperbolicity;
4. expanding-lattice production and relic abundance;
5. production-derived fluid/kinetic coefficients;
6. astrophysical self-interaction/darkness tests;
7. radiative naturalness and the ultra-light dark-energy hierarchy;
8. gravitational false-vacuum decay;
9. Boltzmann-complete perturbations;
10. likelihood-level cosmological viability.

The present program exists to close those gates in a falsifiable order.

### Scientific stop rule

If a load-bearing gate fails robustly after numerical and implementation errors are excluded, **do not hide the failure by immediately adding new fields/operators**. Create a failure report, freeze the failing branch, and open a separately named reformulation branch.

---

# 1. Hardware roles — never say only “local”

We always use these exact names:

### `MACM6`
**Mac mini M6, 16 GB unified memory**

Primary role:
- project/control node;
- symbolic algebra and analytic checks;
- NumPy/SciPy CPU reference implementation;
- small-grid independent validation;
- ODE/bounce calculations;
- report generation and visualization;
- CLASS/Boltzmann development;
- small CPU scans;
- state/checklist maintenance.

Do **not** use MACM6 as the default large 3-D lattice worker. Its purpose is independent verification and control, not duplicating CUDA work.

### `RTX5070`
**NVIDIA RTX 5070, 12 GB VRAM workstation**

Primary role:
- main numerical development machine;
- CUDA PyTorch implementation;
- FFT-based 3-D energies/topology;
- full six-component static minimization;
- matrix-free Hessian-vector products;
- NEB/string-method pilots;
- real-time collision pilots;
- \(64^3\)–\(128^3\)-class expanding-lattice pilots, subject to measured memory;
- profiler-driven optimization.

This is the default machine for new 3-D physics until a task is demonstrated correct.

### `CLOUD`
Not one fixed machine. Select only after local validation:

- **GPU cloud (48–80 GB VRAM):** high-resolution 3-D runs, large ensembles, or FP64-sensitive Hessians.
- **CPU cloud:** CLASS/Cobaya/MontePython likelihood chains and embarrassingly parallel parameter scans.

Cloud is **disabled by default**. Never use cloud merely because it is faster.

---

# 2. Minimal engineering stack

The default stack is intentionally boring:

- Git for code/state/reports.
- Python 3.12.
- PyTorch + CUDA on RTX5070/CLOUD GPU.
- NumPy/SciPy on MACM6 for independent references.
- `torch.fft` for spectral derivatives/Hopf inversion.
- `torch.func`/autograd for gradients and HVPs.
- `torch.compile` only after profiling.
- HDF5 (`h5py`) for large numerical outputs.
- YAML for configs/state.
- Matplotlib for plots.
- CLASS for Boltzmann evolution.
- Cobaya or MontePython for inference, chosen once in G6A and then frozen.

**Do not introduce** Kubernetes, Slurm, Ray, Dask, distributed databases, custom RPC services, or custom CUDA kernels before profiling proves a real need.

### Backend rule

A physics function should have:
1. a pure mathematical definition;
2. a CUDA implementation;
3. when practical, a small-grid CPU reference.

No task may depend on Mac MPS matching CUDA bit-for-bit.

---

# 3. Repository/control-plane layout

```text
/
├── AGENTS.md                  # this contract
├── STATUS.md                  # generated human dashboard
├── NEXT.md                    # exactly one active next action
├── MACHINE_HANDOFF.md         # short handoff only
├── state/
│   └── state.yaml             # canonical task/machine state
├── config/
│   ├── benchmark/
│   ├── gate1/
│   ├── gate2/
│   ├── gate3/
│   ├── gate4/
│   ├── gate5/
│   └── gate6/
├── src/
│   ├── core/
│   ├── static/
│   ├── hessian/
│   ├── dynamics/
│   ├── cosmology/
│   └── analysis/
├── tests/
│   ├── unit/
│   ├── reference/
│   └── regression/
├── scripts/
│   ├── ctl.py                 # lightweight state/checklist CLI
│   ├── run.py                 # config-driven run launcher
│   └── report.py              # report generator
├── runs/                      # metadata/small logs; large arrays ignored by git
├── checkpoints/               # large numerical states; not committed by default
├── reports/
│   ├── G0/
│   ├── G1/
│   ├── G2/
│   ├── G3/
│   ├── G4/
│   ├── G5/
│   └── G6/
└── docs/
    ├── MACM6_CHECKLIST.md
    ├── RTX5070_CHECKLIST.md
    ├── CLOUD_CHECKLIST.md
    └── RUNBOOK.md
```

Large checkpoints are referenced by path/URI + SHA256 in reports, not stored blindly in Git.

---

# 4. Canonical task state and the `[X]` machine rule

Each task has a stable ID such as `G1B-T04`.

Allowed task states:

`TODO -> CLAIMED -> RUNNING -> PASS | FAIL | BLOCKED -> ARCHIVED`

Each task also has explicit machine completion flags:

```yaml
machine_done:
  MACM6: false
  RTX5070: false
  CLOUD: false
```

When a machine has finished **its assigned responsibility** for a task, it changes only its own flag to `true`. The human-facing checklist must render this as:

- `[X] MACM6`
- `[ ] RTX5070`
- `[ ] CLOUD`

A machine that is *not required* for the task is shown as `N/A`, not as completed.

### Completion command contract

When `scripts/ctl.py` exists, use:

```bash
python scripts/ctl.py machine-done G1B-T04 --machine RTX5070 --report reports/G1/...
```

This must:
1. validate that a report exists;
2. update `state/state.yaml`;
3. regenerate `STATUS.md`;
4. regenerate per-machine checklist files;
5. update `NEXT.md` if all prerequisites are satisfied.

Until `ctl.py` is implemented, the same fields may be edited manually, but the state file remains canonical.

---

# 5. Run identity and reproducibility

Every numerical run receives:

```text
<GATE-TASK>__<MACHINE>__<UTC_TIMESTAMP>__<GIT_SHORT_SHA>__<CONFIG_HASH8>
```

Example:

```text
G1B-T04__RTX5070__20261001T040500Z__a13fd21__9c07b4e1
```

Every run records:

- git commit;
- uncommitted-diff flag;
- config SHA256;
- machine;
- OS/CUDA/PyTorch/Python versions;
- precision (`float32`, `float64`, mixed);
- random seed(s);
- grid/box/time step;
- optimizer/integrator;
- tolerances;
- wall time;
- peak RAM/VRAM;
- checkpoint SHA256;
- all pass/fail metrics.

**No anonymous runs.**

---

# 6. Mandatory SUBSTEP REPORT

Every completed or failed substep produces exactly one report under `reports/`.

Filename:

```text
reports/G1/G1B-T04__<run-id>__REPORT.md
```

Required schema:

```markdown
# SUBSTEP REPORT — G1B-T04

status: PASS | FAIL | BLOCKED
machine: MACM6 | RTX5070 | CLOUD
git_commit:
config_sha256:
run_ids:
started_utc:
finished_utc:
wall_time:
peak_ram_gb:
peak_vram_gb:
precision:

## Objective
## Inputs
## Numerical method
## Tolerances
## Primary metrics
## Convergence checks
## Pass/fail evaluation
## Anomalies
## Artifacts/checkpoints
## Reproduction command
## What changed from previous report
## Next action
## Handoff references
```

If a run fails, the report is still mandatory.

---

# 7. Handoff protocol — designed for switching devices quickly

`MACHINE_HANDOFF.md` must stay short: target < 80 lines.

Template:

```markdown
# MACHINE HANDOFF

from: RTX5070
to: MACM6
task: G1B-T04
status: PASS
read:
  - AGENTS.md#g1b
  - reports/G1/<latest-report>.md
  - config/gate1/<exact-config>.yaml
latest_checkpoint:
checkpoint_sha256:
do_next:
  - verify continuum fit
  - update STATUS
do_not_repeat:
  - 33^3 minimization already passed
known_issue:
```

The receiving machine should **not** read thousands of lines of old logs. It reads only the referenced gate, latest report, exact config, and handoff.

---

# 8. Mobile/phone control model

The control plane is repository state, not an always-on bespoke daemon.

## Phone-level commands

The user should be able to say:

- `status`
- `continue G1B`
- `show failures`
- `show RTX queue`
- `show Mac queue`
- `pause cloud`
- `approve cloud G2E budget 80 USD`
- `rerun G1C-T03 seed 4`
- `archive failed branch G1D`
- `what do I do on the RTX now?`

An agent translates those requests into reads/updates of `state/state.yaml`, `STATUS.md`, and `NEXT.md`.

## Remote execution levels

### Level 0 — default, no extra infrastructure
You open the target machine, pull Git, read `NEXT.md`, and run the one command shown there.

This is the default until G0D.

### Level 1 — optional phone-triggerable workers
After G0D, optionally install:
- one self-hosted GitHub Actions runner labeled `macm6`;
- one self-hosted runner labeled `rtx5070`.

A tiny workflow may dispatch **only predeclared task IDs/configs**. This creates an auditable remote start mechanism without building a custom control server.

Cloud runners remain ephemeral and require explicit budget approval.

### Important limitation
ChatGPT cannot magically control a powered-off or disconnected home computer. Phone-driven remote continuation requires that the relevant self-hosted runner/remote agent is online and connected.

---

# 9. Cloud cost guard

Cloud state is initially:

```yaml
cloud:
  paused: true
  approved_gate: null
  max_usd_per_run: 0
```

A cloud job is legal only if all are true:

1. its local precursor task is `PASS`;
2. the run is too large/slow/precision-sensitive for RTX5070 or MACM6 by measured evidence;
3. config is frozen;
4. a dry-run memory/runtime estimate exists;
5. `cloud.paused == false`;
6. budget is explicit.

Abort cloud jobs automatically if numerical diagnostics fail early.

---

# 10. Dependency graph

```text
G0A -> G0B -> G0C -> G0D(optional remote control)

G0B -> G1A -> G1B -> G1C -> G1D
                     \-> G1E -> G1F -> G1G
G1B + G1E -> G2A -> G2B -> G2C -> G2D -> G2E -> G2F

G1G + G2F -> G3A -> G3B -> G3C -> G3D

G0A -> G4A -> G4B -> G4C
G1B -> G4D
G4C -> G4E

G2F + G3D + G4C + G4D -> G5A -> G5B -> G5C -> G5D -> G5E
G5E -> G6A -> G6B -> G6C -> G6D -> G6E
```

G4 is a parallel theory track and should start early; it does not have to wait for G3.

---

<a id="g0"></a>
# GATE 0 — Reproducibility foundation

Goal: before adding new physics, reproduce the paper’s existing reduced numerical core.

The published numerical anchors include the reduced \(17^3,21^3,25^3,33^3\) stationary sequence, the Hopf charge near \(-1\), the collective-deflated Hessian checks, the homogeneous trigger benchmark, and the reduced perturbation benchmark.

---

<a id="g0a"></a>
## GATE 0-A — Repository, environment, and control plane

### G0A-T01 — Create repo skeleton
Checklist:
- [ ] create directory tree from §3;
- [ ] add `.gitignore` for large checkpoints;
- [ ] add `pyproject.toml` or equivalent lock strategy;
- [ ] add `config/schema.yaml`;
- [ ] add initial `state/state.yaml`;
- [ ] add report template.

Machines:
- `[X]` MACM6 when repo skeleton and state files are committed.
- RTX5070: N/A.
- CLOUD: N/A.

**Machine order:** `MACM6 -> done`.

### G0A-T02 — Define mathematical core API
Implement backend-neutral definitions for:
- \(M_{ab}\);
- \(C_1\);
- \(C_2=\mathrm{Pf}\,M\);
- self/anti-self-dual projections;
- \(Q_{ab}\);
- reduced \(S^2\) fields;
- static two-derivative term;
- quartic Faddeev-Skyrme term;
- Hopf functional.

Pass criteria:
- analytic identities from Appendix A pass random numerical tests in float64;
- rotation/invariant tests pass;
- CPU finite-difference gradient checks pass.

**Machine order:** `MACM6 -> RTX5070 CUDA mirror`.

### G0A-T03 — Run/config discipline
Implement config loading, run IDs, metadata capture, SHA256, seed control.

Pass criteria:
- same config cannot silently change;
- run directory contains immutable metadata;
- dirty Git tree is explicitly recorded.

**Machine order:** `MACM6`.

---

<a id="g0b"></a>
## GATE 0-B — Reproduce the published reduced Hopf solver

### G0B-T01 — Reduced static energy and spectral derivatives
Implement Eq. (65)-class reduced static functional and full-grid FFT derivatives.

Validation:
- derivative convergence on analytic periodic test fields;
- Parseval consistency;
- boundary/vacuum behavior.

**Machine order:** `MACM6 small test -> RTX5070`.

### G0B-T02 — Hopf invariant
Implement Coulomb-gauge Fourier inversion and the paper’s sign convention.

Validation:
- degree-one initial map;
- smooth deformations preserve charge;
- known trivial map yields \(Q_H\approx0\).

Target:
- reproduce the paper’s unit sector \(Q_H\simeq-1\).

**Machine order:** `MACM6 -> RTX5070`.

### G0B-T03 — Augmented-Lagrangian minimizer
Implement:
- pointwise \(S^2\) projection;
- augmented charge constraint;
- strong-Wolfe L-BFGS or numerically equivalent solver;
- constrained residual.

Run:
- \(17^3,21^3,25^3,33^3\) published sequence.

Engineering pass:
- optimizer residual reaches configured tolerance;
- no NaN/Inf;
- charge remains resolved.

Reproduction target:
- energy and charge agree with the published tables at a predeclared tolerance; default acceptance is:
  - relative energy difference \(\le 5\times10^{-4}\) for matched grid/box;
  - \(|\,|Q_H|-1\,|\le5\times10^{-4}\);
  - qualitative virial trend reproduced.

If a different discretization/optimizer is intentionally used, create a separate equivalence report rather than silently loosening tolerances.

**Machine order:** `RTX5070 -> MACM6 report/fit`.

### G0B-T04 — Published reduced Hessian
Implement:
- tangent frames;
- charge projection;
- matrix-free HVP;
- collective subspace construction;
- Lanczos/LOBPCG lowest modes;
- physical \(h^{-3}\) normalization.

Reproduce:
- positive first non-collective gap;
- refinement trend;
- enlarged-box low-band check.

Pass:
- HVP finite-difference consistency;
- Hessian symmetry residual below tolerance;
- eigenpair residuals numerically controlled;
- collective modes classified rather than mistaken for instabilities.

**Machine order:** `RTX5070 -> MACM6 fit/independent checks`.

---

<a id="g0c"></a>
## GATE 0-C — Cross-device reference validation

### G0C-T01 — CPU reference
MACM6 runs small grids in float64 with a deliberately simple implementation.

Compare:
- energy;
- \(Q_H\);
- gradients;
- HVP directional products.

Pass:
- differences explained by precision/discretization;
- no device-dependent sign convention.

**Machine order:** `MACM6 -> RTX5070 comparison`.

### G0C-T02 — Precision policy
Benchmark RTX5070 float32, float64, and selected mixed precision.

Rule:
- minimization may use faster precision if final observables are rechecked;
- any near-zero Hessian eigenvalue must be recomputed in a numerically appropriate precision, usually CLOUD FP64 if RTX5070 precision is insufficient.

**Machine order:** `RTX5070 -> MACM6 analysis`.

---

<a id="g0d"></a>
## GATE 0-D — Optional remote/mobile runner

Do this only after G0B PASS.

### G0D-T01 — Self-hosted runner on MACM6
- install runner;
- label `macm6`;
- restrict workflow to approved scripts/configs;
- no arbitrary shell from untrusted PRs.

### G0D-T02 — Self-hosted runner on RTX5070
- install runner;
- label `rtx5070`;
- verify CUDA visibility;
- enforce one GPU job at a time.

### G0D-T03 — Phone workflow dispatch
Create actions:
- `status`;
- `run-task`;
- `pause`;
- `cancel`;
- `collect-report`.

No cloud provisioning yet.

**Machine order:** `MACM6 -> RTX5070`.  
CLOUD: N/A.

---

<a id="g1"></a>
# GATE 1 — Unrestricted finite-stiffness soliton sector

**Scientific question:** Does the unit Hopf carrier remain a real, stable, long-lived excitation when the fixed-radius/fixed-balance reduction is removed?

This is the first decisive viability gate.

---

<a id="g1a"></a>
## GATE 1-A — Full six-component static theory

### G1A-T01 — Six-component field representation
Represent
\[
M=(M_{12},M_{13},M_{14},M_{23},M_{24},M_{34})
\]
directly.

Implement:
- \(C_1[M]\);
- \(C_2[M]\);
- \(M_\pm\);
- radial potential;
- finite Pfaffian stiffness;
- full quartic derivative operator as stated in the EFT;
- static energy density.

Tests:
- antisymmetry;
- \(SO(4)\) invariant checks;
- reduction back to fixed-radius/fixed-balance limit;
- finite-difference gradient tests.

**Machine order:** `MACM6 symbolic/reference -> RTX5070 production implementation`.

### G1A-T02 — Lift reduced Hopf state into full \(M\)
Build a deterministic map from the reproduced reduced \((N_+,N_-)=(1,0)\) checkpoint into the six-component field.

Store:
- full field;
- \(C_1-\sigma_0^2\);
- \(C_2\);
- \(Q_+\), \(Q_-\).

Pass:
- lifted state reproduces reduced energy in the heavy-normal-mode limit to declared tolerance.

**Machine order:** `RTX5070 -> MACM6 verification`.

### G1A-T03 — Continuation parameters
Use dimensionless stiffness controls such as
\[
A=\alpha\zeta/Z_M^2,\qquad P=\mu(\lambda_v)\zeta/Z_M^2.
\]

Start deep in the heavy-normal regime and continue gradually toward finite stiffness.

Default continuation philosophy:
- logarithmic steps;
- warm-start each point from the previous converged solution;
- adaptive step reduction near bifurcations;
- never jump directly from the reduced limit to weak stiffness.

**Machine order:** `RTX5070`.

---

<a id="g1b"></a>
## GATE 1-B — Branch persistence and continuum/box convergence

### G1B-T01 — First full-\(M\) stationary point
Suggested first grid:
- \(33^3\), box chosen to match/reuse reduced benchmark scale.

Outputs:
- \(E\);
- \(R_H\);
- \(Q_\pm\);
- constrained/unconstrained residuals;
- max/RMS radial deviation;
- max/RMS \(C_2\);
- minimum \(|M_+|\), \(|M_-|\);
- energy decomposition.

Pass:
- localized nontrivial state exists;
- solver residual controlled;
- no unresolved singular core;
- topology diagnostics are stable under small perturbations.

**Machine order:** `RTX5070 -> MACM6 report`.

### G1B-T02 — Stiffness continuation map
Scan \((A,P)\) from heavy to moderate stiffness.

Use adaptive branch following rather than a blind 2-D brute-force grid.

Track:
- existence;
- energy;
- size;
- normal-mode deformation;
- topology diagnostics.

Stop conditions:
- branch disappears;
- field crosses a true unwinding configuration;
- numerical resolution becomes insufficient.

**Machine order:** `RTX5070`.  
Cloud forbidden at this stage.

### G1B-T03 — Resolution sequence
Preferred staged sequence:
- \(33^3\);
- \(49^3\);
- \(65^3\);
- \(97^3\) only if needed and memory allows.

Do not assume these sizes fit; benchmark measured VRAM first.

Numerical acceptance target for a candidate point:
- last two trustworthy resolutions differ by < 1% in \(E\) and \(R_H\);
- charges/topology diagnostics converge;
- residuals converge;
- qualitative field structure is grid-independent.

**Machine order:** `RTX5070 -> MACM6 convergence fit`.

### G1B-T04 — Box-size sequence
At fixed resolved spacing, enlarge the box until finite-volume compression is controlled.

Pass:
- virial/shape observables and \(E,R_H\) no longer move materially under box enlargement.

**Machine order:** `RTX5070 -> MACM6`.

### G1B-T05 — Cloud escalation decision
Cloud is allowed only if:
- G1B-T01..T04 PASS;
- a specific unresolved continuum/volume question remains;
- RTX memory/runtime profiling is attached.

Cloud target:
- one or two confirmatory high-resolution FP64 or large-memory runs, not a blind scan.

**Machine order:** `RTX5070 evidence -> MACM6 approval packet -> CLOUD -> MACM6 report`.

---

<a id="g1c"></a>
## GATE 1-C — Full physical Hessian

### G1C-T01 — Matrix-free full HVP
Differentiate the full six-component stationary functional.

Requirements:
- no dense Hessian allocation;
- directional finite-difference check;
- symmetry check \(\langle u,Hv\rangle \approx \langle Hu,v\rangle\).

**Machine order:** `RTX5070`.

### G1C-T02 — Collective/gauge-like mode catalog
Construct and remove only justified collective modes:
- translations;
- spatial rotations as applicable;
- internal global rotations compatible with boundary conditions;
- exact constraint/projector nulls if used.

Do not deflate a suspicious mode just because it is small.

**Machine order:** `MACM6 analytic catalog -> RTX5070 implementation`.

### G1C-T03 — Lowest spectrum
Compute the lowest physical eigenpairs at multiple resolutions.

Science pass:
- no robust negative physical mode in the converged full theory.

Numerical rule:
- any eigenvalue whose sign is precision-sensitive is **not PASS**.

**Machine order:** `RTX5070 pilot -> CLOUD FP64 only if sign/size requires it -> MACM6 convergence analysis`.

### G1C-T04 — \(\lambda\)-response / scalar charge precursor
Repeat static solutions for nearby \(\lambda\) values to estimate
\[
\beta_H=M_{\rm Pl}\,\partial_\lambda\ln M_H.
\]

This feeds later perturbation work.

**Machine order:** `RTX5070 -> MACM6 fit`.

---

<a id="g1d"></a>
## GATE 1-D — Minimum-energy unwinding saddle

### G1D-T01 — Path construction
Create endpoints:
- finite-stiffness Hopfion;
- vacuum.

Construct an initial path that allows radial/Pfaffian excursions.

### G1D-T02 — NEB/string method
Use a modest number of images first.

Diagnostics:
- perpendicular force;
- image spacing;
- energy profile;
- charge/topology behavior along path.

### G1D-T03 — Saddle refinement
Refine the highest-energy image with appropriate saddle-search method.

Output:
\[
\Delta E_{\rm unwind}(A,P).
\]

Science pass:
- a positive, resolution-stable barrier exists in the parameter region used later.

A nonzero static barrier is **not by itself** a cosmological lifetime.

**Machine order:** `RTX5070 pilot -> MACM6 path diagnostics -> CLOUD only for final high-resolution refinement`.

---

<a id="g1e"></a>
## GATE 1-E — Real-time stability and principal-symbol monitor

### G1E-T01 — Full PDE formulation
Derive method-of-lines equations from the stated first-derivative EFT.

MACM6 must verify the principal coefficients symbolically or semi-symbolically where feasible.

### G1E-T02 — Time integrator
Default:
- explicit RK4 or another transparent method first;
- CFL chosen from measured characteristic speeds;
- no exotic integrator before validation.

Validation:
- free-wave tests;
- small-amplitude mode frequencies vs Hessian;
- controlled energy drift in a closed static box.

### G1E-T03 — Perturbed-soliton lifetime
Evolve random and mode-aligned perturbations.

Outputs:
- energy;
- charges;
- core diagnostics;
- radiation loss;
- drift in \(C_1,C_2\).

### G1E-T04 — Hyperbolicity monitor
At each saved time:
- construct/evaluate the relevant principal symbol;
- detect sign loss or complex characteristic speeds;
- store minimum kinetic/gradient eigenvalues.

Science rule:
- a visually stable field evolution does not pass if the PDE traverses a non-hyperbolic region.

**Machine order:** `MACM6 derivation -> RTX5070 dynamics -> MACM6 audit`.

---

<a id="g1f"></a>
## GATE 1-F — Collision pilots

### G1F-T01 — Boosted initial states
Build validated two-soliton initial data with:
- velocity;
- impact parameter;
- charge pairing;
- internal orientation.

### G1F-T02 — Boundary treatment
Use a large-enough box plus tested absorbing/sponge region.

Measure reflection with free-wave benchmarks.

### G1F-T03 — Representative channels
At minimum pilot:
- like-charge active sector;
- opposite-charge active sector;
- mixed \((1,0)+(0,1)\)-type sector;
- several internal orientations.

### G1F-T04 — Collision diagnostics
Record:
- \(Q_\pm(t)\);
- core count;
- outgoing velocities;
- scattering angle;
- emitted wave energy;
- capture/annihilation/charge transfer;
- minimum hyperbolicity margin.

**Machine order:** `RTX5070 only for pilots -> MACM6 analysis`.  
Cloud forbidden until pilots are numerically stable.

---

<a id="g1g"></a>
## GATE 1-G — Collision campaign and microscopic cross sections

### G1G-T01 — Adaptive parameter design
Do not brute-force a dense 5-D grid.

Use staged sampling over:
- velocity;
- impact parameter;
- internal orientation;
- selected stiffness points.

Refine only near channel boundaries/resonances.

### G1G-T02 — Cross sections
Compute:
- transfer cross section;
- annihilation probability/cross section;
- capture;
- charge exchange;
- radiation fraction.

### G1G-T03 — Continuum checks
Select representative collision classes for higher resolution.

### G1G-T04 — Production handoff
Export collision kernel tables with uncertainty metadata for Gate 2/3.

**Machine order:**  
`RTX5070 small campaign -> MACM6 adaptive design -> CLOUD GPU ensemble -> MACM6 reduction`.

---

<a id="g2"></a>
# GATE 2 — Expanding-lattice production and relic abundance

**Scientific question:** Does the topology-changing transition actually produce a conserved, sufficiently cold soliton population with the required abundance in an open parameter region?

---

<a id="g2a"></a>
## GATE 2-A — Closed FLRW equations and energy accounting

### G2A-T01 — Replace prescribed bath
Derive the closed homogeneous/inhomogeneous energy exchange consistent with the EFT’s total conservation law.

Required:
- matter/dark exchange bookkeeping;
- \(M,\chi,\lambda\) stresses;
- scale-factor dependence.

### G2A-T02 — Homogeneous closed benchmark
Before any 3-D expansion:
- reproduce trigger-like behavior in a closed ODE system;
- check total Friedmann constraint;
- check exchange residual.

### G2A-T03 — Comoving field equations
Derive equations in variables chosen to minimize numerical stiffness.

**Machine order:** `MACM6 derivation/reference -> RTX5070 smoke test`.

---

<a id="g2b"></a>
## GATE 2-B — Expanding-lattice pilot

### G2B-T01 — 3-D comoving solver
Fields:
- six \(M_{ab}\);
- \(\chi\);
- \(\lambda\).

Start with a prescribed FLRW background only as a code validation mode; the viability run must use the closed accounting from G2A.

### G2B-T02 — Initial fluctuation generator
Every spectrum and seed must be explicit.

No phrase such as “small random noise” without:
- distribution;
- amplitude;
- UV cutoff;
- seed;
- normalization.

### G2B-T03 — \(64^3\) pilot
Measure:
- stability;
- energy/Friedmann residual;
- topology formation;
- VRAM;
- throughput.

### G2B-T04 — \(96^3/128^3\) pilot
Run only after \(64^3\) passes.

**Machine order:** `MACM6 config/check -> RTX5070`.  
Cloud forbidden.

---

<a id="g2c"></a>
## GATE 2-C — Soliton finder and topology tracker

### G2C-T01 — Candidate core detection
Use energy/core diagnostics to propose localized objects.

### G2C-T02 — Charge confirmation
Confirm candidate objects using local/global topology diagnostics robust to noisy wave backgrounds.

### G2C-T03 — Tracking
Track objects across snapshots:
- position;
- velocity;
- charge;
- merger/annihilation history.

### G2C-T04 — Synthetic validation
Test finder on:
- isolated stored solitons;
- boosted solitons;
- two-soliton superpositions;
- pure wave/noise fields.

False positive/negative rates must be reported.

**Machine order:** `MACM6 analysis prototype -> RTX5070 on real snapshots`.

---

<a id="g2d"></a>
## GATE 2-D — Coarse production parameter map

### G2D-T01 — Dimensionless parameter reduction
Reduce redundant scales before scanning.

### G2D-T02 — Space-filling coarse design
Use Sobol/Latin-hypercube or similarly efficient sampling.

Do not grid every parameter blindly.

### G2D-T03 — Multi-seed pilot
Promising parameter points require multiple seeds before escalation.

### G2D-T04 — Early rejection
Automatically reject points with:
- no stable solitons;
- hyperbolicity loss;
- overwhelming residual radiation;
- severe energy-budget failure;
- obviously wrong abundance trend.

**Machine order:** `MACM6 design -> RTX5070 coarse map -> MACM6 classification`.

---

<a id="g2e"></a>
## GATE 2-E — Production continuum/volume/ensemble campaign

### G2E-T01 — Select only promising open regions
No cloud for isolated “lucky” points.

### G2E-T02 — Resolution scaling
Typical ladder:
- local \(128^3\) or largest validated RTX grid;
- cloud \(256^3\);
- \(384^3/512^3\) only if convergence demands it.

### G2E-T03 — Volume scaling
Separate lattice-spacing effects from finite-volume statistics.

### G2E-T04 — Seed ensemble
Estimate cosmic/sample variance of:
- number density;
- charge distribution;
- correlation length;
- wave fraction.

### G2E-T05 — Relic abundance
Redshift the complete energy budget consistently.

**Science pass:** an **open parameter region**, not a hand-normalized single point, produces acceptable present-day dark-matter abundance while surviving the preceding stability tests.

**Machine order:**  
`RTX5070 validation -> MACM6 cloud packet/budget -> CLOUD GPU -> MACM6 ensemble analysis`.

---

<a id="g2f"></a>
## GATE 2-F — Production-derived kinetic/closure data

Extract from successful production runs:

- number density \(n_H(a)\);
- mass spectrum if non-monodisperse;
- phase-space/velocity distribution;
- residual Goldstone/radial wave fractions;
- shot-noise spectrum;
- compensated/uncompensated isocurvature;
- effective sound speed;
- finite-size response coefficients;
- anisotropic stress coefficient;
- mediator excitation spectrum.

Combine with G1C-T04 for \(\beta_H\).

These values replace the illustrative closure inputs in the paper.

**Machine order:** `MACM6 analysis + RTX5070 selected reprocessing`; cloud only if raw-data reduction requires proximity to cloud storage.

---

<a id="g3"></a>
# GATE 3 — Astrophysical darkness

**Scientific question:** Given the *measured* microscopic collision/production outputs, is the soliton population astrophysically acceptable?

---

<a id="g3a"></a>
## GATE 3-A — Self-interaction and number-changing rates

### G3A-T01
Convert dimensionless G1G collision outputs to physical units for each viable scale choice.

### G3A-T02
Construct \(\sigma_T(v)/M_H\) with interpolation uncertainty.

### G3A-T03
Compute annihilation/capture/charge-exchange rates over the produced velocity distribution.

**Machine order:** `MACM6`. RTX5070 used only for missing collision points.

---

<a id="g3b"></a>
## GATE 3-B — Scalar-mediated and long-range interactions

Use measured/derived \(\beta_H\), mediator/scalar masses, and the EFT portal.

Calculate:
- soliton-soliton fifth-force correction;
- range dependence;
- environmental dependence if present;
- whether residual tangent modes create unacceptable long-range effects.

Do not substitute the paper’s illustrative \(\beta_H=0.02\) once G1C-T04 exists.

**Machine order:** `MACM6`.

---

<a id="g3c"></a>
## GATE 3-C — Visible-sector/stellar constraints

Version-lock the observational/astrophysical input dataset and cite its source in the report.

Evaluate, as applicable:
- visible scattering induced by the matter portal;
- equivalence-principle/fifth-force consequences;
- stellar cooling/energy-loss channels;
- capture/heating constraints;
- small-scale structure implications.

If a coupling is absent at a given perturbative order, document the derivation rather than assuming zero forever.

**Machine order:** `MACM6`; CLOUD CPU only for large population integrations if profiling justifies it.

---

<a id="g3d"></a>
## GATE 3-D — Astrophysical allowed region

Intersect:
- Gate 1 stability;
- Gate 2 abundance;
- Gate 3 interaction limits.

Output a machine-readable allowed-region table, not only a plot.

Pass:
- at least one finite-volume/open region remains after uncertainties.

**Machine order:** `MACM6`.

---

<a id="g4"></a>
# GATE 4 — Radiative naturalness, vacuum decay, and gravity

This gate may run in parallel starting after G0A.

The paper explicitly notes that the stated symmetries do **not** protect the absolute dark-energy scale, the ultra-light \(\lambda\) curvature, or the quartic onset of \(\mu(\lambda)\); lower-order counterterms are allowed. Treat this as a real gate, not a footnote.

---

<a id="g4a"></a>
## GATE 4-A — Operator basis and symmetry audit

### G4A-T01
Enumerate operators up to the chosen EFT order consistent with:
- diffeomorphism invariance;
- internal \(SO(4)\);
- \(\chi\to-\chi\);
- stated field content.

### G4A-T02
Classify which absent operators are:
- symmetry forbidden;
- redundant by field redefinition/EOM;
- merely tuned to zero.

### G4A-T03
Specifically audit lower-order
\[
\lambda^n C_2^2
\]
terms and the functional form of \(\Xi(\chi)\).

**Machine order:** `MACM6`.

---

<a id="g4b"></a>
## GATE 4-B — One-loop EFT corrections and matching

Compute the relevant one-loop effective-potential/counterterm structure at the precision needed to assess:

- \(\lambda\) mass stability;
- vacuum-energy stability;
- \(\mu(\lambda)\) switching hierarchy;
- mediator/scalar mixing;
- portal-induced corrections.

Output:
- renormalization conditions;
- scale dependence;
- tuning measure(s);
- cutoff/matching sensitivity.

**Machine order:** `MACM6`.  
CLOUD unnecessary unless symbolic/numerical integration profiling proves otherwise.

---

<a id="g4c"></a>
## GATE 4-C — Naturalness decision branch

Classify the result explicitly:

1. technically natural in the stated EFT;
2. viable but radiatively tuned;
3. requires an added protection mechanism;
4. inconsistent/uncontrolled.

If option 3 is chosen, create a **new theory branch**; do not silently alter the baseline model.

**Machine order:** `MACM6`.

---

<a id="g4d"></a>
## GATE 4-D — Gravitational Coleman–De Luccia decay

### G4D-T01 — Flat-space regression
Reproduce the published bounce coefficient first.

### G4D-T02 — Gravity-aware equations
Implement CDL O(4)-symmetric bounce including gravitational backreaction.

### G4D-T03 — Lifetime region
Compute the semiclassical action and prefactor treatment at the level justified by the EFT.

Pass:
- metastable branch lifetime comfortably exceeds the required cosmological timescale over the retained parameter region.

**Machine order:** `MACM6`.  
Cloud CPU only for broad parameter scans.

---

<a id="g4e"></a>
## GATE 4-E — Gravitating soliton relevance test

First compute compactness:
\[
{\cal C}\sim G M_H/R_H.
\]

Conditional path:
- if \({\cal C}\ll1\) over the viable region, document quantitative negligibility and stop;
- if not, solve the coupled gravitating soliton/background problem and repeat the relevant stability analysis.

This conditional gate prevents unnecessary GR numerics.

**Machine order:** `MACM6 estimate -> RTX5070/CLOUD only if required`.

---

<a id="g5"></a>
# GATE 5 — Boltzmann-complete cosmology

Do not begin final implementation until G2F supplies production-derived inputs.

---

<a id="g5a"></a>
## GATE 5-A — Species model and initial conditions

Derive the complete linear system including, where required:

- Hopfion density/velocity;
- measured effective sound speed;
- anisotropic stress;
- shot noise;
- residual Goldstone/radial waves;
- mediator perturbations;
- scalar perturbations;
- compensated/uncompensated isocurvature;
- radiation;
- neutrino hierarchy;
- metric response;
- super-horizon initial conditions.

**Machine order:** `MACM6`.

---

<a id="g5b"></a>
## GATE 5-B — CLASS implementation

Implement the minimum invasive extension.

Rules:
- preserve a clean decoupling limit to baseline CLASS;
- each new species/term behind explicit parameters;
- no hard-coded production values;
- load G2F outputs through versioned tables/configs.

**Machine order:** `MACM6`.

---

<a id="g5c"></a>
## GATE 5-C — Cosmological stability and regression

Tests:
- \(\beta_H\to0\) decoupling;
- residual-wave fraction \(\to0\);
- cold limit;
- numerical gauge/regression checks;
- no ghost/gradient pathology in implemented regime;
- super-horizon behavior;
- conservation identities.

Compare reduced limit against the paper’s candidate-level benchmark where the assumptions overlap.

**Machine order:** `MACM6`.

---

<a id="g5d"></a>
## GATE 5-D — Spectra production

Generate:
- CMB TT/TE/EE;
- lensing;
- matter \(P(k)\);
- growth observables;
- transfer functions;
- isocurvature contributions.

Build fast failure checks before expensive scans.

**Machine order:** `MACM6 development -> CLOUD CPU only for ensembles`.

---

<a id="g5e"></a>
## GATE 5-E — Parameter-to-observable emulator decision

Do **not** automatically build an emulator.

Only if likelihood profiling shows CLASS runtime is the bottleneck:
- build a controlled surrogate;
- validate it on held-out points;
- never use outside its training domain.

**Machine order:** `MACM6 decision -> CLOUD CPU/GPU only if justified`.

---

<a id="g6"></a>
# GATE 6 — Likelihood-level viability

---

<a id="g6a"></a>
## GATE 6-A — Likelihood stack and data freeze

Choose one inference framework and freeze:
- dataset versions;
- nuisance treatment;
- priors;
- covariance/likelihood versions.

Potential categories are those identified by the paper:
- CMB temperature/polarization/lensing;
- BAO;
- supernovae;
- growth;
- weak lensing;
- small-scale structure where theoretically controlled.

Do not add every available dataset at once. Stage them.

**Machine order:** `MACM6`.

---

<a id="g6b"></a>
## GATE 6-B — Prior predictive and profile scans

Before MCMC:
- reject unstable regions;
- verify spectra;
- find sensitive parameter combinations;
- inspect degeneracies.

This avoids wasting cloud CPU on obviously bad regions.

**Machine order:** `MACM6 -> small CLOUD CPU if needed`.

---

<a id="g6c"></a>
## GATE 6-C — Full inference

Run converged posterior sampling only over the physically prefiltered region.

Required:
- chain convergence diagnostics;
- effective sample size;
- independent restart;
- nuisance stability;
- reproducible likelihood config.

**Machine order:** `CLOUD CPU -> MACM6 diagnostics`.

---

<a id="g6d"></a>
## GATE 6-D — Robustness

Repeat with:
- prior variations;
- selected dataset removal;
- numerical tolerance tightening;
- production-coefficient uncertainty propagation.

**Machine order:** `CLOUD CPU -> MACM6`.

---

<a id="g6e"></a>
## GATE 6-E — Final viability dossier

Produce one final report that answers, without marketing language:

1. Does the unrestricted Hopf sector exist?
2. Is it linearly/dynamically stable?
3. Is unwinding sufficiently suppressed?
4. Are collision dynamics hyperbolic and astrophysically acceptable?
5. Is the observed abundance produced in an open region?
6. Are residual waves/isocurvature acceptable?
7. Is the DE branch sufficiently long-lived?
8. What radiative tuning remains?
9. Does the full Boltzmann system remain stable?
10. Is there a stable posterior region?

Final labels:
- `VIABLE_WITHIN_TESTED_EFT`
- `VIABLE_BUT_TUNED`
- `PARTIAL / UNRESOLVED`
- `FAILED_LOAD_BEARING_GATE`

**Machine order:** `MACM6`.

---

# 11. Practical per-machine checklists

These are generated from state, but the conceptual order is fixed.

## MACM6 default checklist
- [ ] pull latest repo;
- [ ] read `NEXT.md`;
- [ ] read only referenced gate/report;
- [ ] run symbolic/reference/analysis task;
- [ ] create report;
- [ ] mark MACM6 `[X]`;
- [ ] write concise handoff;
- [ ] push state/report.

## RTX5070 default checklist
- [ ] pull latest repo;
- [ ] confirm exact config hash;
- [ ] run smoke test;
- [ ] record VRAM/runtime;
- [ ] run production task;
- [ ] save checkpoint + SHA256;
- [ ] create report;
- [ ] mark RTX5070 `[X]`;
- [ ] handoff to MACM6 for analysis;
- [ ] push metadata/report, not huge raw data.

## CLOUD default checklist
- [ ] verify cloud approval + budget;
- [ ] verify local precursor PASS;
- [ ] freeze image/environment;
- [ ] dry-run on small input;
- [ ] start bounded job;
- [ ] abort early on diagnostic failure;
- [ ] persist outputs/checkpoint;
- [ ] create report;
- [ ] mark CLOUD `[X]`;
- [ ] terminate resources;
- [ ] handoff to MACM6.

---

# 12. Failure and rollback strategy

For any FAIL:

1. freeze failing checkpoint/config;
2. create `FAIL` report;
3. classify:
   - implementation;
   - discretization;
   - precision;
   - finite volume;
   - optimizer/integrator;
   - genuine physical instability;
   - unknown;
4. perform the *smallest discriminating test*;
5. do not widen the parameter scan until the classification is resolved.

A cloud failure does not automatically justify a larger cloud machine.

---

# 13. Branch discipline

Recommended branches:

```text
main
reproduce/published
gate1/full-m
gate1/collisions
gate2/production
gate4/radiative
gate5/class
gate6/likelihood
```

Scientific results enter `main` only with:
- passing tests;
- a report;
- exact config;
- checkpoint/data reference;
- review of the relevant gate’s pass criteria.

---

# 14. First sprint — what happens now

Do not start with cloud, collisions, or cosmological likelihood.

### Sprint S0
1. `G0A-T01` repo/control files.
2. `G0A-T02` invariant/math core.
3. `G0B-T01` reduced spectral energy.
4. `G0B-T02` Hopf invariant.
5. `G0B-T03` reproduce \(17^3,21^3,25^3,33^3\).
6. `G0B-T04` reproduce reduced Hessian.
7. `G0C-T01` independent MACM6 validation.

### Sprint S1
8. `G1A-T01` six-component full \(M\).
9. `G1A-T02` lift published Hopf checkpoint.
10. `G1B-T01` first full-\(M\) \(33^3\) stationary solution.
11. `G1B-T02` continuation in stiffness.
12. `G1B-T03/T04` resolution and box convergence.
13. `G1C` full physical Hessian.

Only after S1 is scientifically healthy do we invest in:
- G1D unwinding;
- G1E/F/G dynamics/collisions;
- G2 expanding production;
- cloud scale-up.

---

# 15. Machine routing summary by gate

| Gate | MACM6 | RTX5070 | CLOUD | Default order |
|---|---|---|---|---|
| G0 | control/reference/report | reduced numerics | no | MAC -> RTX -> MAC |
| G1A-B | analytic checks/report | **primary** | confirmatory only | MAC -> RTX -> MAC -> optional cloud |
| G1C | mode catalog/analysis | pilot HVP | FP64/large memory if needed | MAC -> RTX -> optional cloud -> MAC |
| G1D | path analysis | pilot NEB | final refinement if needed | RTX -> MAC -> optional cloud |
| G1E-F | derivation/audit | **primary dynamics** | no until stable | MAC -> RTX -> MAC |
| G1G | adaptive design/reduction | small campaign | **ensemble** | RTX -> MAC -> cloud -> MAC |
| G2A | **primary derivation** | smoke test | no | MAC -> RTX |
| G2B-D | configs/analysis | **primary pilots** | no | MAC -> RTX -> MAC |
| G2E | ensemble analysis | validation | **primary large lattice** | RTX -> MAC -> cloud -> MAC |
| G2F | **primary reduction** | selected reprocessing | optional | MAC/RTX |
| G3 | **primary** | fill missing simulations | optional CPU | MAC |
| G4A-C | **primary** | no | no | MAC |
| G4D | **primary** | no | broad scan only | MAC -> optional cloud |
| G4E | estimate | if needed | if needed | MAC -> conditional |
| G5 | **development** | no | CPU ensembles | MAC -> cloud -> MAC |
| G6 | setup/diagnostics | no | **full inference** | MAC -> cloud -> MAC |

---

# 16. Definition of “done”

A task is done only if:

- code/config is committed;
- required tests pass;
- run is identified;
- report exists;
- artifacts/checkpoints are referenced with hashes;
- pass/fail criteria are explicitly evaluated;
- assigned machine marks `[X]`;
- handoff is written if another machine is next;
- `NEXT.md` points to exactly one next action.

No screenshot-only results. No “looks stable”. No untracked parameter tweaks.

---

# 17. Current next action

**Start at `G0A-T01` on MACM6.**

The first device switch occurs only after the repo/control layer and mathematical core are committed. Then RTX5070 takes over the first GPU benchmark work.

