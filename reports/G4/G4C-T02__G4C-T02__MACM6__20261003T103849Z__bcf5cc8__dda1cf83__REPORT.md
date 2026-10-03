# SUBSTEP REPORT — G4C-T02

status: PASS
machine: MACM6
git_commit: bcf5cc8b19fef829ee10ab9e530b35fb3ae181ba
config_sha256: dda1cf83fa69f9ab2799b75161dce9c741b1b0dcaefec01e837b95b1dce2003c
run_ids: G4C-T02__MACM6__20261003T103849Z__bcf5cc8__dda1cf83
started_utc: 2026-10-03T10:38:49.238302+00:00
finished_utc: 2026-10-03T10:38:49.854320+00:00
wall_time: 0.615956 seconds
peak_ram_gb: 0.146522 (sampled parent+registered-child RSS sum at 0.01 s; observed peak)
peak_vram_gb: N/A — no GPU execution
precision: float64
evidence_sha256: c656dc88cb6dfbd75574a0bc3695d9e4bd65d260bd75d17986dd24b04bcaaf5f

report_generator_sha256: 8a6f63d3b2e2beb6078e23fa9079b69831748d82529a120a65df56da89d7b83e

## Objective
Record evidence-derived conditional radiative status without claiming full matching or viability.
## Inputs
Source PDF p.7 Eqs.50-51; source Radiative status p.13, plus the mathematical/engineering contract docs/G4C_CONDITIONAL_STATUS.md and the passed CPU references. Exact inputs:
- `config/frozen_registry.yaml` — SHA256 `8f6988755c7476af1e2a46d79a421aa1f5bae016a2ed9b677cd539f340f0afa2`
- `config/schema.yaml` — SHA256 `727763ae5bf8c510f2b8a933d1ce6b605e4d15d6547b2890d57b4b3c0b5b2acb`
- `yayınlanan.pdf` — SHA256 `09111940dc2575283d8db69ee65785d2b85beb3864e416e63c7538e91c70c312`
- `config/benchmark/publication.source.yaml` — SHA256 `143da835837a98f64ba0246e983e02205e63b56bb2cfc6b092bf5c80db2194aa`
- `docs/MATH_CORE.md` — SHA256 `b6953b026f2a14be2376f4ed7b2143108fcdfcdbf11d24fa8b2e3e24c20c459e`
- `docs/G4C_CONDITIONAL_STATUS.md` — SHA256 `348a2b4cc4a656c9ab246aa35239e1d22ac512baca8ebe120d0733957345f7bd`
- `requirements/macm6.freeze.txt` — SHA256 `f1dfb6de3a4a043bf4dd83598264cbf7e77844a89e342c049c435b291d0ca323`
- `reports/G4/G4B-T01__G4B-T01__MACM6__20261003T103247Z__d64b18b__39461767__REPORT.md` — SHA256 `6f34be2e76d1fa7308b98da8d5afea058d97691da98d0dbebf6875be09756a37`
- `environment.json` — SHA256 `e4b271229fa5b07cf392ea84ee98f3bfc1b6f612fae9ec9961dcde19a5df3fad`
## Numerical method
Verify sealed one-loop evidence and report protected/unprotected conditions and missing inputs.
## Tolerances
Frozen before acceptance:
```json
{
  "integrity": 1e-15
}
```
Every frozen exact/numeric check and all unit tests pass.
## Primary metrics
```json
{
  "layout_complete": true,
  "missing_paths": [],
  "tests_exit_code": 0,
  "tests_run": 113,
  "minimum_tests": 113,
  "state_valid": true,
  "cloud_paused": true,
  "cloud_budget_usd": 0,
  "publication_present": true,
  "preparation": {
    "passed": true,
    "checks": {
      "loop_substep_passed": true,
      "switching_correction_measured": true,
      "physical_inputs_not_invented": true,
      "incomplete_matching_retained": true
    },
    "assessment": "RADIATIVELY_TUNED_EFT; VIABILITY_UNRESOLVED",
    "technically_natural_in_stated_symmetries": false,
    "conditional_branch": "Option 2 tuning qualifier only; viable qualifier requires outstanding gates and full matching",
    "full_G4C_decision_complete": false,
    "overall_label": "PARTIAL / UNRESOLVED",
    "requires_user_selected_new_theory": false,
    "baseline_changed": false,
    "protected": [
      "chi parity",
      "SO4 invariant structure",
      "accidental internal reflection if imposed in matching"
    ],
    "unprotected": [
      "absolute vacuum energy",
      "ultralight lambda curvature",
      "quartic mu onset",
      "Xi coefficient relations"
    ],
    "missing_inputs": [
      "concrete L_m",
      "physical f,Lambda_U,sigma0,m_chi,portal Lambda",
      "UV cutoff/matching coefficients",
      "retained soliton/production parameter region"
    ],
    "future_acceptance": [
      "concrete matter/portal matching and derivative/curvature EFT-control audit",
      "physical target density/mass and cutoff for tuning measures",
      "retained parameter region after soliton and production gates"
    ],
    "loop_evidence_sha256": "e78d3606825d7bc1b6aae04c9563468183a59bcadaec03379edc9776d3227a49"
  }
}
```
## Convergence checks
Exact evidence integrity and recorded one-loop acceptance; no new physical scan.
## Pass/fail evaluation
PASS for the declared MACM6 substep only. Every frozen exact/numeric check and all unit tests pass. Conditional engineering packet only; full Gate4C and model viability remain unresolved.
## Anomalies
- Dirty Git tree: False.
- No CUDA execution; CLOUD paused; remote runner disabled.
- Physical scales/cutoff and concrete matter action absent.
- No new protection mechanism or baseline modification.

