"""CPU preparation cannot falsely complete a deferred GPU prerequisite."""
import copy
import unittest
import tempfile
from pathlib import Path

from test_control import state, task
from ctl import ensure_machine_ready, next_task, validate,render
from common import ROOT


class MachineDependencyTests(unittest.TestCase):
    def fixture(self):
        value=state()
        first=value['tasks']['G0A-T01']
        first.update(status='PASS',machine_reports={'MACM6':'first.md'})
        first['machine_done']['MACM6']=True
        core=value['tasks']['G0A-T02']
        core.update(status='RUNNING',machine_reports={'MACM6':'core.md'})
        core['machine_done']['MACM6']=True
        spectral=task(('MACM6','RTX5070'),('G0A-T02',),'TODO')
        spectral['machine_prerequisites']={'MACM6':[{'task':'G0A-T02','machine':'MACM6'}]}
        spectral['machine_prerequisite_reason']='User requested CPU preparation while deferring CUDA.'
        value['tasks']['G0B-T01']=spectral
        return value

    def test_cpu_ready_with_its_completed_prerequisite_only(self):
        value=self.fixture()
        validate(value)
        before=copy.deepcopy(value['tasks']['G0A-T02'])
        ensure_machine_ready(value,'G0B-T01','MACM6')
        self.assertEqual(value['tasks']['G0A-T02'],before)

    def test_gpu_still_requires_full_prerequisite(self):
        value=self.fixture()
        value['tasks']['G0B-T01']['machine_done']['MACM6']=True
        value['tasks']['G0B-T01']['machine_reports']['MACM6']='spectral.md'
        with self.assertRaises(ValueError):
            ensure_machine_ready(value,'G0B-T01','RTX5070')

    def test_reason_and_all_dependencies_are_required(self):
        for change in ('reason','missing','wrong_machine'):
            value=self.fixture();t=value['tasks']['G0B-T01']
            if change=='reason':
                t.pop('machine_prerequisite_reason')
            elif change=='missing':
                t['machine_prerequisites']['MACM6']=[]
            else:
                t['machine_prerequisites']['MACM6'][0]['machine']='CLOUD'
            with self.subTest(change=change),self.assertRaises(ValueError):
                validate(value)

    def test_failed_parent_blocks_its_cpu_child(self):
        value=self.fixture();value['tasks']['G0A-T02']['status']='FAIL'
        with self.assertRaises(ValueError):
            ensure_machine_ready(value,'G0B-T01','MACM6')

    def test_deferred_gpu_selects_only_ready_cpu_work(self):
        value=self.fixture()
        value['machine_scheduling']={'RTX5070':{'deferred':True,'reason':'Explicit user request'}}
        validate(value)
        self.assertEqual(next_task(value)[0],'G0B-T01')
        with self.assertRaises(ValueError):
            ensure_machine_ready(value,'G0A-T02','RTX5070')
        value['machine_scheduling']['RTX5070']['deferred']=False
        self.assertEqual(next_task(value)[0],'G0A-T02')

    def test_deferred_only_registry_preserves_one_waiting_action(self):
        value=self.fixture();value['tasks']['G0B-T01']['enabled']=False
        value['machine_scheduling']={'RTX5070':{'deferred':True,'reason':'User requested later'}}
        self.assertIsNone(next_task(value))
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);render(value,root)
            text=(root/'NEXT.md').read_text()
            self.assertEqual(text.count('task: '),1)
            self.assertIn('scheduling: DEFERRED',text)
            self.assertIn('scripts/ctl.py status',text)

    def test_cli_sources_are_syntactically_valid(self):
        for path in (ROOT/'scripts').glob('*.py'):
            with self.subTest(path=path.name):
                compile(path.read_text(),str(path),'exec')

    def test_explicit_rtx_preference_never_completes_or_selects_cpu(self):
        value=self.fixture()
        value['execution_preference']={'machine':'RTX5070','reason':'User requested RTX until further notice'}
        before=copy.deepcopy(value['tasks'])
        self.assertEqual(next_task(value)[0],'G0A-T02')
        with self.assertRaisesRegex(ValueError,'device preference'):
            ensure_machine_ready(value,'G0B-T01','MACM6')
        self.assertEqual(value['tasks'],before)

    def test_rtx_preference_waits_when_independent_cpu_is_required(self):
        value=self.fixture()
        core=value['tasks']['G0A-T02']
        core['machine_done']['RTX5070']=True
        core['machine_reports']['RTX5070']='cuda.md'
        core['status']='PASS'
        value['execution_preference']={'machine':'RTX5070','reason':'Explicit user request'}
        self.assertIsNone(next_task(value))
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);render(value,root)
            text=(root/'NEXT.md').read_text()
            self.assertIn('machine: RTX5070',text)
            self.assertIn('required_machine: MACM6',text)
            self.assertIn('WAITING_INDEPENDENT_MACHINE',text)
            self.assertEqual(text.count('task: '),1)


if __name__=='__main__':
    unittest.main()
