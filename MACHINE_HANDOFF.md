# MACHINE HANDOFF

from: MACM6
to: MACM6
task: G4B-T01
status: TODO
read:
  - AGENTS.md#g4b
  - docs/G4B_DARK_LOOP.md
  - config/gate4/g4b_t01_macm6.json.yaml
  - reports/G4/G4A-T03__G4A-T03__MACM6__20261003T102746Z__d2910a1__08b1fafb__REPORT.md
do_next:
  - run the frozen MACM6 substep, write report, record machine completion
  - continue docs/MACM6_COMPLETION_PLAN.md
do_not_repeat:
  - passed references and sealed historical runs
known_issue:
  - RTX5070 deferred until feasible MACM6 work complete
  - concrete matter action and physical scale matching inputs unavailable
  - CLOUD paused; zero budget; no remote runner
