# NEXT

Exactly one active action; generated from state/state.yaml.

task: G0B-T02
machine: RTX5070
status: RUNNING

## Action
After the user resumes RTX5070 and prior CUDA gates pass, compare Hopf FFT/gradient results with the CPU reference.

## Read

- AGENTS.md#g0b
- MACHINE_HANDOFF.md
- reports/G0/G0B-T01__G0B-T01__MACM6__20261001T183741Z__5e9474e__8baddf31__REPORT.md
- docs/G0B_HOPF.md
- docs/G0B_SPECTRAL.md
- config/benchmark/g0b_t02_macm6.json.yaml
- config/benchmark/publication.source.yaml

## One command

```sh
.venv/Scripts/python.exe scripts/run.py --config config/benchmark/g0b_t02_rtx5070.json.yaml
```
