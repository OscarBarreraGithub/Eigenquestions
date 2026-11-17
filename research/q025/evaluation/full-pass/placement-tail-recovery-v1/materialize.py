"""Locked-tail assembly and actual independent challenge preparation."""
import importlib.util,json,sys
from pathlib import Path
import contract
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent;W=E.parents[2]
spec=importlib.util.spec_from_file_location('old_source_checks',F/'placement-continuation-v1/materialize.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
read,dump,sha,verified_pin,check_sources=old.read,old.dump,old.sha,old.verified_pin,old.check_sources

def materialize(request_path,runtime):
 d=Path(request_path).resolve().parent;assert not(d/'dispatch-request.json').exists(),'already materialized; no redispatch';req=read(request_path)
 for pin in req['sourcePins']:verified_pin(pin)
 view=read(E/req['originalPacketPath']);assert sha(E/req['originalPacketPath'])==req['originalPacketSha256'];check_sources(view,read(verified_pin(view['sidecar'])))
 packet={**view,'stage':req['stage'],'priorReview':None};actual={**req,'baseRequestSha256':sha(request_path)}
 if req.get('completion'):
  prefix=read(E/req['prefixPath']);assert sha(E/req['prefixPath'])==req['prefixSha256'];complete=prefix['topLevelPrefix']['completeFields'];scope=prefix['partialFirstScope']['completeFields'];assert len(complete['placements'])==len(view['units']);assert set(prefix['topLevelPrefix']['completeArrayPrefixes'])=={'newScopes'}and not prefix['topLevelPrefix']['completeArrayPrefixes']['newScopes']
  packet['lockedCompletion']={'completeFields':complete,'partialNewScopes':[scope],'prefixSha256':req['prefixSha256'],'originalStreamSha256':prefix['originalStreamSha256']}
  refs={ref for ref in scope['refs']if ref.startswith('u')};public={'familyId':packet['familyId'],'stage':'proposal','lockedCompletion':packet['lockedCompletion'],'newScopeSourceUnits':[u for u in view['units']if u['ref']in refs],'availableRevisionTargetScopes':view['scopes'],'readingLimits':view['readingLimits']};instruction=B/'TAIL-INSTRUCTIONS.md'
 else:
  prior=Path(runtime)/'jobs'/req['dependsOn'];receipt=read(prior/'receipt.json');assert receipt['status']=='complete'and receipt['sourceOnly']and not receipt['toolUseAttempted'];assert receipt['normalizedReplySha256']==sha(prior/'reply.json')and receipt['inputPins']['packetSha256']==sha(prior/'packet.actual.json'),'prior receipt mismatch';pp=read(prior/'packet.actual.json');assert {k:v for k,v in pp.items()if k not in ['stage','priorReview','lockedCompletion']}==view,'prior scientific packet changed'
  proposal=read(prior/'reply.json');contract.base.evaluate({**view,'stage':'proposal','priorReview':None},proposal);packet['priorReview']=proposal;actual.update(priorReceiptSha256=sha(prior/'receipt.json'),priorReplySha256=sha(prior/'reply.json'))
  public={k:v for k,v in packet.items()if k not in ['sidecar','reviewNamespaces']};public['reviewNamespaces']={k:'review-scoped historical context'for k in packet['reviewNamespaces']};instruction=B/'INSTRUCTIONS.md'
 dump(d/'packet.actual.json',packet);text=instruction.read_text();assert text.count('{{MAX_OUTPUT_CHARACTERS}}')==1;prompt=text.replace('{{MAX_OUTPUT_CHARACTERS}}',str(req['maxOutputCharacters']))+'\n\nPRESERVED SOURCE RECORD\n'+json.dumps(public,ensure_ascii=False,separators=(',',':'));(d/'prompt-base.actual.txt').write_text(prompt);actual.update(packetSha256=sha(d/'packet.actual.json'),promptBaseSha256=sha(d/'prompt-base.actual.txt'));dump(d/'dispatch-request.json',actual)
if __name__=='__main__':materialize(sys.argv[1],sys.argv[2])
