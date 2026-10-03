# MACHINE HANDOFF

from: MACM6
to: MACM6
task: G4A-T02
status: TODO
read:
  - AGENTS.md#g4a
  - docs/G4A_SYMMETRY_AUDIT.md
  - config/gate4/g4a_t02_macm6.json.yaml
  - reports/G4/G4A-T01__G4A-T01__MACM6__20261001T193427Z__8e637b1__f5f125f4__REPORT.md
do_next:
  - run the frozen MACM6 substep, write report, record machine completion
  - continue docs/MACM6_COMPLETION_PLAN.md
do_not_repeat:
  - passed references and sealed historical runs
known_issue:
  - RTX5070 deferred until feasible MACM6 work complete
  - concrete matter action and physical scale matching inputs unavailable
  - CLOUD paused; zero budget; no remote runner
