# NEXT

Exactly one active action; generated from state/state.yaml.

task: G0B-T05
machine: MACM6
status: RUNNING

## Action
Validate minimizer/chart, physical residual, exact HVPs and independent direct-DFT reference on small CPU fixtures; leave G0B-T03/T04 science flags unfinished.

## Read

- AGENTS.md#g0b
- MACHINE_HANDOFF.md
- docs/MACM6_COMPLETION_PLAN.md
- docs/G0B_SOLVER_PREPARATION.md
- config/benchmark/g0b_t05_macm6.json.yaml
- reports/G0/G0B-T02__G0B-T02__MACM6__20261001T190551Z__1d2b32d__73b620d2__REPORT.md

## One command

```sh
.venv/bin/python scripts/run.py --config config/benchmark/g0b_t05_macm6.json.yaml
```
