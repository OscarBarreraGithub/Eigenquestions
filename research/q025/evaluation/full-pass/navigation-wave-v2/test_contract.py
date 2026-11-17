import copy,json,unittest
from pathlib import Path
from contract import evaluate
F=Path(__file__).resolve().parent.parent
class Effective(unittest.TestCase):
 def load(self,name):
  d=F/'native-local/navigation-recovery-v3/adopted'/name;p=json.loads((d/'packet.actual.json').read_text());r=json.loads((d/'reply.json').read_text());r.pop('equivalenceIssueReviews',None);r['supersededPriorDecisionIds']=['pd0']if name.startswith('amplitude')else[];return p,r
 def test_real_kk_prior_decisions_without_repeat(self):
  p,r=self.load('kk-prior-reference-challenge');x=evaluate(p,r);self.assertEqual(len(x['effectiveDecisions']),22);self.assertEqual(x['normalizedReview']['decisions'],[])
 def test_real_amplitude_revision_and_single_compound_destination(self):
  p,r=self.load('amplitude-compound-challenge');x=evaluate(p,r);self.assertEqual(len(x['effectiveDecisions']),7);self.assertEqual(x['compoundAnnotationsChecked'][0]['questionRefs'],['pq0'])
 def test_current_routes_may_be_omitted_when_explicitly_supported(self):
  p,r=self.load('kk-prior-reference-challenge');r['navigation']=[];x=evaluate(p,r);self.assertEqual(len(x['effectiveNavigation']),29)
 def test_unsupported_prior_is_not_effective(self):
  p,r=self.load('kk-prior-reference-challenge');r['priorReviews'][0]['verdict']='insufficient_evidence'
  with self.assertRaises(AssertionError):evaluate(p,r)
 def test_changed_prior_definition_rejected(self):
  p,r=self.load('amplitude-compound-challenge');r['newQuestions'][0]['scope']['assumptions'].append('new assumption')
  with self.assertRaises(AssertionError):evaluate(p,r)
 def test_missing_pair_constraint_fails(self):
  p,r=self.load('kk-prior-reference-challenge');r['pairConstraints'].pop()
  with self.assertRaises(AssertionError):evaluate(p,r)
 def test_unknown_compound_target_fails(self):
  p,r=self.load('amplitude-compound-challenge');r['compoundSources'][0]['questionRefs']=['invented']
  with self.assertRaises(AssertionError):evaluate(p,r)
if __name__=='__main__':unittest.main()
