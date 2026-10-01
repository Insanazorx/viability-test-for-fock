# MACHINE HANDOFF

from: MACM6
to: RTX5070
task: G0A-T02
status: DEFERRED (user scheduling); RUNNING (whole task)
read:
  - AGENTS.md#g0a
  - reports/G0/G0A-T02__G0A-T02__MACM6__20261001T060259Z__ec15d04__1f458c06__REPORT.md
  - reports/G0/G0B-T02__G0B-T02__MACM6__20261001T190551Z__1d2b32d__73b620d2__REPORT.md
  - docs/RTX5070_CORE_HANDOFF.md
  - docs/G0B_HOPF.md
  - config/benchmark/g0a_t02_rtx5070.json.yaml
latest_checkpoint: checkpoints/G0B-T02__MACM6__20261001T190551Z__1d2b32d__73b620d2__initial.h5
checkpoint_sha256: 462ee5c0e3015d9014b669eabfd78d47b1050e2301961f4a35cb3deb99e792eb
do_next:
  - preserve CPU references and review STATUS while RTX5070 remains deferred
  - only after an explicit user resume, continue first with the G0A-T02 CUDA core mirror
  - then perform G0B-T01 and G0B-T02 CUDA checks before G0B-T03 stationary minimization
do_not_repeat:
  - G0A-T01 and G0A-T03 MACM6 infrastructure passed
  - G0B-T01 MACM6 energy/derivative reference passed
  - G0B-T02 MACM6 passed; Q_H=-1.000000004972 at 49^3; smooth deformations preserve charge
  - 79 tests passed in the identified Hopf run; reporting/scheduling checks were separately verified
known_issue:
  - no CUDA completion flag changed; G0A-T02/G0B-T01/G0B-T02 whole tasks remain RUNNING
  - the initial HDF5 state is independently derived and stationary=false, not an archived paper soliton
  - source PDF and HDF5 checkpoint are ignored by Git; copy with hashes or regenerate the field
  - paper endpoint grid uses h=2L/(N-1), FFT period N h; no hidden charge normalization
  - remaining minimization/Hessian responsibilities require the pending RTX5070 precursor
  - CLOUD paused; budget zero; remote runners disabled
