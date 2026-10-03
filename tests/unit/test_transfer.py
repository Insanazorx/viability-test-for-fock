import sys
from pathlib import Path
import unittest,json,tempfile,zipfile,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from transfer import verify_packet


class TransferTests(unittest.TestCase):
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
