import sys
from pathlib import Path
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from static.spectral import PeriodicGrid
from static.full_field import SixComponentStatic


class FullStaticTests(unittest.TestCase):
    def setUp(self):
        self.theory=SixComponentStatic(PeriodicGrid.paper(5,4.))

    def test_uniform_fock_vacuum_has_zero_energy_and_gradient(self):
        field=np.zeros((5,5,5,6));field[...,0]=1
        self.assertLess(sum(self.theory.energy(field).values()),1e-25)
        self.assertLess(np.linalg.norm(self.theory.energy_gradient(field)),1e-12)

    def test_finite_pfaffian_excursion_is_not_projected_out(self):
        field=np.zeros((5,5,5,6));field[...,0]=field[...,5]=1/np.sqrt(2)
        self.assertGreater(float(np.sum(self.theory.potential(field))),1.)
        self.assertGreater(np.linalg.norm(self.theory.potential_gradient(field)),1.)

    def test_origin_radial_hessian_is_negative_as_expected(self):
        field=np.zeros(6);direction=np.ones(6)
        np.testing.assert_array_equal(self.theory.potential_hvp(field,direction),-direction)

    def test_six_component_representation_and_coefficients_required(self):
        with self.assertRaises(ValueError):
            self.theory.energy(np.zeros((5,5,5,3)))
        with self.assertRaises(ValueError):
            SixComponentStatic(self.theory.grid,mu=0.)
