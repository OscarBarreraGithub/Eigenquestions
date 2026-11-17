"""Already-authorized class continuation after exact twelve-scope admission."""
import collections,hashlib,json,re
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;W=F.parents[3]
def read(p):return json.loads(p.read_text())
def pin(p):return {'path':str(p.relative_to(W)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
scopepaths=[F/p for p in ['admissions-v5/supported-scope-role-component-v5.json','scope-gap-admissions-v1/component.json','parent-scope-admission-v2/component.json']];ds={d['id']:d for p in scopepaths for d in read(p)['destinations']};auditp=F/'native-local/parent-route-admissions-v1/route-audit.json';known={r['candidateId']for f in ['native-local/parent-route-admissions-v1/admitted-component.json','native-local/parent-route-admissions-v2/admitted-component.json']for r in read(F/f)['sourceObservationLedger']};selected=[];held=[];direction=[];safe=0
for r in read(auditp)['rows']:
 if r['class']!='endpoint_scope_not_admitted'or r['sourceId']not in ds or r['targetId']not in ds or not r['comparisons']:continue
 if r['nativeType']not in ['narrows','related','comparison']:direction.append(r);continue
 safe+=1;flags=[]
 if r['id']in known:flags.append('already_admitted_observation')
 for text in [r['currentReason']]+[x['priorReason']for x in r['comparisons']]:
  if re.search(r'\b(?:and|or|but|the|a|an|of|to|with|under|than|that|where|which|from|must|also|as|for|into|by|without)\s*$',text,re.I)or text.endswith((' ','-','–','—')):flags.append('possible_incomplete_clause')
  if re.search(r'provenance.only|provenance assessment|not a public|not public|review.batch provenance',text,re.I):flags.append('explicit_provenance_or_nonpublic_language')
 if not r['currentRefs']or not any(x['priorRefs']and x['priorReason'].strip()for x in r['comparisons']):flags.append('missing_independent_reason_or_evidence')
 if flags:held.append({'id':r['id'],'flags':sorted(set(flags))})
 else:selected.append(r)
assert safe==59 and len(selected)==53 and len(held)==6 and len(direction)==9
orientation={x for f in read(F/'orientation-design-v1/design-index.json')['families']for x in f['candidateIds']}
report={'sourceAudit':pin(auditp),'scopeInputs':[pin(p)for p in scopepaths],'sameClassDefinition':pin(F/'parent-route-admissions-v1/class-proposal.json'),'safeTypeObservationsBeforeDedup':safe,'newAdditiveObservations':len(selected),'types':dict(collections.Counter(x['nativeType']for x in selected)),'held':held,'directionSensitiveNotAdmitted':[{'id':r['id'],'type':r['nativeType'],'alreadyInFrozenOrientation':r['id']in orientation}for r in direction],'noNewModelCampaign':True}
out=F/'native-local/parent-route-admissions-v3/class-candidates.json';out.write_text(json.dumps({'report':report,'candidateRows':selected,'held':held,'optionalPendingDirections':direction},ensure_ascii=False,indent=2)+'\n');(B/'class-continuation.json').write_text(json.dumps({**report,'exactCandidateInventory':pin(out)},ensure_ascii=False,indent=2)+'\n');print(json.dumps(report))
