# MACHINE HANDOFF

from: MACM6
to: MACM6
task: G0A-T01
status: RUNNING
read:
  - AGENTS.md#g0a
  - NEXT.md
  - config/benchmark/g0a_t01.json.yaml
latest_checkpoint: N/A
checkpoint_sha256: N/A
do_next:
  - validate and commit the repository foundation
  - create one setup report and record MACM6 completion
do_not_repeat:
  - no numerical physics work has started
known_issue:
  - yayınlanan.pdf is absent; required before G0A-T02
  - numerical dependency freeze is pending G0A-T03
