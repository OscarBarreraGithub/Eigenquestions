#!/usr/bin/env python3
"""Semantic envelope validator for planned q025 leaf reviews; independent of native execution."""
import json
from pathlib import Path
SCHEMA=json.loads((Path(__file__).parent/'output.schema.json').read_text())
def structural(x,s,path='$'):
 t=s.get('type');allowed=t if isinstance(t,list) else [t]
 ok=any({'object':isinstance(x,dict),'array':isinstance(x,list),'string':isinstance(x,str),'integer':isinstance(x,int) and not isinstance(x,bool),'boolean':isinstance(x,bool),'null':x is None}.get(z,False) for z in allowed)
 assert ok,f'{path}: wrong type'
 if 'const' in s:assert x==s['const'],f'{path}: wrong const'
 if 'enum' in s:assert x in s['enum'],f'{path}: bad enum'
 if isinstance(x,dict):
  assert all(k in x for k in s.get('required',[])),f'{path}: missing field'
  assert set(x)<=set(s['properties']),f'{path}: extra field'
  for k,v in x.items():structural(v,s['properties'][k],path+'.'+k)
 if isinstance(x,list):
  assert len(x)>=s.get('minItems',0) and len(x)<=s.get('maxItems',10**9),f'{path}: item count'
  for i,v in enumerate(x):structural(v,s['items'],f'{path}[{i}]')
 if isinstance(x,str):assert len(x)<=s.get('maxLength',10**9),f'{path}: string too long'
 if isinstance(x,int) and not isinstance(x,bool):assert x>=s.get('minimum',-10**9),f'{path}: below minimum'
