"""Small complete exception and unadmitted-scope intake; no inferred admission."""
import json,hashlib
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;W=F.parents[3]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def pin(p):return {'path':str(p.relative_to(W)),'sha256':sha(p)}
def read(p):return json.loads(p.read_text())
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
known={d['id']for file in [F/'admissions-v5/supported-scope-role-component-v5.json',F/'organization-placement-v1/kk-uhecr-admitted-rehearsal-component.json',F/'parent-scope-admission-v2/component.json']for d in read(file)['destinations']};missing={};exceptions=[]
for jd in sorted((F/'native-local/navigation-wave-v3/jobs').glob('*-challenge')):
 if not(jd/'receipt.json').exists()or read(jd/'receipt.json')['status']!='complete':continue
 p=read(jd/'packet.actual.json');r=read(jd/'reply.json');prior=p['priorReview'];bindings=p['machineBindings']['scopeBindings'];scopes={s['ref']:s for s in p['scopes']};units={u['ref']:u for u in p['units']};context={x['ref']:x for x in p['pairedUnitContext']}
 for ref,binding in bindings.items():
  cid=binding.get('admittedDestinationId')or binding['candidateId']
  if cid in known:continue
  row=missing.setdefault(cid,{'candidateId':cid,'fullScope':scopes[ref],'scopeBinding':binding,'currentReviewUses':[],'status':'not_admitted_merely_by_route_mention'})
  ops=[d for d in prior['decisions']if ref in d['members']];nav=[d for d in prior['navigation']if ref in[d['source'],d['target']]];ids={x['id']for x in ops+nav};row['currentReviewUses'].append({'family':p['familyId'],'localRef':ref,'packet':pin(jd/'packet.actual.json'),'challenge':pin(jd/'reply.json'),'proposedOperations':ops,'proposedNavigation':nav,'explicitCurrentAssessments':[a for k in ['priorReviews','navigationReviews']for a in r[k]if a['ref']in ids]})
 checks=[(kind,a)for kind in ['priorReviews','navigationReviews','sourceContributionReviews']for a in r[kind]if a['verdict']!='supported_as_written']
 if not checks:continue
 changed=[];needed=set()
 for kind,a in checks:
  if kind=='priorReviews':old=next(x for x in prior['newQuestions']+prior['decisions']if x['id']==a['ref'])
  elif kind=='navigationReviews':old=next(x for x in prior['navigation']if x['id']==a['ref'])
  else:old=prior['sourceContributions'][a['index']]
  changed.append({'kind':kind,'original':old,'independentJudgment':a});needed.update(old['refs']);needed.update(a['refs'])
 new={k:r[k]for k in ['newQuestions','decisions','navigation','sourceContributions']}
 for coll in new.values():
  for x in coll:needed.update(x['refs'])
 selectedcontexts=[context[x]for x in sorted(needed)if x in context];urefs={x for x in needed if x in units}|{x['unitRef']for x in selectedcontexts};srefs={x for x in needed if x in scopes}
 exceptions.append({'family':p['familyId'],'packet':pin(jd/'packet.actual.json'),'challenge':pin(jd/'reply.json'),'receipt':pin(jd/'receipt.json'),'changedOriginals':changed,'newChallengerObjects':new,'fullExistingScopes':[scopes[x]for x in sorted(srefs)],'allPriorNewDefinitions':prior['newQuestions'],'wholeSourceDescriptions':[units[x]for x in sorted(urefs)],'exactPairedAttributionNotes':selectedcontexts,'limitations':r['limitations'],'unresolved':r['unresolved'],'newPrimaryReading':False,'scientificAdmission':False})
out=F/'native-local/navigation-admissions-v3';out.mkdir(exist_ok=True);mp=out/'unadmitted-scopes.json';ep=out/'scientific-exceptions.json';dump(mp,{'schemaVersion':'q025-v3-existing-scope-admission-intake/1','scopes':list(missing.values()),'newRouteSupportIsNotScopeAdmission':True});dump(ep,{'schemaVersion':'q025-v3-bounded-scientific-exceptions/1','families':exceptions});report={'scopeIntake':pin(mp),'scopeCount':len(missing),'scopeBytes':mp.stat().st_size,'exceptionIntake':pin(ep),'exceptionFamilyCount':len(exceptions),'exceptionBytes':ep.stat().st_size,'missingScopes':[{'id':i,'title':r['fullScope']['definition']['title'],'priorAssessment':r['fullScope']['priorReadingAssessment']}for i,r in missing.items()]};dump(B/'exception-index.json',report);print(json.dumps({k:v for k,v in report.items()if k!='missingScopes'}))
