# NEXT

Exactly one active action; generated from state/state.yaml.

task: G0B-T02
machine: MACM6
status: TODO

## Action
Implement the small-grid MACM6 Coulomb-gauge Hopf inversion and source initial-map/sign checks. Use the passed CPU spectral reference; do not start a stationary minimization.

## Read

- AGENTS.md#g0b
- MACHINE_HANDOFF.md
- reports/G0/G0B-T01__G0B-T01__MACM6__20261001T183741Z__5e9474e__8baddf31__REPORT.md
- docs/G0B_SPECTRAL.md
- config/benchmark/g0b_t01_macm6.json.yaml
- config/benchmark/publication.source.yaml

## One command

```sh
.venv/bin/python scripts/ctl.py start G0B-T02 --machine MACM6
```
