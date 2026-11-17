"""Explicit nullable no-revision marker; frozen scientific validator stays unchanged."""
import copy,importlib.util,json,sys,hashlib
from pathlib import Path
BASE=Path(__file__).resolve().parent.parent/'placement-continuation-v1/contract.py'
spec=importlib.util.spec_from_file_location('frozen_placement_contract',BASE);base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
SCHEMA=copy.deepcopy(base.SCHEMA)
SCHEMA['properties']['newScopes']['items']['properties']['revisesRef']={'type':['string','null']}
def evaluate(packet,reply):
 normalized=copy.deepcopy(reply);derivations=[]
 for i,scope in enumerate(normalized.get('newScopes',[])):
  if'revisesRef'not in scope or scope['revisesRef']is None:
   derivations.append({'kind':'new_scope_without_declared_revision_target','path':f'$.newScopes[{i}].revisesRef','rawRepresentation':'omitted'if'revisesRef'not in scope else'null','normalizedValue':'','doesNotInferRevisedTarget':True,'doesNotAssertScopeNoveltyOrAdmission':True});scope['revisesRef']=''
 result=base.evaluate(packet,normalized)
 result.update(representationDerivations=derivations,sourceScientificValidatorSha256=hashlib.sha256(BASE.read_bytes()).hexdigest(),derivation='Only omitted/null no-revision markers map to the prior empty marker; no scientific text, target, weight or source row changes. Every nonempty revised-target reference remains exact.')
 return result
if __name__=='__main__':
 try:
  x=json.load(sys.stdin);print(json.dumps(evaluate(x['packet'],x['reply']),ensure_ascii=False,separators=(',',':')))
 except (AssertionError,KeyError,TypeError,ValueError)as error:print(str(error),file=sys.stderr);sys.exit(1)
