# MACHINE HANDOFF

from: MACM6
to: RTX5070
task: G0A-T02
status: PASS (MACM6 foundation); RUNNING (CUDA mirror pending)
read:
  - AGENTS.md#g0a
  - reports/G0/G0A-T02__G0A-T02__MACM6__20261001T060259Z__ec15d04__1f458c06__REPORT.md
  - reports/G0/G0A-T03__G0A-T03__MACM6__20261001T174323Z__9336699__a64a600a__REPORT.md
  - docs/MATH_CORE.md
  - docs/RTX5070_CORE_HANDOFF.md
  - config/benchmark/g0a_t02_rtx5070.json.yaml
  - config/benchmark/publication.source.yaml
latest_checkpoint: N/A
checkpoint_sha256: N/A
do_next:
  - open/copy this committed checkout on RTX5070 with the exact supplied source PDF
  - prepare Python 3.12 and CUDA-enabled PyTorch for the measured driver/hardware
  - execute the single frozen CUDA mirror command in NEXT.md
  - create report and record only RTX5070 completion
do_not_repeat:
  - G0A-T01 MACM6 repository foundation passed
  - G0A-T02 MACM6 source/math reference passed; 1536 invariant samples and 96 rotations
  - G0A-T03 MACM6 infrastructure passed; 49 tests, 25 frozen packages, 4 frozen configs
known_issue:
  - RTX5070 is not connected to this session; CUDA remains unexecuted
  - source PDF is ignored by Git; copy it with SHA256 from the source manifest
  - the first G0A-T03 attempt failed on SciPy 1.15.3; its evidence is preserved and 1.16.3 passed
  - a non-fatal Fontconfig cache warning occurred; the PNG smoke check passed
  - no unit Hopf charge, lattice solution, or Hessian is reproduced yet
  - no Git remote configured; remote runners disabled; CLOUD paused and budget zero
