"""Regression checks on actual independent review evidence, not acceptance."""
import json
import unittest
from pathlib import Path

from reconcile_fine_home_audit import reconcile

B = Path(__file__).resolve().parent


class ExistingEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        payload = json.loads((B / 'explicit-fine-home-candidates.local.json').read_text())
        cls.rows = sum((payload[k] for k in ('cleanCandidateRows', 'coverageReviewRows', 'excludedRows')), [])
        cls.result = {r['unitId']: r for r in reconcile(cls.rows)}

    def by_paper(self, paper):
        return next(r for r in self.result.values() if r['paperId'] == paper)

    def test_second_context_does_not_erase_compound_no_scale_targets(self):
        r = self.by_paper('2006.06694')
        self.assertIn('compound_target_coverage_in_a_recorded_context', r['reviewReasons'])
        self.assertIn('multiple_explicit_paired_home_destinations_across_contexts', r['reviewReasons'])

    def test_inflation_tuning_and_initial_condition_targets_remain_visible(self):
        r = self.by_paper('2504.12283')
        self.assertEqual(r['status'], 'requires_targeted_coverage_or_canonical_decision')
        self.assertTrue(r['compoundContextReviewIds'])

    def test_extra_comparison_does_not_erase_explicit_brane_home(self):
        r = self.by_paper('hep-th/9601108')
        self.assertEqual(r['reviewReasons'], [])
        self.assertEqual(len(r['explicitPairedDestinationIds']), 1)

    def test_explicit_specialization_and_instantiation_are_candidate_evidence(self):
        for paper, role in [('2409.02156', 'specializes'), ('2206.12889', 'instantiates')]:
            r = self.by_paper(paper)
            self.assertEqual(r['reviewReasons'], [])
            self.assertIn(role, r['chosenHomeRoles'])

    def test_original_region_overlap_does_not_override_named_fine_home(self):
        r = self.by_paper('1306.1237')
        self.assertEqual(r['reviewReasons'], [])

    def test_missing_home_and_severed_note_are_not_promoted(self):
        uid = 'unit:0034b70ea953b9879b3d6034ad618cbfcb1be80a68ce1e19fa6ffa94793dec60'
        self.assertNotIn(uid, self.result)


if __name__ == '__main__':
    unittest.main()
