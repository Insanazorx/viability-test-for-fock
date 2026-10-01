# NEXT

Exactly one active action; generated from state/state.yaml.

task: G0B-T01
machine: MACM6
status: RUNNING

## Action
Validate small-grid reduced spectral energy and derivatives; report MACM6 only. CUDA is explicitly deferred.

## Read

- AGENTS.md#g0b
- MACHINE_HANDOFF.md
- docs/G0B_SPECTRAL.md
- config/benchmark/g0b_t01_macm6.json.yaml
- reports/G0/G0A-T02__G0A-T02__MACM6__20261001T060259Z__ec15d04__1f458c06__REPORT.md
- reports/G0/G0A-T03__G0A-T03__MACM6__20261001T174323Z__9336699__a64a600a__REPORT.md

## One command

```sh
.venv/bin/python scripts/run.py --config config/benchmark/g0b_t01_macm6.json.yaml
```
