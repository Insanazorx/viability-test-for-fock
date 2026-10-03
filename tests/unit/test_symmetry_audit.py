import sys
from pathlib import Path
import unittest
from fractions import Fraction
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
import json
from analysis.symmetry_audit import validate_classification,validate_switching, classified_catalog,mu_series,xi_series


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

    def test_actual_audit_results_can_be_sealed_as_json(self):
        for task,function in [('g4a_t02',validate_classification),('g4a_t03',validate_switching)]:
            config=json.loads(Path('config/gate4/'+task+'_macm6.json.yaml').read_text())
            json.dumps(function(config),allow_nan=False)
