"""Small scoped-question decisions with explicit public-route semantics."""
import copy,importlib.util,json,sys
from pathlib import Path
B=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('canonical_base',B.parent/'canonical-v1/contract.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
from compact_contract import ob,ar,en,S,A,structure
SCHEMA=copy.deepcopy(base.SCHEMA)
extras={'navigation':ar(ob(id=S,source=S,target=S,type=en('narrower','premise_check','application_of','method_for','comparison','related_question'),title=S,qualification=S,reason=S,refs=A)),'navigationReviews':ar(ob(ref=S,verdict=en('supported_as_written','revise','insufficient_evidence'),reason=S,refs=A)),'sourceContributionReviews':ar(ob(index={'type':'integer'},verdict=en('supported_as_written','revise','insufficient_evidence'),reason=S,refs=A))}
SCHEMA['properties'].update(extras);SCHEMA['required']+=list(extras)
def evaluate(p,r):
 structure(r,SCHEMA);bare={k:v for k,v in r.items()if k not in extras};prior=p.get('priorReview');bp=copy.copy(p)
 if prior:bp['priorReview']={k:v for k,v in prior.items()if k not in extras}
 derived=base.evaluate(bp,bare);known={s['ref']for s in p['scopes']}|{q['id']for q in r['newQuestions']}|{q['id']for q in (prior or {}).get('newQuestions',[])};refs=set(p['refRegistry']);nav={x['id']:x for x in r['navigation']};assert len(nav)==len(r['navigation'])
 for link in nav.values():
  assert link['source']in known and link['target']in known and link['source']!=link['target'];assert link['title']and link['reason']and link['refs'];assert set(link['refs'])<=refs and len(link['refs'])==len(set(link['refs']))
 expected={x['id']for x in (prior or {}).get('navigation',[])};assert len(r['navigationReviews'])==len(expected)and{x['ref']for x in r['navigationReviews']}==expected,'Missing/duplicate independent route assessment'
 expected_roles=set(range(len((prior or {}).get('sourceContributions',[]))));assert len(r['sourceContributionReviews'])==len(expected_roles)and{x['index']for x in r['sourceContributionReviews']}==expected_roles,'Every newly proposed source role needs an explicit confirmation; no omission-as-agreement'
 for row in r['navigationReviews']+r['sourceContributionReviews']:assert row['reason']and row['refs']and set(row['refs'])<=refs
 pairs={tuple(sorted([x['left'],x['right']]))for x in r['pairConstraints']};assert all(tuple(sorted([x['left'],x['right']]))in pairs for x in p['nominations']),'Missing supplied comparison disposition'
 derived['normalizedReview']=copy.deepcopy(r);derived['originalReplyValueSha256']=base.vh(r);derived['normalizedReplyValueSha256']=base.vh(r);derived['validation']['navigationCount']=len(nav);derived['acceptance']='Exact proposal/challenge candidates only. Final scope/group conflict guards, explicit relationUse and source-role/placement receipts remain required.';return derived
if __name__=='__main__':
 if '--schema'in sys.argv:print(json.dumps(SCHEMA,indent=2));sys.exit()
 x=json.load(sys.stdin)
 try:print(json.dumps(evaluate(x['packet'],x['reply']),ensure_ascii=False,separators=(',',':')))
 except(AssertionError,KeyError,ValueError,TypeError)as e:print(json.dumps({'valid':False,'error':str(e)}));sys.exit(1)
