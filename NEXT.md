# NEXT

Exactly one active action; generated from state/state.yaml.

task: G4A-T01
machine: MACM6
status: RUNNING

## Action
Enumerate and validate the d<=4 analytic dark/metric bulk basis and record higher-order source exceptions plus unspecified-matter interface.

## Read

- AGENTS.md#g4a
- MACHINE_HANDOFF.md
- docs/G4A_OPERATOR_BASIS.md
- config/benchmark/publication.source.yaml
- config/gate4/g4a_t01_macm6.json.yaml

## One command

```sh
.venv/bin/python scripts/run.py --config config/gate4/g4a_t01_macm6.json.yaml
```
