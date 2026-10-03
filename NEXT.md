# NEXT

Exactly one active action; generated from state/state.yaml.

task: G0B-T03
machine: RTX5070
status: RUNNING

## Action
Run the frozen float64 CUDA production sequence using docs/G0B_PRODUCTION_CONTRACT.md. Preserve 17^3/21^3/25^3 at L=4 and 33^3 at L=8; stop on a failed source row, report exact residual/energy/charge diagnostics and separate initializer/solver equivalence. Resume only from a verified AL-boundary checkpoint with explicit SHA256. No MACM6 completion or G0B-T04 spectrum is implied.

## Read

- AGENTS.md#g0b
- MACHINE_HANDOFF.md
- reports/G0/G0B-T02__G0B-T02__RTX5070__20261003T203645Z__1cb2c8a__23ad6ac8__REPORT.md
- reports/G0/G0B-T05__G0B-T05__MACM6__20261003T100609Z__d3106d3__f7f8faca__REPORT.md
- docs/G0B_SOLVER_PREPARATION.md
- docs/G0B_HOPF.md
- config/benchmark/publication.source.yaml
- docs/G0B_PRODUCTION_CONTRACT.md
- config/benchmark/g0b_t03_rtx5070.json.yaml

## One command

```sh
.venv/Scripts/python.exe scripts/run.py --config config/benchmark/g0b_t03_rtx5070.json.yaml
```
