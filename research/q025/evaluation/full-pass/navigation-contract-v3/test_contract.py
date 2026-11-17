import copy,json,unittest
from pathlib import Path
from contract import evaluate
F=Path(__file__).resolve().parent.parent
class CurrentScope(unittest.TestCase):
 def load(self):
  d=F/'native-local/navigation-wave-v2/jobs/distance-and-emergence-proposal';return json.loads((d/'packet.actual.json').read_text()),json.loads((d/'reply.raw.txt').read_text())
 def test_actual_complete_proposal(self):
  p,r=self.load();x=evaluate(p,r);self.assertEqual(x['normalizedReview'],r);self.assertEqual([a['ref']for a in x['currentAuthoredScopeContext']],['pq0']);self.assertTrue(x['currentAuthoredScopeContext'][0]['notPrimary']);self.assertNotIn('pq0',p['refRegistry'])
 def test_all_nine_uses_remain_context_with_own_source_roles(self):
  p,r=self.load();count=sum('pq0'in x.get('refs',[])for key in ['decisions','pairConstraints','sourceContributions','navigation']for x in r[key]);self.assertEqual(count,9);x=evaluate(p,r);self.assertEqual(x['normalizedReview']['sourceContributions'],r['sourceContributions']);self.assertTrue(all(z['unitRef']in z['refs']and p['refRegistry'][z['unitRef']]['kind']=='description'for z in r['sourceContributions']))
 def test_unknown_ref_fails(self):
  p,r=self.load();r['decisions'][0]['refs'].append('pq9')
  with self.assertRaises(AssertionError):evaluate(p,r)
 def test_self_source_support_fails(self):
  p,r=self.load();r['newQuestions'][0]['refs']=['pq0']
  with self.assertRaises(AssertionError):evaluate(p,r)
 def test_false_primary_collision_fails(self):
  p,r=self.load();p['refRegistry']['pq0']={'kind':'primary'}
  with self.assertRaises(AssertionError):evaluate(p,r)
if __name__=='__main__':unittest.main()
