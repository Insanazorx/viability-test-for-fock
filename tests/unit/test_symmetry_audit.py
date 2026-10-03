import sys
from pathlib import Path
import unittest
from fractions import Fraction
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from analysis.symmetry_audit import classified_catalog,mu_series,xi_series


class SymmetryAuditTests(unittest.TestCase):
    def test_pf_odd_baseline_absence_is_not_called_a_tuning(self):
        row=next(r for r in classified_catalog() if r['expression']=='C2')
        self.assertTrue(row['stated_symmetry_allowed'])
        self.assertIn('accidental internal reflection',row['absence_class'])

    def test_lower_pf_squared_is_even_and_unprotected(self):
        row=next(r for r in classified_catalog() if r['expression']=='C2^2')
        self.assertFalse(row['baseline_present'])
        self.assertFalse(row['accidental_reflection_odd'])
        self.assertIn('matching coefficient',row['absence_class'])

    def test_series_keep_missing_low_powers_exactly_zero(self):
        self.assertEqual(mu_series(8)[:4],[Fraction(0)]*4)
        self.assertEqual(mu_series(8)[8],Fraction(-1,2))
        self.assertEqual(xi_series(8)[8],Fraction(-1))
