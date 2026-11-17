"""Build one parent stage from immutable ready child reviews; never launch a model."""
import json,sys
from pathlib import Path
from parent_pipeline import make_parent_packet
from build_child_artifact import build
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent;C=F/'compact-v1';sys.path.insert(0,str(C));from compact_pipeline import dump,hfile
request_path=Path(sys.argv[1]);d=request_path.parent;req=json.loads(request_path.read_text());original_path=E/req['originalPacketPath'];assert hfile(original_path)==req['originalPacketSha256'];original=json.loads(original_path.read_text());original['fullMemberCount']=req['fullMemberCount'];plan=json.loads((F/'coverage-plan.json').read_text());regions={r['reviewKey']:r for r in plan['regions']};members=json.loads((F/'coverage-memberships.local.json').read_text());children=[];pins=[]
for dep in req['childDependencies']:
 root=F/('native-local/full-leaf-wave-v3' if dep['kind']=='leaf' else 'native-local/parents-v1');source=root/'jobs'/dep['challengeJobId'];receipt=json.loads((source/'receipt.json').read_text());assert receipt['status']=='complete';artifact=build(source,regions[dep['reviewKey']],members[dep['reviewKey']]);target=F/'native-local/parents-v1/child-artifacts'/f'{dep["reviewKey"]}.json'
 if target.exists():assert json.loads(target.read_text())==artifact,'Frozen child artifact changed'
 else:dump(target,artifact)
 artifact['artifactSha256']=hfile(target);children.append(artifact);pins.append({'reviewKey':dep['reviewKey'],'kind':dep['kind'],'artifactPath':str(target.relative_to(E)),'artifactSha256':hfile(target),'receiptSha256':hfile(source/'receipt.json')})
prior=None
if req['stage']=='challenge':
 source=d.parent/req['dependsOn'];receipt=json.loads((source/'receipt.json').read_text());assert receipt['status']=='complete';assert hfile(source/'reply.json')==receipt['normalizedReplySha256'];prior=json.loads((source/'reply.json').read_text());pins.append({'priorParentJobId':req['dependsOn'],'receiptSha256':hfile(source/'receipt.json'),'replySha256':hfile(source/'reply.json')})
packet,view=make_parent_packet(original,children,req['stage'],prior);dump(d/'packet.actual.json',packet);(d/'prompt-base.actual.txt').write_text((B/'INSTRUCTIONS.md').read_text()+'\n\nPARENT SYNTHESIS PACKET\n'+json.dumps(view,ensure_ascii=False,separators=(',',':'))+'\n');actual={**req,'baseRequestSha256':hfile(request_path),'packetSha256':hfile(d/'packet.actual.json'),'promptBaseSha256':hfile(d/'prompt-base.actual.txt'),'materializedDependencies':pins};dump(d/'dispatch-request.json',actual);print(json.dumps({'materialized':req['jobId'],'children':len(children),'actualContrasts':len(packet['units'])}))
