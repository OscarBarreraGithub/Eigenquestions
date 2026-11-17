"""Full-cap tail and assembled-prior envelope; no native model call."""
import json,shutil,os
from pathlib import Path
import contract
from materialize import read,dump,sha,materialize
from test_contract import tail
B=Path(__file__).resolve().parent;E=B.parent.parent;L=B.parent/'native-local/placement-tail-recovery-v1'
def utf16(x):return len(x.encode('utf-16-le'))//2
def main():
 work=L/f'preflight-run-{len(list(L.glob("preflight-run-*")))+1:03d}';assert not work.exists();work.mkdir();reports=[]
 for row in read(L/'campaign.json')['jobs']:
  d=work/'jobs'/row['jobId'];d.mkdir(parents=True);shutil.copyfile(L/'jobs'/row['jobId']/'request.json',d/'request.json');req=read(d/'request.json');materialize(d/'request.json',work);p=read(d/'packet.actual.json');prompt=(d/'prompt-base.actual.txt').read_text();schema=read(E/req['schemaPath']);budget=(utf16(prompt)+utf16(json.dumps(schema,separators=(',',':'),ensure_ascii=False))+req['maxOutputCharacters']+2)//3+16000;assert budget<=220000,'oversized complete prior'
  reports.append({'jobId':row['jobId'],'stage':req['stage'],'conservativeCombinedTokens':budget,'promptCharacters':utf16(prompt),'maxResponseCharacters':req['maxOutputCharacters'],'actualPriorNormalizedCharacters':utf16(json.dumps(p.get('priorReview'),ensure_ascii=False,separators=(',',':')))if p.get('priorReview')else None})
  if req['stage']=='proposal':
   r=tail(p);raw=json.dumps(r,ensure_ascii=False,separators=(',',':'));r['limitations'][0]+='X'*(req['maxOutputCharacters']-utf16(raw));raw=json.dumps(r,ensure_ascii=False,separators=(',',':'));assert utf16(raw)==req['maxOutputCharacters'];out=contract.evaluate(p,r);dump(d/'reply.json',out['normalizedReview']);dump(d/'receipt.json',{'status':'complete','sourceOnly':True,'toolUseAttempted':False,'normalizedReplySha256':sha(d/'reply.json'),'inputPins':{'packetSha256':sha(d/'packet.actual.json')},'syntheticFixture':True,'nativeLaunches':0})
 dump(B/'preflight.json',{'schemaVersion':'q025-tail-preflight/1','fixtureRuntime':os.path.relpath(work,E),'jobs':reports,'maxConservativeTokens':max(r['conservativeCombinedTokens']for r in reports),'maxAssembledPriorCharacters':max(r['actualPriorNormalizedCharacters']or 0 for r in reports),'maxRawTailCharacters':120000,'dispatchGuardTokens':220000,'nativeLaunches':0});print(json.dumps({'materialized':4,'worstContext':max(r['conservativeCombinedTokens']for r in reports),'assembledPriorMax':max(r['actualPriorNormalizedCharacters']or 0 for r in reports)}))
if __name__=='__main__':main()
