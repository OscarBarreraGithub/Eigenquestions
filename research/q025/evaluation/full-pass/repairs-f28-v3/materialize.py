"""Bind exact source neighborhoods and immutable proposal for independent challenge."""
import hashlib,json,sys
from pathlib import Path
from contract import evaluate
B=Path(__file__).resolve().parent;E=B.parent.parent;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
def materialize(request_path,runtime):
 d=Path(request_path).resolve().parent;req=json.loads(Path(request_path).read_text());src=E/req['originalPacketPath'];assert sha(src)==req['originalPacketSha256'];packet=json.loads(src.read_text());packet['stage']=req['stage'];pins={};source_root=Path(json.loads((Path(runtime)/'execution.json').read_text())['sourceRoot'])
 for case in packet['cases']:
  for e in case['context']['primary']:
   meta=case['refs'][e['ref']];c=meta['sourceContext'];assert sha(source_root/c['path'])==c['fileSha256'];archive=json.loads((source_root/c['path']).read_text());assert archive['source_sha256']==meta['sourceSha256'];assert archive['pages'][c['pdfPage']-1][c['start']:c['end']]==e['text'];assert hashlib.sha256(e['text'].encode()).hexdigest()==c['textSha256']
 if req['dependsOn']:
  old=d.parent/req['dependsOn'];receipt=json.loads((old/'receipt.json').read_text());assert receipt['status']=='complete' and not receipt.get('toolUseAttempted');assert sha(old/'reply.raw.txt')==receipt['replySha256'];assert sha(old/'reply.json')==receipt['normalizedReplySha256'];prior=json.loads((old/'reply.json').read_text());oldp=json.loads((old/'packet.actual.json').read_text());evaluate(oldp,prior);packet['priorReview']=prior;pins={'priorReplySha256':sha(old/'reply.json'),'priorRawReplySha256':receipt['replySha256'],'priorReceiptSha256':sha(old/'receipt.json')}
 dump(d/'packet.actual.json',packet);view={k:v for k,v in packet.items() if k!='sourceReviews'};(d/'prompt-base.actual.txt').write_text((B/'INSTRUCTIONS.md').read_text().replace('{{MAX_OUTPUT_CHARACTERS}}',str(req['maxOutputCharacters']))+'\n\nEXACT CLAUSE REVIEW PACKET\n'+json.dumps(view,ensure_ascii=False,separators=(',',':'))+'\n');actual={**req,**pins,'baseRequestSha256':sha(request_path),'packetSha256':sha(d/'packet.actual.json'),'promptBaseSha256':sha(d/'prompt-base.actual.txt')};dump(d/'dispatch-request.json',actual);return actual
if __name__=='__main__':print(json.dumps({'materialized':materialize(sys.argv[1],sys.argv[2])['jobId']}))
