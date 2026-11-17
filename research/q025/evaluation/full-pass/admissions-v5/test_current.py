import hashlib,json,unittest
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent
class CurrentAdmissionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.c=json.loads((B/'supported-scope-role-component-v5.json').read_text());cls.base=json.loads((F/'admissions-v4/supported-scope-role-component-v4.json').read_text());cls.r=json.loads((B/'scope-role-admission-v5.json').read_text());cls.by={x['id']:x for x in cls.c['destinations']};cls.dec={x['id']:x for x in cls.c['decisions']}
 def test_prior_admissions_are_exactly_preserved(self):
  self.assertEqual(self.c['destinations'][:len(self.base['destinations'])],self.base['destinations']);self.assertEqual(self.c['sourceContributions'][:len(self.base['sourceContributions'])],self.base['sourceContributions'])
 def test_complete_exclusions_preserve_changed_cases(self):
  reasons={x['reason']for x in self.c['exclusions']['roles']};self.assertEqual(reasons,{'no_exact_independent_role_agreement','explicit_changed_regime_or_scope_mismatch'});self.assertEqual(self.c['counts']['carried124RolesAdmitted'],0)
 def test_new_excerpts_require_both_readers(self):
  for row in self.c['sourceContributions'][len(self.base['sourceContributions']):]:
   d=self.dec[row['decisionId']];m=d['readingAgreement'];self.assertNotEqual(m['proposalReviewId'],m['challengeReviewId']);self.assertIn('Original proposal qualification:',row['qualification']);self.assertIn('Independent challenge qualification:',row['qualification'])
   if row['basis']=='source_excerpt_checked':self.assertEqual((m['proposalBasis'],m['challengeBasis']),('excerpt','excerpt'));self.assertTrue(any(e['kind']=='primary'for e in row['evidenceRefs']))
 def test_only_eligible_units_and_no_geometry_or_identity(self):
  inv=json.loads((F/'reconciliation-v1/eligible-preholdout-unit-ids-v1.json').read_text());ids=set(inv['unitIds']);self.assertTrue(all(r['unitId']in ids for r in self.c['sourceContributions']));self.assertEqual(self.c['placements'],[]);self.assertEqual(self.c['aliases'],[]);self.assertEqual(self.c['relations'],[])
 def test_broad_support_preserves_direct_vs_inherited_reading(self):
  for b in self.r['broadRepresentativeBindings']:
   self.assertTrue(b['representatives']);self.assertTrue(all(x['disposition']in ['member','overlap']and not x['sourceContributionOrHomeAdmission']for x in b['representatives']))
   if b['parentCoverage']is not None:self.assertFalse(self.by[b['destinationId']]['readingCoverage']['allDescendantsFreshlyRead'])
 def test_exact_continuation_receipt_and_amendments(self):
  p=self.c['currentPolicyContinuationReceipt'];self.assertEqual(p['sha256'],hashlib.sha256((B/'scope-role-admission-v5.json').read_bytes()).hexdigest());self.assertEqual(len(self.c['annotationAndPremiseOverlays']),2);self.assertEqual(len(self.c['separateExplicitComponents']),2)
if __name__=='__main__':unittest.main()
