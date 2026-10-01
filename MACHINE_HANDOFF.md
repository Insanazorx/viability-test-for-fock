# MACHINE HANDOFF

from: MACM6
to: MACM6
task: G0B-T02
status: RUNNING (CPU Hopf reference); RTX5070 deferred
read:
  - AGENTS.md#g0b
  - reports/G0/G0B-T01__G0B-T01__MACM6__20261001T183741Z__5e9474e__8baddf31__REPORT.md
  - docs/G0B_HOPF.md
  - config/benchmark/g0b_t02_macm6.json.yaml
latest_checkpoint: N/A (acceptance will produce the initial field)
checkpoint_sha256: N/A
do_next:
  - execute the single frozen MACM6 acceptance command in NEXT.md
  - create the mandatory G0B-T02 report and verify initial HDF5 SHA256
  - record MACM6 completion only if all charge/closure/refinement checks pass
do_not_repeat:
  - G0B-T01 CPU spectral energy/derivatives passed
  - 79 unit/control tests pass; independent sign and Berry/winding identity checked
known_issue:
  - PDF omits the exact initial profile; this is an independently derived unit-map fixture
  - paper endpoint grid uses h=2L/(N-1) and FFT period N h, explicitly supported
  - no stationary solution or Hessian is yet reproduced
  - RTX5070 remains explicitly deferred; CLOUD paused and budget zero
  - source PDF and HDF5 states are ignored by Git and require recorded hashes
