# MACHINE HANDOFF

from: RTX5070
to: RTX5070
task: G0B-T03
status: TODO
read:
  - AGENTS.md#g0b
  - NEXT.md
  - docs/RTX5070_READY.md
  - docs/G0B_SOLVER_PREPARATION.md
  - reports/G0/G0B-T02__G0B-T02__RTX5070__20261003T203645Z__1cb2c8a__23ad6ac8__REPORT.md
  - reports/G0/G0B-T05__G0B-T05__MACM6__20261003T100609Z__d3106d3__f7f8faca__REPORT.md
latest_checkpoint: checkpoints/G0B-T02__RTX5070__20261003T203645Z__1cb2c8a__23ad6ac8__initial.h5
checkpoint_sha256: 4e462a0f240fb28f8a21033f07594aa94a73bb51d21eabeb37e0a8015c89d1bb
checkpoint_stationary: false
source_pdf_sha256: 09111940dc2575283d8db69ee65785d2b85beb3864e416e63c7538e91c70c312
environment: docs/RTX5070_ENVIRONMENT.json
environment_freeze: requirements/rtx5070.freeze.txt
python: .venv/Scripts/python.exe
git_remote: https://github.com/Insanazorx/viability-test-for-fock.git
branch: reproduce/rtx5070-cuda
do_next:
  - implement and validate identified/resumable G0B-T03 CUDA production driver
  - freeze matched 17^3,21^3,25^3,33^3 source settings and unchanged tolerances
  - document archived-initializer absence and any solver/initializer equivalence
  - run stationary acceptance before G0B-T04 spectrum; MACM6 analysis follows GPU
do_not_repeat:
  - G0A-T02, G0B-T01, G0B-T02 actual float64 CUDA checks passed
  - completed MACM6 references/reports and original nonstationary checkpoint preserved
known_issue:
  - first G0B-T02 CUDA validator failed on NumPy/scalar detach; FAIL report preserved
  - smallest mixed-type conversion repair passed identical frozen config; no tolerance change
  - G0B-T03/T04 production drivers, stationary sequence and physical spectrum still pending
  - source archived initializer is absent; available checkpoints are independent fixtures
  - GitHub has one upload commit, not original MACM6 history; original bundle needed for old commits
  - full physical matching/production/lifetime and scientific viability remain PARTIAL / UNRESOLVED
  - CLOUD paused, zero budget; optional remote runners disabled
