# MACHINE HANDOFF

from: MACM6
to: MACM6
task: G0A-T03
status: RUNNING
read:
  - AGENTS.md#g0a
  - docs/RUNBOOK.md
  - config/benchmark/g0a_t03_macm6.json.yaml
  - config/frozen_registry.yaml
  - requirements/macm6.freeze.txt
latest_checkpoint: N/A
checkpoint_sha256: N/A
do_next:
  - commit the MACM6 infrastructure and execute the identified acceptance command in NEXT.md
  - create the mandatory G0A-T03 report and record only MACM6 completion
  - return NEXT to the pending G0A-T02 CUDA responsibility on RTX5070
do_not_repeat:
  - MACM6 source/math reference is committed and its 31 tests passed
  - float64 invariants: 1536 samples; SO(4): 96 rotations; gradients: 3 step sizes
known_issue:
  - CUDA implementation is present but unexecuted; RTX5070 verification is required
  - G0A-T03 is the single active action at the user's request; CUDA completion is not waived
  - no unit Hopf charge, lattice solution, or Hessian is yet reproduced
  - source PDF is ignored by Git; required SHA256 is in source manifest
  - no Git remote configured; CLOUD paused
