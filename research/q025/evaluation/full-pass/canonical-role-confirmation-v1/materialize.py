import hashlib,json,sys
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent;W=E.parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
def materialize(request_path,runtime):
 d=Path(request_path).resolve().parent;req=json.loads(Path(request_path).read_text());source=E/req['originalPacketPath'];assert sha(source)==req['originalPacketSha256'];p=json.loads(source.read_text());assert p['familyId']==req['familyId']
 for u in p['units']:assert hashlib.sha256(u['description'].encode()).hexdigest()==p['refRegistry'][u['ref']]['textSha256']
 for e in p['evidence']:assert hashlib.sha256(e['text'].encode()).hexdigest()==p['refRegistry'][e['ref']]['sourceContext']['textSha256']
 dump(d/'packet.actual.json',p);text=(B/'INSTRUCTIONS.md').read_text();assert text.count('{{MAX_OUTPUT_CHARACTERS}}')==1
 view={k:v for k,v in p.items()if k not in ['refRegistry','pins','machineBindings']};(d/'prompt-base.actual.txt').write_text(text.replace('{{MAX_OUTPUT_CHARACTERS}}',str(req['maxOutputCharacters']))+'\n\nEXACT ROLE REVIEW PACKET\n'+json.dumps(view,ensure_ascii=False,separators=(',',':'))+'\n')
 actual={**req,'baseRequestSha256':sha(request_path),'packetSha256':sha(d/'packet.actual.json'),'promptBaseSha256':sha(d/'prompt-base.actual.txt')};dump(d/'dispatch-request.json',actual);return actual
if __name__=='__main__':print(json.dumps({'materialized':materialize(sys.argv[1],sys.argv[2])['jobId']}))
