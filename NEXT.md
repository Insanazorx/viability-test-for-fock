# NEXT

Exactly one active action; generated from state/state.yaml.

task: G0A-T03
machine: MACM6
status: RUNNING

## Action
Validate the frozen MACM6 CPU environment and identified run/config/seed discipline. Preserve the unfinished RTX5070 responsibility.

## Read

- AGENTS.md#g0a
- MACHINE_HANDOFF.md
- docs/RUNBOOK.md
- config/benchmark/g0a_t03_macm6.json.yaml
- config/frozen_registry.yaml
- requirements/macm6.freeze.txt

## One command

```sh
.venv/bin/python scripts/run.py --config config/benchmark/g0a_t03_macm6.json.yaml
```
