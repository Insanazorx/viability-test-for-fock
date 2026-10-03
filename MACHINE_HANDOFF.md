# MACHINE HANDOFF

from: MACM6
to: MACM6
task: G4C-T02
status: TODO
read:
  - AGENTS.md#g4c
  - docs/G4C_CONDITIONAL_STATUS.md
  - config/gate4/g4c_t02_macm6.json.yaml
  - reports/G4/G4B-T01__G4B-T01__MACM6__20261003T103247Z__d64b18b__39461767__REPORT.md
do_next:
  - run the frozen MACM6 substep, write report, record machine completion
  - continue docs/MACM6_COMPLETION_PLAN.md
do_not_repeat:
  - passed references and sealed historical runs
known_issue:
  - RTX5070 deferred until feasible MACM6 work complete
  - concrete matter action and physical scale matching inputs unavailable
  - CLOUD paused; zero budget; no remote runner
