import sys
from pathlib import Path
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from core.scalar_potential import ScalarPotential
from analysis.radiative import scalar_loop


class RadiativeTests(unittest.TestCase):
    def test_massless_goldstones_are_finite_without_log_zero(self):
        with np.errstate(all='raise'):
            self.assertEqual(scalar_loop([0.,0.],1.)['value'],0.)

    def test_unstable_mass_cannot_be_hidden_by_absolute_value(self):
        with self.assertRaises(ValueError):scalar_loop([-1e-30],1.)

    def test_chi_parity_reverses_only_its_gradient_and_mixings(self):
        theory=ScalarPotential();a=np.array([1.,.1,.2,.3,.4,.5,.6,.2]);b=a.copy();b[-1]*=-1
        va,ga,ha,_=theory.evaluate(a);vb,gb,hb,_=theory.evaluate(b)
        sign=np.r_[np.ones(7),-1.]
        self.assertEqual(va,vb);np.testing.assert_array_equal(gb,ga*sign)
        np.testing.assert_array_equal(hb,ha*sign[:,None]*sign[None,:])

    def test_mu_onset_stable_at_tiny_lambda(self):
        theory=ScalarPotential();lam=1e-8
        self.assertGreater(theory.mu(lam)[0],0.)
        self.assertAlmostEqual(theory.mu(lam)[0]/(lam/(theory.f*theory.x_mu))**4,theory.mu_v)
