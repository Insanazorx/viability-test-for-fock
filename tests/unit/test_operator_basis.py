"""Tests target omissions and accidental symmetry assumptions in G4A."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from analysis.operator_basis import catalog, exact_rank, hilbert_coefficients, matter_interface, monomials, name


class OperatorBasisTests(unittest.TestCase):
    def test_hilbert_series_independent_counts(self):
        self.assertEqual(hilbert_coefficients(4),[1,1,4,4,10])
        self.assertEqual(len(monomials(4)),20)

    def test_pfaffian_odd_terms_are_allowed_by_so4(self):
        expressions={name(p) for p in monomials(4)}
        for expression in ('C2','lambda*C2','lambda^2*C2','C1*C2','chi^2*C2'):
            self.assertIn(expression,expressions)

    def test_lambda_tadpole_and_odd_lambda_mixed_terms_allowed(self):
        expressions={name(p) for p in monomials(4)}
        self.assertIn('lambda',expressions)
        self.assertIn('lambda*chi^2',expressions)

    def test_chi_odd_terms_absent_from_dark_basis(self):
        self.assertTrue(all(p[1]%2==0 for p in monomials(4)))
        self.assertIn((0,1,0,0),monomials(4,chi_parity=1))

    def test_curvature_and_dual_kinetic_channels_not_omitted(self):
        rows=catalog();expressions={r['expression'] for r in rows}
        self.assertEqual(len(rows),32)
        self.assertIn('R*C2',expressions)
        self.assertIn('1/2 nabla M_ab nabla (*M)_ab',expressions)
        self.assertTrue(all(r['dimension']+r['coefficient_dimension']==4 for r in rows))

    def test_lower_switching_terms_complete_to_n4(self):
        for n in range(5):
            self.assertIn((n,0,0,2),monomials(8))

    def test_scalar_matter_decorations_obey_stated_chi_parity(self):
        self.assertEqual(matter_interface(3),['1','lambda'])
        self.assertIn('chi^2',matter_interface(2))
        self.assertNotIn('chi',matter_interface(2))
        self.assertEqual(matter_interface(4),['1'])

    def test_exact_rank_resolves_polynomial_dependence(self):
        self.assertEqual(exact_rank([[1,2,4],[1,3,9],[1,4,16]]),3)
        self.assertEqual(exact_rank([[1,2,3],[2,4,6]]),1)

    def test_invalid_scope_rejected(self):
        for value in (True,-1,9,4.5):
            with self.assertRaises(ValueError):
                monomials(value)


if __name__=='__main__':
    unittest.main()
