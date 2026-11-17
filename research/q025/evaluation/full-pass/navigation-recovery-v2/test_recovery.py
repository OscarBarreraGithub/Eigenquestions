import copy,json,unittest
from pathlib import Path
from contract import classify_retained
F=Path(__file__).resolve().parent.parent;D=F/'native-local/navigation-decisions-v1/jobs/inflation-and-late-time-scope-reuse-challenge'
class RetentionTests(unittest.TestCase):
 def setUp(self):self.p=json.loads((D/'packet.actual.json').read_text());self.r=json.loads((D/'reply.raw.txt').read_text())
 def test_exact_actual_retention_is_lossless(self):d=classify_retained(self.p,self.r);self.assertEqual(d['normalizedReview'],self.r);self.assertEqual(len(d['retainedPriorObjects']),20);self.assertEqual(d['logicalObjectsDuplicated'],0)
 def test_definition_change_is_not_retention(self):self.r['newQuestions'][0]['title']+=' changed';self.assertRaises(AssertionError,classify_retained,self.p,self.r)
 def test_decision_change_is_not_retention(self):self.r['decisions'][0]['reason']+=' changed';self.assertRaises(AssertionError,classify_retained,self.p,self.r)
 def test_missing_independent_support_is_rejected(self):self.r['priorReviews']=self.r['priorReviews'][1:];self.assertRaises(AssertionError,classify_retained,self.p,self.r)
 def test_route_change_cannot_hide_under_old_identity(self):self.r['navigation'][0]['type']='application_of';self.assertRaises(AssertionError,classify_retained,self.p,self.r)
if __name__=='__main__':unittest.main()
