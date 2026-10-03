# NEXT

Exactly one active action; generated from state/state.yaml.

task: G4A-T02
machine: MACM6
status: TODO

## Action
Classify absent allowed operators, IBP/EOM redundancies and symmetry-forbidden terms using the passed operator catalog; preserve the baseline action.

## Read

- AGENTS.md#g4a
- MACHINE_HANDOFF.md
- reports/G4/G4A-T01__G4A-T01__MACM6__20261001T193427Z__8e637b1__f5f125f4__REPORT.md
- docs/G4A_OPERATOR_BASIS.md
- config/benchmark/publication.source.yaml

## One command

```sh
.venv/bin/python scripts/ctl.py start G4A-T02 --machine MACM6
```
