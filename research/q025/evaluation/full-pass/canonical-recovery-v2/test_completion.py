import copy,unittest
from contract import evaluate
class CompletionTests(unittest.TestCase):
 def fixture(self):
  p={'familyId':'test','stage':'proposal','scopes':[{'ref':'c0'},{'ref':'c1'}],'refRegistry':{'u0':{'kind':'description','unitId':'one'}},'priorReview':None,'prefixArtifactSha256':'1'*64,'streamVariants':[],'preservedComponents':{'completeFields':{'version':'q025-canonical-review/1','familyId':'test','stage':'proposal','summary':'Preserved source review.','newQuestions':[],'decisions':[]},'completeArrayPrefixes':{'pairConstraints':[]}}};r={'version':'q025-canonical-completion/1','familyId':'test','stage':'proposal','additionalDecisions':[],'additionalPairConstraints':[],'scopeDispositions':[{'ref':x,'resolution':'retained','decisionIds':[],'reason':'No bounded equivalence established.','refs':['u0']} for x in ['c0','c1']],'sourceContributions':[],'compoundSources':[],'variantAssessments':[],'limitations':['Bounded scope search only.'],'unresolved':[]};return p,r
 def test_preserved_components_are_unchanged_and_tail_is_explicit(self):
  p,r=self.fixture();before=copy.deepcopy(p['preservedComponents']);out=evaluate(p,r);self.assertEqual(p['preservedComponents'],before);self.assertEqual(out['normalizedReview']['summary'],before['completeFields']['summary']);self.assertFalse(out['originalCompleteFieldsChanged'])
 def test_missing_scope_coverage_and_invented_sources_fail(self):
  p,r=self.fixture();r['scopeDispositions'].pop()
  with self.assertRaises(AssertionError):evaluate(p,r)
  p,r=self.fixture();r['scopeDispositions'][0]['refs']=['invented']
  with self.assertRaises(AssertionError):evaluate(p,r)
 def test_earlier_definition_variant_cannot_disappear(self):
  p,r=self.fixture();p['streamVariants']=[{'variantRef':'attempt0:pq0','selectedQuestionRef':'pq0'}]
  with self.assertRaises(AssertionError):evaluate(p,r)
  r['variantAssessments']=[{'variantRef':'attempt0:pq0','selectedQuestionRef':'pq0','decision':'unresolved','definitionDifferences':['A condition differs.'],'reason':'Retain conflict for independent challenge.','refs':['u0']}];out=evaluate(p,r);self.assertEqual(out['streamVariantAssessments'],r['variantAssessments'])
 def test_completion_cannot_rewrite_question_definitions(self):
  p,r=self.fixture();r['newQuestions']=[]
  with self.assertRaises(AssertionError):evaluate(p,r)
if __name__=='__main__':unittest.main()
