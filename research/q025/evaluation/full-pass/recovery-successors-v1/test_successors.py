import copy,json,sys,tempfile,unittest
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;sys.path.insert(0,str(B));import contract
from prefix import extract,assemble
sys.path.insert(0,str(F/'compact-v1'));from test_pipeline import fixture
from materialize import verified_review,parent_children,successor_model_view
class RecoveryTests(unittest.TestCase):
 def test_partial_nested_fields_are_locked(self):
  text='{"version":"q025-compact-review/1","familyId":"test","cards":[{"id":"q0","title":"Fixed scope","aliases":'
  prefix=extract(text);self.assertEqual(prefix['completeArrayPrefixes']['cards'],[])
  result=assemble(prefix,{'cards':[{'id':'q0','title':'Fixed scope','aliases':[]}]});self.assertEqual(result['cards'][0]['title'],'Fixed scope')
  with self.assertRaisesRegex(AssertionError,'preserved'):assemble(prefix,{'cards':[{'id':'q0','title':'Changed premise','aliases':[]}]})
 def test_complete_prefix_rows_are_reused_not_reemitted(self):
  original,packet,reply=fixture();ordered={k:reply[k] for k in contract.SCHEMA['properties']};fields=list(ordered);prefix_fields={k:ordered[k] for k in fields[:fields.index('units')]};text=json.dumps(prefix_fields,separators=(',',':'))[:-1]+',"units":['+json.dumps(reply['units'][0],separators=(',',':'))+',';prefix=extract(text);packet={**packet,'preservedComponents':prefix,'prefixArtifactSha256':'a'*64,'streamVariants':[]};remaining={k:copy.deepcopy(v) for k,v in reply.items() if k not in prefix['completeFields']};remaining['units']=remaining['units'][1:];completion={'version':'q025-successor-completion/1','familyId':'test','stage':'proposal','remaining':remaining,'variantAssessments':[]};result=contract.evaluate(packet,completion);self.assertEqual(result['normalizedReview'],reply);self.assertFalse(result['originalCompleteFieldsChanged']);self.assertEqual(result['discardedCompleteScientificComponents'],0)
  completion['remaining']['units']=[]
  with self.assertRaisesRegex(AssertionError,'coverage'):contract.evaluate(packet,completion)
 def test_multiple_attempts_retain_conflicting_complete_values(self):
  first='{"version":"q025-compact-review/1","familyId":"test","summary":"Earlier condition","cards":[';last='{"version":"q025-compact-review/1","familyId":"test","summary":"Later condition","cards":[';prefix=extract(first+last);self.assertEqual(prefix['selectedAttempt'],1);self.assertEqual(prefix['completeFields']['summary'],'Later condition');self.assertTrue(any(v['value']=='Earlier condition' for v in prefix['streamVariants']))
  with self.assertRaisesRegex(AssertionError,'earlier-attempt'):contract.check_variants({'streamVariants':prefix['streamVariants'],'refRegistry':{'e0':{}}},[])
 def test_model_view_preserves_every_locked_value_without_duplicate_archives(self):
  from prefix import at
  for family in ['ce36cae0274019373c8a','ce2e0c80657f40e352ee','076a8e988b123c215a92']:
   prefix=json.loads((F/'native-local/recovery-successors-v1/prefixes'/f'{family}.json').read_text());packet={'preservedComponents':prefix,'streamVariants':prefix['streamVariants']};view=successor_model_view(packet);p=view['preservedComponents']
   for lock in prefix['lockedValues']:
    path=lock['path']
    if path[0] in p['completeFields']:self.assertEqual(at(p['completeFields'],path),lock['value'])
    elif len(path)>1 and path[0] in p['completeArrayPrefixes'] and isinstance(path[1],int) and path[1]<len(p['completeArrayPrefixes'][path[0]]):self.assertEqual(at(p['completeArrayPrefixes'],path),lock['value'])
    else:self.assertIn({'path':path,'value':lock['value']},p['partialValueLocks'])
   self.assertEqual(view['streamVariants'],prefix['streamVariants']);self.assertNotIn('earlierAttempts',p);self.assertEqual(packet['preservedComponents'],prefix)
 def test_no_per_string_caps_in_successor_schema(self):
  def walk(value):
   if isinstance(value,dict):self.assertNotIn('maxLength',value);[walk(v) for v in value.values()]
   elif isinstance(value,list):[walk(v) for v in value]
  walk(contract.regular_schema(True));walk(contract.completion_schema(extract('{"version":"q025-compact-review/1","familyId":"test","cards":[')))
 def test_pf28_is_exact_prior_context_never_primary(self):
  d=F/'native-local/parents-wave-v1/jobs/parent-8d2b5fd7cc13cefc77fe-challenge';packet=json.loads((d/'packet.actual.json').read_text());reply=json.loads((d/'reply.raw.txt').read_text());derived,reference=contract.prior_annotation_context(packet,reply);self.assertEqual(reference['kind'],'prior_annotation_context');self.assertFalse(reference['primaryReadingClaim']);self.assertEqual(reference['definition']['status'],'historical_or_rejected');self.assertEqual(derived['units'],packet['units']);self.assertEqual(reply['cardReviews'][5]['refs'],['e0','e6','e9','pf28']);self.assertEqual(contract.evaluate(derived,reply)['validation']['unitCount'],len(packet['units']))
  bad=copy.deepcopy(reply);bad['cardReviews'][0]['refs'].append('pf28')
  with self.assertRaisesRegex(AssertionError,'exact failed locus'):contract.prior_annotation_context(packet,bad)
 def test_revalidated_imports_keep_failed_originals(self):
  for key in ['leaf-55a2311c12b246ddbd15-proposal','leaf-90980b7a8339256bfea7-proposal','parent-8d2b5fd7cc13cefc77fe-challenge']:
   d=F/'native-local/recovery-successors-v1/adopted'/key;reply,normal,receipt=verified_review(d);self.assertFalse(receipt['nativeTurnStartedHere']);self.assertEqual(receipt['originalNativeStatus'],'failed');old=F.parent/receipt['originalJobPath'];self.assertEqual(json.loads((old/'receipt.json').read_text())['status'],'failed');self.assertEqual(receipt['derivedUnitCount'],len(reply['units']))
 def test_current_manifest_rewires_affected_ancestors_only(self):
  m=json.loads((B/'manifest.json').read_text());self.assertEqual(len(m['jobs']),34);self.assertEqual(len(m['partialRecoveries']),3);self.assertEqual(len(m['importedRevalidations']),3);self.assertEqual(m['nativeLaunches'],0);self.assertEqual(m['maxAuthorizedConcurrency'],8)
  for job in m['jobs']:
   req=json.loads((F/'native-local/recovery-successors-v1/jobs'/job['jobId']/'request.json').read_text());self.assertEqual(req['maxOutputCharacters'],120000);self.assertEqual(req['timeoutSeconds'],1800);self.assertTrue(req['sourceOnly'])
   for dep in req['childDependencies']:
    if dep['reviewKey'] in m['replacements']:self.assertEqual(dep['jobPath'],m['replacements'][dep['reviewKey']])
 def test_parent_handoff_retains_prior_annotation_namespace(self):
  m=json.loads((B/'manifest.json').read_text());entry=next(j for j in m['jobs'] if j['jobId'].endswith('-proposal') and any(d['reviewKey']=='8d2b5fd7cc13cefc77fe' for d in json.loads((F/'native-local/recovery-successors-v1/jobs'/j['jobId']/'request.json').read_text())['childDependencies']));req=json.loads((F/'native-local/recovery-successors-v1/jobs'/entry['jobId']/'request.json').read_text());dep=next(d for d in req['childDependencies'] if d['reviewKey']=='8d2b5fd7cc13cefc77fe')
  with tempfile.TemporaryDirectory(dir=F/'native-local/recovery-successors-v1') as temp:
   children,pins=parent_children({'childDependencies':[dep]},Path(temp));self.assertEqual(children[0]['priorAnnotationContext'][0]['definition']['status'],'historical_or_rejected');self.assertFalse(children[0]['priorAnnotationContext'][0]['primaryReadingClaim']);self.assertTrue(pins[0]['childReceiptSha256'])
if __name__=='__main__':unittest.main()
