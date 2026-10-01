# STATUS

Generated from state/state.yaml; do not edit by hand.

Active action: G0A-T03
Cloud: PAUSED; budget USD 0 per run.

Only G0 tasks are registered initially. Later gates remain untested.

| Task | Status | MACM6 | RTX5070 | CLOUD |
|---|---|---|---|---|
| G0A-T01 | PASS | [X] | N/A | N/A |
| G0A-T02 | RUNNING | [X] | [ ] | N/A |
| G0A-T03 | RUNNING | [ ] | N/A | N/A |
| G0B-T01 | TODO | [ ] | [ ] | N/A |
| G0B-T02 | TODO | [ ] | [ ] | N/A |
| G0B-T03 | TODO | [ ] | [ ] | N/A |
| G0B-T04 | TODO | [ ] | [ ] | N/A |
| G0C-T01 | TODO | [ ] | [ ] | N/A |
| G0C-T02 | TODO | [ ] | [ ] | N/A |
| G0D-T01 | TODO (disabled) | [ ] | N/A | N/A |
| G0D-T02 | TODO (disabled) | N/A | [ ] | N/A |
| G0D-T03 | TODO (disabled) | [ ] | [ ] | N/A |

## Input/environment readiness

- Required publication: yayınlanan.pdf; availability is checked before G0A-T02.
- Python target: 3.12. MACM6 dependency freeze: pending G0A-T03.
- Remote runner setup: disabled; no Git remote configured by bootstrap.
