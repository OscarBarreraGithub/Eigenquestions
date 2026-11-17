import copy,hashlib,json,sys
from pathlib import Path
from extract import model_components
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
def check_source_bindings(packet):
 side=packet['machineSidecar'];assert side['familyId']==packet['familyId'];assert side['registry']['sha256']==packet['registrySha256']
 for s in packet['scopes']:assert hashlib.sha256(json.dumps(s['definition'],ensure_ascii=False,separators=(',',':')).encode()).hexdigest()==side['scopeBindings'][s['ref']]['definitionSha256']
 for u in packet['units']:assert hashlib.sha256(u['description'].encode()).hexdigest()==side['unitBindings'][u['ref']]['textSha256']
 assert set(side['comparisonBindings'])=={n['ref']for n in packet['nominations']}
 for n in packet['nominations']:assert {side['scopeBindings'][n['left']]['recordId'],side['scopeBindings'][n['right']]['recordId']}==set(side['comparisonBindings'][n['ref']]['recordIds'])
 assert not packet['evidence'],'No primary source text belongs to this screen'
def materialize(request_path,runtime):
 d=Path(request_path).resolve().parent;req=json.loads(Path(request_path).read_text());assert not(d/'dispatch-request.json').exists(),'Already materialized; no retry'
 for pin in req['recoveryPins']:assert sha(E/pin['path'])==pin['sha256'],'Frozen recovery input changed'
 source=E/req['originalPacketPath'];assert sha(source)==req['originalPacketSha256'];packet=json.loads(source.read_text());check_source_bindings(packet)
 p=E/req['componentsPath'];assert sha(p)==req['componentsSha256'];packet['preservedScreen']=json.loads(p.read_text());packet['preservedScreenArtifactSha256']=sha(p)
 view={k:copy.deepcopy(v)for k,v in packet.items()if k not in ['machineSidecar','refRegistry','preservedScreen']};view['preservedScreen']=model_components(packet['preservedScreen'])
 dump(d/'packet.actual.json',packet);instructions=(B/'INSTRUCTIONS.md').read_text();assert instructions.count('{{MAX_OUTPUT_CHARACTERS}}')==1;instructions=instructions.replace('{{MAX_OUTPUT_CHARACTERS}}',str(req['maxOutputCharacters']));(d/'prompt-base.actual.txt').write_text(instructions+'\n\nEXACT RETAINED SCREEN AND MISSING-FIELD PACKET\n'+json.dumps(view,ensure_ascii=False,separators=(',',':'))+'\n')
 actual={**req,'baseRequestSha256':sha(request_path),'packetSha256':sha(d/'packet.actual.json'),'promptBaseSha256':sha(d/'prompt-base.actual.txt')};dump(d/'dispatch-request.json',actual);return actual
if __name__=='__main__':print(json.dumps({'materialized':materialize(sys.argv[1],sys.argv[2])['jobId']}))
