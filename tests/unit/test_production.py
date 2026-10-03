"""Production acceptance and safe AL-boundary checkpoint regressions."""
import importlib.util
from pathlib import Path
import random
import sys
import tempfile
import unittest

import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from analysis.validate_stationary import row_checks
from static.solver_checkpoint import save_checkpoint,load_checkpoint,rng_state,restore_rng

HAS_TORCH=importlib.util.find_spec('torch') is not None


class AcceptanceTests(unittest.TestCase):
    def fixture(self):
        m={'energy':281.3653,'charge':-1.,'constrained_rms':1e-7,'virial':-.082}
        ref={'energy':281.3653}
        tol={'energy_relative':5e-4,'unit_charge':5e-4,'constrained_rms':1e-5,
             'unit_error':2e-15,'boundary_error':1e-14}
        history=[{'iterations':120,'evaluations':180} for _ in range(4)]
        return m,ref,tol,history

    def test_matched_row_meets_exact_predeclared_thresholds(self):
        self.assertTrue(all(row_checks(*self.fixture(),0.,0.).values()))

    def test_energy_mismatch_and_stationarity_cannot_be_hidden_by_charge(self):
        args=list(self.fixture());args[0]['energy']*=1.001;args[0]['constrained_rms']=1.1e-5
        checks=row_checks(*args,0.,0.)
        self.assertTrue(checks['unit_charge'])
        self.assertFalse(checks['energy_relative'])
        self.assertFalse(checks['constrained_rms'])

    def test_wrong_sign_exhausted_budget_and_missing_outer_are_not_pass(self):
        args=list(self.fixture());args[0]['charge']=1.;args[3][0]['evaluations']=181;args[3].pop()
        checks=row_checks(*args,0.,0.)
        for key in ('charge_sign','evaluation_budget','outer_updates'):
            self.assertFalse(checks[key])


@unittest.skipUnless(HAS_TORCH,'Torch is not installed on this reference environment')
class CheckpointTests(unittest.TestCase):
    def test_nested_optimizer_tensor_numpy_and_integer_keys_roundtrip(self):
        import torch
        value={'raw':torch.ones((5,3),dtype=torch.float64), 'history':[{'energy':2.}],
               'optimizer':{'state':{0:{'d':torch.arange(5,dtype=torch.float64),'n_iter':3}},
                            'param_groups':[{'params':[0]}]},
               'numpy':np.arange(4,dtype=np.uint32),'none':None,'tuple':(1,True,'x')}
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'state.h5';save_checkpoint(path,value,{'config':'fixed'})
            loaded=load_checkpoint(path,{'config':'fixed'})['state']
            self.assertTrue(torch.equal(value['raw'],loaded['raw']))
            self.assertTrue(torch.equal(value['optimizer']['state'][0]['d'],loaded['optimizer']['state'][0]['d']))
            np.testing.assert_array_equal(value['numpy'],loaded['numpy'])
            self.assertEqual(value['tuple'],loaded['tuple'])
            self.assertIsNone(loaded['none'])

    def test_checkpoint_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'state.h5';save_checkpoint(path,{}, {'config':'fixed'})
            before=path.read_bytes()
            with self.assertRaises(FileExistsError):
                save_checkpoint(path,{}, {'config':'changed'})
            self.assertEqual(before,path.read_bytes())

    def test_wrong_config_code_or_grid_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'state.h5'
            identity={'config':'a','code':'b','grid':17};save_checkpoint(path,{},identity)
            for key in identity:
                changed=dict(identity);changed[key]='wrong'
                with self.subTest(key=key),self.assertRaisesRegex(ValueError,'identity mismatch'):
                    load_checkpoint(path,changed)

    def test_rng_roundtrip_reproduces_python_numpy_and_torch(self):
        import torch
        saved=rng_state()
        expected=(random.random(),np.random.random(),torch.rand(2))
        restore_rng(saved)
        actual=(random.random(),np.random.random(),torch.rand(2))
        self.assertEqual(expected[:2],actual[:2])
        self.assertTrue(torch.equal(expected[2],actual[2]))

    def test_optimizer_state_is_library_loadable_without_pickle(self):
        import torch
        x=torch.nn.Parameter(torch.tensor([2.,-1.],dtype=torch.float64))
        optimizer=torch.optim.LBFGS([x],max_iter=2,line_search_fn='strong_wolfe')
        def closure():
            optimizer.zero_grad();value=(x*x).sum();value.backward();return value
        optimizer.step(closure)
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'state.h5';save_checkpoint(path,optimizer.state_dict(),{})
            other=torch.optim.LBFGS([torch.nn.Parameter(x.detach().clone())],max_iter=2,line_search_fn='strong_wolfe')
            other.load_state_dict(load_checkpoint(path,{})['state'])
            self.assertEqual(next(iter(optimizer.state.values()))['n_iter'],next(iter(other.state.values()))['n_iter'])


