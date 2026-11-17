import json,unittest
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent
class BroadSupport(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.old=json.loads((F/'admissions-v1/supported-scope-role-component-v1.json').read_text());cls.new=json.loads((B/'supported-scope-role-component-v2.json').read_text());cls.receipt=json.loads((B/'broad-scope-support-admission.json').read_text())
 def test_prior_scopes_and_roles_unchanged(self):
  self.assertEqual(self.old['destinations'],self.new['destinations'][:904]);self.assertEqual(self.old['sourceContributions'],self.new['sourceContributions'])
 def test_representatives_have_actual_common_basis(self):
  self.assertEqual(len(self.receipt['representativeBindings']),118)
  for b in self.receipt['representativeBindings']:
   self.assertTrue(b['representatives'])
   for r in b['representatives']:
    self.assertIn(r['disposition'],['member','overlap']);self.assertFalse(r['sourceContributionOrHomeAdmission'])
    if r['basis']=='source_excerpt_checked':self.assertEqual(r['proposalBasis'],'excerpt');self.assertEqual(r['challengeBasis'],'excerpt');self.assertGreater(r['commonPrimaryWindowCount'],0)
 def test_parent_inheritance_is_not_fresh_descendant_reading(self):
  parents=[d for d in self.new['destinations'][904:] if d['readingCoverage']['inheritedParentCoverage']]
  self.assertEqual(len(parents),12)
  for d in parents:self.assertFalse(d['readingCoverage']['allDescendantsFreshlyRead']);self.assertEqual(d['readingCoverage']['descriptionCheckedCount'],d['readingCoverage']['directContrastDescriptions'])
 def test_no_home_or_identity_promotion(self):
  self.assertFalse(self.new['placements']);self.assertFalse(self.new['relations']);self.assertFalse(self.new['aliases'])
  self.assertTrue(all(x['type']=='scope_acceptance' for x in self.new['decisions'][len(self.old['decisions']):]))
if __name__=='__main__':unittest.main()
