"""Repartition only unstarted original jobs; no native call or original-state mutation."""
import json,shutil,os
from pathlib import Path
import contract
from materialize import read,dump,sha,verified_pin
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent;W=E.parents[2];L=F/'native-local/placement-successors-v1';OLD=F/'native-local/placement-continuation-v1'
def pin(p):return {'path':os.path.relpath(p,E),'sha256':sha(p)}
def main():
 assert not(L/'state.json').exists(),'preserve launched successor';state=read(OLD/'state.json');control=read(OLD/'control.json');assert not control['enabled']and not any(x['status']in ['launched','active']for x in state['jobs'].values()),'old pool must be stopped and drained'
 original=read(OLD/'campaign.json');pending={j['jobId']:j for j in original['jobs']if state['jobs'][j['jobId']]['status']=='pending'};assert len(pending)==140
 rename={old:'successor-'+old for old in pending};schema=L/'placement-schema.json';dump(schema,contract.SCHEMA);pins=[pin(schema),pin(F/'placement-continuation-v1/contract.py'),pin(F/'placement-continuation-v1/READY.json')];jobs=[];external={};verified={}
 for old,j in pending.items():
  directory=OLD/'jobs'/old;assert not(directory/'dispatch-request.json').exists(),'already dispatched original'
  req=read(directory/'request.json');assert sha(directory/'request.json')==j['requestSha256'];req.update(jobId=rename[old],schemaPath=str(schema.relative_to(E)),schemaSha256=sha(schema),replacesUnstartedRequest=pin(directory/'request.json'),originalJobId=old)
  if req['dependsOn']:
   dep=req['dependsOn']
   if dep in pending:req['dependsOn']=rename[dep]
   else:
    prior=OLD/'jobs'/dep;receipt=read(prior/'receipt.json');assert state['jobs'][dep]['status']=='complete'and receipt['status']=='complete','external proposal unavailable';req.update(dependsOn=None,priorJobPath=str(prior.relative_to(E)),priorReceiptSha256=sha(prior/'receipt.json'))
    for name in ['receipt.json','reply.json','packet.actual.json','normalization.json']:
     p=prior/name;pins.append(pin(p))
    external[dep]={'jobId':dep,'path':str(prior.relative_to(E)),'receiptSha256':sha(prior/'receipt.json'),'replySha256':sha(prior/'reply.json')}
  for p in req['sourcePins']:
   if p['path']in verified:assert verified[p['path']]==p['sha256']
   else:verified_pin(p);verified[p['path']]=p['sha256']
   pins.append(pin(W/p['path']))
  pins.append(pin(directory/'request.json'));dump(L/'jobs'/req['jobId']/'request.json',req);jobs.append({'jobId':req['jobId'],'dependsOn':req['dependsOn'],'requestSha256':sha(L/'jobs'/req['jobId']/'request.json')})
 partition={'schemaVersion':'q025-unstarted-successor-partition/1','originalStateSha256AtPreparation':sha(OLD/'state.json'),'originalControlSha256AtPreparation':sha(OLD/'control.json'),'originalStatuses':{k:v['status']for k,v in state['jobs'].items()},'successorJobs':len(jobs),'reusedExternalProposals':list(external.values()),'failedAndBlockedNotAdopted':[k for k,v in state['jobs'].items()if v['status']in ['failed','blocked']],'originalFilesChanged':False,'tailRecovery':'Separate placement-tail-recovery-v1; no failed task is silently marked complete.'};dump(B/'partition.json',partition)
 campaign={'schemaVersion':'q025-placement-successor-campaign/1','status':'prepared_not_launched','jobs':jobs,'maxAuthorizedConcurrency':32,'publicPins':[pin(B/n)for n in ['prepare.py','contract.py','materialize.py','INSTRUCTIONS.md','partition.json']],'immutableInputPins':list({p['path']:p for p in pins}.values()),'nativeLaunches':0,'originalRuntime':str(OLD.relative_to(E)),'scope':'140 never-started original tasks only;6 completed proposals reused,2 failed proposals and their2 challenges remain separate recovery.'}
 dump(L/'campaign.json',campaign);shutil.copyfile(OLD/'execution.json',L/'execution.json');dump(L/'control.json',{'enabled':False,'maxActive':8,'maxStartsPerMinute':6,'minStartIntervalMs':5000,'stopWhenComplete':True})
 dump(B/'manifest.json',{**campaign,'campaignSha256':sha(L/'campaign.json'),'runnerSha256':sha(B/'runner.mjs'),'nativeJobs':len(jobs),'launchGate':'Root only; original pool must remain paused. No automatic redispatch.'});dump(B/'source-audit.json',{'verifiedSourceAndHistoryFiles':len(verified),'requests':len(jobs),'externalCompletedProposals':len(external),'nativeLaunches':0,'noFailedAdoptions':True});print(json.dumps({'jobs':len(jobs),'external':len(external),'verifiedFiles':len(verified)}))
if __name__=='__main__':main()
