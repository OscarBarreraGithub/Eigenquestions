import copy,sys,unittest
from pathlib import Path
import contract
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B.parent/'compact-v1'));from test_pipeline import fixture
class RecoveryTests(unittest.TestCase):
 def test_missing_rows_are_not_recovered_from_broad_scope(self):
  o,p,r=fixture();r['units']=[]
  with self.assertRaises(AssertionError):contract.evaluate(p,r)
 def test_no_field_cap_and_complete_empty_aliases_retained(self):
  o,p,r=fixture();r['cards'][0]['readingLimit']='Complete bounded source limitation. '*30;out=contract.evaluate(p,r);self.assertEqual(out['normalizedReview']['cards'][0]['readingLimit'],r['cards'][0]['readingLimit']);self.assertEqual(out['normalizedReview']['cards'][0]['aliases'],[])
if __name__=='__main__':unittest.main()
