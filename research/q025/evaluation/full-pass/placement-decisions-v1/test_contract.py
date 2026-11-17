import copy,json,tempfile,unittest,shutil
from pathlib import Path
import contract,materialize
B=Path(__file__).resolve().parent

def packet():
 return {'familyId':'test-placement','stage':'proposal','units':[{'ref':'u0','paperId':'test','description':'Compute production and late decay under a fixed mass regime.','priorContexts':[{'reviewRef':'r0'}]}],'scopes':[{'ref':'q0'},{'ref':'q1'}],'reviewNamespaces':{'r0':'old-review'},'priorReview':None}
def unresolved(p):
 return {'version':'q025-placement-decision/1','familyId':p['familyId'],'stage':p['stage'],'summary':'Synthetic contract fixture, no scientific result.','placements':[{'unitRef':u['ref'],'status':'unresolved','coverageMode':'unresolved','wholeTargetCoverage':'incomplete','homes':[],'targetCoverage':[],'coverageReason':'The fixture leaves source coverage unresolved.','priorAssessments':[{'reviewRef':c['reviewRef'],'stage':s,'verdict':'insufficient_evidence','reason':'Synthetic structural fixture.','refs':[u['ref'],c['reviewRef']]}for c in u['priorContexts']for s in ['proposal','challenge']],'missingPremises':['Synthetic missing premise.'],'reason':'No home claimed.','refs':[u['ref']]}for u in p['units']],'newScopes':[],'priorPlacementReviews':[],'priorScopeReviews':[],'limitations':['No scientific admission.'],'unresolved':['Fixture only.']}
def whole(p):
 r=unresolved(p);row=r['placements'][0];row.update(status='existing_homes',coverageMode='whole_question_per_home',wholeTargetCoverage='complete',homes=[{'scopeRef':'q0','weight':1,'coverageReason':'Covers both stated targets under the given regime.'}],targetCoverage=[{'sourceSpan':p['units'][0]['description'],'scopeRefs':['q0'],'explanation':'One composite scope covers the complete question.'}],missingPremises=[],refs=['u0','q0']);return r

def new_scope(ident='n0'):
 return {'id':ident,'kind':'question','title':'Composite question','question':'What is the combined target?','summary':'Scoped description.','scope':{k:(['target']if k=='targets'else[])for k in ['systems','targets','regimes','assumptions','conventions','includes','excludes']},'methods':[],'readingCoverage':'Descriptions only.','refs':['u0'],'revisesRef':''}
