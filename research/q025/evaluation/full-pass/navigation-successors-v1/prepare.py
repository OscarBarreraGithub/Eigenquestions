"""One deterministic representation adoption; one independent challenge, never launch."""
import copy,json,os,shutil
from pathlib import Path
import contract
from materialize import sha,read,dump
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent;W=E.parents[2];L=F/'native-local/navigation-successors-v1';ORIGINAL=F/'native-local/navigation-wave-v2/jobs/distance-and-emergence-proposal'
def pin(p):return {'path':os.path.relpath(p,E),'sha256':sha(p)}
def locations(x,path='$'):
 if isinstance(x,dict):
  for k,v in x.items():
   if k=='refs' and isinstance(v,list):
    for i,ref in enumerate(v):
     if ref=='pq0':yield f'{path}.refs[{i}]'
   else:yield from locations(v,path+'.'+k)
 elif isinstance(x,list):
  for i,v in enumerate(x):yield from locations(v,f'{path}[{i}]')
def input_pins(x):
 if isinstance(x,dict):
  if isinstance(x.get('path'),str) and x['path'].startswith('research/') and isinstance(x.get('sha256'),str):
   p=W/x['path'];assert sha(p)==x['sha256'],'source pin changed';yield pin(p)
  if x.get('artifactDirectory'):
   for k,v in x.items():
    if k.endswith('Sha256') and '.' in k[:-6]:
     p=E/x['artifactDirectory']/k[:-6];assert sha(p)==v,'historical artifact changed';yield pin(p)
  for v in x.values():yield from input_pins(v)
 elif isinstance(x,list):
  for v in x:yield from input_pins(v)
def main():
 assert not(L/'state.json').exists(),'preserve launched campaign';old=read(ORIGINAL/'receipt.json');request=read(ORIGINAL/'request.json');p=read(ORIGINAL/'packet.actual.json');reply=read(ORIGINAL/'reply.raw.txt')
 assert old['status']=='failed' and 'Invented/duplicate evidence reference'in old['error'] and not old['toolUseAttempted'] and not old['streamTruncated']
 for name,key in [('request.json','baseRequestSha256'),('dispatch-request.json','requestSha256'),('packet.actual.json','packetSha256'),('prompt.actual.txt','promptSha256')]:assert sha(ORIGINAL/name)==old['inputPins'][key]
 assert sha(ORIGINAL/'reply.raw.txt')==old['replySha256'];uses=list(locations(reply));assert len(uses)==9
 derived=contract.evaluate(p,reply);assert derived['normalizedReview']==reply and derived['scientificContentChanged']is False;contexts=derived['currentAuthoredScopeContext'];assert len(contexts)==1 and contexts[0]['ref']=='pq0' and contexts[0]['notPrimary']and contexts[0]['notIndependentSourceEvidence'];assert len(reply['newQuestions'])==1 and reply['newQuestions'][0]['id']=='pq0'
 adopted=L/'adopted/distance-proposal-authored-context';adopted.mkdir(parents=True,exist_ok=True)
 copied=['request.json','dispatch-request.json','packet.actual.json','prompt.actual.txt','reply.raw.txt']
 for name in copied:shutil.copyfile(ORIGINAL/name,adopted/name)
 dump(adopted/'reply.json',reply);derived.update(originalFailedReceipt=pin(ORIGINAL/'receipt.json'),originalRawSha256=sha(ORIGINAL/'reply.raw.txt'),packetSha256=sha(adopted/'packet.actual.json'),normalizerSha256=sha(F/'navigation-contract-v3/contract.py'),exactContextUsePaths=uses);dump(adopted/'normalization.json',derived)
 receipt={**old,'schemaVersion':'q025-derived-navigation-receipt/1','jobId':adopted.name,'status':'complete','error':None,'originalNativeStatus':'failed','originalFailedReceipt':pin(ORIGINAL/'receipt.json'),'normalizedReplySha256':sha(adopted/'reply.json'),'normalizationReceiptSha256':sha(adopted/'normalization.json'),'representationStatus':derived['status'],'nativeReviewRepeated':False,'scientificContentChanged':False,'logicalObjectsDuplicated':0,'newPrimaryEvidence':False};dump(adopted/'receipt.json',receipt)
 pins=[pin(ORIGINAL/n)for n in copied+['receipt.json','reply.stream.raw.txt']]+[pin(adopted/n)for n in copied+['reply.json','normalization.json','receipt.json']]+list(input_pins(p['machineBindings']));pins=list({x['path']:x for x in pins}.values())
 schema=L/'navigation-schema.json';dump(schema,contract.SCHEMA);pins.append(pin(schema));jid='distance-and-emergence-independent-challenge'
 req={**request,'schemaVersion':'q025-navigation-successor-request/1','jobId':jid,'stage':'challenge','dependsOn':None,'childDependencies':[],'schemaPath':str(schema.relative_to(E)),'schemaSha256':sha(schema),'originalPacketPath':str((adopted/'packet.actual.json').relative_to(E)),'originalPacketSha256':sha(adopted/'packet.actual.json'),'adoptedProposalPath':str(adopted.relative_to(E)),'adoptedReceiptSha256':sha(adopted/'receipt.json'),'immutablePins':pins};assert req['maxOutputCharacters']==80000;dump(L/'jobs'/jid/'request.json',req)
 public=[B/n for n in ['contract.py','materialize.py','prepare.py','INSTRUCTIONS.md']]+[F/n for n in ['navigation-contract-v3/contract.py','navigation-wave-v2/contract.py','navigation-decisions-v1/contract.py','canonical-v1/contract.py']]+[E/'recovery/compact_contract.py'];campaign={'schemaVersion':'q025-navigation-successor-campaign/1','jobs':[{'jobId':jid,'dependsOn':None,'requestSha256':sha(L/'jobs'/jid/'request.json')}],'maxAuthorizedConcurrency':1,'nativeLaunches':0,'publicPins':[pin(x)for x in public],'immutableInputPins':pins};dump(L/'campaign.json',campaign);shutil.copyfile(F/'native-local/navigation-wave-v2/execution.json',L/'execution.json');dump(L/'control.json',{'enabled':False,'maxActive':1,'maxStartsPerMinute':6,'minStartIntervalMs':5000,'stopWhenComplete':True});dump(B/'manifest.json',{**campaign,'campaignSha256':sha(L/'campaign.json'),'runnerSha256':sha(B/'runner.mjs'),'nativeJobs':1,'launchGate':'Root verifies deterministic adoption and launches only the new independent challenge.'})
 report={'schemaVersion':'q025-distance-representation-adoption/1','originalFailedReceipt':pin(ORIGINAL/'receipt.json'),'originalRawReply':pin(ORIGINAL/'reply.raw.txt'),'adoptedDirectory':str(adopted.relative_to(E)),'adoptedReceipt':pin(adopted/'receipt.json'),'adoptedReply':pin(adopted/'reply.json'),'normalization':pin(adopted/'normalization.json'),'currentAuthoredScopeContext':contexts,'exactContextUsePaths':uses,'validation':derived['validation'],'sourceDescriptions':len(p['units']),'pairedAnnotations':len(p['pairedUnitContext']),'primaryWindows':len(p['evidence']),'nominatedPairs':len(p['nominations']),'originalScientificContentChanged':False,'originalFailurePreserved':True,'nativeReviewRepeated':False,'scientificAdmission':False,'nativeLaunches':0};dump(B/'adoption.json',report);print(json.dumps({'adopted':True,'contextUses':len(uses),'requests':1,'nativeLaunches':0,'maxOutputCharacters':req['maxOutputCharacters']}))
if __name__=='__main__':main()
