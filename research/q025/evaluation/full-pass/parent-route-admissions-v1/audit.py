"""Compare full original parent route statements; endpoint co-presence is not a verdict."""
import collections,hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent;W=E.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();inp=F/'reconciliation-v1/parent-navigation-candidates-v6-20261117T144302Z.json';alllinks=json.loads(inp.read_text())['links'];basepaths=[F/'admissions-v5/supported-scope-role-component-v5.json',F/'canonical-pilot-admissions-v1/admitted-scope-role-operation-component.json',F/'organization-placement-v1/kk-uhecr-admitted-rehearsal-component.json',F/'navigation-admissions-v1/inflation-component.json',F/'navigation-admissions-v1/amplitude-component.json'];scopes={d['id']:d for path in basepaths for d in json.loads(path.read_text())['destinations']};cache={};rows=[]
def packet(pin):
 d=E/pin['artifactDirectory'];p=d/pin['packetFile'];assert sha(p)==pin[pin['packetFile']+'Sha256'];return cache.setdefault(str(p),json.loads(p.read_text()))
def evidence(p,ref):
 m=p['refRegistry'].get(ref)
 if not m:return {'unresolvedOriginalRef':ref}
 # Keep exact metadata in sidecar; compare canonical source IDs and content
 # locators rather than local spelling. No source condition is inferred.
 keys=['kind','unitId','paperId','sourceId','nodeId','textSha256','sourceSha256','sourceContext','candidateId','recordId','objectId','relationId'];return {k:m[k]for k in keys if k in m}
def esig(p,refs):return sorted(json.dumps(evidence(p,x),sort_keys=True,ensure_ascii=False)for x in refs)
for link in alllinks:
 src=link['source'];dst=link['target'];s=src.get('candidateId');t=dst.get('candidateId');ch=link['challengeLink'];pri=link['sameEndpointTypePriorLinks'];class_=''
 if src['kind']!='scientific_scope'or dst['kind']!='scientific_scope':class_='provenance_or_source_object_endpoint'
 elif s not in scopes or t not in scopes:class_='endpoint_scope_not_admitted'
 elif not pri:class_='new_or_changed_endpoint_type'
 pp=packet(link['reviewPins']['proposal']);cp=packet(link['reviewPins']['challenge']);comparisons=[]
 for x in pri:
  old=x['link'];comparisons.append({'priorIndex':x['index'],'reasonExact':old['reason']==ch['reason'],'referenceMetadataExact':esig(pp,old['refs'])==esig(cp,ch['refs']),'priorReason':old['reason'],'challengeReason':ch['reason'],'priorRefs':[{'ref':a,**evidence(pp,a)}for a in old['refs']],'challengeRefs':[{'ref':a,**evidence(cp,a)}for a in ch['refs']]})
 if not class_:
  if any(x['reasonExact']and x['referenceMetadataExact']for x in comparisons):class_='exact_statement_and_reference_metadata_reasserted'
  elif any(x['reasonExact']for x in comparisons):class_='same_statement_evidence_changed_or_referenced_differently'
  else:class_='independent_reworded_statement_requires_condition_comparison'
 rows.append({'id':link['id'],'sourceId':s,'targetId':t,'sourceKind':src['kind'],'targetKind':dst['kind'],'sourceTitle':scopes.get(s,{}).get('title'),'targetTitle':scopes.get(t,{}).get('title'),'nativeType':ch['type'],'class':class_,'comparisons':comparisons,'currentReason':ch['reason'],'currentRefs':ch['refs'],'originalCandidate':link,'newerExplicitLinkReviewFieldPresent':False,'scientificAdmission':False})
report={'schemaVersion':'q025-parent-route-agreement-audit/1','input':{'path':str(inp.relative_to(W)),'sha256':sha(inp)},'total':len(rows),'classes':dict(collections.Counter(x['class']for x in rows)),'byType':{c:dict(collections.Counter(x['nativeType']for x in rows if x['class']==c))for c in sorted({x['class']for x in rows})},'originalContract':'Separate source-only parent challenge reauthors a final links list and its own rationale/evidence under explicit target/method/application instructions; it has explicit per-card reviews but no per-link verdict field. Re-authored complete reasoning is evidence of independent assessment; mere shared endpoint/type is insufficient.','admission':False};out=F/'native-local/parent-route-admissions-v1';out.mkdir(exist_ok=True);full=out/'route-audit.json';full.write_text(json.dumps({'report':report,'rows':rows},ensure_ascii=False,separators=(',',':'))+'\n');report['privateRows']={'path':str(full.relative_to(W)),'sha256':sha(full),'bytes':full.stat().st_size};(B/'audit-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
