"""Evidence-derived conditional assessment; never upgrades a partial loop gate."""
import hashlib
import json
from pathlib import Path


def validate_naturalness(config):
    from provenance import verify_run
    p=config['parameters'];run=Path(p['loop_run'])
    seal=verify_run(run)
    if seal!=p['loop_seal_sha256']:raise ValueError('One-loop evidence changed')
    result=json.loads((run/'result.json').read_text());loop=result['metrics']['preparation']
    checks=dict(loop_substep_passed=result['status']=='PASS',
                switching_correction_measured=loop['checks']['lower_switch_counterterm'],
                physical_inputs_not_invented=bool(loop['missing_inputs']),
                incomplete_matching_retained=not loop['matter_portal_matching_complete'] and not loop['curvature_derivative_matching_complete'])
    return dict(passed=all(checks.values()),checks=checks,
                assessment='RADIATIVELY_TUNED_EFT; VIABILITY_UNRESOLVED',
                technically_natural_in_stated_symmetries=False,
                conditional_branch='Option 2 tuning qualifier only; viable qualifier requires outstanding gates and full matching',
                full_G4C_decision_complete=False,overall_label='PARTIAL / UNRESOLVED',
                requires_user_selected_new_theory=False,baseline_changed=False,
                protected=['chi parity','SO4 invariant structure','accidental internal reflection if imposed in matching'],
                unprotected=['absolute vacuum energy','ultralight lambda curvature','quartic mu onset','Xi coefficient relations'],
                missing_inputs=loop['missing_inputs'],
                future_acceptance=['concrete matter/portal matching and derivative/curvature EFT-control audit','physical target density/mass and cutoff for tuning measures','retained parameter region after soliton and production gates'],
                loop_evidence_sha256=seal)
