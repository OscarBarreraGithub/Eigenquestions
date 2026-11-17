import copy,json,tempfile,unittest,shutil
from pathlib import Path
import contract,materialize
B=Path(__file__).resolve().parent;L=B.parent/'native-local/placement-tail-recovery-v1'
def fixture(n='0002'):
 req=json.loads((L/'jobs'/f'placement-tail-{n}-proposal'/'request.json').read_text());view=json.loads((B.parent.parent/req['originalPacketPath']).read_text());prefix=json.loads((B.parent.parent/req['prefixPath']).read_text());return {**view,'stage':'proposal','priorReview':None,'lockedCompletion':{'completeFields':prefix['topLevelPrefix']['completeFields'],'partialNewScopes':[prefix['partialFirstScope']['completeFields']],'prefixSha256':req['prefixSha256'],'originalStreamSha256':prefix['originalStreamSha256']}}
def tail(packet):return {'version':'q025-placement-tail/1','familyId':packet['familyId'],'stage':'proposal','scopeRevisionIntents':[{'id':s['id'],'revisesRef':None,'reason':'Synthetic preflight assumes no revised target; this is not a model or scientific decision.'}for s in packet['lockedCompletion']['partialNewScopes']],'priorPlacementReviews':[],'priorScopeReviews':[],'limitations':['Synthetic representation test only.'],'unresolved':['No scientific decision from this fixture.']}
class Tests(unittest.TestCase):
 def test_actual_complete_rows_and_scope_text_are_locked(self):
  for n,count in [('0002',32),('0007',30)]:
   p=fixture(n);before=copy.deepcopy(p);out=contract.evaluate(p,tail(p));r=out['normalizedReview'];self.assertEqual(r['placements'],p['lockedCompletion']['completeFields']['placements']);self.assertEqual(len(r['placements']),count);self.assertEqual({k:v for k,v in r['newScopes'][0].items()if k!='revisesRef'},p['lockedCompletion']['partialNewScopes'][0]);self.assertEqual(p,before)
 def test_tail_cannot_reemit_or_modify_placements_or_science(self):
  p=fixture();r=tail(p)
  for k,v in [('placements',[]),('newScopes',[]),('summary','Changed')]:
   bad=copy.deepcopy(r);bad[k]=v
   with self.assertRaisesRegex(AssertionError,'extra'):contract.evaluate(p,bad)
 def test_missing_or_duplicate_intent_rejected(self):
  p=fixture();r=tail(p)
  for values in [[],[r['scopeRevisionIntents'][0]]*2]:
   bad=copy.deepcopy(r);bad['scopeRevisionIntents']=values
   with self.assertRaisesRegex(AssertionError,'scope intent'):contract.evaluate(p,bad)
 def test_unknown_revision_target_not_guessed(self):
  p=fixture();r=tail(p);r['scopeRevisionIntents'][0]['revisesRef']='q9999'
  with self.assertRaisesRegex(AssertionError,'revision target'):contract.evaluate(p,r)
 def test_missing_scientific_field_cannot_be_filled_by_adapter(self):
  p=fixture();del p['lockedCompletion']['partialNewScopes'][0]['summary']
  with self.assertRaisesRegex(AssertionError,'scientific scope field'):contract.evaluate(p,tail(p))
 def test_proposal_prior_arrays_are_empty_not_assumed_agreement(self):
  p=fixture();r=tail(p);r['priorScopeReviews']=[{'ref':'n0','verdict':'retain','reason':'Invented prior.','refs':['n0']}]
  with self.assertRaisesRegex(AssertionError,'prior reviews'):contract.evaluate(p,r)
 def test_independent_challenge_must_assess_all_finished_rows_and_new_scope(self):
  p=fixture();prior=contract.evaluate(p,tail(p))['normalizedReview'];cp={k:v for k,v in p.items()if k!='lockedCompletion'};cp.update(stage='challenge',priorReview=prior);r=copy.deepcopy(prior);r['stage']='challenge';r['newScopes']=[];r['priorPlacementReviews']=[{'ref':u['ref'],'verdict':'retain','reason':'Synthetic independent fixture.','refs':[u['ref']]}for u in p['units']];r['priorScopeReviews']=[{'ref':'n0','verdict':'retain','reason':'Synthetic fixture.','refs':['n0']}];contract.evaluate(cp,r);r['priorPlacementReviews'].pop()
  with self.assertRaisesRegex(AssertionError,'assessment'):contract.evaluate(cp,r)
 def test_no_string_caps_or_scientific_output_budget_shadow(self):
  p=fixture();r=tail(p);r['limitations']=['Complete qualifier. '*10000];contract.evaluate(p,r);self.assertNotIn('maxLength',json.dumps(contract.TAIL_SCHEMA))
if __name__=='__main__':unittest.main()
