import sys
from pathlib import Path
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from cosmology.vacuum_decay import force,regular_origin,cdl_rhs,false_vacuum_action


class DecayTests(unittest.TestCase):
    def test_regular_origin_cancels_apparent_friction_singularity(self):
        x0=.01;rho=1e-5;state=regular_origin(x0,rho)
        self.assertAlmostEqual(force(state[0])-3*state[1]/rho,force(x0)/4,places=12)

    def test_zero_gravity_rhs_recovers_flat_space(self):
        x=.1;v=.02;r=2.
        rhs=cdl_rhs(r,[x,v,r,1.],0.)
        np.testing.assert_allclose(rhs,[v,force(x)-3*v/r,1.,0.],rtol=0,atol=0)

    def test_compact_false_vacuum_action_rejects_flat_limit(self):
        with self.assertRaises(ValueError):false_vacuum_action(0.,.0036)
        self.assertLess(false_vacuum_action(.1,.0036),0.)
