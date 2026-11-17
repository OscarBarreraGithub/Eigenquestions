"""One explicit judgment per exact proposed source role; no silent carry."""
import copy,hashlib,json,sys
from pathlib import Path
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B.parent.parent/'recovery'))
from compact_contract import structure,ob,ar,en,S,A
ROLES=['addresses','instantiates','specializes','method','boundary','comparison']
SCHEMA=ob(version={'type':'string','const':'q025-source-role-confirmation/1'},familyId=S,stage={'type':'string','const':'confirmation'},summary=S,rows=ar(ob(id=S,verdict=en('supported_as_written','supported_with_limits','revise_role','withhold'),basis=en('description_checked','source_excerpt_checked','insufficient'),revisedRole=en('unchanged',*ROLES),additionalQualifications=A,reason=S,refs=A)),limitations=A,unresolved=A)
def evaluate(p,r):
 structure(r,SCHEMA);assert r['familyId']==p['familyId'];rows={x['id']:x for x in p['rows']};assert len(r['rows'])==len(rows)and{x['id']for x in r['rows']}==set(rows),'Missing or duplicate exact-row coverage'
 known=set(p['refRegistry'])|{s['ref']for s in p['scopes']}|{n['ref']for n in p['pairedUnitContext']}
 units={u['ref']:u for u in p['units']}
 for a in r['rows']:
  original=rows[a['id']];assert a['reason']and a['refs']and len(a['refs'])==len(set(a['refs']))and set(a['refs'])<=known,'Invented/duplicate/missing evidence ref'
  assert original['unitRef']in a['refs']and original['questionRef']in a['refs'],'Own description and exact target must be explicit'
  if a['basis']=='source_excerpt_checked':assert any(p['refRegistry'].get(ref,{}).get('kind')=='primary'and p['refRegistry'][ref]['paperId']==units[original['unitRef']]['paperId']for ref in a['refs']),'Excerpt basis requires supplied own-paper primary text'
  if a['verdict']=='revise_role':assert a['revisedRole']!='unchanged'and a['revisedRole']!=original['role'],'Revision needs a genuinely changed role'
  else:assert a['revisedRole']=='unchanged','Only revise_role changes the exact role'
  if a['verdict']=='supported_with_limits':assert a['additionalQualifications'],'New restriction must be explicit'
  if a['verdict']=='supported_as_written':assert not a['additionalQualifications'],'Exact agreement cannot conceal a new restriction'
 return {'schemaVersion':'q025-source-role-confirmation-derived/1','status':'valid_original_representation','normalizedReview':copy.deepcopy(r),'factorRenameMap':{},'rowAgreementTransforms':[],'crossUnitDescriptionContext':[],'validation':{'valid':True,'exactRowCount':len(rows)},'sourceRoleAdmission':False,'scopeAdmission':False,'homeAdmission':False,'identityAdmission':False}
if __name__=='__main__':
 if '--schema'in sys.argv:print(json.dumps(SCHEMA,indent=2));sys.exit()
 x=json.load(sys.stdin)
 try:print(json.dumps(evaluate(x['packet'],x['reply']),ensure_ascii=False,separators=(',',':')))
 except(AssertionError,KeyError,ValueError,TypeError)as e:print(json.dumps({'valid':False,'error':str(e)}));sys.exit(1)
