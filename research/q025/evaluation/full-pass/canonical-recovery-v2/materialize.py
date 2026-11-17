import hashlib,json,sys
from pathlib import Path
from contract import evaluate,base
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
def materialize(request_path,runtime):
 d=Path(request_path).resolve().parent;req=json.loads(Path(request_path).read_text());source=E/req['originalPacketPath'];assert sha(source)==req['originalPacketSha256'];packet=json.loads(source.read_text());packet['stage']=req['stage'];pins={}
 if req['stage']=='proposal':
  prefix=E/req['prefixPath'];assert sha(prefix)==req['prefixSha256'];packet['preservedComponents']=json.loads(prefix.read_text());packet['prefixArtifactSha256']=sha(prefix);packet['streamVariants']=packet['preservedComponents']['streamVariants']
 else:
  old=d.parent/req['dependsOn'];r=json.loads((old/'receipt.json').read_text());assert r['status']=='complete' and not r.get('toolUseAttempted');assert sha(old/'reply.raw.txt')==r['replySha256'];assert sha(old/'reply.json')==r['normalizedReplySha256'];normal=json.loads((old/'normalization.json').read_text());assert sha(old/'normalization.json')==r['normalizationReceiptSha256'];assert normal['originalCompleteFieldsChanged'] is False and normal['discardedCompleteScientificComponents']==0;prior=json.loads((old/'reply.json').read_text());check={**packet,'stage':'proposal','priorReview':None};base.evaluate(check,prior);packet['priorReview']=prior;prefix=E/req['prefixPath'];assert sha(prefix)==req['prefixSha256'];packet['streamVariants']=json.loads(prefix.read_text())['streamVariants'];packet['priorStreamVariantAssessments']=normal.get('streamVariantAssessments',[]);pins={'priorReplySha256':sha(old/'reply.json'),'priorRawReplySha256':r['replySha256'],'priorReceiptSha256':sha(old/'receipt.json'),'prefixArtifactSha256':normal['prefixArtifactSha256']}
 dump(d/'packet.actual.json',packet);view={k:v for k,v in packet.items() if k!='sourceReviews'};(d/'prompt-base.actual.txt').write_text((B/'INSTRUCTIONS.md').read_text()+'\n\nEXACT RECOVERY PACKET\n'+json.dumps(view,ensure_ascii=False,separators=(',',':'))+'\n');actual={**req,**pins,'baseRequestSha256':sha(request_path),'packetSha256':sha(d/'packet.actual.json'),'promptBaseSha256':sha(d/'prompt-base.actual.txt')};dump(d/'dispatch-request.json',actual);return actual
if __name__=='__main__':print(json.dumps({'materialized':materialize(sys.argv[1],sys.argv[2])['jobId']}))
