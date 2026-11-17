"""Prepare eight proposal/challenge requests; no native model calls."""
import json,os,shutil
from pathlib import Path
import contract
from materialize import sha,dump,read,verified_pin,check_sources,source_pins
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent;W=E.parents[2];L=F/'native-local/placement-decisions-v1'
MAX_OUTPUT_CHARACTERS=120000
DELIVERY=W/'research/q025/assembly/organization-residual-v1/placement-pilot-delivery.json'
def pin(p):return {'path':os.path.relpath(p,E),'sha256':sha(p)}
def main():
 assert not(L/'state.json').exists(),'Preserve launched runtime';L.mkdir(parents=True,exist_ok=True)
 delivery=read(DELIVERY);pins=[pin(DELIVERY)];jobs=[];reports=[];units=set();verified={}
 def verify(p):
  if p['path'] in verified:assert verified[p['path']]==p['sha256'],'conflicting source pins'
  else:verified_pin(p);verified[p['path']]=p['sha256']
 for p in [delivery['inputIndex'],delivery['script']]:verify(p);pins.append(pin(W/p['path']))
 schema=L/'placement-schema.json';dump(schema,contract.SCHEMA);pins.append(pin(schema))
 for item in delivery['packets']:
  for p in [item['view'],item['sidecar']]:verify(p)
  view=read(W/item['view']['path']);side=read(W/item['sidecar']['path']);report=check_sources(view,side)
  assert view['sidecar']==item['sidecar'] and report['sourceCount']==item['units'] and report['scopeCount']==item['scopes']
  ids={u['unitId'] for u in side['units']};assert not(ids&units),'repeated source across pilots';units.update(ids)
  sp=[item['view'],item['sidecar'],*source_pins(side)]
  for p in sp:verify(p);pins.append(pin(W/p['path']))
  for stage in ['proposal','challenge']:
   jobId=item['familyId']+'-'+stage;dep=item['familyId']+'-proposal' if stage=='challenge' else None
   req={'schemaVersion':'q025-placement-request/1','jobId':jobId,'familyId':item['familyId'],'stage':stage,'kind':'placement','dependsOn':dep,'childDependencies':[],'model':'gpt-6-astra','effort':'xhigh','sandbox':'read-only','sourceOnly':True,'timeoutSeconds':1800,'maxOutputCharacters':MAX_OUTPUT_CHARACTERS,'originalPacketPath':os.path.relpath(W/item['view']['path'],E),'originalPacketSha256':item['view']['sha256'],'schemaPath':str(schema.relative_to(E)),'schemaSha256':sha(schema),'sourcePins':sp,'sourceCount':report['sourceCount'],'primaryPagesSupplied':0,'scientificAdmission':False}
   dump(L/'jobs'/jobId/'request.json',req);jobs.append({'jobId':jobId,'dependsOn':dep,'requestSha256':sha(L/'jobs'/jobId/'request.json')})
  reports.append({'familyId':item['familyId'],**report,'scientificViewBytes':item['view']['bytes'],'sidecarBytes':item['sidecar']['bytes'],'sourcePins':len(sp)})
 public=[B/x for x in ['prepare.py','contract.py','materialize.py','INSTRUCTIONS.md']]
 campaign={'schemaVersion':'q025-placement-campaign/1','status':'prepared_not_launched','jobs':jobs,'maxAuthorizedConcurrency':4,'publicPins':[pin(p)for p in public],'immutableInputPins':list({p['path']:p for p in pins}.values()),'nativeLaunches':0,'scope':'87 complete source placement decisions, each independently challenged; no automatic scientific admission.'}
 dump(L/'campaign.json',campaign);shutil.copyfile(F/'native-local/screen-recovery-v1/execution.json',L/'execution.json');dump(L/'control.json',{'enabled':False,'maxActive':4,'maxStartsPerMinute':6,'minStartIntervalMs':5000,'stopWhenComplete':True})
 dump(B/'manifest.json',{**campaign,'campaignSha256':sha(L/'campaign.json'),'runnerSha256':sha(B/'runner.mjs'),'nativeJobs':len(jobs),'launchGate':'Root verifies READY pins and global concurrency. Preparation starts zero native tasks.'})
 dump(B/'source-audit.json',{'schemaVersion':'q025-placement-source-audit/1','families':reports,'distinctSources':len(units),'verifiedHistoricalAndSourceFiles':len(verified),'originalFilesChanged':False,'nativeLaunches':0,'primaryPagesSupplied':0,'descriptionAndOldAnnotationProjection':'Exact full text/object equality checked against pinned sidecars; every explicit historical packet/reply/raw/receipt/normalization pin verified.'})
 print(json.dumps({'jobs':len(jobs),'sources':len(units),'verifiedFiles':len(verified),'nativeLaunches':0}))
if __name__=='__main__':main()
