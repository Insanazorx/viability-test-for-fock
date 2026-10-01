"""Independent known geometries, invariance and domain checks for G0A-T02."""
import math
from pathlib import Path
import sys
import unittest
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from core.math_core import MathCore
from analysis.validate_core import evaluate_seed


class MathCoreTests(unittest.TestCase):
    def setUp(self):
        self.core = MathCore()

    def test_appendix_a_component_signs(self):
        l, a = np.array([2.,3.,5.]), np.array([7.,11.,13.])
        field = np.array([5.,-3.,7.,2.,11.,13.])
        expected = np.array([[0.,5.,-3.,7.],[-5.,0.,2.,11.],[3.,-2.,0.,13.],[-7.,-11.,-13.,0.]])
        np.testing.assert_array_equal(self.core.matrix(field), expected)
        self.assertEqual(self.core.c1(field), float(l@l+a@a))
        self.assertEqual(self.core.c2(field), float(l@a))

    def test_two_plane_exact_q_eigenvalues(self):
        field = np.array([2.,0.,0.,0.,0.,3.])
        self.assertEqual(self.core.c1(field),13.)
        self.assertEqual(self.core.c2(field),6.)
        np.testing.assert_array_equal(self.core.stf(field),np.diag([-2.5,-2.5,2.5,2.5]))
        np.testing.assert_array_equal(self.core.stf(field)@self.core.stf(field),6.25*np.eye(4))

    def test_hodge_basis_orientation_and_involution(self):
        field = np.array([1.,0.,0.,0.,0.,0.])
        np.testing.assert_array_equal(self.core.hodge(field),np.array([0.,0.,0.,0.,0.,1.]))
        np.testing.assert_array_equal(self.core.hodge(self.core.hodge(field)),field)

    def test_self_dual_has_zero_stf_and_undefined_other_direction(self):
        field = np.array([1.,0.,0.,0.,0.,1.])
        np.testing.assert_array_equal(self.core.stf(field),np.zeros((4,4)))
        _, minus = self.core.projections(field)
        np.testing.assert_array_equal(minus,np.zeros(6))
        with self.assertRaises(ValueError):
            self.core.reduced_fields(field)

    def test_decomposable_plane_saturates_norm_gap(self):
        u, v = np.array([1.,2.,3.,4.]), np.array([2.,-1.,5.,3.])
        matrix = np.outer(u,v)-np.outer(v,u)
        field = self.core.packed(matrix)
        self.assertAlmostEqual(float(self.core.c2(field)),0.)
        q = self.core.stf(field)
        self.assertAlmostEqual(float(np.trace(q@q)),float(self.core.c1(field)**2))

    def test_fixed_fock_lift_preserves_both_directions_and_radius(self):
        plus, minus = np.array([1.,0.,0.]), np.array([0.,0.,1.])
        field = self.core.lift_reduced(plus,minus,2.)
        self.assertAlmostEqual(float(self.core.c1(field)),4.)
        self.assertAlmostEqual(float(self.core.c2(field)),0.)
        np_out,nm_out,rp,rm = self.core.reduced_fields(field)
        np.testing.assert_allclose(np_out,plus,atol=1e-14)
        np.testing.assert_allclose(nm_out,minus,atol=1e-14)
        self.assertAlmostEqual(float(rp),math.sqrt(2))
        self.assertAlmostEqual(float(rm),math.sqrt(2))

    def test_two_derivative_double_counting(self):
        dm = np.zeros((3,6))
        dm[0,0] = 2.
        self.assertEqual(self.core.static_two_derivative(dm,3.),6.)

    def test_reduced_energy_half_factors(self):
        n = np.array([0.,0.,1.])
        dn = np.array([[2.,0.,0.],[0.,3.,0.],[0.,0.,0.]])
        self.assertEqual(self.core.reduced_energy(n,dn),(6.5,18.))

    def test_physical_quartic_reduction_coefficient(self):
        dn = np.array([[2.,0.,0.],[0.,3.,0.],[0.,0.,0.]])
        dm = self.core.from_dual_vectors(dn/math.sqrt(2),np.zeros((3,3)))
        self.assertAlmostEqual(float(self.core.static_quartic(dm)),36/32)

    def test_magnetic_field_orientation(self):
        n = np.array([0.,0.,1.])
        dn = np.array([[1.,0.,0.],[0.,0.,0.],[0.,1.,0.]])
        np.testing.assert_array_equal(self.core.magnetic_field(self.core.field_strength(n,dn)),np.array([0.,-1.,0.]))

    def test_hopf_prefactor_and_uniform_cell_volume(self):
        a = np.array([[1.,2.,3.],[4.,5.,6.]])
        b = np.ones((2,3))
        self.assertAlmostEqual(float(self.core.hopf_functional(a,b,2.)),42/(16*math.pi**2))

    def test_invalid_domains_rejected(self):
        for invalid in (np.zeros(5), np.zeros(6,dtype=np.int64), np.full(6,np.nan)):
            with self.assertRaises(ValueError):
                self.core.c1(invalid)
        with self.assertRaises(ValueError):
            self.core.packed(np.eye(4))
        with self.assertRaises(ValueError):
            self.core.lift_reduced(np.array([2.,0.,0.]),np.array([0.,1.,0.]))
        with self.assertRaises(ValueError):
            self.core.static_quartic(np.zeros((3,6)),sigma0=0)

    def test_independent_contractions_rotations_and_gradient_checks(self):
        config = {"parameters": {"samples_per_seed": 32,"rotations_per_seed": 8,
                  "gradient_step_sizes": [1e-3,1e-4,1e-5]}}
        metrics = evaluate_seed(self.core,config,23)
        for key in ("identity_normalized","rotation_normalized","reduction_normalized"):
            self.assertLess(metrics[key],5e-12)
        self.assertLess(metrics["gradient_normalized"],1e-8)


if __name__ == "__main__":
    unittest.main()
