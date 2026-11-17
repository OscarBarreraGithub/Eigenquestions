import hashlib,json,sys
from pathlib import Path
import contract
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent;sys.path.insert(0,str(F/'compact-v1'));from compact_pipeline import compile_packet,dump,hfile

def materialize(request_path,runtime):
 d=Path(request_path).resolve().parent;req=json.loads(Path(request_path).read_text());source=E/req['originalPacketPath'];assert hfile(source)==req['originalPacketSha256'];original=json.loads(source.read_text());prior=None;pins={}
 if req['dependsOn']:
  old=d.parent/req['dependsOn'];r=json.loads((old/'receipt.json').read_text());assert r['status']=='complete' and not r.get('toolUseAttempted');assert hfile(old/'reply.raw.txt')==r['replySha256'];assert hfile(old/'reply.json')==r['normalizedReplySha256'];prior=json.loads((old/'reply.json').read_text());contract.evaluate(json.loads((old/'packet.actual.json').read_text()),prior);pins={'priorReplySha256':hfile(old/'reply.json'),'priorRawReplySha256':r['replySha256'],'priorReceiptSha256':hfile(old/'receipt.json')}
 packet,view=compile_packet(original,req['stage'],prior);dump(d/'packet.actual.json',packet);(d/'prompt-base.actual.txt').write_text((B/'INSTRUCTIONS.md').read_text()+'\n\nEXACT RECOVERY SOURCE PACKET\n'+json.dumps(view,ensure_ascii=False,separators=(',',':'))+'\n');actual={**req,**pins,'baseRequestSha256':hfile(request_path),'packetSha256':hfile(d/'packet.actual.json'),'promptBaseSha256':hfile(d/'prompt-base.actual.txt')};dump(d/'dispatch-request.json',actual);return actual
if __name__=='__main__':print(json.dumps({'materialized':materialize(sys.argv[1],sys.argv[2])['jobId']}))
