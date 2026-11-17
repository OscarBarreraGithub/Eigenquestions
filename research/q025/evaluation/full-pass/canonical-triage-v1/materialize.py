import hashlib,json,sys
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent;W=E.parents[2];sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
def materialize(request_path,runtime):
 d=Path(request_path).resolve().parent;req=json.loads(Path(request_path).read_text());vp=W/req['scientificViewPath'];sp=W/req['sidecarPath'];assert sha(vp)==req['scientificViewSha256']and sha(sp)==req['sidecarSha256'];view=json.loads(vp.read_text());side=json.loads(sp.read_text());assert view['familyId']==req['familyId']==side['familyId'];assert side['registry']['sha256']==req['registrySha256']
 for s in view['scopes']:assert hashlib.sha256(json.dumps(s['definition'],ensure_ascii=False,separators=(',',':')).encode()).hexdigest()==side['scopeBindings'][s['ref']]['definitionSha256']
 for u in view['units']:assert hashlib.sha256(u['description'].encode()).hexdigest()==side['unitBindings'][u['ref']]['textSha256']
 assert set(side['comparisonBindings'])=={n['ref']for n in view['nominations']}
 for n in view['nominations']:assert {side['scopeBindings'][n['left']]['recordId'],side['scopeBindings'][n['right']]['recordId']}==set(side['comparisonBindings'][n['ref']]['recordIds'])
 packet={**view,'stage':'triage','evidence':[],'refRegistry':{},'machineSidecar':side};dump(d/'packet.actual.json',packet);instructions=(B/'INSTRUCTIONS.md').read_text();assert instructions.count('{{MAX_OUTPUT_CHARACTERS}}')==1;(d/'prompt-base.actual.txt').write_text(instructions.replace('{{MAX_OUTPUT_CHARACTERS}}',str(req['maxOutputCharacters']))+'\n\nEXACT SCIENTIFIC TRIAGE VIEW\n'+json.dumps({**view,'stage':'triage'},ensure_ascii=False,separators=(',',':'))+'\n');actual={**req,'baseRequestSha256':sha(request_path),'packetSha256':sha(d/'packet.actual.json'),'promptBaseSha256':sha(d/'prompt-base.actual.txt')};dump(d/'dispatch-request.json',actual);return actual
if __name__=='__main__':print(json.dumps({'materialized':materialize(sys.argv[1],sys.argv[2])['jobId']}))
