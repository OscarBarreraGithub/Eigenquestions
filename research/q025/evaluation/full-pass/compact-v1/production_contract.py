"""Production compact contract with explicit, lossless reference namespace handling."""
import copy,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'recovery'))
from compact_contract import SCHEMA,structure,validate as validate_frozen

def value_hash(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,separators=(',',':'),sort_keys=True).encode()).hexdigest()
def evaluate(packet,reply):
 structure(reply,SCHEMA);assert len({f['id'] for f in reply['factors']})==len(reply['factors']),'duplicate output factor definitions';original=copy.deepcopy(reply);out=copy.deepcopy(reply);prior={f['id']:f for f in packet.get('priorFactors',[])};used={f['id'] for f in out['factors']}|set(prior);renames={};factors=[];changes=[]
 # Every output definition is retained either as a prior reuse or an explicit new candidate.
 for f in out['factors']:
  old=prior.get(f['id'])
  if old is None:factors.append(f);continue
  if value_hash(old)==value_hash(f):
   changes.append({'kind':'identical_prior_definition_reuse','originalId':f['id'],'definitionSha256':value_hash(f),'originalDefinition':old,'outputDefinition':f});continue
  new='f_revision_'+f['id'];suffix=0
  while new in used:suffix+=1;new='f_revision_'+f['id']+'_'+str(suffix)
  used.add(new);renames[f['id']]=new;changes.append({'kind':'redeclared_factor_new_candidate','originalId':f['id'],'derivedId':new,'originalDefinition':copy.deepcopy(old),'outputDefinition':copy.deepcopy(f),'oldDefinitionSha256':value_hash(old),'newDefinitionSha256':value_hash(f),'scientificStatus':'new_candidate_not_prior_agreement'});f['id']=new;factors.append(f)
 out['factors']=factors;contexts=[]
 for row in out['units']:
  row['f']=[renames.get(x,x) for x in row['f']]
  own=[]
  for ref in row['refs']:
   item=packet['refRegistry'].get(ref)
   if item and item['kind']=='description' and item['unitIndex']!=row['i']:
    contexts.append({'unitIndex':row['i'],'reference':ref,'referencedUnitIndex':item['unitIndex'],'referencedUnitId':item.get('unitId'),'basis':'other_unit_description_context','role':'comparison_or_context_not_own_source_evidence','sourceRefRecord':copy.deepcopy(item),'scientificImplicationInferred':False});continue
   own.append(ref)
  row['refs']=own
 result=validate_frozen(packet,out)
 # The original answer, all cross-unit refs and both versions of every changed definition survive.
 return {'schemaVersion':'q025-compact-derived-review/1','status':'valid_derived_representation' if changes or contexts else 'valid_original_representation','originalReplyValueSha256':value_hash(original),'normalizedReplyValueSha256':value_hash(out),'normalizedReview':out,'factorTransformations':changes,'factorRenameMap':renames,'crossUnitDescriptionContext':contexts,'validation':result,'semanticRepairPerformed':False,'acceptance':'Changed factor definitions remain new scientific candidates; no scope, placement or identity is admitted here.'}
def main():
 data=json.load(sys.stdin)
 try:print(json.dumps(evaluate(data['packet'],data['reply']),ensure_ascii=False,separators=(',',':')))
 except (AssertionError,KeyError,TypeError,ValueError) as e:print(json.dumps({'valid':False,'error':str(e)}));sys.exit(1)
if __name__=='__main__':main()
