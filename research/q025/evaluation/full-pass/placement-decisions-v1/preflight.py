"""Materialize isolated synthetic dependency fixtures, including worst-case prior budget."""
import copy,json,os,shutil
from pathlib import Path
import contract
from materialize import read,dump,sha,materialize
from test_contract import unresolved
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent;L=F/'native-local/placement-decisions-v1'
def utf16(s):return len(s.encode('utf-16-le'))//2
def estimate(prompt,request):
 schema=json.dumps(contract.SCHEMA,separators=(',',':'),ensure_ascii=False)
 n=utf16(prompt)+utf16(schema)+request['maxOutputCharacters']
 return {'actualPromptCharacters':utf16(prompt),'schemaCharacters':utf16(schema),'maxResponseCharacters':request['maxOutputCharacters'],'reasoningAndProtocolHeadroomTokens':16000,'dispatchGuardTokens':220000,'conservativeCombinedTokens':(n+2)//3+16000}
def main():
 old=sorted(L.glob('preflight-run-*'));work=L/f'preflight-run-{len(old)+1:03d}';assert not work.exists();work.mkdir();reports=[]
 for j in read(L/'campaign.json')['jobs']:
  d=work/'jobs'/j['jobId'];d.mkdir(parents=True);shutil.copyfile(L/'jobs'/j['jobId']/'request.json',d/'request.json');req=read(d/'request.json');materialize(d/'request.json',work);packet=read(d/'packet.actual.json');prompt=(d/'prompt-base.actual.txt').read_text();budget=estimate(prompt,req);assert budget['conservativeCombinedTokens']<=budget['dispatchGuardTokens'],'oversized prompt'
  reports.append({'jobId':j['jobId'],'stage':req['stage'],'actualMaterialization':'synthetic preflight only, zero native calls','packetSha256':sha(d/'packet.actual.json'),'promptSha256':sha(d/'prompt-base.actual.txt'),'budget':budget,'dependentPriorMode':'maximum permitted serialized reply'if req['dependsOn']else None})
  if req['stage']=='proposal':
   response=unresolved(packet);raw=json.dumps(response,ensure_ascii=False,separators=(',',':'));remaining=req['maxOutputCharacters']-utf16(raw);assert remaining>0;response['summary']+='X'*remaining;raw=json.dumps(response,ensure_ascii=False,separators=(',',':'));assert utf16(raw)==req['maxOutputCharacters'];contract.evaluate(packet,response);dump(d/'reply.json',response);dump(d/'receipt.json',{'status':'complete','sourceOnly':True,'toolUseAttempted':False,'normalizedReplySha256':sha(d/'reply.json'),'inputPins':{'packetSha256':sha(d/'packet.actual.json')},'syntheticFixture':True,'nativeLaunches':0})
 dump(B/'preflight.json',{'schemaVersion':'q025-placement-preflight/1','nativeLaunches':0,'fixtureRuntime':os.path.relpath(work,E),'jobs':reports,'maxConservativeTokens':max(r['budget']['conservativeCombinedTokens']for r in reports),'maxAuthorizedConcurrency':4,'maximumDependentPriorReplyCharacters':max(x['budget']['maxResponseCharacters']for x in reports),'noScientificResultOrAdmission':True});print(json.dumps({'materialized':len(reports),'maxConservativeTokens':max(r['budget']['conservativeCombinedTokens']for r in reports),'nativeLaunches':0}))
if __name__=='__main__':main()
