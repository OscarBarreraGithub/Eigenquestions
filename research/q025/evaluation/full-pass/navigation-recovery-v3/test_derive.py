import copy,json,unittest
from derive import derive,F,vh
class Recovery(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.a=F/'native-local/navigation-recovery-v2/jobs/amplitude-explicit-equivalence-challenge';cls.k=F/'native-local/navigation-kk-v1/jobs/kk-cross-field-routes-challenge'
 def load(self,d):return json.loads((d/'packet.actual.json').read_text()),json.loads((d/'reply.raw.txt').read_text())
 def test_actual_amplitude_exact_retention(self):
  p,r=self.load(self.a);x=derive(p,r,allow_one_destination_compound=True,require_equivalence_issue=True);self.assertEqual(x['normalizedReview'],r);self.assertEqual(len(x['compoundAnnotationsChecked']),1);self.assertFalse(x['compoundAnnotationsChecked'][0]['atomicIdentitiesEstablished'])
 def test_actual_kk_prior_references(self):
  p,r=self.load(self.k);x=derive(p,r);self.assertEqual(x['normalizedReview'],r);self.assertEqual(len(x['resolvedPriorDecisionReferences']),22);self.assertEqual(r['decisions'],[])
 def test_unsupported_prior_fails(self):
  p,r=self.load(self.k);r['priorReviews'][0]['verdict']='revise'
  with self.assertRaises(AssertionError):derive(p,r)
 def test_unknown_reference_fails(self):
  p,r=self.load(self.k);r['scopeDispositions'][0]['decisionIds'].append('invented')
  with self.assertRaises(AssertionError):derive(p,r)
 def test_missing_review_fails(self):
  p,r=self.load(self.k);r['navigationReviews'].pop()
  with self.assertRaises(AssertionError):derive(p,r)
 def test_compound_requires_exact_authority(self):
  p,r=self.load(self.a)
  with self.assertRaises(AssertionError):derive(p,r,require_equivalence_issue=True)
  r['compoundSources'][0]['questionRefs']=['c0']
  with self.assertRaises(AssertionError):derive(p,r,allow_one_destination_compound=True,require_equivalence_issue=True)
 def test_changed_equivalence_fails(self):
  p,r=self.load(self.a);r['decisions'][0]['definingDifferences']=['changed physical premise']
  with self.assertRaises(AssertionError):derive(p,r,allow_one_destination_compound=True,require_equivalence_issue=True)
if __name__=='__main__':unittest.main()
