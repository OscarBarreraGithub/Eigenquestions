import copy,unittest
from contract import evaluate
class NavigationContractTests(unittest.TestCase):
 def setUp(self):
  self.p={'familyId':'t','stage':'proposal','scopes':[{'ref':'c0'},{'ref':'c1'}],'refRegistry':{'c0':{'kind':'scope'},'c1':{'kind':'scope'},'u0':{'kind':'description'}},'nominations':[{'left':'c0','right':'c1'}]}
  self.r={'version':'q025-canonical-review/1','familyId':'t','stage':'proposal','summary':'Two distinct questions, one conditional comparison.','newQuestions':[],'decisions':[{'id':'pd0','operation':'comparison','members':['c0','c1'],'target':'','definingDifferences':['Distinct targets'],'reason':'Related comparison.','refs':['c0','c1']}],'pairConstraints':[{'left':'c0','right':'c1','relation':'different','reason':'Different targets.','refs':['c0','c1']}],'scopeDispositions':[{'ref':v,'resolution':'retained','decisionIds':['pd0'],'reason':'Retain scoped identity.','refs':[v]}for v in ['c0','c1']],'sourceContributions':[],'compoundSources':[],'priorReviews':[],'limitations':['Definitions only.'],'unresolved':[],'navigation':[{'id':'pl0','source':'c0','target':'c1','type':'comparison','title':'Compare the scoped setting','qualification':'No implication.','reason':'A useful contrast.','refs':['c0','c1']}],'navigationReviews':[],'sourceContributionReviews':[]}
 def test_pair_identity_and_route_remain_separate(self):self.assertEqual(evaluate(self.p,self.r)['validation']['navigationCount'],1)
 def test_missing_pair_constraint_rejected(self):self.r['pairConstraints']=[];self.assertRaises(AssertionError,evaluate,self.p,self.r)
 def test_source_object_cannot_be_destination(self):self.r['navigation'][0]['target']='u0';self.assertRaises(AssertionError,evaluate,self.p,self.r)
 def challenge(self):
  p=copy.deepcopy(self.p);p['stage']='challenge';p['priorReview']=copy.deepcopy(self.r);r=copy.deepcopy(self.r);r['stage']='challenge';r['decisions'][0]['id']='cd0';r['navigation'][0]['id']='cl0'
  for x in r['scopeDispositions']:x['decisionIds']=['cd0']
  r['priorReviews']=[{'ref':'pd0','kind':'decision','verdict':'supported_as_written','reason':'Exact decision supported.','refs':['c0','c1']}];r['navigationReviews']=[{'ref':'pl0','verdict':'supported_as_written','reason':'Exact route supported.','refs':['c0','c1']}];return p,r
 def test_each_route_needs_independent_assessment(self):p,r=self.challenge();r['navigationReviews']=[];self.assertRaises(AssertionError,evaluate,p,r)
 def test_each_new_source_role_needs_explicit_assessment(self):
  p,r=self.challenge();p['priorReview']['sourceContributions']=[{'unitRef':'u0','questionRef':'c0','role':'addresses','reason':'Exact own target.','refs':['u0']}];self.assertRaises(AssertionError,evaluate,p,r)
 def test_challenge_preserves_whole_output_hash(self):p,r=self.challenge();d=evaluate(p,r);self.assertEqual(d['normalizedReview'],r)
if __name__=='__main__':unittest.main()
