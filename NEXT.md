# NEXT

Exactly one active action; generated from state/state.yaml.

task: G0B-T01
machine: RTX5070
status: RUNNING

## Action
After G0A-T02 CUDA passes and the user resumes this machine, validate spectral CUDA/autograd against the CPU reference.

## Read

- AGENTS.md#g0b
- MACHINE_HANDOFF.md
- docs/G0B_SPECTRAL.md
- config/benchmark/g0b_t01_macm6.json.yaml
- reports/G0/G0A-T02__G0A-T02__MACM6__20261001T060259Z__ec15d04__1f458c06__REPORT.md
- reports/G0/G0A-T03__G0A-T03__MACM6__20261001T174323Z__9336699__a64a600a__REPORT.md

## One command

```sh
.venv/Scripts/python.exe scripts/run.py --config config/benchmark/g0b_t01_rtx5070.json.yaml
```
