"""Prepare only the newly failed branches; never run native models or mutate v1."""
import copy,importlib.util,json,shutil,sys,time
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent;V1=F/'recovery-successors-v1';L=F/'native-local/recovery-successors-v2';N=F/'native-local'
import contract
from prefix import extract,assemble,value_hash
from materialize import verified_review
spec=importlib.util.spec_from_file_location('q025_v1_prepare_helpers',V1/'prepare.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
dump=old.dump;hfile=old.hfile;rel=old.relative

def main():
 assert not (L/'state.json').exists(),'Never overwrite a launched successor'
 L.mkdir(parents=True,exist_ok=True);source_root=Path(json.loads((N/'full-leaf-wave-v3/execution.json').read_text())['sourceRoot']);pins={};jobs=[];requests={}
 def remember(p):pins[rel(p)]={'path':rel(p),'sha256':hfile(p)}
 def remember_job(d):
  for name in ['request.json','receipt.json','packet.actual.json','packet.json','reply.raw.txt','reply.stream.raw.txt','normalization.json','reply.json','dispatch-request.json','prompt.actual.txt']:
   if (d/name).exists():remember(d/name)
 def common(r,j,kind,stage):return {**{k:v for k,v in r.items() if k in ['familyId','originalPacketPath','originalPacketSha256','fullMemberCount']},'schemaVersion':'q025-recovery-successor-request/1','jobId':j,'kind':kind,'stage':stage,'dependsOn':None,'model':'gpt-6-astra','effort':'xhigh','sandbox':'read-only','sourceOnly':True,'timeoutSeconds':1800,'maxOutputCharacters':120000,'childDependencies':[]}
 def emit(r,schema):
  p=L/'schemas'/(r['jobId']+'.json');dump(p,schema);r.update(schemaPath=rel(p),schemaSha256=hfile(p));remember(p);requests[r['jobId']]=r
 # Exact complete v1 response: only its three structural empty-array references
 # need typed artifact context. No source reading or scientific field is redone.
 failed=N/'recovery-successors-v1/jobs/successor-leaf-ce36cae0274019373c8a-proposal';receipt,r,packet_path,packet=old.original(failed,source_root);raw=(failed/'reply.raw.txt').read_bytes();assert hfile(failed/'reply.raw.txt')==receipt['replySha256'];reply=json.loads(raw)
 prefix=E/r['prefixPath'];assert hfile(prefix)==r['prefixSha256'];origin={'packetPath':rel(packet_path),'packetSha256':hfile(packet_path),'prefixPath':rel(prefix),'prefixSha256':hfile(prefix),'replyPath':rel(failed/'reply.raw.txt'),'replySha256':hfile(failed/'reply.raw.txt'),'compositeReviewValueSha256':value_hash(assemble(packet['preservedComponents'],reply['remaining']))}
 derived_packet,contexts=contract.structural_context(packet,reply,origin);start=time.perf_counter();normal=contract.evaluate(derived_packet,reply);duration=time.perf_counter()-start;assert len(normal['normalizedReview']['units'])==51
 target=L/'adopted'/failed.name;dump(target/'request.json',{**r,'executionMode':'deterministic_structural_context_only','originalJobPath':rel(failed)});(target/'reply.raw.txt').write_bytes(raw);dump(target/'packet.actual.json',derived_packet);dump(target/'reply.json',normal['normalizedReview']);normal.update(originalRawSha256=receipt['replySha256'],originalPacketSha256=hfile(packet_path),derivedPacketSha256=hfile(target/'packet.actual.json'),originalFailureReceiptSha256=hfile(failed/'receipt.json'));dump(target/'normalization.json',normal)
 derived={**{k:receipt[k] for k in ['jobId','model','effort','sourceOnly','sandbox','threadId','turnId']},'schemaVersion':'q025-derived-revalidation-receipt/1','status':'complete','origin':'deterministic_structural_context','nativeTurnStartedHere':False,'toolUseAttempted':False,'usage':None,'independence':'Same original source-only completion; no new reviewer or native turn. Independent challenge is still required.','originalNativeStatus':'failed','originalError':receipt['error'],'originalJobPath':rel(failed),'originalReceiptSha256':hfile(failed/'receipt.json'),'inputPins':{'packetSha256':hfile(target/'packet.actual.json'),'originalPacketSha256':hfile(packet_path)},'replySha256':hfile(target/'reply.raw.txt'),'normalizedReplySha256':hfile(target/'reply.json'),'normalizationReceiptSha256':hfile(target/'normalization.json'),'derivedUnitCount':51,'scientificAdmission':False};dump(target/'receipt.json',derived);remember_job(failed);remember_job(target);remember(prefix)
 j='successor2-leaf-ce36cae0274019373c8a-challenge';req=common(r,j,'leaf','challenge');req.update(priorJobPath=rel(target),priorReceiptSha256=hfile(target/'receipt.json'),prefixPath=rel(prefix),prefixSha256=hfile(prefix),originalFailedJobPath=rel(failed));emit(req,contract.regular_schema(True));replacement={r['familyId']:rel(L/'jobs'/j)}
 # One newly interrupted original leaf; preserve exact complete components.
 failed=N/'full-leaf-wave-v3/jobs/leaf-27b96c79f67176367791-proposal';receipt,r,packet_path,packet=old.original(failed,source_root);assert not (failed/'reply.raw.txt').exists();text=(failed/'reply.stream.raw.txt').read_text();p=extract(text);assert not p['attemptComplete'] and not p['streamVariants'];assert p['completeFields']['familyId']==r['familyId'];assert len(packet['units'])==32
 for key,value in p['completeFields'].items():contract.structure(value,contract.SCHEMA['properties'][key])
 p.update(originalFailedJobPath=rel(failed),originalFailureReceiptSha256=hfile(failed/'receipt.json'),retainedStreamSha256=hfile(failed/'reply.stream.raw.txt'),preservedPacketSha256=hfile(packet_path));prefix=L/'prefixes'/f'{r["familyId"]}.json';dump(prefix,p);remember(prefix);remember_job(failed)
 first='successor2-leaf-27b96c79f67176367791-proposal';second=first.replace('-proposal','-challenge');req=common(r,first,'leaf','proposal');req.update(completion=True,preservedPacketPath=rel(packet_path),preservedPacketSha256=hfile(packet_path),prefixPath=rel(prefix),prefixSha256=hfile(prefix),originalFailedJobPath=rel(failed));emit(req,contract.completion_schema(p));req=common(r,second,'leaf','challenge');req.update(dependsOn=first,prefixPath=rel(prefix),prefixSha256=hfile(prefix));emit(req,contract.regular_schema());replacement[r['familyId']]=rel(L/'jobs'/second)
 # Use the latest existing lineage for every unaffected sibling. New pairs only
 # replace terminal blocked ancestors, never completed or running work.
 prior=json.loads((N/'recovery-successors-v1/campaign.json').read_text());parents={x['familyId']:x for x in [json.loads(p.read_text()) for p in (N/'parents-wave-v1/jobs').glob('parent-*-proposal/request.json')]};affected=set(replacement)
 while True:
  added={key for key,r in parents.items() if any(d['reviewKey'] in affected for d in r['childDependencies'])}
  if added<=affected:break
  affected|=added
 for family in sorted(affected&parents.keys()):
  prior_path=prior['replacements'].get(family,f'full-pass/native-local/parents-wave-v1/jobs/parent-{family}-challenge');d=E/prior_path;s=json.loads((d.parent.parent/'state.json').read_text());assert s['jobs'][d.name]['status']=='blocked','Would duplicate nonblocked parent';replacement[family]=rel(L/'jobs'/f'successor2-parent-{family}-challenge')
 for family in sorted(affected&parents.keys()):
  r=parents[family]
  for stage in ['proposal','challenge']:
   j=f'successor2-parent-{family}-{stage}';req=common(r,j,'parent',stage);req.update(dependsOn=j.replace('-challenge','-proposal') if stage=='challenge' else None,supersedesBlockedJobPath=prior['replacements'].get(family,f'full-pass/native-local/parents-wave-v1/jobs/parent-{family}-challenge').replace('-challenge','-'+stage))
   deps=[]
   for original in r['childDependencies']:
    dep=copy.deepcopy(original);path=replacement.get(dep['reviewKey'],prior['replacements'].get(dep['reviewKey'],dep['jobPath']));dep.update(jobPath=path,challengeJobId=Path(path).name)
    if path!=original['jobPath']:dep['supersedesJobPath']=original['jobPath']
    d=E/path
    if not path.startswith(rel(L/'jobs')+'/'):
     dep['externalRequestSha256']=hfile(d/'request.json');remember(d/'request.json')
     if (d/'receipt.json').exists():verified_review(d);dep['receiptSha256']=hfile(d/'receipt.json');remember_job(d)
    deps.append(dep)
   req['childDependencies']=deps;emit(req,contract.regular_schema())
 for req in requests.values():dump(L/'jobs'/req['jobId']/'request.json',req);jobs.append({'jobId':req['jobId'],'dependsOn':req['dependsOn'],'requestSha256':hfile(L/'jobs'/req['jobId']/'request.json')});remember(E/req['originalPacketPath'])
 code=[{'path':rel(p),'sha256':hfile(p)} for p in [B/'prepare.py',B/'contract.py',B/'materialize.py',B/'INSTRUCTIONS.md',V1/'prefix.py',V1/'contract.py',V1/'prepare.py']]
 code+=[x for x in prior['publicPins'] if x['path'] not in {p['path'] for p in code}]
 campaign={'schemaVersion':'q025-recovery-successor-campaign/1','status':'prepared_not_launched','jobs':jobs,'maxAuthorizedConcurrency':8,'globalConcurrencyOwner':'root; total active across campaigns must remain <=48','nativeLaunches':0,'publicPins':code,'immutableInputPins':list(pins.values()),'replacements':replacement,'priorCampaignSha256':hfile(N/'recovery-successors-v1/campaign.json'),'scope':'New leaf27 interrupted output and v1 ce36 structural-context failure only; no completed source reading repeated.'};dump(L/'campaign.json',campaign);shutil.copyfile(N/'full-leaf-wave-v3/execution.json',L/'execution.json');dump(L/'control.json',{'enabled':False,'maxActive':2,'maxStartsPerMinute':6,'minStartIntervalMs':5000,'stopWhenComplete':True})
 dump(B/'manifest.json',{**campaign,'campaignSha256':hfile(L/'campaign.json'),'runnerSha256':hfile(B/'runner.mjs'),'nativeJobs':len(jobs),'launchGate':'Root verification and global concurrency accounting required; no model calls during preparation.'})
 dump(B/'failure-audit.json',{'nativeLaunches':0,'adopted':{'originalJobId':'successor-leaf-ce36cae0274019373c8a-proposal','originalReceiptSha256':derived['originalReceiptSha256'],'derivedReceiptSha256':hfile(target/'receipt.json'),'unitCount':51,'variantAssessments':27,'structuralContextCount':len(contexts),'validationSeconds':duration,'scientificAdmission':False},'partial':{'familyId':'27b96c79f67176367791','sourceUnitCount':32,'primaryExcerptCount':24,'streamCharacters':len(text),'completeFields':list(p['completeFields']),'completeArrayItems':{k:len(v) for k,v in p['completeArrayPrefixes'].items()},'lockedValues':len(p['lockedValues']),'streamVariants':0},'parentSuccessorFamilies':len(affected&parents.keys()),'sourceHashFilesVerified':len(old.SOURCE_CACHE),'noOriginalStateModified':True})
 print(json.dumps({'nativeJobs':len(jobs),'deterministicAdoptions':1,'partialRecoveries':1,'parentSuccessorFamilies':len(affected&parents.keys()),'nativeLaunches':0}))
if __name__=='__main__':main()
