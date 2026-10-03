# NEXT

Exactly one active action; generated from state/state.yaml.

task: G1A-T04
machine: MACM6
status: RUNNING

## Action
Validate the unrestricted six-component static NumPy reference and exact matrix-free derivatives on MACM6 before GPU branch work.

## Read

- AGENTS.md#g1a
- MACHINE_HANDOFF.md
- docs/MACM6_COMPLETION_PLAN.md
- docs/G1A_FULL_STATIC_PREPARATION.md
- config/gate1/g1a_t04_macm6.json.yaml
- reports/G0/G0B-T05__G0B-T05__MACM6__20261003T100609Z__d3106d3__f7f8faca__REPORT.md

## One command

```sh
.venv/bin/python scripts/run.py --config config/gate1/g1a_t04_macm6.json.yaml
```
