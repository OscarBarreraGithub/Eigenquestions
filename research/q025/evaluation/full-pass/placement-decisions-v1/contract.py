"""Bounded whole-source placement decisions; validation never admits science."""
import json, math, re, sys
S={'type':'string'}
def en(*xs): return {'type':'string','enum':list(xs)}
def ar(x): return {'type':'array','items':x}
def ob(**xs): return {'type':'object','properties':xs,'required':list(xs),'additionalProperties':False}
A=ar(S)
scope=ob(systems=A,targets=A,regimes=A,assumptions=A,conventions=A,includes=A,excludes=A)
proposed=ob(id=S,kind=en('question','region'),title=S,question=S,summary=S,scope=scope,methods=A,readingCoverage=S,refs=A,revisesRef=S)
home=ob(scopeRef=S,weight={'type':'number'},coverageReason=S)
coverage=ob(sourceSpan=S,scopeRefs=A,explanation=S)
oldreview=ob(reviewRef=S,stage=en('proposal','challenge'),verdict=en('retain','revise','insufficient_evidence'),reason=S,refs=A)
placement=ob(unitRef=S,status=en('existing_homes','new_scope_proposed','unresolved'),coverageMode=en('whole_question_per_home','explicit_compound_union','unresolved'),wholeTargetCoverage=en('complete','incomplete'),homes=ar(home),targetCoverage=ar(coverage),coverageReason=S,priorAssessments=ar(oldreview),missingPremises=A,reason=S,refs=A)
review=ob(ref=S,verdict=en('retain','revise','insufficient_evidence'),reason=S,refs=A)
SCHEMA=ob(version={'type':'string','const':'q025-placement-decision/1'},familyId=S,stage=en('proposal','challenge'),summary=S,placements=ar(placement),newScopes=ar(proposed),priorPlacementReviews=ar(review),priorScopeReviews=ar(review),limitations=A,unresolved=A)

def structure(x,s,path='$'):
 t=s['type'];ok={'object':isinstance(x,dict),'array':isinstance(x,list),'string':isinstance(x,str),'number':isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x)}[t]
 assert ok,f'{path}: wrong type'
 if 'const' in s: assert x==s['const'],f'{path}: const'
 if 'enum' in s: assert x in s['enum'],f'{path}: enum'
 if t=='object':
  assert set(x)==set(s['properties']),f'{path}: missing/extra fields'
  for k,v in x.items():structure(v,s['properties'][k],path+'.'+k)
 elif t=='array':
  for i,v in enumerate(x):structure(v,s['items'],f'{path}[{i}]')

