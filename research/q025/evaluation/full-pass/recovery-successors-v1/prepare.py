"""Prepare disjoint successors only; never execute native models or edit old states."""
import copy,hashlib,importlib.util,json,shutil,subprocess,sys,time
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent;L=F/'native-local/recovery-successors-v1'
sys.path.insert(0,str(B));import contract
from prefix import extract,value_hash
sys.path.insert(0,str(F/'compact-v1'));from compact_pipeline import dump,hfile
from materialize import verified_review
SOURCE_CACHE={}
def relative(path):return str(Path(path).relative_to(E))
def pin(path):return {'path':relative(path),'sha256':hfile(path)}
def source_check(packet,source_root):
 count=0
 for e in packet.get('evidence',[]):
  record=packet['refRegistry'][e['ref']]['sourceContext'];path=source_root/record['path']
  if path not in SOURCE_CACHE:SOURCE_CACHE[path]=hfile(path)
  assert SOURCE_CACHE[path]==record['fileSha256'],'Archived source changed'
  assert hashlib.sha256(e['text'].encode()).hexdigest()==record['textSha256'],'Excerpt text changed';count+=1
 return count

def original(job,source_root):
 receipt=json.loads((job/'receipt.json').read_text());request=json.loads((job/'request.json').read_text());packet_path=job/('packet.actual.json' if (job/'packet.actual.json').exists() else 'packet.json');packet=json.loads(packet_path.read_text())
 assert receipt['status']=='failed' and not receipt.get('toolUseAttempted');assert hfile(packet_path)==receipt['inputPins']['packetSha256'];assert hfile(job/'request.json')==receipt['inputPins']['baseRequestSha256'];assert hfile(job/'prompt.actual.txt')==receipt['inputPins']['promptSha256'];assert hfile(E/request['originalPacketPath'])==request['originalPacketSha256'];source_check(packet,source_root)
 return receipt,request,packet_path,packet

def adopt(job,source_root,annotation=False):
 receipt,request,packet_path,packet=original(job,source_root);raw=(job/'reply.raw.txt').read_bytes();assert hashlib.sha256(raw).hexdigest()==receipt['replySha256'];reply=json.loads(raw);start=time.perf_counter()
 if annotation:
  packet,context=contract.prior_annotation_context(packet,reply);result=contract.evaluate(packet,reply)
 else:
  check=subprocess.run(['python3',str(F/'production-v3/contract.py')],input=json.dumps({'packet':packet,'reply':reply}),text=True,capture_output=True,timeout=120);assert check.returncode==0,check.stdout+check.stderr;result=json.loads(check.stdout)
 elapsed=time.perf_counter()-start;target=L/'adopted'/job.name;target.mkdir(parents=True,exist_ok=True);dump(target/'request.json',{**request,'executionMode':'deterministic_revalidation_only','originalJobPath':relative(job),'originalRequestSha256':hfile(job/'request.json')});(target/'reply.raw.txt').write_bytes(raw);dump(target/'packet.actual.json',packet);dump(target/'reply.json',result['normalizedReview']);result.update(originalRawSha256=receipt['replySha256'],originalPacketSha256=hfile(packet_path),derivedPacketSha256=hfile(target/'packet.actual.json'),originalFailureReceiptSha256=hfile(job/'receipt.json'));dump(target/'normalization.json',result)
 derived={'schemaVersion':'q025-derived-revalidation-receipt/1','jobId':job.name,'status':'complete','origin':'deterministic_revalidation','nativeTurnStartedHere':False,'model':receipt['model'],'effort':receipt['effort'],'sourceOnly':True,'sandbox':'read-only','toolUseAttempted':False,'threadId':receipt.get('threadId'),'turnId':receipt.get('turnId'),'independence':'Same original source-only turn; no new reviewer or model call.','usage':None,'originalNativeStatus':'failed','originalError':receipt['error'],'originalJobPath':relative(job),'originalReceiptSha256':hfile(job/'receipt.json'),'originalRawReplySha256':receipt['replySha256'],'inputPins':{'packetSha256':hfile(target/'packet.actual.json'),'originalPacketSha256':hfile(packet_path)},'replySha256':hfile(target/'reply.raw.txt'),'normalizedReplySha256':hfile(target/'reply.json'),'normalizationReceiptSha256':hfile(target/'normalization.json'),'derivedUnitCount':len(result['normalizedReview']['units']),'scientificAdmission':False};dump(target/'receipt.json',derived)
 return target,{'jobId':job.name,'nativeStatus':'failed','derivedStatus':'complete_revalidated_representation','originalReceiptSha256':hfile(job/'receipt.json'),'originalRawReplySha256':receipt['replySha256'],'derivedReceiptSha256':hfile(target/'receipt.json'),'unitCount':derived['derivedUnitCount'],'validationSeconds':elapsed,'priorAnnotationContextCount':len(result.get('priorAnnotationContext',[]))}

