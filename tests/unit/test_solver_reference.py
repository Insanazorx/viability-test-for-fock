import sys
from pathlib import Path
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from static.spectral import PeriodicGrid,SpectralEnergy
from static.minimizer import SphereChart,AugmentedHopfObjective
from hessian.reduced import energy_hvp,charge_hvp,tangent_frames,TangentChargeHessian
from analysis.direct_reference import direct_observables


class SolverReferenceTests(unittest.TestCase):
    def setUp(self):
        self.engine=SpectralEnergy(PeriodicGrid.paper(5,4.))
        self.chart=SphereChart(self.engine);self.field=self.chart.template.copy()

    def test_chart_fixes_boundary_and_normalizes_every_oracle_call(self):
        raw=self.chart.pack(self.field);raw[:,0]=.2
        field,_=self.chart.unpack(raw)
        np.testing.assert_allclose(np.sum(field*field,-1),1,atol=1e-15)
        np.testing.assert_array_equal(field[~self.chart.mask],self.field[~self.chart.mask])

    def test_chart_singularity_and_wrong_boundary_rejected(self):
        with self.assertRaises(ValueError):
            self.chart.unpack(self.chart.pack(self.field)*0)
        changed=self.field.copy();changed[0,0,0]=[0,0,1]
        with self.assertRaises(ValueError):
            self.chart.pack(changed)

    def test_vacuum_oracle_is_exact_zero(self):
        value,gradient=AugmentedHopfObjective(self.engine,0.).value_gradient(self.chart.pack(self.field),0.,2e4)
        self.assertLess(abs(value),1e-25)
        self.assertLess(np.linalg.norm(gradient),1e-13)

    def test_frames_are_orthonormal_even_at_coordinate_poles(self):
        frames=tangent_frames(self.engine,self.field)
        np.testing.assert_allclose(np.einsum('...ia,...ja->...ij',frames,frames),np.eye(2)+np.zeros((*self.engine.grid.shape,2,2)),atol=1e-15)
        np.testing.assert_array_equal(np.sum(frames*self.field[...,None,:],-1),0.)

    def test_vacuum_charge_hvp_zero_and_energy_hvp_nonzero(self):
        direction=np.random.default_rng(0).normal(size=self.field.shape)
        np.testing.assert_array_equal(charge_hvp(self.engine,self.field,direction),0.)
        self.assertGreater(np.linalg.norm(energy_hvp(self.engine,self.field,direction)),0.)

    def test_hessian_boundary_is_fixed_without_collective_deflation(self):
        hessian=TangentChargeHessian(self.engine,self.field)
        result=hessian.apply(np.ones((*self.engine.grid.shape,2)))
        np.testing.assert_array_equal(result[~self.chart.mask],0.)

    def test_direct_reference_constant_is_zero(self):
        with np.errstate(all='raise'):
            self.assertLess(direct_observables(self.field,self.engine.grid.spacing[0])['energy'],1e-25)

    def test_direct_reference_large_grid_rejected(self):
        with self.assertRaises(ValueError):
            direct_observables(np.zeros((11,11,11,3)),1.)
