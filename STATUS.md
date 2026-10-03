# STATUS

Generated from state/state.yaml; do not edit by hand.

Active action: none — RTX5070 deferred; next is G0A-T02
Cloud: PAUSED; budget USD 0 per run.

Only G0 tasks are registered initially. Later gates remain untested.

| Task | Status | MACM6 | RTX5070 | CLOUD |
|---|---|---|---|---|
| G0A-T01 | PASS | [X] | N/A | N/A |
| G0A-T02 | RUNNING | [X] | [ ] | N/A |
| G0A-T03 | PASS | [X] | N/A | N/A |
| G0B-T01 | RUNNING | [X] | [ ] | N/A |
| G0B-T02 | RUNNING | [X] | [ ] | N/A |
| G0B-T03 | TODO | [ ] | [ ] | N/A |
| G0B-T04 | TODO | [ ] | [ ] | N/A |
| G0C-T01 | TODO | [ ] | [ ] | N/A |
| G0C-T02 | TODO | [ ] | [ ] | N/A |
| G0D-T01 | TODO (disabled) | [ ] | N/A | N/A |
| G0D-T02 | TODO (disabled) | N/A | [ ] | N/A |
| G0D-T03 | TODO (disabled) | [ ] | [ ] | N/A |
| G4A-T01 | PASS | [X] | N/A | N/A |
| G4A-T02 | PASS | [X] | N/A | N/A |
| G4A-T03 | PASS | [X] | N/A | N/A |
| G0B-T05 | PASS | [X] | N/A | N/A |
| G1A-T04 | PASS | [X] | N/A | N/A |
| G4B-T01 | PASS | [X] | N/A | N/A |
| G4C-T02 | PASS | [X] | N/A | N/A |
| G4D-T04 | PASS | [X] | N/A | N/A |

## Input/environment readiness

- Required publication: yayınlanan.pdf; availability is checked before G0A-T02.
- Python target: 3.12. MACM6 dependency freeze: complete.
- Remote runner setup: disabled; no Git remote configured by bootstrap.

- RTX5070: DEFERRED — User explicitly requested all feasible MACM6 work first, then RTX5070 (2026-10-03).