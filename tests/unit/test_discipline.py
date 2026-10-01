"""Config/type/hash, run-evidence and scheduling regressions for G0A-T03."""
from __future__ import annotations

import copy
from datetime import datetime, timezone, timedelta
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"scripts"))
from common import ROOT, decode_data, read_data
from configuration import CONFIGS, REGISTRY, freeze_configs, load_config, validate_config
from provenance import RamMonitor, freeze, run_identity, seal_run, verify_run
from ctl import focus, next_task, render
from test_control import state, task


class DisciplineTests(unittest.TestCase):
    def config(self):
        return read_data(ROOT/"config/benchmark/g0a_t03_macm6.json.yaml")

    def test_plain_safe_yaml(self):
        self.assertEqual(decode_data("value: 3\nitems: [1, 2]\n"),{"value":3,"items":[1,2]})

    def test_duplicate_json_and_yaml_keys_rejected(self):
        for raw in ('{"value":1,"value":2}',"value: 1\nvalue: 2\n",
                    "nested:\n  value: 1\n  value: 2\n"):
            with self.subTest(raw=raw),self.assertRaises(ValueError):
                decode_data(raw)

    def test_nonfinite_config_values_rejected(self):
        for raw in ('{"value":NaN}','{"value":1e999}',"value: .nan\n","value: .inf\n"):
            with self.subTest(raw=raw),self.assertRaises(ValueError):
                decode_data(raw)

    def test_unsafe_yaml_constructor_rejected(self):
        with self.assertRaises(ValueError):
            decode_data("value: !!python/object/apply:os.system ['unreachable']\n")

    def test_cyclic_alias_rejected(self):
        with self.assertRaises(ValueError):
            decode_data("value: &cycle [*cycle]\n")

    def test_negative_boolean_and_duplicate_seeds_rejected(self):
        for seeds in ([-1],[True],[1,1],[4294967296]):
            value = dict(self.config(),seeds=seeds)
            with self.subTest(seeds=seeds),self.assertRaises(ValueError):
                validate_config(value)

    def test_unknown_fields_and_invalid_grid_rejected(self):
        for change in ({"unreviewed_command":"never-executed"},{"grid":[1,2,3]},{"grid":[3,3]},
                       {"time_step":-1},{"precision":"implicit"},{"tolerances":{"bad":0}}):
            value = dict(self.config(),**change)
            with self.subTest(change=change),self.assertRaises(ValueError):
                validate_config(value)

    def test_cloud_and_arbitrary_handlers_rejected(self):
        for machine,handler,allow_cloud in (("CLOUD","validate_run_discipline",False),
                                            ("MACM6","arbitrary_module",False),
                                            ("MACM6","validate_run_discipline",True)):
            value = self.config()
            value['machine']=machine
            value['parameters'].update(handler=handler,allow_cloud=allow_cloud)
            with self.assertRaises(ValueError):
                validate_config(value)

    def fixture_root(self, folder):
        root=Path(folder)
        (root/"config/benchmark").mkdir(parents=True)
        shutil.copyfile(ROOT/"config/schema.yaml",root/"config/schema.yaml")
        for relative,_ in CONFIGS.values():
            shutil.copyfile(ROOT/relative,root/relative)
        freeze_configs(root)
        return root

    def test_valid_config_load_and_byte_change_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root=self.fixture_root(folder)
            path=root/"config/benchmark/g0a_t03_macm6.json.yaml"
            self.assertEqual(load_config(path,root)[0]['task'],'G0A-T03')
            path.write_bytes(path.read_bytes()+b'\n')
            with self.assertRaises(ValueError):
                load_config(path,root)

    def test_noncanonical_alias_config_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root=self.fixture_root(folder)
            path=root/"config/benchmark/alias.yaml"
            shutil.copyfile(root/"config/benchmark/g0a_t03_macm6.json.yaml",path)
            with self.assertRaises(ValueError):
                load_config(path,root)

    def test_run_identity_is_utc_and_hashed(self):
        started=datetime(2026,10,1,10,0,tzinfo=timezone(timedelta(hours=3)))
        actual=run_identity('G0A-T03','MACM6',started,'a'*40,'b'*64)
        self.assertEqual(actual,'G0A-T03__MACM6__20261001T070000Z__aaaaaaa__bbbbbbbb')
        with self.assertRaises(ValueError):
            run_identity('G0A-T03','MACM6',started.replace(tzinfo=None),'a'*40,'b'*64)

    def test_invalid_identity_and_nonfinite_metadata_rejected(self):
        with self.assertRaises(ValueError):
            run_identity('anonymous','MACM6',datetime.now(timezone.utc),'a'*40,'b'*64)
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'metadata.json'
            with self.assertRaises(ValueError):
                freeze(path,{'bad':float('nan')})
            self.assertFalse(path.exists())

    def test_run_seal_rejects_changed_result(self):
        with tempfile.TemporaryDirectory() as folder:
            run=Path(folder)
            for name in ('config.yaml','metadata.json','environment.json','result.json'):
                freeze(run/name,{'fixture':name})
            (run/'validation.log').write_text('fixture\n')
            seal_run(run)
            self.assertEqual(len(verify_run(run)),64)
            (run/'result.json').chmod(0o644)
            (run/'result.json').write_text('{"status":"forged PASS"}')
            with self.assertRaises(ValueError):
                verify_run(run)

    def test_ram_monitor_reports_observed_samples(self):
        result=RamMonitor().start().finish()
        self.assertGreater(result['peak_ram_gb'],0)
        self.assertGreaterEqual(result['ram_samples'],2)

    def test_missing_integrity_fields_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            run=Path(folder)
            freeze(run/'integrity.json',{'schema_version':1,'artifact_sha256':{}})
            with self.assertRaises(ValueError):
                verify_run(run)

    def independent_state(self):
        value=state()
        first=value['tasks']['G0A-T01']
        first.update(status='PASS',machine_reports={'MACM6':'fixture.md'})
        first['machine_done']['MACM6']=True
        second=value['tasks']['G0A-T02']
        second['status']='RUNNING'
        second['machine_done']['MACM6']=True
        second['machine_reports']['MACM6']='fixture.md'
        value['tasks']['G0A-T03']=task(('MACM6',),('G0A-T01',),'TODO')
        return value

    def test_independent_focus_preserves_waiting_gpu_flags(self):
        value=self.independent_state()
        before=copy.deepcopy(value['tasks']['G0A-T02'])
        focus(value,'G0A-T03','MACM6','GPU unavailable; user requested independent MACM6 task')
        self.assertEqual(next_task(value)[0],'G0A-T03')
        self.assertEqual(value['tasks']['G0A-T02'],before)
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            render(value,root)
            self.assertEqual((root/'NEXT.md').read_text().count('task: '),1)

    def test_focus_cannot_bypass_prerequisites(self):
        value=state()
        with self.assertRaises(ValueError):
            focus(value,'G0A-T02','MACM6','test')

    def test_completed_focus_returns_to_waiting_gpu(self):
        value=self.independent_state()
        focus(value,'G0A-T03','MACM6','test')
        third=value['tasks']['G0A-T03']
        third.update(status='PASS',machine_reports={'MACM6':'fixture.md'})
        third['machine_done']['MACM6']=True
        self.assertEqual(next_task(value)[0],'G0A-T02')


if __name__=='__main__':
    unittest.main()