def validate(packet,out):
 structural(out,SCHEMA)
 assert out['familyId']==packet['familyId'] and out['stage']==packet['stage'],'wrong packet identity'
 units={x['unitIndex']:x for x in packet['units']};assert len(units)==len(packet['units'])
 evidence={x['id']:x for x in packet['evidence']};relations={x['id']:x for x in packet.get('sourceRelations',[])}
 existing=set(packet.get('existingQuestionRefs',[]));cards={x['localId']:x for x in out['questionCards']}
 assert len(cards)==len(out['questionCards']),'duplicate card ID'
 qrefs=set(cards)|existing
 def check_q(q,allow_empty=False):assert q in qrefs or (allow_empty and q==''),f'unknown question {q}'
 def check_ev(ids,u=None):
  assert set(ids)<=set(evidence),'unsupported evidence ID'
  if u is not None:assert set(ids)<=set(units[u]['sourceEvidenceIds']),'evidence not attached to unit'
 def check_basis(x,u):
  if x['basis']=='source_excerpt_checked':assert x['evidenceIds'],'excerpt basis without evidence';check_ev(x['evidenceIds'],u)
  else:check_ev(x['evidenceIds'])
 def check_ref(r):
  kind,i=r['kind'],r['id'];start,end=r['start'],r['end']
  assert (start is None)==(end is None),'partial source span'
  if kind=='description':
   assert i.isdecimal() and int(i) in units,'unknown description';assert start is not None,'description factor needs literal offsets'
   text=units[int(i)]['description']
  elif kind=='source_anchor':assert i in evidence,'unsupported source anchor';text=evidence[i].get('text',evidence[i].get('sourceContext',{}).get('text',''))
  elif kind=='source_relation':assert i in relations,'unsupported source relation';text=relations[i].get('statement','')
  else:assert i in existing,'unsupported existing question';text=''
  if start is not None:assert 0<=start<end<=len(text),'invalid literal source span'
 factors={x['id']:x for x in out['factorDictionary']};assert len(factors)==len(out['factorDictionary']),'duplicate factor'
 for f in factors.values():
  assert set(f['supportingUnitIndices'])<=set(units),'factor refers to absent unit'
  for r in f['evidenceRefs']:check_ref(r)
  if f['status']=='supported_reading_proposal':assert f['evidenceRefs'],'supported factor without basis'
  if f['attachmentScope']=='direct_record_relation':
   rr=[relations[r['id']] for r in f['evidenceRefs'] if r['kind']=='source_relation'];assert rr,'direct relation label without relation'
   assert all(any(u in r.get('directUnitIndices',[]) for r in rr) for u in f['supportingUnitIndices']),'direct relation does not support these units'
  if f['attachmentScope']=='unknown':assert f['uncertainty'],'unknown attachment without uncertainty'
 assessments=out['unitAssessments'];assert len(assessments)==len(units) and {a['unitIndex'] for a in assessments}==set(units),'missing/duplicate unit assessment'
 for a in assessments:
  if packet['stage']=='proposal':assert a['priorAssignmentAgreement']=='first_proposal','proposal claims prior agreement'
  u=a['unitIndex'];check_basis(a,u)
  for q in a['questionRefs']:check_q(q)
  assert set(a['factorRefs'])<=set(factors),'unknown factor'
  assert all(u in factors[f]['supportingUnitIndices'] for f in a['factorRefs']),'factor not supported for this unit'
  assert all(factors[f]['status']!='unsupported' for f in a['factorRefs']),'unsupported factor assigned'
  known={factors[f]['kind'] for f in a['factorRefs']};assert known|set(a['unknownRoles'])=={'system','target','regime','method','assumption'},'unrecorded unknown roles'
  assert not known&set(a['unknownRoles']),'role both assigned and unknown'
  if a['disposition'] in ['exclude','unresolved']:assert a['alternateHome'].strip(),'missing alternate home or explicit gap'
 for c in cards.values():
  assert c['title'].strip() and c['question'].strip() and c['scope']['targets'],'empty question card'
  check_q(c['existingQuestionRef'],True);check_ev(c['evidenceIds'])
  for x in c['sourceContributions']:
   assert x['unitIndex'] in units,'unknown contribution unit';check_basis(x,x['unitIndex'])
  if c['scientificStatus']=='source_reviewed_proposal':assert c['evidenceIds'] and any(x['basis']=='source_excerpt_checked' for x in c['sourceContributions']),'source-reviewed card without source contribution'
  for d in c['nextDirections']:
   check_q(d['targetQuestionRef'],d['relationType']=='gap')
   for r in d['evidenceRefs']:check_ref(r)
 for d in out['regionCard']['directions']:
  check_q(d['targetQuestionRef'],d['relationType']=='gap')
  for r in d['evidenceRefs']:check_ref(r)
 prior=set(packet.get('priorQuestionRefs',[]));pa=out['priorCardAssessments']
 assert len(pa)==len(prior) and {a['priorQuestionRef'] for a in pa}==prior,'incomplete/duplicate prior-card assessment'
 for a in pa:
  assert set(a['agreedUnitIndices']+a['disputedUnitIndices'])<=set(units),'prior-card verdict refers to unprovided unit'
  for r in a['evidenceRefs']:check_ref(r)
  check_q(a['replacementQuestionRef'],True)
  if a['decision']=='supported_as_written':assert a['scopeAgreement']=='unchanged' and a['evidenceRefs'],'rewritten/unsupported card labeled agreed'
 for a in out['identityAssessments']:
  check_q(a['leftQuestionRef']);check_q(a['rightQuestionRef'])
  for r in a['evidenceRefs']:check_ref(r)
  if a['decision']=='alias_equivalent':assert a['evidenceRefs'] and not a['changedPremises'],'unsupported or changed-premise merge'
 for r in out['navigationRelations']:
  check_q(r['sourceQuestionRef']);check_q(r['targetQuestionRef'])
  for e in r['evidenceRefs']:check_ref(e)
 cov=out['coverage'];assert cov['providedDescriptionCount']==len(units)==cov['reviewedDescriptionCount'] and cov['allProvidedDescriptionsReviewed'],'false description coverage'
 assert cov['reservedUnreviewedCount']==packet['reservedUnreviewedCount'],'wrong heldout coverage'
 assert cov['sourceExcerptCheckedUnitCount']==sum(a['basis']=='source_excerpt_checked' for a in assessments),'wrong excerpt coverage'
 return {'valid':True,'units':len(units),'cards':len(cards),'factors':len(factors)}

if __name__=='__main__':
 import sys
 payload=json.load(sys.stdin)
 try:
  result=validate(payload['packet'],payload['reply']);print(json.dumps(result))
 except (AssertionError,KeyError,TypeError,ValueError) as e:
  print(json.dumps({'valid':False,'error':str(e)}));sys.exit(1)
