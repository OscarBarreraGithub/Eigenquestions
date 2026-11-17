"""Exact orientation decisions on supplied endpoint pairs; never scientific admission."""
import copy,json,re,sys
S={'type':'string'}
def en(*xs):return {'type':'string','enum':list(xs)}
def ar(x):return {'type':'array','items':x}
def ob(**xs):return {'type':'object','properties':xs,'required':list(xs),'additionalProperties':False}
A=ar(S);TYPES=['narrower','method_for','application_of','premise_check','comparison','related_question']
decision=ob(id=S,originalRef=S,status=en('route','withheld'),source=S,target=S,type={'type':['string','null'],'enum':TYPES+[None]},title=S,rationale=S,qualification=S,missingPremise=S,refs=A)
review=ob(ref=S,verdict=en('supported_as_written','replace'),reason=S,refs=A)
SCHEMA=ob(version={'type':'string','const':'q025-orientation-decision/1'},familyId=S,stage=en('proposal','challenge'),summary=S,decisions=ar(decision),priorReviews=ar(review),limitations=A,unresolved=A)
def structure(x,s,path='$'):
 ts=s['type'] if isinstance(s['type'],list)else[s['type']]
 assert any({'object':isinstance(x,dict),'array':isinstance(x,list),'string':isinstance(x,str),'null':x is None}[t]for t in ts),path+': wrong type'
 if 'const'in s:assert x==s['const'],path+': const'
 if 'enum'in s:assert x in s['enum'],path+': enum'
 if isinstance(x,dict):
  assert set(x)==set(s['properties']),path+': missing/extra fields'
  for k,v in x.items():structure(v,s['properties'][k],path+'.'+k)
 elif isinstance(x,list):
  for i,v in enumerate(x):structure(v,s['items'],f'{path}[{i}]')
def evaluate(packet,r):
 structure(r,SCHEMA);assert r['familyId']==packet['familyId'] and r['stage']==packet['stage'],'wrong family/stage'
 originals={x['ref']:x for x in packet['relations']};scopes={x['ref']:x for x in packet['scopes']};valid=set(originals)|set(scopes)
 assert len(originals)==len(packet['relations']) and len(scopes)==len(packet['scopes']),'duplicate input IDs'
 def refs(xs,required=()):
  assert len(xs)==len(set(xs)) and set(xs)<=valid,'unknown/duplicate context refs; no supplied primary evidence'
  assert set(required)<=set(xs),'missing endpoint/original context refs'
 def nonempty(x):assert isinstance(x,str) and x.strip(),'missing complete explanation'
 def check(d):
  assert re.fullmatch(r'[a-z][A-Za-z0-9_-]*',d['id']) and d['id']not in valid,'invalid decision ID'
  assert d['originalRef']in originals,'unknown original route';old=originals[d['originalRef']]
  assert d['source']!=d['target'] and (d['source'],d['target'])in[(old['source'],old['target']),(old['target'],old['source'])],'changed endpoint pair'
  assert d['source']in scopes and d['target']in scopes,'endpoint absent'
  refs(d['refs'],[d['originalRef'],d['source'],d['target']]);nonempty(d['rationale'])
  if d['status']=='route':assert d['type']in TYPES and not d['missingPremise'],'route has withheld premise or invalid type';nonempty(d['title'])
  else:assert d['type']is None,'withheld record invents a scientific type';nonempty(d['missingPremise'])
 for d in r['decisions']:check(d)
 ids=[d['id']for d in r['decisions']];keys=[d['originalRef']for d in r['decisions']];assert len(ids)==len(set(ids))and len(keys)==len(set(keys)),'duplicate logical decision'
 prior=packet.get('priorReview');retained=[]
 if packet['stage']=='proposal':
  assert prior is None and not r['priorReviews'],'proposal has a prior'
  assert set(keys)==set(originals),'missing original relation decision'
 else:
  assert prior is not None,'challenge lacks prior';evaluate({**packet,'stage':'proposal','priorReview':None},prior)
  previous={d['id']:d for d in prior['decisions']};reviews={x['ref']:x for x in r['priorReviews']}
  assert len(reviews)==len(r['priorReviews'])and set(reviews)==set(previous),'missing/duplicate explicit prior review'
  assert not(set(ids)&set(previous)),'replacement must use fresh decision ID'
  replacements={d['originalRef']:d for d in r['decisions']};expected=set()
  for ident,old in previous.items():
   row=reviews[ident];refs(row['refs'],[old['originalRef'],old['source'],old['target']]);nonempty(row['reason'])
   if row['verdict']=='supported_as_written':retained.append(copy.deepcopy(old));assert old['originalRef']not in replacements,'supported row re-emitted or changed'
   else:expected.add(old['originalRef']);assert old['originalRef']in replacements,'replacement missing'
  assert set(replacements)==expected,'replacement not explicitly reviewed'
 effective=retained+copy.deepcopy(r['decisions']);assert {d['originalRef']for d in effective}==set(originals) and len(effective)==len(originals),'effective coverage gap'
 return {'status':'valid_representation_no_scientific_admission','normalizedReview':copy.deepcopy(r),'effectiveDecisions':effective,'retainedPriorDecisionIds':[d['id']for d in retained],'factorRenameMap':{},'validation':{'originalRelationCount':len(originals),'effectiveDecisionCount':len(effective),'retainedCount':len(retained),'newOrReplacementCount':len(r['decisions']),'routeCount':sum(d['status']=='route'for d in effective),'withheldCount':sum(d['status']=='withheld'for d in effective),'primaryPagesSupplied':0,'scientificAdmission':False}}
if __name__=='__main__':
 try:
  x=json.load(sys.stdin);print(json.dumps(evaluate(x['packet'],x['reply']),ensure_ascii=False,separators=(',',':')))
 except (AssertionError,KeyError,TypeError,ValueError)as e:print(str(e),file=sys.stderr);sys.exit(1)
