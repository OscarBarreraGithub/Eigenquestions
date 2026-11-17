"""Prepare two explicit missing-only screen successors; never start a model."""
import copy,json,shutil,os
from pathlib import Path
import contract
from extract import extract,sha
from materialize import check_source_bindings
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent;W=E.parents[2];L=F/'native-local/screen-recovery-v1'
def dump(p,x):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
def pin(p):return {'path':os.path.relpath(p,E),'sha256':sha(p)}
def main():
 assert not(L/'state.json').exists(),'Preserve launched campaign';L.mkdir(parents=True,exist_ok=True);pins=[];jobs=[];reports=[]
 schema=L/'completion-schema.json';dump(schema,contract.SCHEMA);pins.append(pin(schema))
 for number,selected,expected,variants in [('0039',0,95,61),('0047',1,82,49)]:
  d=F/f'native-local/canonical-triage-wave-v2/jobs/canonical-continuation-v4-{number}-screen';request=json.loads((d/'request.json').read_text());receipt=json.loads((d/'receipt.json').read_text());assert receipt['status']=='failed'and receipt['error'].startswith('Output exceeded')and not receipt['toolUseAttempted']and not receipt['streamTruncated']
  for name,key in [('packet.actual.json','packetSha256'),('request.json','baseRequestSha256'),('prompt.actual.txt','promptSha256'),('dispatch-request.json','requestSha256')]:assert sha(d/name)==receipt['inputPins'][key]
  originalpins=[pin(p)for p in sorted(d.iterdir())if p.name in ['request.json','receipt.json','packet.actual.json','reply.raw.txt','reply.stream.raw.txt','prompt.actual.txt','dispatch-request.json','events.jsonl']]
  for pathkey,hashkey in [('scientificViewPath','scientificViewSha256'),('sidecarPath','sidecarSha256')]:
   p=W/request[pathkey];assert sha(p)==request[hashkey];originalpins.append(pin(p))
  packet=json.loads((d/'packet.actual.json').read_text());check_source_bindings(packet);text=(d/'reply.stream.raw.txt').read_text();parts=extract(text,packet,selected);assert len(parts['selectedFields']['comparisonReviews'])==expected and len(parts['attemptVariants'])==variants
  parts.update(originalFailedReceiptSha256=sha(d/'receipt.json'),sourcePacketSha256=sha(d/'packet.actual.json'))
  artifact=L/f'preserved-{number}.json';dump(artifact,parts);originalpins.append(pin(artifact));pins+=originalpins
  # Verify complete retained rows against the unchanged scientific contract,
  # using a narrowed nomination inventory and temporary tail placeholders only.
  retained=copy.deepcopy(parts['selectedFields']);retained.update(limitations=[],unresolved=[]);subset=copy.deepcopy(packet);kept={x['ref']for x in retained['comparisonReviews']};subset['nominations']=[x for x in packet['nominations']if x['ref']in kept];validation=contract.base.evaluate(subset,retained)['validation']
  jobId=f'canonical-continuation-v4-{number}-screen-completion';req={**request,'jobId':jobId,'kind':'triage','completion':True,'dependsOn':None,'childDependencies':[],'originalPacketPath':str((d/'packet.actual.json').relative_to(E)),'originalPacketSha256':sha(d/'packet.actual.json'),'componentsPath':str(artifact.relative_to(E)),'componentsSha256':sha(artifact),'schemaPath':str(schema.relative_to(E)),'schemaSha256':sha(schema),'recoveryPins':originalpins+[pin(schema)]};dump(L/'jobs'/jobId/'request.json',req);jobs.append({'jobId':jobId,'dependsOn':None,'requestSha256':sha(L/'jobs'/jobId/'request.json')})
  events=[json.loads(line)for line in (d/'events.jsonl').read_text().splitlines()];assert sum(x['type']=='thread_started'for x in events)==sum(x['type']=='turn_started'for x in events)==1
  reports.append({'originalJobId':d.name,'successorJobId':jobId,'originalReceiptSha256':sha(d/'receipt.json'),'streamSha256':sha(d/'reply.stream.raw.txt'),'streamCharacters':len(text),'streamTruncated':False,'oneRecordedThreadAndTurn':True,'nativeReconnectEvents':[{'message':x.get('message'),'willRetry':x.get('willRetry')}for x in events if x['type']=='native_error'],'attemptStartBytes':[a['jsonStartByte']for a in parts['attempts']],'selectedAttempt':selected,'retainedScopes':len(retained['scopeReviews']),'retainedComparisons':expected,'missingScopeRefs':parts['missingRefs']['scopeReviews'],'missingComparisonRefs':parts['missingRefs']['comparisonReviews'],'variantObligations':variants,'sourceDescriptions':len(packet['units']),'primaryExcerpts':0,'componentsSha256':sha(artifact),'retainedRowsStructuralValidation':validation,'structuralNotice':'Narrowed nomination set and temporary tail placeholders only verify retained rows; no completed scientific review was adopted.'})
 public=[B/x for x in ['prepare.py','extract.py','contract.py','materialize.py','INSTRUCTIONS.md']]+[F/'canonical-triage-wave-v2/contract.py',F/'canonical-recovery-v2/extract_prefix.py',E/'recovery/compact_contract.py']
 campaign={'schemaVersion':'q025-screen-completion-campaign/1','status':'prepared_not_launched','jobs':jobs,'maxAuthorizedConcurrency':2,'publicPins':[pin(p)for p in public],'immutableInputPins':pins,'nativeLaunches':0,'scope':'Missing comparison/tail completion plus explicit alternate-attempt review; no repeated full screen and no scientific admission.'};dump(L/'campaign.json',campaign);shutil.copyfile(F/'native-local/canonical-triage-wave-v2/execution.json',L/'execution.json');dump(L/'control.json',{'enabled':False,'maxActive':2,'maxStartsPerMinute':6,'minStartIntervalMs':5000,'stopWhenComplete':True})
 dump(B/'manifest.json',{**campaign,'campaignSha256':sha(L/'campaign.json'),'runnerSha256':sha(B/'runner.mjs'),'nativeJobs':len(jobs),'launchGate':'Root verifies READY pins and global concurrency; no model calls in preparation.'});dump(B/'prefix-audit.json',{'schemaVersion':'q025-screen-prefix-audit/1','jobs':reports,'nativeLaunches':0,'originalFilesChanged':False});print(json.dumps({'jobs':len(jobs),'missingComparisons':11,'variants':110,'nativeLaunches':0}))
if __name__=='__main__':main()
