"""Read-only MACM6 preflight for a reproducible deferred device handoff."""
import json
import re
from pathlib import Path
from common import ROOT,sha256,read_data
from provenance import verify_run


def legacy_artifacts(run,text):
    """Original pre-seal reports bind their artifacts individually; do not invent a seal."""
    hashes={}
    for name in ('config.yaml','metadata.json','result.json','validation.log'):
        path=run/name
        match=re.search(r'`[^`]*'+re.escape(run.name+'/'+name)+r'`[^\n]*SHA256 `([0-9a-f]{64})`',text)
        if not match or sha256(path)!=match[1]:raise ValueError('Legacy report-bound evidence differs: '+name)
        hashes[name]=match[1]
    return hashes


def validate_transfer(config):
    p=config['parameters'];s=read_data(ROOT/'state/state.yaml');rows=[];checks={}
    for key in p['required_macm6_tasks']:
        task=s['tasks'][key];report=task['machine_reports']['MACM6'];text=(ROOT/report).read_text()
        run_id=next(line.split(': ',1)[1] for line in text.splitlines() if line.startswith('run_ids: '))
        run=ROOT/'runs'/run_id;metadata=read_data(run/'metadata.json');legacy={}
        if metadata.get('integrity_schema_version') or (run/'integrity.json').exists():evidence=verify_run(run)
        else:evidence=None;legacy=legacy_artifacts(run,text)
        result=read_data(run/'result.json')
        checks[key]=task['machine_done']['MACM6'] and result['status']=='PASS'
        rows.append(dict(task=key,report=report,report_sha256=sha256(ROOT/report),run_id=run_id,evidence_sha256=evidence,legacy_report_bound_artifact_sha256=legacy))
    for path,expected in p['external_inputs'].items():checks[path]=sha256(ROOT/path)==expected
    pending=['G0A-T02','G0B-T01','G0B-T02','G0B-T03','G0B-T04','G0C-T01','G0C-T02']
    checks['gpu_flags_preserved']=all(not s['tasks'][key]['machine_done']['RTX5070'] for key in pending)
    checks['cloud_disabled']=s['cloud']['paused'] and s['cloud']['max_usd_per_run']==0
    checks['source_initializer_not_mislabeled']=not read_data(ROOT/'runs/G0B-T02__MACM6__20261001T190551Z__1d2b32d__73b620d2/result.json')['metrics']['hopf'].get('stationary',False)
    return dict(passed=all(checks.values()),checks=checks,completed_macm6_reports=rows,
                external_inputs=p['external_inputs'],first_rtx_task='G0A-T02',gpu_tasks_pending=pending,
                package_command='.venv/bin/python scripts/transfer.py create transfers/RTX5070__UTC__COMMIT.zip',
                source_checkpoint_stationary=False,remote_started=False,
                missing_physical_inputs=['concrete L_m','physical EFT scales/cutoff/matching','retained soliton/production region'],
                overall_scientific_label='PARTIAL / UNRESOLVED')
