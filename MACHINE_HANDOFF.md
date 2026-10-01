# MACHINE HANDOFF

from: MACM6
to: RTX5070
task: G0A-T02
status: PASS (MACM6 responsibility); RUNNING (whole task)
read:
  - AGENTS.md#g0a
  - reports/G0/G0A-T02__G0A-T02__MACM6__20261001T060259Z__ec15d04__1f458c06__REPORT.md
  - docs/MATH_CORE.md
  - docs/RTX5070_CORE_HANDOFF.md
  - config/benchmark/g0a_t02_rtx5070.json.yaml
  - config/benchmark/publication.source.yaml
latest_checkpoint: N/A
checkpoint_sha256: N/A
do_next:
  - copy exact source PDF and prepare Python 3.12 plus CUDA-enabled PyTorch on RTX5070
  - run the single frozen CUDA mirror command in NEXT.md
  - create report and record only RTX5070 completion
do_not_repeat:
  - MACM6 source/math reference is committed and its 31 tests passed
  - float64 invariants: 1536 samples; SO(4): 96 rotations; gradients: 3 step sizes
known_issue:
  - CUDA implementation is present but unexecuted; RTX5070 verification is required
  - G0A-T03 full environment/run discipline remains TODO
  - no unit Hopf charge, lattice solution, or Hessian is yet reproduced
  - source PDF is ignored by Git; required SHA256 is in source manifest
  - no Git remote configured; CLOUD paused