class CudaProductionTests(unittest.TestCase):
    def setUp(self):
        if not HAS_TORCH:
            self.skipTest('Torch unavailable')
        import torch
        if not torch.cuda.is_available():
            self.skipTest('Actual CUDA unavailable')

    def test_engineering_restart_and_backend_checks_on_actual_cuda(self):
        from analysis.validate_stationary import engineering_checks
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'checkpoints').mkdir()
            result=engineering_checks(root,'test',{'config_sha256':'a'},
                                      {'backend':5e-11,'autograd':5e-10,'resume':5e-12})
            self.assertTrue(result['passed'],result)
            self.assertLess(result['vacuum_final']['energy'],result['vacuum_initial_energy'])

    def test_cuda_production_rejects_host_fields(self):
        import torch
        from core.backends import TorchBackend
        from static.spectral import PeriodicGrid,SpectralEnergy
        from static.minimizer import AugmentedHopfObjective
        from static.production import solve_cuda
        engine=SpectralEnergy(PeriodicGrid.paper(5,4.),TorchBackend('cpu'))
        objective=AugmentedHopfObjective(engine,0.)
        field=torch.tensor(objective.chart.template,dtype=torch.float64)
        with self.assertRaisesRegex(ValueError,'actual float64 CUDA'):
            solve_cuda(objective,field,{})

    def test_final_field_oracle_matches_host_and_autograd(self):
        import torch
        from core.backends import TorchBackend
        from static.spectral import PeriodicGrid,SpectralEnergy
        from static.hopf_initial import compact_hopf
        from static.minimizer import AugmentedHopfObjective
        from analysis.validate_stationary import oracle_comparison
        grid=PeriodicGrid.paper(5,4.)
        objective=AugmentedHopfObjective(SpectralEnergy(grid,TorchBackend()))
        field=torch.tensor(compact_hopf(grid)['field'],device='cuda',dtype=torch.float64)
        result=oracle_comparison(objective,field,.7,200.)
        self.assertLess(result['backend'],5e-11)
        self.assertLess(result['autograd'],5e-10)
        self.assertAlmostEqual(result['cpu_metrics']['constrained_rms'],objective.metrics(field)['constrained_rms'],places=10)

    def test_actual_evaluation_budget_is_strict_and_not_convergence(self):
        import torch
        from core.backends import TorchBackend
        from static.spectral import PeriodicGrid,SpectralEnergy
        from static.hopf_initial import compact_hopf
        from static.minimizer import AugmentedHopfObjective
        from static.production import solve_cuda
        grid=PeriodicGrid.paper(5,4.)
        objective=AugmentedHopfObjective(SpectralEnergy(grid,TorchBackend()))
        field=torch.tensor(compact_hopf(grid)['field'],device='cuda',dtype=torch.float64)
        result=solve_cuda(objective,field,{'penalty':20000.,'outer_updates':1,'maxiter':3,'maxfun':1,
                                         'gtol':1e-30,'ftol':1e-30,'history_size':2})
        row=result['history'][0]
        self.assertEqual(row['evaluations'],1)
        self.assertTrue(row['evaluation_budget_exceeded'])
        self.assertFalse(row['inner_converged_by_gradient'])


if __name__=='__main__':
    unittest.main()
