import copy,unittest
from contract import evaluate
class CanonicalTests(unittest.TestCase):
 def fixture(self):
  p={'familyId':'test','stage':'proposal','scopes':[{'ref':'c0'},{'ref':'c1'}],'refRegistry':{'u0':{'kind':'description','unitId':'one'}},'priorReview':None};r={'version':'q025-canonical-review/1','familyId':'test','stage':'proposal','summary':'Test.','newQuestions':[],'decisions':[{'id':'pd0','operation':'same_scoped_question','members':['c0','c1'],'target':'c0','definingDifferences':[],'reason':'Same stated target and conditions.','refs':['u0']}],'pairConstraints':[{'left':'c0','right':'c1','relation':'same_scoped_question','reason':'Same stated conditions.','refs':['u0']}],'scopeDispositions':[{'ref':x,'resolution':'reused','decisionIds':['pd0'],'reason':'Same question.','refs':['u0']} for x in ['c0','c1']],'sourceContributions':[],'compoundSources':[],'priorReviews':[],'limitations':['Synthetic fixture.'],'unresolved':[]};return p,r
 def test_complete_group_retains_exact_source_and_scope_ids(self):
  p,r=self.fixture();out=evaluate(p,r);self.assertEqual(out['normalizedReview'],r);self.assertFalse(out['semanticRepairPerformed'])
 def test_missing_scope_cannot_disappear(self):
  p,r=self.fixture();r['scopeDispositions'].pop()
  with self.assertRaises(AssertionError):evaluate(p,r)
 def test_changed_defining_scope_cannot_be_alias(self):
  p,r=self.fixture();r['decisions'][0]['definingDifferences']=['Different regime']
  with self.assertRaises(AssertionError):evaluate(p,r)
 def test_group_requires_all_pair_constraints(self):
  p,r=self.fixture();r['pairConstraints']=[]
  with self.assertRaises(AssertionError):evaluate(p,r)
 def test_invented_source_rejected(self):
  p,r=self.fixture();r['decisions'][0]['refs']=['invented']
  with self.assertRaises(AssertionError):evaluate(p,r)
 def test_challenge_must_review_prior_decisions(self):
  p,r=self.fixture();p['priorReview']=copy.deepcopy(r);p['stage']='challenge';r['stage']='challenge';r['decisions'][0]['id']='cd0'
  for x in r['scopeDispositions']:x['decisionIds']=['cd0']
  with self.assertRaises(AssertionError):evaluate(p,r)
  r['priorReviews']=[{'ref':'pd0','kind':'decision','verdict':'supported_as_written','reason':'Independently assessed same scope.','refs':['u0']}];self.assertTrue(evaluate(p,r)['validation']['valid'])
if __name__=='__main__':unittest.main()
