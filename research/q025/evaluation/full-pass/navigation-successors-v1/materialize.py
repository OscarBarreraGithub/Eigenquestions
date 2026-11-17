import copy,hashlib,json,sys
from pathlib import Path
import contract
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent;W=E.parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def dump(p,x):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
def materialize(request_path,runtime):
 d=Path(request_path).resolve().parent;assert not(d/'dispatch-request.json').exists(),'already materialized; no redispatch';req=read(request_path)
 for pin in req['immutablePins']:assert sha(E/pin['path'])==pin['sha256'],'changed source or adopted artifact'
 src=E/req['originalPacketPath'];assert sha(src)==req['originalPacketSha256'];p=read(src);adopted=E/req['adoptedProposalPath'];receipt=read(adopted/'receipt.json')
 assert receipt['status']=='complete' and receipt['originalNativeStatus']=='failed' and receipt['scientificContentChanged']is False and receipt['nativeReviewRepeated']is False,'not a valid deterministic adoption'
 assert sha(adopted/'receipt.json')==req['adoptedReceiptSha256'] and sha(adopted/'reply.json')==receipt['normalizedReplySha256'],'adopted proposal receipt mismatch'
 prior=read(adopted/'reply.json');assert prior==read(adopted/'reply.raw.txt'),'logical scientific content changed';contract.evaluate(p,prior)
 p['stage']='challenge';p['priorReview']=prior
 for kind,key in [('prior_authored_scope','newQuestions'),('prior_typed_decision','decisions'),('prior_navigation_candidate','navigation')]:
  for obj in prior.get(key,[]):
   ref=obj['id'];assert ref not in p['refRegistry'],'prior reference collision';p['refRegistry'][ref]={'kind':kind,'objectValueSha256':contract.shared.base.vh(obj),'notPrimary':True,'notIndependentSourceEvidence':True}
 p['representationRecovery']={'kind':'current_authored_scope_context_registration','originalFailedReceiptSha256':receipt['originalFailedReceipt']['sha256'],'adoptedReceiptSha256':req['adoptedReceiptSha256'],'scientificContentChanged':False,'newPrimaryEvidence':False,'instruction':'Independently challenge all original scientific decisions; authored scope context is not evidence proving that scope.'}
 for u in p['units']:assert hashlib.sha256(u['description'].encode()).hexdigest()==p['refRegistry'][u['ref']]['textSha256'],'source description changed'
 assert not p['evidence'],'This successor authorizes no new primary-source text'
 dump(d/'packet.actual.json',p);text=(B/'INSTRUCTIONS.md').read_text();assert text.count('{{MAX_OUTPUT_CHARACTERS}}')==1;view={k:v for k,v in p.items()if k not in ['refRegistry','machineBindings']};(d/'prompt-base.actual.txt').write_text(text.replace('{{MAX_OUTPUT_CHARACTERS}}',str(req['maxOutputCharacters']))+'\n\nEXACT NAVIGATION DECISION PACKET\n'+json.dumps(view,ensure_ascii=False,separators=(',',':'))+'\n')
 actual={**req,'baseRequestSha256':sha(request_path),'packetSha256':sha(d/'packet.actual.json'),'promptBaseSha256':sha(d/'prompt-base.actual.txt'),'priorReceiptSha256':req['adoptedReceiptSha256'],'priorReplySha256':sha(adopted/'reply.json'),'priorRawReplySha256':sha(adopted/'reply.raw.txt')};dump(d/'dispatch-request.json',actual);return actual
if __name__=='__main__':print(json.dumps({'materialized':materialize(sys.argv[1],sys.argv[2])['jobId']}))
