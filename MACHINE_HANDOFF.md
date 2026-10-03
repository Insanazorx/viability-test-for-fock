# MACHINE HANDOFF

from: RTX5070
to: RTX5070
task: G0B-T03
status: FAIL
read:
  - AGENTS.md#g0b
  - NEXT.md
  - reports/G0/G0B-T03__G0B-T03__RTX5070__20261003T220757Z__68eddf6__9df9405b__REPORT.md
  - reports/G0/G0B-T03__G0B-T03__RTX5070__20261003T220757Z__68eddf6__9df9405b__EQUIVALENCE.md
  - docs/G0B_CONVERGENCE_DIAGNOSIS.md
  - docs/G0B_PRODUCTION_CONTRACT.md
  - config/benchmark/g0b_t03_rtx5070.json.yaml
latest_checkpoint: checkpoints/G0B-T03__RTX5070__20261003T220757Z__68eddf6__9df9405b__N21__outer4.h5
checkpoint_sha256: 2d44f98c2ce75f9a48aaef529aba7b8eabac87d98a29d419ff8bef10ecb18fc9
checkpoint_stationary: false
partial_accepted_checkpoint: checkpoints/G0B-T03__RTX5070__20261003T220757Z__68eddf6__9df9405b__N17__accepted.h5
partial_accepted_sha256: 165388f307dfa8eac761c316d930890e92566bc5d80cedf583dd70ed9656eff7
partial_scope: 17^3 row only; not full task completion or physical Hessian
config_sha256: 9df9405b559f40888a11681483375bc59bde622ea2846eee5de3c460b3e8c761
source_pdf_sha256: 09111940dc2575283d8db69ee65785d2b85beb3864e416e63c7538e91c70c312
environment: docs/RTX5070_ENVIRONMENT.json
environment_freeze: requirements/rtx5070.freeze.txt
python: .venv/Scripts/python.exe
git_remote: https://github.com/Insanazorx/viability-test-for-fock.git
branch: reproduce/rtx5070-cuda
execution_preference: RTX5070 until explicit user change
restored_macm6_branch: codex/macm6-completion
bundle_sha256: b2b03fa07c1e8e9177316eee035af3831252829ef88e2b01438f53c87c888d3e
do_next:
  - diagnose 21^3 chart/initializer/AL convergence in a separately identified narrow test
  - preserve source settings and unchanged energy/charge/residual acceptance
  - record explicit recovery only after classifying the frozen FAIL; do not widen grids
do_not_repeat:
  - G0A-T02, G0B-T01, G0B-T02 actual float64 CUDA checks passed
  - completed MACM6 references/reports and original nonstationary checkpoint preserved
  - 17^3 row accepted; no full G0B-T03 device completion was marked
  - final source-field NumPy/CUDA/autograd comparisons already agree
known_issue:
  - first G0B-T02 CUDA validator failed on NumPy/scalar detach; FAIL report preserved
  - smallest mixed-type conversion repair passed identical frozen config; no tolerance change
  - 21^3 final constrained RMS 3.430415758e-5 exceeds predeclared 1e-5
  - energy/charge pass; all inner solves reach 120 iterations, none pass the gradient stop
  - third AL update RMS 9.8244e-6 cannot replace the configured fourth update
  - 25^3/33^3 NOT_RUN; G0B-T04 spectrum/driver still pending
  - archived production initializer absent; independent realization equivalence unresolved
  - numerical optimizer failure, not an established physical instability or EFT reformulation
  - original MACM6 history restored separately from bundle; current RTX5070 branch preserved
  - full physical matching/production/lifetime and scientific viability remain PARTIAL / UNRESOLVED
  - CLOUD paused, zero budget; no automatic MACM6 switch or new machine completion
