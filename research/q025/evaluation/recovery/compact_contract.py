"""Compact review contract: one unit mapping, typed immutable references, separate fine identity."""
import json
from pathlib import Path
B=Path(__file__).resolve().parent
S={'type':'string'};I={'type':'integer','minimum':0}
def en(*x):return {'type':'string','enum':list(x)}
def ar(x,**kw):return {'type':'array','items':x,**kw}
def ob(**x):return {'type':'object','properties':x,'required':list(x),'additionalProperties':False}
def st(n):return {'type':'string','maxLength':n}
A=ar(S);scope=ob(systems=A,targets=A,regimes=A,assumptions=A,conventions=A,includes=A,excludes=A)
card=ob(id=S,title=st(90),question=st(420),summary=st(650),scope=scope,methods=A,refs=A,readingLimit=st(400),aliases=A)
factor=ob(id=S,kind=en('system','framework','target','regime','method','assumption','convention'),label=st(140),status=en('scope_candidate','uncertain','historical_or_rejected'),qualification=st(240),refs=A)
row=ob(i=I,b=en('description','excerpt'),d=en('member','overlap','alternate','unresolved'),q=ar(ob(id=S,role=en('addresses','instantiates','specializes','method','boundary','comparison'))),f=A,refs=A,a=en('initial','same','changed','not_compared'),reason=en('central','specialized','distinct_target','method_bridge','application','scope_mismatch','changed_regime','weak_support','ambiguous','unresolved'),note=st(160),home=st(160),identity=S,title=st(90))
identitygroup=ob(id=S,representative=I,title=st(90),reason=st(360),definingDifferences=A,refs=A)
assessment=ob(id=S,decision=en('supported_as_written','supported_with_limits','revise','insufficient_evidence','not_evaluable'),scopeChange=en('same','broader','narrower','different','unclear'),replacement=S,note=st(420),refs=A)
link=ob(source=S,target=S,type=en('narrows','broadens','method','application','comparison','premise_check','related','source_context'),reason=st(240),refs=A)
identity=ob(left=S,right=S,decision=en('equivalent_candidate','distinct','unresolved'),reason=st(360),changedPremises=A,refs=A)
SCHEMA=ob(version={'type':'string','const':'q025-compact-review/1'},familyId=S,stage=en('proposal','challenge','fresh'),verdict=en('usable_with_limits','needs_revision','insufficient_evidence'),summary=st(1500),region=ob(title=st(90),question=st(420),summary=st(700),scope=scope,readingLimit=st(450)),cards=ar(card,maxItems=8),factors=ar(factor),units=ar(row),identityGroups=ar(identitygroup),cardReviews=ar(assessment),groupReviews=ar(assessment),links=ar(link,maxItems=64),identityComparisons=ar(identity,maxItems=24),limitations=A,unresolved=A)

def structure(x,s,path='$'):
 t=s['type'];ok={'object':isinstance(x,dict),'array':isinstance(x,list),'string':isinstance(x,str),'integer':isinstance(x,int) and not isinstance(x,bool)}[t];assert ok,f'{path}: wrong type'
 if 'const' in s:assert x==s['const'],f'{path}: const'
 if 'enum' in s:assert x in s['enum'],f'{path}: enum'
 if t=='object':
  assert set(x)==set(s['properties']),f'{path}: missing/extra fields'
  for k,v in x.items():structure(v,s['properties'][k],path+'.'+k)
 elif t=='array':
  assert len(x)<=s.get('maxItems',100000),f'{path}: too many items'
  for i,v in enumerate(x):structure(v,s['items'],f'{path}[{i}]')
 elif t=='string':assert len(x)<=s.get('maxLength',10**9),f'{path}: too long'
 elif t=='integer':assert x>=s.get('minimum',0),f'{path}: integer bound'

