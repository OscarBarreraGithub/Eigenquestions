import copy,json,tempfile,shutil,unittest
from pathlib import Path
import contract,materialize,prepare
B=Path(__file__).resolve().parent;F=B.parent;L=F/'native-local/navigation-successors-v1';O=F/'native-local/navigation-wave-v2/jobs/distance-and-emergence-proposal'
class Tests(unittest.TestCase):
 def setUp(self):self.p=materialize.read(O/'packet.actual.json');self.r=materialize.read(O/'reply.raw.txt')
 def test_exact_complete_raw_is_unchanged_and_nine_context_uses_preserved(self):
  result=contract.evaluate(self.p,self.r);self.assertEqual(result['normalizedReview'],self.r);self.assertEqual(len(list(prepare.locations(self.r))),9);self.assertFalse(result['scientificContentChanged']);context=result['currentAuthoredScopeContext'][0];self.assertEqual(context['ref'],'pq0');self.assertTrue(context['notPrimary']and context['notIndependentSourceEvidence'])
 def test_unknown_scope_context_is_rejected(self):
  self.r['decisions'][0]['refs'].append('pq999')
  with self.assertRaises(AssertionError):contract.evaluate(self.p,self.r)
 def test_authored_definition_cannot_support_itself_or_another_new_definition(self):
  self.r['newQuestions'][0]['refs'].append('pq0')
  with self.assertRaisesRegex(AssertionError,'source evidence'):contract.evaluate(self.p,self.r)
  self.setUp();other=copy.deepcopy(self.r['newQuestions'][0]);other['id']='pq1';self.r['newQuestions'].append(other);self.r['newQuestions'][0]['refs'].append('pq1')
  with self.assertRaisesRegex(AssertionError,'source evidence'):contract.evaluate(self.p,self.r)
 def test_generated_scope_cannot_override_a_supplied_evidence_ref(self):
  self.p['refRegistry']['pq0']={'kind':'description','textSha256':'a'*64}
  with self.assertRaisesRegex(AssertionError,'collides'):contract.evaluate(self.p,self.r)
 def test_materialized_challenge_retains_all_actual_proposal_objects_and_pins(self):
  request=L/'jobs/distance-and-emergence-independent-challenge/request.json'
  with tempfile.TemporaryDirectory()as t:
   d=Path(t);shutil.copyfile(request,d/'request.json');materialize.materialize(d/'request.json',L);p=materialize.read(d/'packet.actual.json');self.assertEqual(p['priorReview'],self.r);self.assertEqual(p['stage'],'challenge');self.assertEqual(len(p['units']),32);self.assertEqual(len(p['evidence']),0)
   for key in ['newQuestions','decisions','navigation']:
    for obj in self.r[key]:self.assertEqual(p['refRegistry'][obj['id']]['objectValueSha256'],contract.shared.base.vh(obj));self.assertTrue(p['refRegistry'][obj['id']]['notPrimary'])
   with self.assertRaisesRegex(AssertionError,'no redispatch'):materialize.materialize(d/'request.json',L)
 def test_no_per_string_caps_and_original_failure_not_marked_complete(self):
  self.assertNotIn('maxLength',json.dumps(contract.SCHEMA));self.assertEqual(materialize.read(O/'receipt.json')['status'],'failed');r=materialize.read(L/'adopted/distance-proposal-authored-context/receipt.json');self.assertEqual(r['originalNativeStatus'],'failed');self.assertFalse(r['nativeReviewRepeated']);self.assertFalse(r['scientificContentChanged'])
if __name__=='__main__':unittest.main()
