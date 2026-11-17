"""Two missing-tail calls and two independent challenges; zero native launches."""
import json,os,shutil
from pathlib import Path
import contract
from materialize import read,dump,sha,verified_pin
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent;W=E.parents[2];L=F/'native-local/placement-tail-recovery-v1'
def pin(p):return {'path':os.path.relpath(p,E),'sha256':sha(p)}
def main():
 assert not(L/'state.json').exists();jobs=[];pins=[pin(F/'placement-continuation-v1/contract.py'),pin(F/'placement-continuation-v1/materialize.py')];audit=[]
 for n in ['0002','0007']:
  original=F/'native-local/placement-continuation-v1/jobs'/f'placement-continuation-{n}-proposal';r=read(original/'request.json');receipt=read(original/'receipt.json');assert receipt['status']=='failed';prefix=F/'native-local/placement-continuation-triage-v1'/original.name/'extracted-prefix.json';value=read(prefix);assert value['originalStreamSha256']==sha(original/'reply.stream.raw.txt')
  extra=[{'path':str((original/name).relative_to(W)),'sha256':sha(original/name)}for name in ['receipt.json','reply.stream.raw.txt','packet.actual.json']]+[{'path':str(prefix.relative_to(W)),'sha256':sha(prefix)}]
  for p in r['sourcePins']+extra:verified_pin(p);pins.append(pin(W/p['path']))
  for stage in ['proposal','challenge']:
   jid=f'placement-tail-{n}-{stage}';schema=L/(f'tail-schema.json'if stage=='proposal'else'placement-schema.json');dump(schema,contract.TAIL_SCHEMA if stage=='proposal'else contract.SCHEMA);pins.append(pin(schema));req={**r,'jobId':jid,'stage':stage,'dependsOn':f'placement-tail-{n}-proposal'if stage=='challenge'else None,'completion':stage=='proposal','schemaPath':str(schema.relative_to(E)),'schemaSha256':sha(schema),'sourcePins':r['sourcePins']+extra,'prefixPath':str(prefix.relative_to(E)),'prefixSha256':sha(prefix),'originalFailedJobPath':str(original.relative_to(E)),'maxOutputCharacters':120000};dump(L/'jobs'/jid/'request.json',req);jobs.append({'jobId':jid,'dependsOn':req['dependsOn'],'requestSha256':sha(L/'jobs'/jid/'request.json')})
  audit.append({'originalJobId':original.name,'originalFailureReceiptSha256':sha(original/'receipt.json'),'originalStreamSha256':sha(original/'reply.stream.raw.txt'),'lockedPlacementRows':len(value['topLevelPrefix']['completeFields']['placements']),'lockedNewScopeFields':list(value['partialFirstScope']['completeFields']),'missingScopeFields':['revisesRef'],'modelRereadsOfCompletedPlacementsRequested':False})
 dump(B/'locked-prefix-audit.json',{'cases':audit,'lockedPlacementRows':sum(a['lockedPlacementRows']for a in audit),'originalsChanged':False,'failedOriginalsAdopted':False,'nativeLaunches':0})
 c={'schemaVersion':'q025-placement-tail-campaign/1','jobs':jobs,'maxAuthorizedConcurrency':2,'publicPins':[pin(B/n)for n in ['prepare.py','materialize.py','contract.py','INSTRUCTIONS.md','TAIL-INSTRUCTIONS.md','locked-prefix-audit.json']],'immutableInputPins':list({p['path']:p for p in pins}.values()),'nativeLaunches':0};dump(L/'campaign.json',c);shutil.copyfile(F/'native-local/placement-continuation-v1/execution.json',L/'execution.json');dump(L/'control.json',{'enabled':False,'maxActive':2,'maxStartsPerMinute':6,'minStartIntervalMs':5000,'stopWhenComplete':True});dump(B/'manifest.json',{**c,'campaignSha256':sha(L/'campaign.json'),'runnerSha256':sha(B/'runner.mjs'),'nativeJobs':4});print(json.dumps({'jobs':4,'lockedRows':62,'nativeLaunches':0}))
if __name__=='__main__':main()