## Artifacts/checkpoints
- `runs/G4C-T02__MACM6__20261003T103849Z__bcf5cc8__dda1cf83/config.yaml` — SHA256 `dda1cf83fa69f9ab2799b75161dce9c741b1b0dcaefec01e837b95b1dce2003c`
- `runs/G4C-T02__MACM6__20261003T103849Z__bcf5cc8__dda1cf83/metadata.json` — SHA256 `08efe225cd6f313b44cefe1464daf37aafe59821ea1aa0d5b271577ab17322e8`
- `runs/G4C-T02__MACM6__20261003T103849Z__bcf5cc8__dda1cf83/result.json` — SHA256 `207b8e835edd3a96f3d1b9b8f26fa371e712f7f5f2ffbef71e169123bda75ba9`
- `runs/G4C-T02__MACM6__20261003T103849Z__bcf5cc8__dda1cf83/validation.log` — SHA256 `3b453f562a87f07423e79ad7aedbb658b1f69ccfe86b018470962ebb3bcde9f1`
- `runs/G4C-T02__MACM6__20261003T103849Z__bcf5cc8__dda1cf83/environment.json` — SHA256 `e4b271229fa5b07cf392ea84ee98f3bfc1b6f612fae9ec9961dcde19a5df3fad`
- `runs/G4C-T02__MACM6__20261003T103849Z__bcf5cc8__dda1cf83/integrity.json` — SHA256 `c656dc88cb6dfbd75574a0bc3695d9e4bd65d260bd75d17986dd24b04bcaaf5f`
Small verification metrics/catalogs are sealed in result.json; no stationary checkpoint or dense lattice Hessian is produced.
## Reproduction command
```sh
.venv/bin/python scripts/run.py --config config/gate4/g4c_t02_macm6.json.yaml
.venv/bin/python scripts/report.py --run-id EXACT_NEW_RUN_ID
```
Use isolated checkout `bcf5cc8b19fef829ee10ab9e530b35fb3ae181ba` with the exact source PDF and requirements/macm6.freeze.txt; task must be RUNNING/unfinished.
## What changed from previous report
First explicit conditional radiative status from computed evidence.
## Next action
Finish available-input MACM6 validation and prepare the deferred RTX5070 handoff.
## Handoff references
NEXT.md, MACHINE_HANDOFF.md, docs/MACM6_COMPLETION_PLAN.md and docs/G4C_CONDITIONAL_STATUS.md
