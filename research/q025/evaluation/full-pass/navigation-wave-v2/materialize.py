import copy,hashlib,json,sys
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent;W=E.parents[2];sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
def materialize(request_path,runtime):
 d=Path(request_path).resolve().parent;req=json.loads(Path(request_path).read_text());source=E/req['originalPacketPath'];assert sha(source)==req['originalPacketSha256'];p=json.loads(source.read_text());p['stage']=req['stage'];actual={**req,'baseRequestSha256':sha(request_path)}
 if req['dependsOn']:
  prior=Path(runtime)/'jobs'/req['dependsOn'];receipt=json.loads((prior/'receipt.json').read_text());assert receipt['status']=='complete'and receipt['normalizedReplySha256']==sha(prior/'reply.json');p['priorReview']=json.loads((prior/'reply.json').read_text());
  for kind,key in [('prior_authored_scope','newQuestions'),('prior_typed_decision','decisions'),('prior_navigation_candidate','navigation')]:
   for obj in p['priorReview'].get(key,[]):
    ref=obj['id'];assert ref not in p['refRegistry'];p['refRegistry'][ref]={'kind':kind,'objectValueSha256':hashlib.sha256(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'notPrimary':True}
  actual.update({'priorReceiptSha256':sha(prior/'receipt.json'),'priorReplySha256':sha(prior/'reply.json')})
 for u in p['units']:assert hashlib.sha256(u['description'].encode()).hexdigest()==p['refRegistry'][u['ref']]['textSha256']
 dump(d/'packet.actual.json',p);text=(B/'INSTRUCTIONS.md').read_text();assert text.count('{{MAX_OUTPUT_CHARACTERS}}')==1;view={k:v for k,v in p.items()if k not in ['refRegistry','machineBindings']};(d/'prompt-base.actual.txt').write_text(text.replace('{{MAX_OUTPUT_CHARACTERS}}',str(req['maxOutputCharacters']))+'\n\nEXACT NAVIGATION DECISION PACKET\n'+json.dumps(view,ensure_ascii=False,separators=(',',':'))+'\n');actual.update({'packetSha256':sha(d/'packet.actual.json'),'promptBaseSha256':sha(d/'prompt-base.actual.txt')});dump(d/'dispatch-request.json',actual);return actual
if __name__=='__main__':print(json.dumps({'materialized':materialize(sys.argv[1],sys.argv[2])['jobId']}))
