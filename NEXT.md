# NEXT

Exactly one active action; generated from state/state.yaml.

task: G0A-T01
machine: MACM6
status: RUNNING

## Action
Validate and commit the repository/control-plane foundation; create its identified substep report.

## Read

- AGENTS.md#g0a
- MACHINE_HANDOFF.md
- config/benchmark/g0a_t01.json.yaml

## One command

```sh
.venv/bin/python scripts/run.py --config config/benchmark/g0a_t01.json.yaml
```
