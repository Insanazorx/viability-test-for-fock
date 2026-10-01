# MACHINE HANDOFF

from: MACM6
to: MACM6
task: G4A-T01
status: RUNNING
read:
  - AGENTS.md#g4a
  - docs/G4A_OPERATOR_BASIS.md
  - config/gate4/g4a_t01_macm6.json.yaml
  - config/benchmark/publication.source.yaml
  - reports/G0/G0B-T02__G0B-T02__MACM6__20261001T190551Z__1d2b32d__73b620d2__REPORT.md
latest_checkpoint: checkpoints/G0B-T02__MACM6__20261001T190551Z__1d2b32d__73b620d2__initial.h5
checkpoint_sha256: 462ee5c0e3015d9014b669eabfd78d47b1050e2301961f4a35cb3deb99e792eb
do_next:
  - commit the chosen-order operator definitions/config before the identified MACM6 acceptance run
  - report exact counts/rank and continuous invariant witnesses; mark only this responsibility
  - then classify absent operators in G4A-T02 before the G4A-T03 functional audit
do_not_repeat:
  - MACM6 repository/environment/core, spectral energy and Hopf reference passed
  - no stationary minimization or CUDA benchmark is authorized for this MACM6 theory inventory
known_issue:
  - scope is analytic dark/metric d<=4 modulo IBP; source higher-order exceptions are separate
  - L_m is unspecified; no concrete matter basis, loop coefficient or naturalness decision exists
  - G0A-T02/G0B-T01/G0B-T02 CUDA remain unfinished and RTX5070 remains deferred
  - CLOUD paused, budget zero, remote runners disabled
