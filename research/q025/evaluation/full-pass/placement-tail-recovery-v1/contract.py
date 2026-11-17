"""Additive no-revision representation and locked-tail completion; original science validator unchanged."""
import copy,importlib.util,json,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent.parent/'placement-continuation-v1/contract.py'
spec=importlib.util.spec_from_file_location('frozen_placement_contract',BASE);base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
SCHEMA=copy.deepcopy(base.SCHEMA);SCHEMA['properties']['newScopes']['items']['properties']['revisesRef']={'type':['string','null']}
S={'type':'string'}
def ob(**x):return {'type':'object','properties':x,'required':list(x),'additionalProperties':False}
def ar(x):return {'type':'array','items':x}
TAIL_SCHEMA=ob(version={'type':'string','const':'q025-placement-tail/1'},familyId=S,stage={'type':'string','const':'proposal'},scopeRevisionIntents=ar(ob(id=S,revisesRef={'type':['string','null']},reason=S)),priorPlacementReviews={'type':'array','items':base.review,'maxItems':0},priorScopeReviews={'type':'array','items':base.review,'maxItems':0},limitations=ar(S),unresolved=ar(S))
def _tail_structure(value,schema,path='$'):
 types=schema['type']if isinstance(schema['type'],list)else[schema['type']]
 assert any({'object':isinstance(value,dict),'array':isinstance(value,list),'string':isinstance(value,str),'null':value is None}[t]for t in types),path+': wrong type'
 if'const'in schema:assert value==schema['const'],path+': const'
 if isinstance(value,dict):
  assert set(value)==set(schema['properties']),path+': missing/extra fields'
  for k,v in value.items():_tail_structure(v,schema['properties'][k],path+'.'+k)
 elif isinstance(value,list):
  if'maxItems'in schema:assert len(value)<=schema['maxItems'],path+': unexpected prior reviews'
  for i,v in enumerate(value):_tail_structure(v,schema['items'],f'{path}[{i}]')
def evaluate(packet,reply):
 transformations=[];raw=copy.deepcopy(reply);completion=packet.get('lockedCompletion')
 if completion is not None:
  _tail_structure(raw,TAIL_SCHEMA);assert raw['familyId']==packet['familyId']and packet['stage']==raw['stage']=='proposal','tail identity mismatch'
  expected={s['id']for s in completion['partialNewScopes']};intents={x['id']:x for x in raw['scopeRevisionIntents']};assert len(intents)==len(raw['scopeRevisionIntents'])and set(intents)==expected,'missing/duplicate locked scope intent'
  full=copy.deepcopy(completion['completeFields']);assert full['familyId']==packet['familyId']and full['stage']=='proposal'
  assert set(full)=={'version','familyId','stage','summary','placements'},'unexpected locked prefix fields'
  full['newScopes']=[]
  for original in completion['partialNewScopes']:
   assert set(original)==set(base.proposed['properties'])-{'revisesRef'},'missing scientific scope field cannot be inferred'
   intent=intents[original['id']];assert intent['reason'].strip(),'missing explicit revision-intent reason'
   full['newScopes'].append({**copy.deepcopy(original),'revisesRef':intent['revisesRef']})
  for key in ['priorPlacementReviews','priorScopeReviews','limitations','unresolved']:full[key]=copy.deepcopy(raw[key])
  transformations.append({'kind':'locked_complete_prefix_plus_missing_tail','lockedPlacementCount':len(full['placements']),'lockedNewScopeFieldsPreserved':True,'missingRevisionIntentExplicit':True,'prefixSha256':completion['prefixSha256'],'originalFailedStreamSha256':completion['originalStreamSha256'],'scientificAdmission':False})
 else:full=raw
 for i,s in enumerate(full.get('newScopes',[])):
  if'revisesRef'not in s or s['revisesRef']is None:
   transformations.append({'kind':'explicit_new_definition_without_revision_target','path':f'$.newScopes[{i}].revisesRef','rawRepresentation':'omitted'if'revisesRef'not in s else'null','normalizedValue':'','doesNotInferRevisedTarget':True,'doesNotAssertScopeNoveltyOrAdmission':True});s['revisesRef']=''
 science_packet={k:v for k,v in packet.items()if k!='lockedCompletion'}
 result=base.evaluate(science_packet,full)
 result.update(representationDerivations=transformations,sourceScientificValidatorSha256=__import__('hashlib').sha256(BASE.read_bytes()).hexdigest(),derivation='Only no-revision markers and an explicitly requested locked-tail completion are assembled; scientific strings, rows and original failures remain unchanged.')
 return result
if __name__=='__main__':
 try:
  x=json.load(sys.stdin);print(json.dumps(evaluate(x['packet'],x['reply']),ensure_ascii=False,separators=(',',':')))
 except (AssertionError,KeyError,TypeError,ValueError)as e:print(str(e),file=sys.stderr);sys.exit(1)
