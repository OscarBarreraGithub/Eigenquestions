import copy,unittest
from contract import evaluate
class ClauseTests(unittest.TestCase):
 def fixture(self):
  p={'familyId':'test','stage':'proposal','cases':[{'caseId':'case0','originalText':'An incomplete condition and','refs':{'e0':{'kind':'primary'}}}],'priorReview':None};r={'version':'q025-clause-review/1','familyId':'test','stage':'proposal','summary':'Bounded source review.','results':[{'caseId':'case0','status':'replace_proposed','replacementText':'A complete source-specific condition.','meaningChange':'clarification_within_supplied_scope','scopeImpact':'annotation_only','reason':'Supported by the supplied window; no lost words claimed.','refs':['e0']}],'priorAssessments':[],'limitations':['Bounded primary only.'],'unresolved':[]};return p,r
 def test_replacement_is_retained_as_proposal(self):
  p,r=self.fixture();out=evaluate(p,r);self.assertEqual(out['normalizedReview'],r);self.assertFalse(out['semanticRepairPerformed'])
 def test_original_byte_identity_required_for_unchanged(self):
  p,r=self.fixture();r['results'][0]['status']='complete_as_written';r['results'][0]['meaningChange']='unchanged'
  with self.assertRaises(AssertionError):evaluate(p,r)
 def test_missing_cases_and_invented_sources_rejected(self):
  p,r=self.fixture();r['results']=[]
  with self.assertRaises(AssertionError):evaluate(p,r)
  p,r=self.fixture();r['results'][0]['refs']=['invented']
  with self.assertRaises(AssertionError):evaluate(p,r)
 def test_abstention_cannot_smuggle_completion(self):
  p,r=self.fixture();r['results'][0]['status']='insufficient_evidence'
  with self.assertRaises(AssertionError):evaluate(p,r)
 def test_challenge_requires_independent_result_per_case(self):
  p,r=self.fixture();p['priorReview']=copy.deepcopy(r);p['stage']='challenge';r['stage']='challenge'
  with self.assertRaises(AssertionError):evaluate(p,r)
  r['priorAssessments']=[{'caseId':'case0','decision':'supported_as_written','reason':'Supplied text supports this qualification.','refs':['e0']}];self.assertTrue(evaluate(p,r)['validation']['valid'])
if __name__=='__main__':unittest.main()
