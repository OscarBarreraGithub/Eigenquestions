import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'compact-v1'))
from test_pipeline import fixture
from contract import evaluate
class Tests(unittest.TestCase):
 def test_no_prior_not_compared_is_initial(self):
  o,p,r=fixture()
  for a in r['units']:a['a']='not_compared'
  d=evaluate(p,r);self.assertEqual(len(d['rowAgreementTransforms']),2);self.assertTrue(all(a['a']=='initial' for a in d['normalizedReview']['units']));self.assertTrue(all(a['a']=='not_compared' for a in r['units']))
 def test_agreement_without_prior_is_still_rejected(self):
  o,p,r=fixture();r['units'][0]['a']='same'
  with self.assertRaises(AssertionError):evaluate(p,r)
 def test_initial_not_reinterpreted_with_prior_records(self):
  o,p,r=fixture();p['priorAssignments']=[{'i':0}];r['units'][0]['a']='not_compared'
  with self.assertRaises(AssertionError):evaluate(p,r)
if __name__=='__main__':unittest.main()
