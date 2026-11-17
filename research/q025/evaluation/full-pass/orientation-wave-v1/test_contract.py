import copy,json,shutil,tempfile,unittest
from pathlib import Path
import contract,materialize
B=Path(__file__).resolve().parent

def packet():return {'familyId':'test','stage':'proposal','scopes':[{'ref':'s0'},{'ref':'s1'}],'relations':[{'ref':'l0','source':'s0','target':'s1'}],'priorReview':None}
def withheld(p):return {'version':'q025-orientation-decision/1','familyId':p['familyId'],'stage':p['stage'],'summary':'Synthetic representation check.','decisions':[{'id':'d'+str(i),'originalRef':r['ref'],'status':'withheld','source':r['source'],'target':r['target'],'type':None,'title':'','rationale':'Fixture leaves a precise applicability condition unestablished.','qualification':'','missingPremise':'The exact regime compatibility is not supplied.','refs':[r['ref'],r['source'],r['target']]}for i,r in enumerate(p['relations'])],'priorReviews':[],'limitations':['No scientific admission.'],'unresolved':['Fixture only.']}
def route(p):
 r=withheld(p);r['decisions'][0].update(status='route',type='method_for',title='Examine the supplied method under its stated conditions',qualification='Only the supplied regime.',missingPremise='');return r
def challenge(p,prior):
 cp={**p,'stage':'challenge','priorReview':prior};r=withheld(cp);r['decisions']=[];r['priorReviews']=[{'ref':d['id'],'verdict':'supported_as_written','reason':'Independent exact scoped review.','refs':d['refs']}for d in prior['decisions']];return cp,r
class Tests(unittest.TestCase):
 def test_every_original_has_exactly_one_proposal(self):
  p=packet();r=route(p);self.assertEqual(contract.evaluate(p,r)['validation']['effectiveDecisionCount'],1)
  for mutate in [lambda x:x['decisions'].clear(),lambda x:x['decisions'].append(copy.deepcopy(x['decisions'][0]))]:
   v=copy.deepcopy(r);mutate(v)
   with self.assertRaises(AssertionError):contract.evaluate(p,v)
 def test_same_endpoints_or_explicit_reversal_only(self):
  p=packet();r=route(p);d=r['decisions'][0];d['source'],d['target']=d['target'],d['source'];contract.evaluate(p,r)
  for key,value in [('source','s0'),('target','s2')]:
   bad=copy.deepcopy(r);bad['decisions'][0][key]=value
   with self.assertRaisesRegex(AssertionError,'endpoint'):contract.evaluate(p,bad)
 def test_withheld_has_no_fabricated_type(self):
  p=packet();r=withheld(p);contract.evaluate(p,r);r['decisions'][0]['type']='related_question'
  with self.assertRaisesRegex(AssertionError,'withheld'):contract.evaluate(p,r)
 def test_routes_require_supported_type_title_no_missing_premise(self):
  p=packet();r=route(p)
  for key,value in [('type','application'),('title',''),('missingPremise','Unknown applicability')]:
   bad=copy.deepcopy(r);bad['decisions'][0][key]=value
   with self.assertRaises(AssertionError):contract.evaluate(p,bad)
 def test_no_unprovided_primary_or_duplicate_context_refs(self):
  p=packet();r=route(p)
  for value in ['e0','s0']:
   bad=copy.deepcopy(r);bad['decisions'][0]['refs'].append(value)
   with self.assertRaisesRegex(AssertionError,'context refs'):contract.evaluate(p,bad)
 def test_supported_rows_retained_exactly_without_reemission(self):
  p=packet();prior=route(p);cp,r=challenge(p,prior);out=contract.evaluate(cp,r);self.assertEqual(out['effectiveDecisions'],prior['decisions']);self.assertEqual(out['retainedPriorDecisionIds'],['d0'])
  r['decisions']=[{**prior['decisions'][0],'id':'new0'}]
  with self.assertRaisesRegex(AssertionError,'re-emitted'):contract.evaluate(cp,r)
 def test_every_prior_including_withheld_requires_explicit_review(self):
  p=packet();prior=withheld(p);cp,r=challenge(p,prior);contract.evaluate(cp,r);r['priorReviews']=[]
  with self.assertRaisesRegex(AssertionError,'explicit prior'):contract.evaluate(cp,r)
 def test_replacement_is_fresh_and_keeps_original_reference(self):
  p=packet();prior=route(p);cp,r=challenge(p,prior);r['priorReviews'][0]['verdict']='replace';r['decisions']=[withheld(p)['decisions'][0]]
  with self.assertRaisesRegex(AssertionError,'fresh'):contract.evaluate(cp,r)
  r['decisions'][0]['id']='replacement0';out=contract.evaluate(cp,r);self.assertEqual(out['validation']['withheldCount'],1)
  r['decisions'][0]['originalRef']='l9'
  with self.assertRaisesRegex(AssertionError,'original'):contract.evaluate(cp,r)
 def test_no_new_scientific_fields_or_string_caps(self):
  p=packet();r=route(p);r['summary']='Retained qualification. '*10000;contract.evaluate(p,r);self.assertNotIn('maxLength',json.dumps(contract.SCHEMA));r['newScopes']=[]
  with self.assertRaisesRegex(AssertionError,'extra'):contract.evaluate(p,r)
 def test_complete_projection_detects_original_clause_loss(self):
  root=B.parents[4];index=json.loads((B.parent/'orientation-design-v1/design-index.json').read_text());family=index['families'][0];v=json.loads((root/family['view']['path']).read_text());s=json.loads((root/family['bindings']['path']).read_text());materialize.check_sources(v,s);v['relations'][0]['proposalStatements'][0]='Shortened'
  with self.assertRaisesRegex(AssertionError,'paired statement'):materialize.check_sources(v,s)
 def test_dependency_receipt_hash_and_redispatch_guard(self):
  report=json.loads((B/'preflight.json').read_text());runtime=B.parent.parent/report['fixtureRuntime'];job='parent-orientation-00-challenge';prior='parent-orientation-00-proposal'
  with tempfile.TemporaryDirectory()as tmp:
   root=Path(tmp);d=root/'jobs'/job;d.mkdir(parents=True);shutil.copyfile(runtime/'jobs'/job/'request.json',d/'request.json');pd=root/'jobs'/prior;pd.mkdir()
   for name in ['receipt.json','reply.json','packet.actual.json']:shutil.copyfile(runtime/'jobs'/prior/name,pd/name)
   receipt=json.loads((pd/'receipt.json').read_text());receipt['normalizedReplySha256']='0'*64;materialize.dump(pd/'receipt.json',receipt)
   with self.assertRaisesRegex(AssertionError,'receipt mismatch'):materialize.materialize(d/'request.json',root)
   (d/'dispatch-request.json').write_text('{}')
   with self.assertRaisesRegex(AssertionError,'no redispatch'):materialize.materialize(d/'request.json',root)
if __name__=='__main__':unittest.main()
