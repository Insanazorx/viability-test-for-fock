# MACHINE HANDOFF

from: RTX5070
to: RTX5070
task: G0B-T03
status: RUNNING
read:
  - AGENTS.md#g0b
  - NEXT.md
  - docs/RTX5070_READY.md
  - reports/G0/REPOSITORY_BUNDLE__RTX5070__20261003T211442Z__REPORT.md
  - docs/G0B_SOLVER_PREPARATION.md
  - docs/G0B_PRODUCTION_CONTRACT.md
  - config/benchmark/g0b_t03_rtx5070.json.yaml
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
execution_preference: RTX5070 until explicit user change
restored_macm6_branch: codex/macm6-completion
bundle_sha256: b2b03fa07c1e8e9177316eee035af3831252829ef88e2b01438f53c87c888d3e
do_next:
  - run frozen G0B-T03 CUDA production driver after clean code/config commit
  - preserve matched 17^3,21^3,25^3,33^3 settings and unchanged tolerances
  - document archived-initializer absence and any solver/initializer equivalence
  - run stationary acceptance before G0B-T04 spectrum; MACM6 analysis follows GPU
do_not_repeat:
  - G0A-T02, G0B-T01, G0B-T02 actual float64 CUDA checks passed
  - completed MACM6 references/reports and original nonstationary checkpoint preserved
known_issue:
  - first G0B-T02 CUDA validator failed on NumPy/scalar detach; FAIL report preserved
  - smallest mixed-type conversion repair passed identical frozen config; no tolerance change
  - G0B-T03 driver implemented/tested; stationary acceptance and G0B-T04 spectrum pending
  - source archived initializer is absent; available checkpoints are independent fixtures
  - original MACM6 history restored separately from bundle; current RTX5070 branch preserved
  - full physical matching/production/lifetime and scientific viability remain PARTIAL / UNRESOLVED
  - CLOUD paused, zero budget; optional remote runners disabled
