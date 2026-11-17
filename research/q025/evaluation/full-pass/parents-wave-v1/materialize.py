"""Materialize one parent only from complete, hash-bound child review artifacts."""
import json,sys
from pathlib import Path
import contract  # Local schema amendment in this process; frozen source files unchanged.
from build_child_artifact import build
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent;sys.path.insert(0,str(F/'parents-v1'));from parent_pipeline import make_parent_packet
from compact_pipeline import dump,hfile

def materialize(request_path,runtime):
 request_path=Path(request_path).resolve();d=request_path.parent;req=json.loads(request_path.read_text());runtime=Path(runtime).resolve();source=E/req['originalPacketPath'];assert hfile(source)==req['originalPacketSha256'];original=json.loads(source.read_text());original['fullMemberCount']=req['fullMemberCount'];plan=json.loads((F/'coverage-plan.json').read_text());regions={r['reviewKey']:r for r in plan['regions']};members=json.loads((F/'coverage-memberships.local.json').read_text());children=[];pins=[]
 for dep in req['childDependencies']:
  job=E/dep['jobPath'];receipt=json.loads((job/'receipt.json').read_text());assert receipt['status']=='complete','Child has not completed';artifact=build(job,regions[dep['reviewKey']],members[dep['reviewKey']]);target=runtime/'child-artifacts'/f'{dep["reviewKey"]}.json'
  if target.exists():assert json.loads(target.read_text())==artifact,'Frozen child artifact changed'
  else:dump(target,artifact)
  artifact['artifactSha256']=hfile(target);children.append(artifact);pins.append({'reviewKey':dep['reviewKey'],'kind':dep['kind'],'path':str(target.relative_to(E)),'sha256':hfile(target),'childReceiptSha256':hfile(job/'receipt.json'),'childReplySha256':hfile(job/'reply.json')})
 prior=None;priorpins={}
 if req['stage']=='challenge':
  job=d.parent/req['dependsOn'];r=json.loads((job/'receipt.json').read_text());assert r['status']=='complete' and not r.get('toolUseAttempted');assert hfile(job/'reply.json')==r['normalizedReplySha256'];assert hfile(job/'reply.raw.txt')==r['replySha256'];prior=json.loads((job/'reply.json').read_text());priorpins={'priorReplySha256':hfile(job/'reply.json'),'priorRawReplySha256':r['replySha256'],'priorReceiptSha256':hfile(job/'receipt.json')}
 packet,view=make_parent_packet(original,children,req['stage'],prior);dump(d/'packet.actual.json',packet);(d/'prompt-base.actual.txt').write_text((B/'INSTRUCTIONS.md').read_text()+'\n\nPARENT SYNTHESIS PACKET\n'+json.dumps(view,ensure_ascii=False,separators=(',',':'))+'\n');actual={**req,**priorpins,'baseRequestSha256':hfile(request_path),'packetSha256':hfile(d/'packet.actual.json'),'promptBaseSha256':hfile(d/'prompt-base.actual.txt'),'childArtifacts':pins};dump(d/'dispatch-request.json',actual);return actual
if __name__=='__main__':
 actual=materialize(sys.argv[1],sys.argv[2]);print(json.dumps({'materialized':actual['jobId'],'childArtifacts':len(actual['childArtifacts'])}))
