# MACHINE HANDOFF

from: MACM6
to: MACM6
task: G4A-T02
status: TODO; predecessor G4A-T01 PASS
read:
  - AGENTS.md#g4a
  - reports/G4/G4A-T01__G4A-T01__MACM6__20261001T193427Z__8e637b1__f5f125f4__REPORT.md
  - docs/G4A_OPERATOR_BASIS.md
  - config/gate4/g4a_t01_macm6.json.yaml
  - config/benchmark/publication.source.yaml
latest_checkpoint: checkpoints/G0B-T02__MACM6__20261001T190551Z__1d2b32d__73b620d2__initial.h5
checkpoint_sha256: 462ee5c0e3015d9014b669eabfd78d47b1050e2301961f4a35cb3deb99e792eb
do_next:
  - classify absent operators: symmetry-forbidden, IBP/EOM redundant, or allowed with a matching condition
  - distinguish field/frame choices from physical coefficient relations; preserve baseline action
  - after G4A-T02, audit lambda^n C2^2 and Xi in G4A-T03 before G4B loops/matching
do_not_repeat:
  - G4A-T01 passed: 32 bulk dark/metric operators at d<=4; exact potential rank 20
  - 90 tests passed; prior FAIL and the one-line temporary config-directory repair are preserved
  - MACM6 core, spectral and independent unit-Hopf references passed
known_issue:
  - this is an IBP basis, not yet an EOM quotient or a naturalness decision
  - higher-dimension source interactions are separate; no complete d=8/10 basis exists yet
  - L_m unspecified: concrete matter basis and portal matching remain input-dependent
  - topological/boundary densities are recorded separately; retain global effects for G4D
  - G0A-T02/G0B-T01/G0B-T02 CUDA remain unfinished; RTX5070 explicitly deferred
  - CLOUD paused, budget zero, remote runners disabled