def main():
 assert not (L/'state.json').exists(),'Successor campaign already launched; no overwrite'
 L.mkdir(parents=True,exist_ok=True);execution=json.loads((F/'native-local/full-leaf-wave-v3/execution.json').read_text());source_root=Path(execution['sourceRoot']);jobs=[];imports=[];prefixes=[];input_pins={};replacement={};request_by_id={};oldpins=[]
 def remember(path):input_pins[relative(path)]=pin(path)
 def remember_job(job):
  for name in ['request.json','receipt.json','packet.actual.json','packet.json','reply.raw.txt','reply.stream.raw.txt','normalization.json','reply.json','dispatch-request.json','prompt.actual.txt']:
   p=job/name
   if p.exists():remember(p)
 def emit(request,schema):
  schema_path=L/'schemas'/(request['jobId']+'.json');dump(schema_path,schema);request.update(schemaPath=relative(schema_path),schemaSha256=hfile(schema_path));dump(L/'jobs'/request['jobId']/'request.json',request);jobs.append({'jobId':request['jobId'],'dependsOn':request.get('dependsOn'),'requestSha256':hfile(L/'jobs'/request['jobId']/'request.json')});request_by_id[request['jobId']]=request;remember(schema_path)
 def common(old,jobid,kind,stage):return {**{k:v for k,v in old.items() if k in ['familyId','originalPacketPath','originalPacketSha256','fullMemberCount']},'schemaVersion':'q025-recovery-successor-request/1','jobId':jobid,'kind':kind,'stage':stage,'dependsOn':None,'model':'gpt-6-astra','effort':'xhigh','sandbox':'read-only','sourceOnly':True,'timeoutSeconds':1800,'maxOutputCharacters':120000,'childDependencies':[]}
 # Known complete failed turns are revalidated, never reread.
 for family in ['55a2311c12b246ddbd15','90980b7a8339256bfea7']:
  job=F/f'native-local/full-leaf-wave-v3/jobs/leaf-{family}-proposal';target,audit=adopt(job,source_root);imports.append(audit);remember_job(job);remember_job(target);old=json.loads((job/'request.json').read_text());jid=f'successor-leaf-{family}-challenge';req=common(old,jid,'leaf','challenge');req.update(priorJobPath=relative(target),priorReceiptSha256=hfile(target/'receipt.json'),originalFailedJobPath=relative(job));emit(req,contract.regular_schema());replacement[family]=relative(L/'jobs'/jid)
 job=F/'native-local/parents-wave-v1/jobs/parent-8d2b5fd7cc13cefc77fe-challenge';target,audit=adopt(job,source_root,True);imports.append(audit);remember_job(job);remember_job(target);replacement['8d2b5fd7cc13cefc77fe']=relative(target)
 # Already completed independent recovery pair is reused exactly.
 recovered=F/'native-local/leaf-recovery-v4/jobs/leaf-recovery-54e3e83d0ccbf2700b0f-challenge';reply,normal,receipt=verified_review(recovered);remember_job(recovered);replacement['54e3e83d0ccbf2700b0f']=relative(recovered)
 native_states={lane:json.loads((F/f'native-local/{lane}/state.json').read_text()) for lane in ['full-leaf-wave-v3','parents-wave-v1']}
 for lane in ['full-leaf-wave-v3','parents-wave-v1']:
  for oldid,state in native_states[lane]['jobs'].items():
   if state['status']!='failed' or oldid.split('-')[1] in replacement:continue
   job=F/'native-local'/lane/'jobs'/oldid;receipt,old,packet_path,packet=original(job,source_root);assert old['stage']=='proposal','New challenge failure needs explicit deterministic triage before campaign freeze';assert not (job/'reply.raw.txt').exists(),'New complete reply needs deterministic revalidation first';stream=(job/'reply.stream.raw.txt').read_text();prefix=extract(stream);assert prefix['completeFields']['familyId']==old['familyId'];assert not prefix['attemptComplete'],'Complete stream attempt needs deterministic validation first'
   for key,value in prefix['completeFields'].items():contract.structure(value,contract.SCHEMA['properties'][key])
   for key,values in prefix['completeArrayPrefixes'].items():
    for value in values:contract.structure(value,contract.SCHEMA['properties'][key]['items'])
   prefix.update(originalFailedJobPath=relative(job),originalFailureReceiptSha256=hfile(job/'receipt.json'),retainedStreamSha256=hfile(job/'reply.stream.raw.txt'),preservedPacketSha256=hfile(packet_path));prefix_path=L/'prefixes'/f'{old["familyId"]}.json';dump(prefix_path,prefix);remember(prefix_path);remember_job(job)
   prefixes.append({'familyId':old['familyId'],'originalJobId':oldid,'sourceUnitCount':len(packet['units']),'primaryExcerptCount':len(packet['evidence']),'streamCharacters':len(stream),'tabCharacters':stream.count('\t'),'attempts':1+len(prefix['earlierAttempts']),'preservedTopFields':list(prefix['completeFields']),'preservedArrayItems':{k:len(v) for k,v in prefix['completeArrayPrefixes'].items()},'lockedValues':len(prefix['lockedValues']),'earlierVariantReviewObligations':len(prefix['streamVariants']),'prefixPath':relative(prefix_path),'prefixSha256':hfile(prefix_path),'originalReceiptSha256':hfile(job/'receipt.json')})
   kind='parent' if lane=='parents-wave-v1' else 'leaf';first=f'successor-{kind}-{old["familyId"]}-proposal';second=first.replace('-proposal','-challenge');req=common(old,first,kind,'proposal');req.update(completion=True,preservedPacketPath=relative(packet_path),preservedPacketSha256=hfile(packet_path),prefixPath=relative(prefix_path),prefixSha256=hfile(prefix_path),originalFailedJobPath=relative(job),childDependencies=old.get('childDependencies',[]));emit(req,contract.completion_schema(prefix));req=common(old,second,kind,'challenge');req.update(dependsOn=first,prefixPath=relative(prefix_path),prefixSha256=hfile(prefix_path),childDependencies=old.get('childDependencies',[]));emit(req,contract.regular_schema(bool(prefix['streamVariants'])));replacement[old['familyId']]=relative(L/'jobs'/second)
 # Rewire only ancestors of these failures, never completed unaffected work.
 parents={p.parent.name:json.loads(p.read_text()) for p in (F/'native-local/parents-wave-v1/jobs').glob('parent-*-proposal/request.json')};affected=set(replacement);changed=True
 while changed:
  changed=False
  for req in parents.values():
   if req['familyId'] not in affected and any(d['reviewKey'] in affected for d in req['childDependencies']):affected.add(req['familyId']);changed=True
 for oldid,old in parents.items():
  family=old['familyId']
  if family not in affected or family in replacement:continue
  oldstate=native_states['parents-wave-v1']['jobs'][oldid];assert oldstate['status'] in ['blocked','pending'],'Would duplicate already running/completed parent'
  replacement[family]=relative(L/'jobs'/f'successor-parent-{family}-challenge')
 for oldid,old in parents.items():
  family=old['familyId'];target=replacement.get(family)
  if not target or family in {r['familyId'] for r in request_by_id.values()} or family=='8d2b5fd7cc13cefc77fe':continue
  for stage in ['proposal','challenge']:
   jid=f'successor-parent-{family}-{stage}';req=common(old,jid,'parent',stage);req.update(dependsOn=jid.replace('-challenge','-proposal') if stage=='challenge' else None,childDependencies=old['childDependencies'],supersedesBlockedJobPath=f'full-pass/native-local/parents-wave-v1/jobs/parent-{family}-{stage}');emit(req,contract.regular_schema())
 for entry in jobs:
  req=request_by_id[entry['jobId']];deps=[]
  for olddep in req.get('childDependencies',[]):
   dep=copy.deepcopy(olddep)
   if dep['reviewKey'] in replacement:dep.update(jobPath=replacement[dep['reviewKey']],challengeJobId=Path(replacement[dep['reviewKey']]).name,supersedesJobPath=olddep['jobPath'])
   job=E/dep['jobPath']
   if not dep['jobPath'].startswith(relative(L/'jobs')+'/') and (job/'request.json').exists():dep['externalRequestSha256']=hfile(job/'request.json');remember(job/'request.json')
   if (job/'receipt.json').exists():
    _,_,r=verified_review(job);dep['receiptSha256']=hfile(job/'receipt.json');remember_job(job)
   deps.append(dep)
  req['childDependencies']=deps;dump(L/'jobs'/req['jobId']/'request.json',req);entry['requestSha256']=hfile(L/'jobs'/req['jobId']/'request.json')
 # Every original source packet is immutable, including future parent contrasts.
 for req in request_by_id.values():remember(E/req['originalPacketPath'])
 code=[B/'prepare.py',B/'prefix.py',B/'contract.py',B/'materialize.py',B/'INSTRUCTIONS.md',F/'parents-wave-v1/contract.py',F/'parents-wave-v1/build_child_artifact.py',F/'parents-wave-v1/INSTRUCTIONS.md',F/'parents-v1/parent_pipeline.py',F/'parents-v1/build_child_artifact.py',F/'production-v3/contract.py',F/'compact-v1/production_contract.py',F/'compact-v1/production_pipeline.py',F/'compact-v1/compact_pipeline.py',E/'recovery/compact_contract.py',E/'recovery/compact_inputs.py',F/'production-v3/INSTRUCTIONS.md',F/'coverage-plan.json',F/'coverage-memberships.local.json']
 campaign={'schemaVersion':'q025-recovery-successor-campaign/1','status':'prepared_not_launched','jobs':jobs,'maxAuthorizedConcurrency':8,'globalConcurrencyOwner':'root; total active across campaigns must remain<=48','nativeLaunches':0,'schemaPolicy':'Per-job output schema matches exact request; no per-string caps;120000 total characters.','publicPins':[pin(p) for p in code],'immutableInputPins':list(input_pins.values()),'replacements':replacement,'importedRevalidations':imports,'completedRecoveryReused':{'familyId':'54e3e83d0ccbf2700b0f','challengeReceiptSha256':hfile(recovered/'receipt.json')},'partialRecoveries':prefixes};dump(L/'campaign.json',campaign);shutil.copyfile(F/'native-local/full-leaf-wave-v3/execution.json',L/'execution.json');dump(L/'control.json',{'enabled':False,'maxActive':2,'maxStartsPerMinute':6,'minStartIntervalMs':5000,'stopWhenComplete':True})
 public={**campaign,'campaignSha256':hfile(L/'campaign.json'),'runnerSha256':hfile(B/'runner.mjs'),'nativeJobs':len(jobs),'launchGate':'Root verifies READY, exact inputs and global concurrency; preparation launches no model. Original failed/blocked states remain unchanged.'};dump(B/'manifest.json',public);dump(B/'failure-audit.json',{'adoptions':imports,'partialRecoveries':prefixes,'replacements':replacement,'nativeJobs':len(jobs),'nativeLaunches':0,'noOriginalStateModified':True,'sourceHashFilesVerified':len(SOURCE_CACHE)})
 print(json.dumps({'nativeJobs':len(jobs),'adoptedCompleteReplies':len(imports),'partialRecoveries':len(prefixes),'reusedCompletedRecovery':1,'sourceHashFilesVerified':len(SOURCE_CACHE),'parentSuccessorFamilies':len({r['familyId'] for r in request_by_id.values() if r['kind']=='parent'})}))
if __name__=='__main__':main()
