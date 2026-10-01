# NEXT

Exactly one active action; generated from state/state.yaml.

task: G0A-T02
machine: RTX5070
status: RUNNING

## Action
Follow docs/RTX5070_CORE_HANDOFF.md, prepare the real CUDA environment and run the frozen float64 mirror comparison. Record only RTX5070 completion; no cloud or lattice solve.

## Read

- AGENTS.md#g0a
- MACHINE_HANDOFF.md
- reports/G0/G0A-T02__G0A-T02__MACM6__20261001T060259Z__ec15d04__1f458c06__REPORT.md
- docs/MATH_CORE.md
- docs/RTX5070_CORE_HANDOFF.md
- config/benchmark/g0a_t02_rtx5070.json.yaml
- config/benchmark/publication.source.yaml

## One command

```sh
.venv/bin/python scripts/run.py --config config/benchmark/g0a_t02_rtx5070.json.yaml
```
