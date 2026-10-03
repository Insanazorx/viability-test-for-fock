# MACHINE HANDOFF

from: MACM6
to: MACM6
task: G4D-T04
status: TODO
read:
  - AGENTS.md#g4d
  - docs/G4D_DECAY_PREPARATION.md
  - config/gate4/g4d_t04_macm6.json.yaml
  - reports/G4/G4C-T02__G4C-T02__MACM6__20261003T103849Z__bcf5cc8__dda1cf83__REPORT.md
do_next:
  - run the frozen MACM6 substep, write report, record machine completion
  - continue docs/MACM6_COMPLETION_PLAN.md
do_not_repeat:
  - passed references and sealed historical runs
known_issue:
  - RTX5070 deferred until feasible MACM6 work complete
  - concrete matter action and physical scale matching inputs unavailable
  - CLOUD paused; zero budget; no remote runner
