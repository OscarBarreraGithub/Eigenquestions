"""Explicit initial/not-compared equivalence only when no prior unit review exists."""
import copy,hashlib,importlib.util,json,sys
from pathlib import Path
B=Path(__file__).resolve().parent;BASE=B.parent/'compact-v1/production_contract.py';spec=importlib.util.spec_from_file_location('q025_frozen_production_contract',BASE);base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
def evaluate(packet,reply):
 original=copy.deepcopy(reply);prepared=copy.deepcopy(reply);changes=[]
 if packet['stage']=='proposal' and not packet.get('priorAssignments'):
  for row in prepared.get('units',[]):
   if row.get('a')=='not_compared':changes.append({'unitIndex':row['i'],'field':'a','original':'not_compared','derived':'initial','basis':'Proposal has no prior unit-assignment records; neither value claims agreement.'});row['a']='initial'
 out=base.evaluate(packet,prepared);out['schemaVersion']='q025-compact-derived-review/2';out['rowAgreementTransforms']=changes
 if changes:out['baseNormalizerInputReplyValueSha256']=out['originalReplyValueSha256'];out['originalReplyValueSha256']=base.value_hash(original);out['status']='valid_derived_representation'
 return out
if __name__=='__main__':
 data=json.load(sys.stdin)
 try:print(json.dumps(evaluate(data['packet'],data['reply']),ensure_ascii=False,separators=(',',':')))
 except (AssertionError,KeyError,TypeError,ValueError) as e:print(json.dumps({'valid':False,'error':str(e)}));sys.exit(1)
