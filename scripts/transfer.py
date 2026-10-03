"""Offline RTX5070 transfer packaging and SHA256 verification, no remote action."""
from datetime import datetime,timezone
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import zipfile
from common import ROOT,sha256,read_data


def verify_packet(path):
    with zipfile.ZipFile(path) as archive:
        names=archive.namelist()
        if len(names)!=len(set(names)):raise ValueError('Duplicate transfer member')
        manifest=json.loads(archive.read('TRANSFER.json'))
        allowed={'TRANSFER.json',*manifest['files']}
        if set(names)!=allowed:raise ValueError('Unmanifested transfer member')
        for name,digest in manifest['files'].items():
            if name.startswith('/') or '..' in Path(name).parts:raise ValueError('Unsafe transfer path')
            actual=hashlib.sha256(archive.read(name)).hexdigest()
            if actual!=digest:raise ValueError('Transfer SHA256 mismatch: '+name)
    return manifest


def create_packet(output):
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip():
        raise ValueError('Commit code/state/reports before packaging')
    state=read_data(ROOT/'state/state.yaml')
    if state['tasks']['G0A-T04']['status']!='PASS':raise ValueError('MACM6 transfer preflight must pass first')
    data=read_data(ROOT/'runs/G0B-T02__MACM6__20261001T190551Z__1d2b32d__73b620d2/result.json')
    files={'yayınlanan.pdf':ROOT/'yayınlanan.pdf',data['checkpoint_path']:ROOT/data['checkpoint_path']}
    output=output.resolve()
    if not output.is_relative_to((ROOT/'transfers').resolve()):raise ValueError('Packet must stay under transfers/')
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='rtx-transfer-') as tmp:
        bundle=Path(tmp)/'REPOSITORY.bundle'
        branch=subprocess.check_output(['git','symbolic-ref','--short','HEAD'],cwd=ROOT,text=True).strip()
        subprocess.run(['git','bundle','create',str(bundle),branch,'HEAD'],cwd=ROOT,check=True,capture_output=True)
        subprocess.run(['git','bundle','verify',str(bundle)],cwd=ROOT,check=True,capture_output=True)
        heads=subprocess.check_output(['git','bundle','list-heads',str(bundle)],text=True)
        refs={ref:sha for sha,ref in (line.split() for line in heads.splitlines())}
        if refs!={'HEAD':commit,'refs/heads/'+branch:commit}:raise ValueError('Bundle commit/branch differs')
        files['REPOSITORY.bundle']=bundle
        manifest=dict(schema_version=1,created_utc=datetime.now(timezone.utc).isoformat(),git_commit=commit,branch=branch,
                      files={name:sha256(path) for name,path in files.items()},
                      first_task='G0A-T02',first_machine='RTX5070',
                      instructions='Clone REPOSITORY.bundle, copy external PDF/checkpoints into checkout, read docs/RTX5070_READY.md; environment is machine-specific.',
                      checkpoint_stationary=False,cloud_enabled=False)
        with zipfile.ZipFile(output,'x',compression=zipfile.ZIP_DEFLATED) as archive:
            for name,path in files.items():archive.write(path,name)
            archive.writestr('TRANSFER.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    verify_packet(output)
    return dict(path=output.relative_to(ROOT).as_posix(),sha256=sha256(output),bytes=output.stat().st_size,git_commit=commit)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=['create','verify']);parser.add_argument('path')
    args=parser.parse_args();path=Path(args.path)
    print(json.dumps(create_packet(path) if args.action=='create' else verify_packet(path),ensure_ascii=False,indent=2))


if __name__=='__main__':main()
