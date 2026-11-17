"""Verify exact endpoint scopes and paired statements; attach a completed proposal."""
import hashlib,json,sys
from pathlib import Path
import contract
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent;W=E.parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def dump(p,x):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
def verified_pin(pin):
 p=(W/pin['path']).resolve();assert p.is_relative_to(W.resolve())and sha(p)==pin['sha256'],'changed or external pin '+pin['path'];return p
def source_pins(bindings):
 out=list(bindings['inputs'].values())
 for r in bindings['relationBindings'].values():
  for artifact in r['originalCandidate']['reviewPins'].values():
   base=E/artifact['artifactDirectory']
   for k,v in artifact.items():
    if k.endswith('Sha256'):out.append({'path':str((base/k[:-6]).relative_to(W)),'sha256':v})
   if artifact.get('resolvedFromRequest'):out.append(artifact['resolvedFromRequest'])
 by={}
 for p in out:assert p['path']not in by or by[p['path']]['sha256']==p['sha256'];by[p['path']]=p
 return list(by.values())
def check_sources(view,binding):
 components=[read(verified_pin(binding['inputs'][k]))for k in ['scopeComponent','previouslyAdjudicatedParent']];definitions={d['id']:d for c in components for d in c['destinations']}
 scopes={s['ref']:s for s in view['scopes']};relations={r['ref']:r for r in view['relations']}
 assert scopes.keys()==binding['scopeBindings'].keys()and len(scopes)==len(view['scopes']),'scope inventory changed'
 assert relations.keys()==binding['relationBindings'].keys()and len(relations)==len(view['relations']),'route inventory changed'
 for ref,s in scopes.items():
  bound=binding['scopeBindings'][ref];d=definitions[bound['id']];assert d['scopeContentSha256']==bound['scopeContentSha256'],'scope hash changed'
  assert s=={'ref':ref,**{k:d[k]for k in ['kind','title','question','summary','scope','readingCoverage']}},'scope projection changed'
 for ref,r in relations.items():
  old=binding['relationBindings'][ref]
  assert binding['scopeBindings'][r['source']]['id']==old['sourceId']and binding['scopeBindings'][r['target']]['id']==old['targetId'],'route endpoints changed'
  assert r['nativeType']==old['nativeType']and r['proposalStatements']==[c['priorReason']for c in old['comparisons']]and r['challengeStatement']==old['currentReason'],'paired statement changed'
  assert r['originalEvidenceKinds']==sorted({x['kind']for c in old['comparisons']for x in c['priorRefs']+c['challengeRefs']}),'inherited evidence kinds changed'
  assert r['originalEvidenceProvidedAsText']is False,'fresh primary evidence claim'
 return {'scopeCount':len(scopes),'relationCount':len(relations),'primaryPagesSupplied':0}
def materialize(request_path,runtime):
 d=Path(request_path).resolve().parent;assert not(d/'dispatch-request.json').exists(),'already materialized; no redispatch';req=read(request_path)
 for p in req['sourcePins']:verified_pin(p)
 view=read(verified_pin({'path':str((E/req['originalPacketPath']).relative_to(W)),'sha256':req['originalPacketSha256']}));binding=read(verified_pin(req['bindings']));check_sources(view,binding)
 p={**view,'stage':req['stage'],'priorReview':None};actual={**req,'baseRequestSha256':sha(request_path)}
 if req['dependsOn']:
  prior=Path(runtime)/'jobs'/req['dependsOn'];receipt=read(prior/'receipt.json');assert receipt['status']=='complete'and receipt['sourceOnly']and not receipt['toolUseAttempted'],'prior not complete source-only'
  assert receipt['normalizedReplySha256']==sha(prior/'reply.json')and receipt['inputPins']['packetSha256']==sha(prior/'packet.actual.json'),'prior receipt mismatch'
  pp=read(prior/'packet.actual.json');assert {k:v for k,v in pp.items()if k not in ['stage','priorReview']}==view and pp['stage']=='proposal','prior packet differs'
  proposal=read(prior/'reply.json');contract.evaluate(pp,proposal);p['priorReview']=proposal;actual.update(priorReceiptSha256=sha(prior/'receipt.json'),priorReplySha256=sha(prior/'reply.json'))
 dump(d/'packet.actual.json',p);instructions=(B/'INSTRUCTIONS.md').read_text();assert instructions.count('{{MAX_OUTPUT_CHARACTERS}}')==1
 prompt=instructions.replace('{{MAX_OUTPUT_CHARACTERS}}',str(req['maxOutputCharacters']))+'\n\nSOURCE PACKET\n'+json.dumps(p,ensure_ascii=False,separators=(',',':'))
 (d/'prompt-base.actual.txt').write_text(prompt);actual.update(packetSha256=sha(d/'packet.actual.json'),promptBaseSha256=sha(d/'prompt-base.actual.txt'));dump(d/'dispatch-request.json',actual)
if __name__=='__main__':materialize(sys.argv[1],Path(sys.argv[2]))