def evaluate(packet,r):
 structure(r,SCHEMA)
 assert r['familyId']==packet['familyId'] and r['stage']==packet['stage'],'wrong packet/stage'
 units={x['ref']:x for x in packet['units']};existing={x['ref']:x for x in packet['scopes']}
 prior=packet.get('priorReview');prior_scopes={x['id']:x for x in (prior or {}).get('newScopes',[])}
 new={x['id']:x for x in r['newScopes']};rows={x['unitRef']:x for x in r['placements']}
 assert len(rows)==len(r['placements'])==len(units) and set(rows)==set(units),'missing/duplicate source decision'
 assert len(new)==len(r['newScopes']) and not(set(new)&(set(existing)|set(prior_scopes))),'new scope overwrites prior ID'
 assert all(re.fullmatch(r'n\d+',x) for x in new),'new definitions require fresh n* IDs'
 assert len(new)<=len(units),'more new scopes than source questions'
 all_scopes={**existing,**prior_scopes,**new};valid_refs=set(units)|set(existing)|set(packet['reviewNamespaces'])|set(prior_scopes)|set(new)
 def refs(xs,required=()):
  assert len(xs)==len(set(xs)) and set(xs)<=valid_refs,'unknown/duplicate current reference (old evidence is inherited context only)'
  assert set(required)<=set(xs),'missing source/context reference'
 def nonempty(x):assert isinstance(x,str) and x.strip(),'missing explanation'
 for s in new.values():
  for k in ['title','question','summary','readingCoverage']:nonempty(s[k])
  assert s['scope']['targets'],'new definition lacks a target'
  assert s['revisesRef']=='' or s['revisesRef'] in existing or s['revisesRef'] in prior_scopes,'unknown revision target'
  refs(s['refs']);assert set(s['refs'])&set(units),'new scope lacks supplied source anchor'
  signature=lambda x:tuple(json.dumps(x.get(k),sort_keys=True,ensure_ascii=False)for k in ['kind','title','question','summary','scope','methods'])
  assert all(signature(s)!=signature(old)for old in list(existing.values())+list(prior_scopes.values())), 'unchanged definition needs existing/prior ID, not a duplicate new ID'
 selected_new=set();resolved=0;compound=0
 for uref,row in rows.items():
  u=units[uref];refs(row['refs'],[uref]);nonempty(row['reason']);nonempty(row['coverageReason'])
  expected={(c['reviewRef'],stage) for c in u['priorContexts'] for stage in ['proposal','challenge']}
  got=[(x['reviewRef'],x['stage'])for x in row['priorAssessments']]
  assert len(got)==len(set(got)) and set(got)==expected,'missing/duplicate prior annotation assessment'
  for a in row['priorAssessments']:refs(a['refs'],[uref,a['reviewRef']]);nonempty(a['reason'])
  ids=[h['scopeRef']for h in row['homes']];assert len(ids)==len(set(ids)) and set(ids)<=set(all_scopes),'unknown/duplicate home'
  for h in row['homes']:assert h['weight']>0,'nonpositive membership weight';nonempty(h['coverageReason'])
  if row['status']=='unresolved':
   assert not ids and not row['targetCoverage'] and row['coverageMode']=='unresolved' and row['wholeTargetCoverage']=='incomplete','unresolved case carries proposed home mass'
   assert row['missingPremises'] or row['reason'],'unexplained unresolved source'
  else:
   resolved+=1
   assert ids and abs(sum(h['weight'] for h in row['homes'])-1)<1e-9,'home weights must normalize to1'
   assert row['wholeTargetCoverage']=='complete' and row['coverageMode']!='unresolved','incomplete coverage cannot allocate'
   assert not row['missingPremises'],'consequential missing premises must remain unresolved'
   assert row['targetCoverage'],'no explicit target coverage'
   covered=set()
   for c in row['targetCoverage']:
    nonempty(c['sourceSpan']);assert c['sourceSpan'] in u['description'],'coverage span is not exact source-description text'
    assert c['scopeRefs'] and len(c['scopeRefs'])==len(set(c['scopeRefs'])) and set(c['scopeRefs'])<=set(ids),'coverage uses unselected scope'
    covered.update(c['scopeRefs']);nonempty(c['explanation'])
   assert covered==set(ids),'home lacks coverage mapping'
   if row['coverageMode']=='explicit_compound_union':assert len(ids)>=2 and len(row['targetCoverage'])>=2,'compound union needs multiple targets and homes';compound+=1
   else:
    assert all(set(c['scopeRefs'])==set(ids) for c in row['targetCoverage']),'whole-question homes must each cover every mapped target'
   if row['status']=='existing_homes':assert set(ids)<=set(existing),'proposed definition called existing'
   else:assert set(ids)&(set(new)|set(prior_scopes)),'new-scope status lacks proposed scope'
   selected_new.update(set(ids)&set(new))
 assert selected_new==set(new),'unused new definition (do not add unrequested scope work)'
 def assessments(xs,expected):
  keys=[a['ref']for a in xs];assert len(keys)==len(set(keys)) and set(keys)==set(expected),'missing/duplicate previous-stage assessment'
  for a in xs:nonempty(a['reason']);refs(a['refs'],[a['ref']])
  return {a['ref']:a for a in xs}
 if r['stage']=='proposal':
  assert prior is None and not r['priorPlacementReviews'] and not r['priorScopeReviews'],'proposal invents previous stage'
 else:
  assert prior and prior['stage']=='proposal' and prior['familyId']==r['familyId'],'missing actual independent proposal'
  assessments(r['priorPlacementReviews'],units);sr=assessments(r['priorScopeReviews'],prior_scopes)
  prows={x['unitRef']:x for x in prior['placements']}
  for a in r['priorPlacementReviews']:
   if a['verdict']=='retain':
    for key in ['status','coverageMode','wholeTargetCoverage','homes','targetCoverage','missingPremises']:assert rows[a['ref']][key]==prows[a['ref']][key],'retained placement changed; use revise'
  selected_prior={h['scopeRef']for row in rows.values() for h in row['homes']} & set(prior_scopes)
  assert all(sr[x]['verdict']=='retain' for x in selected_prior),'selected previous definition was not retained'
  for x,a in sr.items():
   if a['verdict']=='revise':assert any(s['revisesRef']==x for s in new.values()) or x not in selected_prior,'revision must use fresh ID or remain unallocated'
 return {'status':'validated_placement_candidate_not_admitted','normalizedReview':r,'factorRenameMap':{},'validation':{'valid':True,'sourceCount':len(units),'resolvedCandidateCount':resolved,'unresolvedCount':len(units)-resolved,'compoundUnionCount':compound,'newScopeCount':len(new),'priorNewScopesRetained':len(prior_scopes),'primaryPagesRead':0,'scientificAdmission':False,'sourceSplits':0},'derivation':'No scientific row, definition, weight, or text normalized; prior new definitions retained exactly in packet.priorReview.'}

if __name__=='__main__':
 try:
  p=json.load(sys.stdin);print(json.dumps(evaluate(p['packet'],p['reply']),ensure_ascii=False))
 except (AssertionError,KeyError,TypeError,ValueError) as e:print(json.dumps({'valid':False,'error':str(e)}));sys.exit(1)
