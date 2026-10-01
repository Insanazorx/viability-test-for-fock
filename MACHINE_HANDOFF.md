# MACHINE HANDOFF

from: MACM6
to: MACM6
task: G0B-T01
status: RUNNING (CPU preparation); RTX5070 explicitly deferred
read:
  - AGENTS.md#g0b
  - reports/G0/G0A-T02__G0A-T02__MACM6__20261001T060259Z__ec15d04__1f458c06__REPORT.md
  - reports/G0/G0A-T03__G0A-T03__MACM6__20261001T174323Z__9336699__a64a600a__REPORT.md
  - docs/G0B_SPECTRAL.md
  - config/benchmark/g0b_t01_macm6.json.yaml
latest_checkpoint: N/A
checkpoint_sha256: N/A
do_next:
  - commit the spectral reference and execute the single acceptance command in NEXT.md
  - create G0B-T01 report and record MACM6 completion only
  - continue MACM6 Hopf-invariant preparation after CPU spectral acceptance passes
do_not_repeat:
  - G0A-T01 and G0A-T03 infrastructure passed on MACM6
  - G0A-T02 CPU invariant/reference responsibility passed
known_issue:
  - the user requested RTX5070 later; its completion flags remain false
  - whole G0A-T02 and whole G0B-T01 require actual CUDA reports
  - no Hopf charge, stationary solution or Hessian is reproduced yet
  - source PDF is ignored by Git and must retain the source-manifest SHA256
  - CLOUD paused; budget zero; remote runners disabled
