# NEXT

Exactly one active action; generated from state/state.yaml.

task: G0B-T03
machine: RTX5070
status: FAIL

## Action
Diagnose the frozen 21^3 optimizer convergence failure before an explicit recovery. The 17^3 row passed; 21^3 energy/charge and final CPU/CUDA/autograd checks passed, but the final physical constrained RMS is 3.430415758e-5 > 1e-5 after the required fourth AL update. Do not cherry-pick the third update, loosen tolerances, add outer/inner iterations silently, run 25^3/33^3 or advance to G0B-T04. Next discriminating work is a separately identified 21^3 chart/initializer-equivalence diagnostic with the original source limits. Stay on RTX5070; no MACM6 flag changes.

## Read

- AGENTS.md#g0b
- MACHINE_HANDOFF.md
- reports/G0/G0B-T03__G0B-T03__RTX5070__20261003T220757Z__68eddf6__9df9405b__REPORT.md
- reports/G0/G0B-T03__G0B-T03__RTX5070__20261003T220757Z__68eddf6__9df9405b__EQUIVALENCE.md
- docs/G0B_CONVERGENCE_DIAGNOSIS.md
- docs/G0B_PRODUCTION_CONTRACT.md
- config/benchmark/g0b_t03_rtx5070.json.yaml

## One command

```sh
.venv/Scripts/python.exe scripts/ctl.py failures
```

Resolve the recorded outcome before launching any new run.
