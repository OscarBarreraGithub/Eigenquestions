"""Synthetic completion values test validation only; they are never adopted."""
import copy,json,sys,unittest
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;L=F/'native-local/canonical-recovery-v4';sys.path.insert(0,str(B));import contract
from extract import extract,model_components,sha
class CompletionTests(unittest.TestCase):
 def setUp(self):
  self.packet=json.loads((L/'preflight/run-002/jobs/canonical-fields-control-statistics-challenge/packet.actual.json').read_text());self.prefix=self.packet['preservedChallenge'];ref=next(iter(self.packet['refRegistry']))
  self.reply={'version':'q025-canonical-challenge-completion/1','familyId':'control-statistics','stage':'challenge','additionalLimitations':[],'unresolved':[],'streamVariantReviews':[{'variantRef':v['variantRef'],'selectedQuestionRef':v['selectedQuestionRef'],'decision':'consistent_revision','definitionDifferences':[],'reason':'Synthetic validator test, not scientific adjudication.','refs':[ref]}for v in self.packet['streamVariants']],'attemptVariantReviews':[{'variantRef':v['variantRef'],'judgment':'consistent_revision','definingDifferences':[],'reason':'Synthetic validator test, not scientific adjudication.','refs':[ref]}for v in self.prefix['attemptVariants']]}
 def test_both_attempts_and_complete_prior_assessments_are_preserved(self):
  self.assertEqual(len(self.prefix['attempts']),2);self.assertEqual(len(self.prefix['completeFields']['priorReviews']),46);self.assertEqual(len(self.prefix['attempts'][1]['completeArrayPrefixes']['priorReviews']),32);self.assertEqual(len(self.prefix['attemptVariants']),145)
  out=contract.evaluate(self.packet,self.reply);self.assertEqual(len(out['normalizedReview']['priorReviews']),46);self.assertEqual(out['normalizedReview']['limitations'],self.prefix['completeArrayPrefixes']['limitations']);self.assertFalse(out['originalCompleteFieldsChanged']);self.assertEqual(out['discardedCompleteScientificComponents'],0)
 def test_lossless_alternate_changes_reconstruct_every_full_record(self):
  view=model_components(self.prefix);full={r['variantRef']:r for r in self.prefix['attemptVariants']}
  for row in view['attemptVariants']:
   if 'alternateChanges'in row:
    value=copy.deepcopy(view['completeFields'])
    for k in row['selectedPath']:value=value[k]
    value.update(row['alternateChanges'])
   else:value=row['alternateValue']
   self.assertEqual(value,full[row['variantRef']]['alternateValue'])
 def test_missing_either_variant_set_fails(self):
  for key in ['streamVariantReviews','attemptVariantReviews']:
   bad=copy.deepcopy(self.reply);bad[key].pop()
   with self.assertRaises(AssertionError):contract.evaluate(self.packet,bad)
 def test_cannot_overwrite_complete_scientific_collections(self):
  bad=copy.deepcopy(self.reply);bad['priorReviews']=[]
  with self.assertRaises(AssertionError):contract.evaluate(self.packet,bad)
 def test_unchanged_strict_semantic_validator_still_rejects_missing_coverage(self):
  packet=copy.deepcopy(self.packet);packet['preservedChallenge']['completeFields']['priorReviews'].pop()
  with self.assertRaisesRegex(AssertionError,'prior independent'):contract.evaluate(packet,self.reply)
 def test_conflicts_remain_withheld_not_spliced(self):
  bad=copy.deepcopy(self.reply);bad['attemptVariantReviews'][0].update(judgment='material_conflict',definingDifferences=['Synthetic difference for contract test only.']);out=contract.evaluate(self.packet,bad);self.assertEqual(out['withheldAttemptVariantRefs'],[bad['attemptVariantReviews'][0]['variantRef']]);self.assertEqual(out['normalizedReview']['newQuestions'],self.prefix['completeFields']['newQuestions'])
 def test_invented_refs_fail(self):
  self.reply['attemptVariantReviews'][0]['refs']=['invented']
  with self.assertRaisesRegex(AssertionError,'variant evidence'):contract.evaluate(self.packet,self.reply)
 def test_no_per_string_caps(self):
  def walk(v):
   if isinstance(v,dict):self.assertNotIn('maxLength',v);[walk(x)for x in v.values()]
   elif isinstance(v,list):[walk(x)for x in v]
  walk(contract.SCHEMA)
 def test_parser_extraction_does_not_execute_frozen_script_side_effects(self):
  files=list((F/'native-local/canonical-recovery-v2').glob('prefix-*.json'));before={str(p):sha(p)for p in files};text=(F/'native-local/canonical-recovery-v3/jobs/canonical-independent-control-statistics-challenge/reply.stream.raw.txt').read_text();parsed=extract(text);self.assertEqual(len(parsed['attemptVariants']),145);self.assertEqual(before,{str(p):sha(p)for p in files})
if __name__=='__main__':unittest.main()