class Tests(unittest.TestCase):
 def test_exact_rows_and_both_annotations(self):
  p=packet();r=unresolved(p);self.assertEqual(contract.evaluate(p,r)['validation']['sourceCount'],1)
  for mutate in [lambda x:x['placements'].clear(),lambda x:x['placements'].append(copy.deepcopy(x['placements'][0])),lambda x:x['placements'][0]['priorAssessments'].pop()]:
   x=copy.deepcopy(r);mutate(x)
   with self.assertRaises(AssertionError):contract.evaluate(p,x)
 def test_one_composite_question_is_sufficient(self):
  p=packet();r=whole(p);self.assertEqual(contract.evaluate(p,r)['validation']['resolvedCandidateCount'],1)
 def test_compound_union_is_explicit_complete_and_not_atomic_units(self):
  p=packet();r=whole(p);x=r['placements'][0];x['coverageMode']='explicit_compound_union';x['homes']=[{'scopeRef':'q0','weight':.4,'coverageReason':'Production branch.'},{'scopeRef':'q1','weight':.6,'coverageReason':'Decay branch.'}];x['targetCoverage']=[{'sourceSpan':'production','scopeRefs':['q0'],'explanation':'Production.'},{'sourceSpan':'late decay under a fixed mass regime','scopeRefs':['q1'],'explanation':'Decay under its stated regime.'}]
  self.assertEqual(contract.evaluate(p,r)['validation']['compoundUnionCount'],1)
  x['coverageMode']='whole_question_per_home'
  with self.assertRaisesRegex(AssertionError,'every mapped target'):contract.evaluate(p,r)
 def test_weights_refs_and_source_spans(self):
  p=packet();r=whole(p)
  for mutate in [lambda x:x['placements'][0]['homes'][0].update(weight=0),lambda x:x['placements'][0]['homes'][0].update(weight=.5),lambda x:x['placements'][0]['refs'].append('e0'),lambda x:x['placements'][0]['targetCoverage'][0].update(sourceSpan='invented premise'),lambda x:x['placements'][0]['missingPremises'].append('missing consequential premise')]:
   x=copy.deepcopy(r);mutate(x)
   with self.assertRaises(AssertionError):contract.evaluate(p,x)
 def test_unresolved_never_carries_mass(self):
  p=packet();r=unresolved(p);r['placements'][0]['homes']=[{'scopeRef':'q0','weight':1,'coverageReason':'Forced fallback.'}]
  with self.assertRaises(AssertionError):contract.evaluate(p,r)
 def test_challenge_carries_prior_definition_without_rewrite(self):
  p=packet();r=whole(p);s=new_scope();r['newScopes']=[s];row=r['placements'][0];row['status']='new_scope_proposed';row['homes'][0]['scopeRef']='n0';row['targetCoverage'][0]['scopeRefs']=['n0'];contract.evaluate(p,r)
  cp={**p,'stage':'challenge','priorReview':r};c=copy.deepcopy(r);c['stage']='challenge';c['newScopes']=[];c['priorPlacementReviews']=[{'ref':'u0','verdict':'retain','reason':'Independent coverage check.','refs':['u0']}];c['priorScopeReviews']=[{'ref':'n0','verdict':'retain','reason':'Unchanged complete scope.','refs':['n0','u0']}]
  self.assertEqual(contract.evaluate(cp,c)['validation']['priorNewScopesRetained'],1)
  c['newScopes']=[copy.deepcopy(s)]
  with self.assertRaisesRegex(AssertionError,'overwrites'):contract.evaluate(cp,c)
 def test_challenge_must_review_every_row_and_scope_and_not_restamp(self):
  p=packet();r=whole(p);cp={**p,'stage':'challenge','priorReview':r};c=copy.deepcopy(r);c['stage']='challenge'
  with self.assertRaises(AssertionError):contract.evaluate(cp,c)
  c['priorPlacementReviews']=[{'ref':'u0','verdict':'retain','reason':'Checked.','refs':['u0']}];c['placements'][0]['homes'][0]['scopeRef']='q1';c['placements'][0]['targetCoverage'][0]['scopeRefs']=['q1']
  with self.assertRaisesRegex(AssertionError,'retained placement changed'):contract.evaluate(cp,c)
 def test_no_per_string_caps(self):
  p=packet();r=unresolved(p);r['summary']='Long retained scientific qualification. '*5000;contract.evaluate(p,r)
  self.assertNotIn('maxLength',json.dumps(contract.SCHEMA))
 def test_source_projection_detects_annotation_loss(self):
  root=B.parents[4];delivery=json.loads((root/'research/q025/assembly/organization-residual-v1/placement-pilot-delivery.json').read_text());item=delivery['packets'][0];v=json.loads((root/item['view']['path']).read_text());s=json.loads((root/item['sidecar']['path']).read_text());materialize.check_sources(v,s);v['units'][0]['priorContexts'][0]['proposal']['note']='silently shortened'
  with self.assertRaisesRegex(AssertionError,'attribution'):materialize.check_sources(v,s)
 def test_duplicate_definition_under_fresh_id_rejected(self):
  p=packet();r=whole(p);s=new_scope();p['scopes'][0]={**s,'ref':'q0'};r['newScopes']=[s];r['placements'][0]['homes'][0]['scopeRef']='n0';r['placements'][0]['targetCoverage'][0]['scopeRefs']=['n0'];r['placements'][0]['status']='new_scope_proposed'
  with self.assertRaisesRegex(AssertionError,'duplicate new ID'):contract.evaluate(p,r)
 def test_dependent_actual_receipt_hash_is_required(self):
  report=json.loads((B/'preflight.json').read_text());runtime=B.parent.parent/report['fixtureRuntime'];job='placement-pilot-annotation-challenge';prior='placement-pilot-annotation-proposal'
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);d=root/'jobs'/job;d.mkdir(parents=True);shutil.copyfile(runtime/'jobs'/job/'request.json',d/'request.json');pd=root/'jobs'/prior;pd.mkdir()
   for name in ['receipt.json','reply.json','packet.actual.json']:shutil.copyfile(runtime/'jobs'/prior/name,pd/name)
   receipt=json.loads((pd/'receipt.json').read_text());receipt['normalizedReplySha256']='0'*64;materialize.dump(pd/'receipt.json',receipt)
   with self.assertRaisesRegex(AssertionError,'receipt mismatch'):materialize.materialize(d/'request.json',root)
 def test_materialized_request_cannot_redispatch(self):
  with tempfile.TemporaryDirectory() as tmp:
   d=Path(tmp);(d/'dispatch-request.json').write_text('{}')
   with self.assertRaisesRegex(AssertionError,'no redispatch'):materialize.materialize(d/'request.json',d)
 def test_wrong_schema_type_and_extra_admission(self):
  p=packet();r=whole(p);r['placements'][0]['homes'][0]['weight']=True
  with self.assertRaises(AssertionError):contract.evaluate(p,r)
  r=whole(p);r['admitted']=True
  with self.assertRaises(AssertionError):contract.evaluate(p,r)
if __name__=='__main__':unittest.main()
