import json,unittest
from derive import derive,F
class Dispositions(unittest.TestCase):
 def load(self):
  d=F/'native-local/navigation-wave-v2/jobs/de-sitter-organization-challenge';return json.loads((d/'packet.actual.json').read_text()),json.loads((d/'reply.raw.txt').read_text())
 def test_complete_actual_extra_is_retained(self):
  p,r=self.load();x=derive(p,r);self.assertEqual(x['normalizedReview'],r);self.assertEqual(x['originalSuppliedScopeCount'],8);self.assertEqual(x['additionalSupportedAuthoredDispositions'][0]['ref'],'pq0');self.assertEqual(len(p['scopes']),8)
 def test_missing_original_fails(self):
  p,r=self.load();r['scopeDispositions'].pop(0)
  with self.assertRaises(AssertionError):derive(p,r)
 def test_unsupported_extra_fails(self):
  p,r=self.load();next(x for x in r['priorReviews']if x['ref']=='pq0')['verdict']='insufficient_evidence'
  with self.assertRaises(AssertionError):derive(p,r)
 def test_duplicate_conflicting_disposition_fails(self):
  p,r=self.load();r['scopeDispositions'].append({**r['scopeDispositions'][0],'resolution':'unresolved'})
  with self.assertRaises(AssertionError):derive(p,r)
 def test_unknown_decision_fails(self):
  p,r=self.load();r['scopeDispositions'][-1]['decisionIds'].append('invented')
  with self.assertRaises(AssertionError):derive(p,r)
if __name__=='__main__':unittest.main()
