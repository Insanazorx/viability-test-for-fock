import sys
from pathlib import Path
import unittest,json,tempfile,zipfile,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from transfer import verify_packet
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from analysis.validate_transfer import legacy_artifacts


class TransferTests(unittest.TestCase):
    def test_original_report_hashes_bind_pre_seal_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            run=Path(tmp)/'historical-run';run.mkdir();text=''
            for name in ('config.yaml','metadata.json','result.json','validation.log'):
                (run/name).write_bytes(b'original')
                text+=f'- `runs/{run.name}/{name}` — SHA256 `{hashlib.sha256(b"original").hexdigest()}`\n'
            self.assertEqual(len(legacy_artifacts(run,text)),4)
            (run/'result.json').write_bytes(b'changed')
            with self.assertRaises(ValueError):legacy_artifacts(run,text)

    def test_altered_payload_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'packet.zip'
            with zipfile.ZipFile(path,'w') as z:
                z.writestr('input.txt','changed')
                z.writestr('TRANSFER.json',json.dumps({'files':{'input.txt':hashlib.sha256(b'original').hexdigest()}}))
            with self.assertRaises(ValueError):verify_packet(path)

    def test_unmanifested_payload_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'packet.zip'
            with zipfile.ZipFile(path,'w') as z:
                z.writestr('extra.txt','unlisted');z.writestr('TRANSFER.json',json.dumps({'files':{}}))
            with self.assertRaises(ValueError):verify_packet(path)
