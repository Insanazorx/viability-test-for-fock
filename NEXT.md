# NEXT

Exactly one active action; generated from state/state.yaml.

task: G4B-T01
machine: MACM6
status: RUNNING

## Action
Compute and verify the available-input homogeneous dark-scalar one-loop potential, UV pole, scale response, mixing and lower switching counterterm.

## Read

- AGENTS.md#g4b
- MACHINE_HANDOFF.md
- docs/G4B_DARK_LOOP.md
- config/gate4/g4b_t01_macm6.json.yaml
- reports/G4/G4A-T03__G4A-T03__MACM6__20261003T102746Z__d2910a1__08b1fafb__REPORT.md

## One command

```sh
.venv/bin/python scripts/run.py --config config/gate4/g4b_t01_macm6.json.yaml
```
