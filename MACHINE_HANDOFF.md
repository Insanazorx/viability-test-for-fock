# MACHINE HANDOFF

from: MACM6
to: RTX5070
task: G0A-T02
status: RUNNING
scheduling: DEFERRED — user opens RTX5070 after MACM6 preparation
read:
  - AGENTS.md#g0a
  - docs/DEVICE_CONTINUATION.md
  - docs/G0_MACM6_REMAINING.md
  - docs/RTX5070_READY.md
  - config/benchmark/g0a_t02_rtx5070.json.yaml
  - reports/G0/G0A-T02__G0A-T02__MACM6__20261001T060259Z__ec15d04__1f458c06__REPORT.md
  - reports/G0/G0A-T04__G0A-T04__MACM6__20261003T104642Z__ff719b7__32d67550__REPORT.md
latest_checkpoint: checkpoints/G0B-T02__MACM6__20261001T190551Z__1d2b32d__73b620d2__initial.h5
checkpoint_sha256: 462ee5c0e3015d9014b669eabfd78d47b1050e2301961f4a35cb3deb99e792eb
checkpoint_stationary: false
source_pdf_sha256: 09111940dc2575283d8db69ee65785d2b85beb3864e416e63c7538e91c70c312
do_next:
  - restore the offline Git bundle, exact PDF and independent checkpoint
  - create and record the actual Python3.12/CUDA environment on RTX5070
  - resume/focus G0A-T02 on that device, verify CUDA preflight, run its frozen config
  - write one report and record only RTX5070 completion; follow NEXT
do_not_repeat:
  - completed MACM6 available-input preparation: docs/MACM6_COMPLETION_SUMMARY.md
known_issue:
  - G0B-T03/T04 production drivers/sequence/spectrum remain RTX5070 work
  - source archived initializer absent; checkpoint is an independent nonstationary fixture
  - full matter/portal matching and physical scales/cutoff unresolved
  - final radiative viability and gravitational lifetime remain PARTIAL / UNRESOLVED
  - CLOUD paused, zero budget; no remote runner or Git remote configured
