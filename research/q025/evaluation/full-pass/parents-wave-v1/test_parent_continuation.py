import copy,importlib.util,sys,unittest
from pathlib import Path
B=Path(__file__).resolve().parent
import contract
from build_child_artifact import augment_parent_frontier
sys.path.insert(0,str(B.parent/'parents-v1'))
from test_parent_pipeline import ParentTests
from parent_pipeline import make_parent_packet
class ContinuationTests(unittest.TestCase):
 def test_reuse_only_parent_preserves_exact_identity_and_unresolved_status(self):
  q={'id':'x0_0','candidateId':'question-existing','scopeStatus':'unresolved_scope_change','title':'A question','question':'What is tested?','summary':'A summary','scope':{},'readingLimit':'Only bounded source context.'}
  a={'questions':[]};p={'kind':'parent','existingCards':[q],'refRegistry':{}};r={'links':[{'source':'r','target':'x0_0','type':'method'}],'units':[]};out=augment_parent_frontier(a,p,r)
  self.assertEqual(out['questions'][0]['candidateId'],'question-existing');self.assertEqual(out['questions'][0]['scopeStatus'],'unresolved_scope_change');self.assertFalse(out['questions'][0]['primaryReadingClaim']);self.assertEqual(out['reusedQuestionFrontierCount'],1)
 def valid(self):
  o,c,r=ParentTests().make();p,_=make_parent_packet(o,c);r['cards']=[]
  for a in r['units']:a['q']=[{'id':'c0','role':'comparison'}]
  r['links'][0]['target']='c0';r['cardReviews']=[{'id':'c0','decision':'supported_as_written','scopeChange':'same','replacement':'','note':'Complete source-qualified justification. '*20,'refs':['d0']}];return p,r
 def test_complete_long_scientific_fields_are_retained(self):
  p,r=self.valid();r['region']['readingLimit']='Complete reading limitation. '*40;out=contract.evaluate(p,r);self.assertEqual(out['normalizedReview']['region']['readingLimit'],r['region']['readingLimit']);self.assertTrue(out['validation']['valid'])
 def test_relaxed_string_length_does_not_relax_sources_or_coverage(self):
  p,r=self.valid();r['cardReviews'][0]['refs']=['invented']
  with self.assertRaises(AssertionError):contract.evaluate(p,r)
  p,r=self.valid();r['units'].pop()
  with self.assertRaises(AssertionError):contract.evaluate(p,r)
if __name__=='__main__':unittest.main()
