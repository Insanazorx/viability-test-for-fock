"""CPU preparation cannot falsely complete a deferred GPU prerequisite."""
import copy
import unittest

from test_control import state, task
from ctl import ensure_machine_ready, next_task, validate


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


if __name__=='__main__':
    unittest.main()
