# MACHINE HANDOFF

from: MACM6
to: MACM6
task: G0B-T05
status: RUNNING
read:
  - AGENTS.md#g0b
  - docs/MACM6_COMPLETION_PLAN.md
  - docs/G0B_SOLVER_PREPARATION.md
  - config/benchmark/g0b_t05_macm6.json.yaml
  - reports/G0/G0B-T02__G0B-T02__MACM6__20261001T190551Z__1d2b32d__73b620d2__REPORT.md
latest_checkpoint: checkpoints/G0B-T02__MACM6__20261001T190551Z__1d2b32d__73b620d2__initial.h5
checkpoint_sha256: 462ee5c0e3015d9014b669eabfd78d47b1050e2301961f4a35cb3deb99e792eb
do_next:
  - commit and run the frozen small-grid solver/HVP/independent-DFT preparation
  - write a report and complete only G0B-T05 MACM6 engineering responsibility
  - continue the independent MACM6 program before switching to RTX5070
do_not_repeat:
  - prior MACM6 core/energy/Hopf and G4A operator basis passed
known_issue:
  - G0B-T03/T04 scientific sequence/spectrum remain pending RTX5070 production
  - CPU small-grid vacuum convergence does not establish nontrivial soliton stationarity
  - source archive/initializer unavailable; fixture independently derived
  - concrete L_m and all later GPU-derived mass/size/production inputs remain unavailable
  - RTX5070 deferred until feasible MACM6 work complete; CLOUD paused, budget zero
