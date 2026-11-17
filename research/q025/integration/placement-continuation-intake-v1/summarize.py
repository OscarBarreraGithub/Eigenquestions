"""Read-only paired placement intake. Geometry remains the sole admission compiler."""
import collections,datetime,hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent;W=B.parents[3];E=W/'research/q025/evaluation';L=E/'full-pass/native-local'
def read(p):return json.loads(p.read_text())
def pin(p):return {'path':str(p.relative_to(W)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
def stage(d):
 receipt=read(d/'receipt.json');reply=read(d/'reply.json');packet=read(d/'packet.actual.json');normal=read(d/'normalization.json')
 assert receipt['status']=='complete' and receipt['sourceOnly'] and not receipt['toolUseAttempted']
 assert receipt['normalizedReplySha256']==pin(d/'reply.json')['sha256']
 assert receipt['normalizationReceiptSha256']==pin(d/'normalization.json')['sha256']
 assert normal['packetSha256']==pin(d/'packet.actual.json')['sha256']
 sidepath=W/packet['sidecar']['path'];assert pin(sidepath)['sha256']==packet['sidecar']['sha256'];side=read(sidepath)
 refs={u['ref']for u in side['units']};assert len(reply['placements'])==len(refs) and {r['unitRef']for r in reply['placements']}==refs
 return receipt,reply,packet,side,{'jobPath':str(d.relative_to(W)),'pins':[pin(d/n)for n in ['request.json','receipt.json','packet.actual.json','reply.json','reply.raw.txt','normalization.json']],'sourceSidecar':pin(sidepath),'placementCounts':dict(collections.Counter(r['status']for r in reply['placements'])),'coverageModeCounts':dict(collections.Counter(r['coverageMode']for r in reply['placements'])),'wholeTargetCoverageCounts':dict(collections.Counter(r['wholeTargetCoverage']for r in reply['placements'])),'priorPlacementJudgments':dict(collections.Counter(r['verdict']for r in reply['priorPlacementReviews'])),'priorScopeJudgments':dict(collections.Counter(r['verdict']for r in reply['priorScopeReviews'])),'newScopeCount':len(reply['newScopes']),'representationDerivations':normal.get('representationDerivations',[])}
def collect():
 families=[];states={};seen=set()
 for lane in ['placement-continuation-v1','placement-successors-v1','placement-tail-recovery-v1']:
  statepath=L/lane/'state.json'
  if not statepath.exists():continue
  state=read(statepath);states[lane]=dict(collections.Counter(v['status']for v in state['jobs'].values()))
  for job,info in state['jobs'].items():
   if info['status']!='complete' or not job.endswith('-challenge'):continue
   d=L/lane/'jobs'/job;req=read(d/'request.json');family=req['familyId'];assert family not in seen,'duplicate completed lineage: '+family
   if req.get('dependsOn'):prior=d.parent/req['dependsOn'];assert state['jobs'][req['dependsOn']]['status']=='complete'
   else:
    assert req.get('priorJobPath') and req.get('priorReceiptSha256'),'no explicit proposal dependency'
    prior=E/req['priorJobPath'];assert pin(prior/'receipt.json')['sha256']==req['priorReceiptSha256']
   pr,pp,pkt,side,ps=stage(prior);cr,cp,ct,cs,cc=stage(d)
   assert pp['familyId']==cp['familyId']==family and ct['priorReview']==pp
   assert pkt['sidecar']==ct['sidecar'];scopes={s['ref']:s for s in side['scopes']};units={u['ref']:u for u in side['units']}
   rows=[]
   for row in cp['placements']:
    rows.append({'unitId':units[row['unitRef']]['unitId'],'unitRef':row['unitRef'],'paperId':units[row['unitRef']]['paperId'],'status':row['status'],'coverageMode':row['coverageMode'],'wholeTargetCoverage':row['wholeTargetCoverage'],'homes':[{'scopeRef':h['scopeRef'],'destinationId':scopes[h['scopeRef']]['id']if h['scopeRef']in scopes else None,'scopeContentSha256':scopes[h['scopeRef']]['scopeContentSha256']if h['scopeRef']in scopes else None,'weight':h['weight'],'proposedScopeNamespace':None if h['scopeRef']in scopes else family}for h in row['homes']],'targetCoverageSpanCount':len(row['targetCoverage']),'missingPremiseCount':len(row['missingPremises']),'exactRecordPointer':'/placements/'+str(cp['placements'].index(row))})
   proposed=[{'stage':st,'id':r['id'],'revisesRef':r.get('revisesRef'),'definitionSha256':hashlib.sha256(json.dumps(r,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'exactReply':pin(path/'reply.json'),'pointer':'/newScopes/'+str(i),'globalInventoryLookupRequiredBeforeAdmission':True}for st,path,reply in [('proposal',prior,pp),('challenge',d,cp)]for i,r in enumerate(reply['newScopes'])]
   families.append({'familyId':family,'completedLineage':lane,'proposal':ps,'challenge':cc,'selectedPlacements':rows,'proposedDefinitions':proposed,'scientificAdmission':False});seen.add(family)
 return {'schemaVersion':'q025-placement-completed-pair-intake/1','observedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'states':states,'completedPairs':len(families),'sourceQuestions':sum(len(f['selectedPlacements'])for f in families),'families':families,'scientificAdmission':False,'limits':['Mechanical validated-pair inventory only; geometry owns placement compilation and evaluation/root review exceptions.','Existing targets are bound to the exact supplied sidecar scope hash, not silently upgraded to a later catalog.','New-scope definitions are exact reply pointers; global current-inventory lookup remains required, not claimed complete.','Every full rationale, coverage span, missing premise and inherited reading limit remains in the pinned normalized reply and packet.']}
if __name__=='__main__':
 result=collect();out=B/('intake-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'.json');out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'output':pin(out),'completedPairs':result['completedPairs'],'sourceQuestions':result['sourceQuestions'],'families':[{'familyId':f['familyId'],'priorPlacementJudgments':f['challenge']['priorPlacementJudgments'],'newDefinitions':len(f['proposedDefinitions'])}for f in result['families']]}))
