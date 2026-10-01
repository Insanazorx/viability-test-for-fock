# NEXT

Exactly one active action; generated from state/state.yaml.

task: G0A-T02
machine: MACM6
status: RUNNING

## Action
Validate the source-derived math core in float64 with the frozen CPU config and create its substep report.

## Read

- AGENTS.md#g0a
- MACHINE_HANDOFF.md
- reports/G0/G0A-T01__G0A-T01__MACM6__20261001T042108Z__c131218__3e5f3754__REPORT.md
- config/benchmark/publication.source.yaml
- docs/MATH_CORE.md
- config/benchmark/g0a_t02_macm6.json.yaml

## One command

```sh
.venv/bin/python scripts/run.py --config config/benchmark/g0a_t02_macm6.json.yaml
```
