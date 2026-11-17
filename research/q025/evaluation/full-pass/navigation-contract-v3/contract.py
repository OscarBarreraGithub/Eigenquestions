"""Current authored scope refs are logical context, never new primary evidence."""
import copy,hashlib,importlib.util,json,sys
from pathlib import Path
B=Path(__file__).resolve().parent;spec=importlib.util.spec_from_file_location('effective_navigation',B.parent/'navigation-wave-v2/contract.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base);SCHEMA=base.SCHEMA

def evaluate(packet,reply):
 p=copy.deepcopy(packet);registrations=[];generated={q['id']for q in reply.get('newQuestions',[])}
 for q in reply.get('newQuestions',[]):
  ref=q['id'];assert not(set(q['refs'])&generated),'An authored scope cannot use its own or another new definition as source evidence'
  signature=base.vh(q)
  if ref in p['refRegistry']:
   assert p['refRegistry'][ref].get('kind')=='prior_authored_scope'and p['refRegistry'][ref].get('objectValueSha256')==signature,'Generated scope collides with a different supplied evidence object'
  else:p['refRegistry'][ref]={'kind':'current_authored_scope_context','objectValueSha256':signature,'notPrimary':True,'notIndependentSourceEvidence':True};registrations.append({'ref':ref,**p['refRegistry'][ref]})
 result=base.evaluate(p,reply);result['schemaVersion']='q025-effective-navigation-review/3';result['currentAuthoredScopeContext']=registrations;result['scientificContentChanged']=False;result['acceptance']='Complete representation and exact context references only; new authored scopes are not independent source evidence. All separate scientific admission/global-group gates remain.';return result
if __name__=='__main__':
 if '--schema'in sys.argv:print(json.dumps(SCHEMA,indent=2));sys.exit()
 x=json.load(sys.stdin)
 try:print(json.dumps(evaluate(x['packet'],x['reply']),ensure_ascii=False,separators=(',',':')))
 except(AssertionError,KeyError,TypeError,ValueError)as e:print(json.dumps({'valid':False,'error':str(e)}));sys.exit(1)