def validate(packet,r):
 structure(r,SCHEMA);assert r['familyId']==packet['familyId'] and r['stage']==packet['stage'],'wrong packet'
 units={u['i']:u for u in packet['units']};refs=packet['refRegistry'];prior={c['id'] for c in packet.get('priorCards',[])};existing={c['id'] for c in packet.get('existingCards',[])};pg={g['id'] for g in packet.get('priorGroups',[])}
 cards={c['id']:c for c in r['cards']};priorf={f['id']:f for f in packet.get('priorFactors',[])};newf={f['id']:f for f in r['factors']};assert not(set(priorf)&set(newf)),'factor ID overwrites prior definition';factors={**priorf,**newf};groups={g['id']:g for g in r['identityGroups']}
 assert len(cards)==len(r['cards']) and all(k.startswith('q') for k in cards),'bad/duplicate new card ID'
 assert len(newf)==len(r['factors']) and len(groups)==len(r['identityGroups']),'duplicate factor/group ID'
 assert all(k.startswith('i') for k in groups),'new fine group must use i-prefix'
 qids=set(cards)|prior|existing;scope_ids=qids|set(groups)|pg;source_ids={k for k,v in refs.items() if v['kind'] in ['source_unit','source_object']}
 def checkrefs(xs):assert len(xs)==len(set(xs)) and set(xs)<=set(refs),'duplicate or invented reference ID'
 def evidence_for_unit(xs,i):
  checkrefs(xs)
  for x in xs:
   ref=refs[x]
   if ref['kind']=='description':assert ref['unitIndex']==i,'description belongs to another unit'
 def checkassessments(items,required,optional):
  ids=[a['id'] for a in items];assert len(ids)==len(set(ids)) and required<=set(ids)<=required|optional,'missing/duplicate/unknown prior assessment'
  for a in items:
   checkrefs(a['refs']);assert a['replacement'] in scope_ids or a['replacement']=='','unknown replacement'
   if a['decision']=='supported_as_written':assert a['scopeChange']=='same' and a['refs'],'rewritten/unsupported scope called agreed'
 for c in cards.values():
  assert c['title'] and c['question'] and c['scope']['targets'],'empty scoped question';checkrefs(c['refs'])
 for f in factors.values():checkrefs(f['refs'])
 rows=r['units'];assert len(rows)==len(units) and {a['i'] for a in rows}==set(units),'missing/duplicate unit coverage'
 bygroup={}
 for a in rows:
  i=a['i'];evidence_for_unit(a['refs'],i);assert set(a['f'])<=set(factors),'unknown factor';assert len(a['f'])==len(set(a['f'])),'duplicate factor assignment'
  assert all(q['id'] in qids for q in a['q']),'source facet is not an authored overview card'
  assert len({(q['id'],q['role']) for q in a['q']})==len(a['q']),'duplicate unit/card contribution'
  if a['b']=='excerpt':assert set(a['refs'])&set(units[i]['primaryRefs']),'excerpt basis without own supplied primary source'
  if a['d'] in ['alternate','unresolved']:assert a['home'] or a['note'],'missing alternate home/explicit gap'
  assert a['identity'] in {'s','?'}|set(groups)|pg,'unknown fine identity group'
  if a['identity']=='?':assert a['note'],'unresolved identity needs explanation'
  if a['identity'] in groups:bygroup.setdefault(a['identity'],[]).append(i)
  if packet['stage']=='proposal':assert a['a']=='initial','proposal claims previous agreement'
 for gid,g in groups.items():
  assert len(bygroup.get(gid,[]))>=2 and g['representative'] in bygroup[gid],'fine equivalence group lacks two members/own representative'
  assert g['reason'] and g['title'],'unexplained group';checkrefs(g['refs'])
 checkassessments(r['cardReviews'],prior,existing);checkassessments(r['groupReviews'],pg,set())
 counts={}
 for link in r['links']:
  assert link['source'] in scope_ids|source_ids|{'r'} and link['target'] in scope_ids|source_ids|{'r'},'unknown link endpoint';checkrefs(link['refs']);counts[link['source']]=counts.get(link['source'],0)+1
 assert all(n<=15 for n in counts.values()),'more than15 directions from one destination'
 assert 1<=counts.get('r',0)<=15,'region needs1–15 useful directions'
 for x in r['identityComparisons']:
  assert x['left'] in scope_ids and x['right'] in scope_ids,'identity comparison uses source-facet ID';checkrefs(x['refs'])
  if x['decision']=='equivalent_candidate':assert not x['changedPremises'] and x['refs'],'changed-premise or unsupported equivalence'
 return {'valid':True,'unitCount':len(rows),'excerptCheckedCount':sum(x['b']=='excerpt' for x in rows),'fineSingletonCandidates':sum(x['identity']=='s' for x in rows),'unresolvedFineIdentities':sum(x['identity']=='?' for x in rows),'fineGroupCount':len(groups),'newOverviewCards':len(cards),'unknownRolesDerived':True,'reverseContributionsDerived':True,'historicalFactorsExcludedFromActivePremises':sum(f['status']=='historical_or_rejected' for f in factors.values())}

if __name__=='__main__':
 import sys
 if '--schema' in sys.argv:(B/'compact.schema.json').write_text(json.dumps(SCHEMA,indent=2)+'\n')
 else:
  p=json.load(sys.stdin)
  try:print(json.dumps(validate(p['packet'],p['reply'])))
  except (AssertionError,KeyError,TypeError,ValueError) as e:print(json.dumps({'valid':False,'error':str(e)}));sys.exit(1)
