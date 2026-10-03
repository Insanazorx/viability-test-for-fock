# MACHINE HANDOFF

from: MACM6
to: MACM6
task: G1A-T04
status: RUNNING
read:
  - AGENTS.md#g1a
  - docs/MACM6_COMPLETION_PLAN.md
  - docs/G1A_FULL_STATIC_PREPARATION.md
  - config/gate1/g1a_t04_macm6.json.yaml
  - reports/G0/G0B-T05__G0B-T05__MACM6__20261003T100609Z__d3106d3__f7f8faca__REPORT.md
latest_checkpoint: checkpoints/G0B-T02__MACM6__20261001T190551Z__1d2b32d__73b620d2__initial.h5
checkpoint_sha256: 462ee5c0e3015d9014b669eabfd78d47b1050e2301961f4a35cb3deb99e792eb
do_next:
  - commit and run the frozen six-component static reference validation
  - complete only G1A-T04 MACM6 engineering responsibility
  - continue G4 symmetry and radiative audits before RTX5070
do_not_repeat:
  - G0B-T05 CPU solver/HVP/direct-DFT preparation passed 98 tests
known_issue:
  - G0B-T03/T04 production sequence/spectrum remain pending RTX5070
  - full-field CPU checks do not establish a stationary soliton or physical spectrum
  - source archived initializer unavailable; existing checkpoint is an independent nonstationary fixture
  - concrete L_m and GPU-derived mass/size/production inputs unavailable
  - RTX5070 deferred; CLOUD paused with zero budget
