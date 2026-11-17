"""Synthetic completion judgments test shape/coverage only; never adopted."""
import copy,json,sys,unittest
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;L=F/'native-local/screen-recovery-v1';sys.path.insert(0,str(B));import contract
from extract import extract,model_components,sha
from materialize import check_source_bindings
def packet(number):return json.loads((L/f'preflight/run-003/jobs/canonical-continuation-v4-{number}-screen-completion/packet.actual.json').read_text())
def completion(p):
 ref=p['scopes'][0]['ref'];parts=p['preservedScreen'];assert not parts['missingRefs']['scopeReviews']
 return {'version':'q025-screen-completion/1','familyId':p['familyId'],'stage':'triage','missingScopeReviews':[],'missingComparisonReviews':[{'ref':refid,'identityScreen':'unresolved','scientificConnections':['unresolved'],'basis':'scope_definition','priority':'unresolved','definingDifferences':[],'reason':'Synthetic validator test only; not a scientific judgment.','refs':[ref]}for refid in parts['missingRefs']['comparisonReviews']],'additionalLimitations':['Synthetic test, not an adopted scientific screen.'],'unresolved':[],'attemptVariantReviews':[{'variantRef':v['variantRef'],'judgment':'unresolved','definingDifferences':[],'reason':'Synthetic validator test only.','refs':[ref]}for v in parts['attemptVariants']]}
class CompletionTests(unittest.TestCase):
 def test_exact_retained_and_missing_coverage_both_attempts(self):
  for number,selected,nscopes,ncomparisons,missing,nvariants in [('0039',0,26,95,5,61),('0047',1,39,82,6,49)]:
   p=packet(number);s=p['preservedScreen'];self.assertEqual(len(s['attempts']),2);self.assertEqual(s['selectedAttempt'],selected);self.assertEqual(len(s['selectedFields']['scopeReviews']),nscopes);self.assertEqual(len(s['selectedFields']['comparisonReviews']),ncomparisons);self.assertEqual(len(s['missingRefs']['comparisonReviews']),missing);self.assertEqual(len(s['attemptVariants']),nvariants);out=contract.evaluate(p,completion(p));self.assertEqual(out['normalizedReview']['comparisonReviews'][:ncomparisons],s['selectedFields']['comparisonReviews']);self.assertFalse(out['scientificAdmission']);self.assertEqual(out['discardedCompleteScientificComponents'],0)
 def test_lossless_alternates(self):
  for n in ['0039','0047']:
   p=packet(n)['preservedScreen'];view=model_components(p);original={r['variantRef']:r for r in p['attemptVariants']}
   for row in view['attemptVariants']:
    if 'alternateChanges'in row:
     value=copy.deepcopy(view['selectedFields'])
     for key in row['selectedPath']:value=value[key]
     value.update(row['alternateChanges'])
    else:value=row['alternateValue']
    self.assertEqual(value,original[row['variantRef']]['alternateValue'])
 def test_missing_duplicate_or_overwritten_records_rejected(self):
  p=packet('0039')
  for key in ['missingComparisonReviews','attemptVariantReviews']:
   r=completion(p);r[key].pop()
   with self.assertRaises(AssertionError):contract.evaluate(p,r)
   r=completion(p);r[key][-1]=copy.deepcopy(r[key][0])
   with self.assertRaises(AssertionError):contract.evaluate(p,r)
  r=completion(p);r['missingComparisonReviews'][0]['ref']=p['preservedScreen']['selectedFields']['comparisonReviews'][0]['ref']
  with self.assertRaises(AssertionError):contract.evaluate(p,r)
 def test_full_validator_still_requires_valid_evidence_and_identity_contrast(self):
  p=packet('0039');r=completion(p);r['missingComparisonReviews'][0]['identityScreen']='different_scoped_targets'
  with self.assertRaisesRegex(AssertionError,'defining contrast'):contract.evaluate(p,r)
  r=completion(p);r['missingComparisonReviews'][0]['basis']='description_checked'
  with self.assertRaisesRegex(AssertionError,'actual supplied description'):contract.evaluate(p,r)
 def test_conflict_remains_withheld_and_no_completed_field_can_be_overwritten(self):
  p=packet('0047');r=completion(p);r['attemptVariantReviews'][0].update(judgment='material_conflict',definingDifferences=['Synthetic conflict.']);out=contract.evaluate(p,r);self.assertIn(r['attemptVariantReviews'][0]['variantRef'],out['withheldAttemptVariantRefs']);self.assertEqual(out['normalizedReview']['scopeReviews'],p['preservedScreen']['selectedFields']['scopeReviews']);r['scopeReviews']=[]
  with self.assertRaises(AssertionError):contract.evaluate(p,r)
 def test_source_sidecar_hashes_and_variant_refs(self):
  p=packet('0047');check_source_bindings(p);p['units'][0]['description']+='changed'
  with self.assertRaises(AssertionError):check_source_bindings(p)
  p=packet('0039');r=completion(p);r['attemptVariantReviews'][0]['refs']=['invented']
  with self.assertRaisesRegex(AssertionError,'variant evidence'):contract.evaluate(p,r)
 def test_no_per_string_caps(self):
  def walk(v):
   if isinstance(v,dict):self.assertNotIn('maxLength',v);[walk(x)for x in v.values()]
   elif isinstance(v,list):[walk(x)for x in v]
  walk(contract.SCHEMA)
 def test_parser_only_executes_pure_function_and_preserves_utf8_ranges(self):
  old=list((F/'native-local/canonical-recovery-v2').glob('prefix-*.json'));before={str(p):sha(p)for p in old};p=packet('0039');d=F/'native-local/canonical-triage-wave-v2/jobs/canonical-continuation-v4-0039-screen';text=(d/'reply.stream.raw.txt').read_text();parts=extract(text,p,0)
  import hashlib
  for attempt in parts['attempts']:
   for row in attempt['exactValueRanges']:self.assertEqual(hashlib.sha256(text.encode()[row['start']:row['end']]).hexdigest(),row['sha256'])
  for row in parts['incompleteTails']:self.assertEqual(text.encode()[row['start']:row['end']].decode(),row['text']);self.assertEqual(hashlib.sha256(row['text'].encode()).hexdigest(),row['sha256'])
  self.assertEqual(before,{str(p):sha(p)for p in old})
 def test_deterministic_adoption_keeps_original_failed_receipt(self):
  audit=json.loads((B/'adoption-0065.json').read_text());d=F/'native-local/canonical-triage-wave-v2/jobs/canonical-continuation-v4-0065-screen';target=F.parent/audit['derivedJobPath'];self.assertEqual(json.loads((d/'receipt.json').read_text())['status'],'failed');self.assertEqual((d/'reply.raw.txt').read_bytes(),(target/'reply.raw.txt').read_bytes());self.assertEqual(json.loads((d/'reply.raw.txt').read_text()),json.loads((target/'reply.json').read_text()));self.assertFalse(audit['nativeLaunches'])
if __name__=='__main__':unittest.main()
