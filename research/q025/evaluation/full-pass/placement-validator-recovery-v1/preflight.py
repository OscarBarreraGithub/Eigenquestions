"""Materialize isolated synthetic dependency fixtures, including worst-case prior budget."""
import copy,json,os,shutil
from pathlib import Path
import contract
from materialize import read,dump,sha,materialize
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent;L=F/'native-local/placement-validator-recovery-v1'
def utf16(s):return len(s.encode('utf-16-le'))//2
def estimate(prompt,request):
 schema=json.dumps(contract.SCHEMA,separators=(',',':'),ensure_ascii=False)
 n=utf16(prompt)+utf16(schema)+request['maxOutputCharacters']
 return {'actualPromptCharacters':utf16(prompt),'schemaCharacters':utf16(schema),'maxResponseCharacters':request['maxOutputCharacters'],'reasoningAndProtocolHeadroomTokens':16000,'dispatchGuardTokens':220000,'conservativeCombinedTokens':(n+2)//3+16000}
def main():
 old=sorted(L.glob('preflight-run-*'));work=L/f'preflight-run-{len(old)+1:03d}';assert not work.exists();work.mkdir();reports=[]
 for j in read(L/'campaign.json')['jobs']:
  d=work/'jobs'/j['jobId'];d.mkdir(parents=True);shutil.copyfile(L/'jobs'/j['jobId']/'request.json',d/'request.json');req=read(d/'request.json');materialize(d/'request.json',work);packet=read(d/'packet.actual.json');prompt=(d/'prompt-base.actual.txt').read_text();budget=estimate(prompt,req);assert budget['conservativeCombinedTokens']<=budget['dispatchGuardTokens'],'oversized prompt'
  reports.append({'jobId':j['jobId'],'stage':req['stage'],'actualMaterialization':'synthetic preflight only, zero native calls','packetSha256':sha(d/'packet.actual.json'),'promptSha256':sha(d/'prompt-base.actual.txt'),'budget':budget,'dependentPriorMode':'maximum permitted serialized reply'if req['dependsOn']else 'actual completed immutable proposal'if req.get('priorJobPath')else None})
 dump(B/'preflight.json',{'schemaVersion':'q025-placement-preflight/1','nativeLaunches':0,'fixtureRuntime':os.path.relpath(work,E),'jobs':reports,'maxConservativeTokens':max(r['budget']['conservativeCombinedTokens']for r in reports),'maxAuthorizedConcurrency':1,'maximumResponseCharacters':120000,'actualDependentPriorCharacters':utf16(json.dumps(read(E/req['priorJobPath']/'reply.json'),ensure_ascii=False,separators=(',',':'))),'noScientificResultOrAdmission':True});print(json.dumps({'materialized':len(reports),'maxConservativeTokens':max(r['budget']['conservativeCombinedTokens']for r in reports),'nativeLaunches':0}))
if __name__=='__main__':main()
