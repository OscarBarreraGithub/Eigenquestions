"""Prepare 32 bounded native requests without launching models."""
import os,shutil,json
from pathlib import Path
import contract
from materialize import sha,read,dump,verified_pin,source_pins,check_sources
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent;W=E.parents[2];L=F/'native-local/orientation-wave-v1'
MAX_OUTPUT_CHARACTERS=80000
D=F/'orientation-design-v1/design-index.json'
def pin(p):return {'path':os.path.relpath(p,E),'sha256':sha(p)}
def main():
 assert not(L/'state.json').exists(),'already launched';L.mkdir(parents=True,exist_ok=True)
 index=read(D);pins=[pin(D),pin(D.parent/'SCIENTIFIC-CONTRACT.md'),pin(D.parent/'prepare.py')];jobs=[];reports=[];seen=set();verified={}
 def verify(p):
  if p['path']in verified:assert verified[p['path']]==p['sha256']
  else:verified_pin(p);verified[p['path']]=p['sha256']
 schema=L/'orientation-schema.json';dump(schema,contract.SCHEMA);pins.append(pin(schema))
 for item in index['families']:
  view=read(verified_pin(item['view']));bindings=read(verified_pin(item['bindings']));report=check_sources(view,bindings)
  assert view['familyId']==item['id']and report['scopeCount']==item['scopeCount']and report['relationCount']==item['relationCount']
  ids={r['id']for r in bindings['relationBindings'].values()};assert ids==set(item['candidateIds'])and not(ids&seen),'duplicate/missing candidate';seen.update(ids)
  sp=[item['view'],item['bindings'],*source_pins(bindings)]
  for p in sp:verify(p);pins.append(pin(W/p['path']))
  for stage in ['proposal','challenge']:
   jid=item['id']+'-'+stage;dep=item['id']+'-proposal'if stage=='challenge'else None
   req={'schemaVersion':'q025-orientation-request/1','jobId':jid,'familyId':item['id'],'stage':stage,'kind':'orientation','dependsOn':dep,'childDependencies':[],'model':'gpt-6-astra','effort':'xhigh','sandbox':'read-only','sourceOnly':True,'timeoutSeconds':1800,'maxOutputCharacters':MAX_OUTPUT_CHARACTERS,'originalPacketPath':str((W/item['view']['path']).relative_to(E)),'originalPacketSha256':item['view']['sha256'],'bindings':item['bindings'],'schemaPath':str(schema.relative_to(E)),'schemaSha256':sha(schema),'sourcePins':sp,'relationCount':report['relationCount'],'primaryPagesSupplied':0,'scientificAdmission':False}
   dump(L/'jobs'/jid/'request.json',req);jobs.append({'jobId':jid,'dependsOn':dep,'requestSha256':sha(L/'jobs'/jid/'request.json')})
  reports.append({'familyId':item['id'],**report,'sourcePins':len(sp)})
 assert len(seen)==index['candidateCount']==491 and len(jobs)==32
 campaign={'schemaVersion':'q025-orientation-campaign/1','status':'prepared_not_launched','jobs':jobs,'maxAuthorizedConcurrency':16,'publicPins':[pin(B/x)for x in ['prepare.py','contract.py','materialize.py','INSTRUCTIONS.md']],'immutableInputPins':list({p['path']:p for p in pins}.values()),'nativeLaunches':0,'scope':'491 legacy route orientations, exact endpoint pairs; no automatic admission.'}
 dump(L/'campaign.json',campaign);shutil.copyfile(F/'native-local/placement-decisions-v1/execution.json',L/'execution.json');dump(L/'control.json',{'enabled':False,'maxActive':4,'maxStartsPerMinute':6,'minStartIntervalMs':5000,'stopWhenComplete':True})
 dump(B/'manifest.json',{**campaign,'campaignSha256':sha(L/'campaign.json'),'runnerSha256':sha(B/'runner.mjs'),'nativeJobs':len(jobs),'launchGate':'Root verifies READY, global concurrency and quota; no native start during preparation.'})
 dump(B/'source-audit.json',{'schemaVersion':'q025-orientation-source-audit/1','families':reports,'distinctOriginalRoutes':len(seen),'verifiedSourceAndHistoryFiles':len(verified),'primaryPagesSupplied':0,'nativeLaunches':0,'projections':'Complete endpoint definitions and both exact original statement collections checked against pinned sidecars and admitted components.'})
 print(json.dumps({'jobs':len(jobs),'routes':len(seen),'verifiedFiles':len(verified),'nativeLaunches':0}))
if __name__=='__main__':main()
