"""Canonical scoped-question review, distinct from source-statement equivalence."""
import copy,hashlib,json,sys
from pathlib import Path
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B.parent.parent/'recovery'));from compact_contract import structure,ob,ar,en,S,A,scope
question=ob(id=S,kind=en('question','region'),title=S,question=S,summary=S,scope=scope,methods=A,readingLimit=S,refs=A)
decision=ob(id=S,operation=en('same_scoped_question','common_target','specializes','shared_parent_distinct','method_bridge','comparison','different','unresolved'),members=A,target=S,definingDifferences=A,reason=S,refs=A)
SCHEMA=ob(version={'type':'string','const':'q025-canonical-review/1'},familyId=S,stage=en('proposal','challenge'),summary=S,newQuestions=ar(question),decisions=ar(decision),pairConstraints=ar(ob(left=S,right=S,relation=en('same_scoped_question','specializes_left','specializes_right','different','changed_scope','overlap','unresolved'),reason=S,refs=A)),scopeDispositions=ar(ob(ref=S,resolution=en('retained','reused','specialized','common_target','unresolved'),decisionIds=A,reason=S,refs=A)),sourceContributions=ar(ob(unitRef=S,questionRef=S,role=en('addresses','instantiates','specializes','method','boundary','comparison'),reason=S,refs=A)),compoundSources=ar(ob(unitRef=S,questionRefs=A,reason=S,refs=A)),priorReviews=ar(ob(ref=S,kind=en('decision','new_question'),verdict=en('supported_as_written','revise','insufficient_evidence'),reason=S,refs=A)),limitations=A,unresolved=A)
def vh(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def evaluate(packet,r):
 structure(r,SCHEMA);assert r['familyId']==packet['familyId'] and r['stage']==packet['stage'],'Wrong packet'
 scopes={x['ref']:x for x in packet['scopes']};refs=packet['refRegistry'];prior=packet.get('priorReview');oldq={q['id']:q for q in prior['newQuestions']} if prior else {};newq={q['id']:q for q in r['newQuestions']};ds={d['id']:d for d in r['decisions']};assert len(newq)==len(r['newQuestions']) and len(ds)==len(r['decisions']),'Duplicate generated IDs';assert not set(oldq)&set(newq),'Changed/redeclared prior question must use new ID';known=set(scopes)|set(newq)|set(oldq)
 qprefix,dprefix=('pq','pd') if r['stage']=='proposal' else ('cq','cd');assert all(x.startswith(qprefix) for x in newq) and all(x.startswith(dprefix) for x in ds),'Use explicit stage namespaces'
 def checkrefs(xs):assert len(xs)==len(set(xs)) and set(xs)<=set(refs),'Invented/duplicate evidence reference'
 for q in newq.values():assert q['question'] and q['scope']['targets'] and q['refs'],'Empty/unsupported scope';checkrefs(q['refs'])
 for d in ds.values():
  assert len(d['members'])>=2 and len(set(d['members']))==len(d['members']) and set(d['members'])<=known,'Decision needs distinct known scope members';assert d['target']=='' or d['target'] in known,'Unknown decision target';assert d['reason'] and d['refs'],'Unexplained decision';checkrefs(d['refs'])
  if d['operation']=='same_scoped_question':assert not d['definingDifferences'] and d['target'] in d['members'],'Scope equivalence cannot hide changed defining premises'
  if d['operation']=='specializes':assert len(d['members'])==2 and d['target']==d['members'][1] and d['definingDifferences'],'Specialization is ordered narrow→broad with explicit difference'
  if d['operation'] in ['common_target','shared_parent_distinct']:assert d['target'],'Common target needs an authored existing/new scope'
 constraints={}
 for pair in r['pairConstraints']:
  assert pair['left'] in known and pair['right'] in known and pair['left']!=pair['right'],'Unknown pair constraint';key=tuple(sorted([pair['left'],pair['right']]));assert key not in constraints,'Duplicate pair constraint';constraints[key]=pair;checkrefs(pair['refs']);assert pair['reason'] and pair['refs']
 for d in ds.values():
  if d['operation']=='same_scoped_question':
   for i,left in enumerate(d['members']):
    for right in d['members'][i+1:]:assert constraints.get(tuple(sorted([left,right])),{}).get('relation')=='same_scoped_question','Equivalence group lacks complete pair constraints'
 rows=r['scopeDispositions'];assert len(rows)==len(scopes) and {x['ref'] for x in rows}==set(scopes),'Incomplete authored-scope coverage'
 for row in rows:
  checkrefs(row['refs']);assert row['reason'];assert set(row['decisionIds'])<=set(ds),'Unknown decision'
  if row['resolution'] in ['reused','specialized','common_target']:assert row['decisionIds'],'Positive disposition needs exact decision'
  assert all(row['ref'] in ds[x]['members'] or ds[x]['target']==row['ref'] for x in row['decisionIds']),'Unrelated scope disposition'
 for c in r['sourceContributions']:
  assert c['unitRef'] in refs and refs[c['unitRef']]['kind']=='description','Contribution needs exact immutable source unit';assert c['questionRef'] in known,'Unknown contribution question';checkrefs(c['refs']);assert c['refs'] and c['reason']
 for c in r['compoundSources']:
  assert c['unitRef'] in refs and refs[c['unitRef']]['kind']=='description';assert len(set(c['questionRefs']))>=2 and set(c['questionRefs'])<=known,'Compound source needs distinct scoped targets';checkrefs(c['refs'])
 expected={d['id']:'decision' for d in prior['decisions']} if prior else {};expected.update({q['id']:'new_question' for q in oldq.values()});assert len(r['priorReviews'])==len(expected) and {a['ref'] for a in r['priorReviews']}==set(expected),'Missing/duplicate prior independent assessments'
 for a in r['priorReviews']:assert a['kind']==expected[a['ref']];checkrefs(a['refs']);assert a['reason'] and a['refs']
 return {'schemaVersion':'q025-canonical-derived-review/1','status':'valid_original_representation','originalReplyValueSha256':vh(r),'normalizedReplyValueSha256':vh(r),'normalizedReview':copy.deepcopy(r),'factorRenameMap':{},'rowAgreementTransforms':[],'crossUnitDescriptionContext':[],'validation':{'valid':True,'scopeCount':len(rows),'decisionCount':len(ds),'newQuestionCount':len(newq)},'semanticRepairPerformed':False,'acceptance':'Format validation admits no destination equivalence, common target, source contribution or scientific truth. Exact independently agreed decisions and final scope hashes are required.'}
if __name__=='__main__':
 if '--schema' in sys.argv:print(json.dumps(SCHEMA,indent=2));sys.exit(0)
 data=json.load(sys.stdin)
 try:print(json.dumps(evaluate(data['packet'],data['reply']),ensure_ascii=False,separators=(',',':')))
 except (AssertionError,KeyError,TypeError,ValueError) as e:print(json.dumps({'valid':False,'error':str(e)}));sys.exit(1)
