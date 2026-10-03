# NEXT

Exactly one active action; generated from state/state.yaml.

task: G0B-T03
machine: RTX5070
status: TODO

## Action
Develop and validate the identified RTX5070 production driver for the matched 17^3,21^3,25^3,33^3 stationary sequence, including resumable optimizer/AL/RNG checkpoints and measured residual/energy/charge acceptance. The archived source initializer is absent; the available compact field is independent and nonstationary. Document initializer/solver equivalence separately; preserve all source settings and 5e-4 energy/charge tolerances. G0B-T04 production spectrum remains pending.

## Read

- AGENTS.md#g0b
- MACHINE_HANDOFF.md
- reports/G0/G0B-T02__G0B-T02__RTX5070__20261003T203645Z__1cb2c8a__23ad6ac8__REPORT.md
- reports/G0/G0B-T05__G0B-T05__MACM6__20261003T100609Z__d3106d3__f7f8faca__REPORT.md
- docs/G0B_SOLVER_PREPARATION.md
- docs/G0B_HOPF.md
- config/benchmark/publication.source.yaml

## One command

```sh
.venv/Scripts/python.exe scripts/ctl.py start G0B-T03 --machine RTX5070
```
