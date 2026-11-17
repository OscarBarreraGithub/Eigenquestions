"""Preserve complete values from every partial JSON attempt; never splice attempts."""
import hashlib,json,re
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;L=F/'native-local/canonical-recovery-v2';L.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();reports=[]
def parse_attempt(s,start):
 dec=json.JSONDecoder();i=start+1;out={};prefix={};ranges=[]
 def bound(a,b):return {'start':len(s[:a].encode()),'end':len(s[:b].encode()),'sha256':hashlib.sha256(s[a:b].encode()).hexdigest()}
 while i<len(s):
  while i<len(s) and (s[i].isspace() or s[i]==','):i+=1
  try:
   k,j=dec.raw_decode(s,i);i=j
   while s[i].isspace():i+=1
   assert s[i]==':';i+=1
   while s[i].isspace():i+=1
   begin=i
   try:v,j=dec.raw_decode(s,i);out[k]=v;ranges.append({'field':k,'complete':True,**bound(begin,j)});i=j
   except json.JSONDecodeError:
    assert s[i]=='[';i+=1;values=[]
    while i<len(s):
     while i<len(s) and (s[i].isspace() or s[i]==','):i+=1
     begin=i
     try:v,j=dec.raw_decode(s,i);values.append(v);ranges.append({'field':k,'index':len(values)-1,'complete':True,**bound(begin,j)});i=j
     except json.JSONDecodeError:break
    prefix[k]=values;break
  except (IndexError,json.JSONDecodeError):break
 return {'jsonStartByte':len(s[:start].encode()),'completeFields':out,'completeArrayPrefixes':prefix,'exactValueRanges':ranges}
for family in ['mediation-scope','control-statistics']:
 d=F/'native-local/canonical-pilot-v1/jobs'/f'canonical-{family}-proposal';s=(d/'reply.stream.raw.txt').read_text();starts=[m.start() for m in re.finditer(r'\{\s*"version"\s*:\s*"q025-canonical-review/1"',s)];attempts=[parse_attempt(s,i) for i in starts];selected=attempts[-1];assert selected['completeFields']['familyId']==family;variants=[]
 for ai,a in enumerate(attempts[:-1]):
  for q in a['completeFields'].get('newQuestions',a['completeArrayPrefixes'].get('newQuestions',[])):variants.append({'variantRef':f'attempt{ai}:{q["id"]}','selectedQuestionRef':q['id'],'earlierDefinition':q,'status':'earlier_partial_attempt_requires_conflict_review_not_silent_discard'})
 artifact={'schemaVersion':'q025-complete-stream-components/2','familyId':family,'originalFailedReceiptSha256':sha(d/'receipt.json'),'retainedStreamSha256':sha(d/'reply.stream.raw.txt'),'sourcePacketSha256':sha(d/'packet.actual.json'),'offsetUnit':'utf8_bytes',**selected,'earlierAttempts':attempts[:-1],'streamVariants':variants,'selectionBasis':'Latest coherent top-level JSON attempt is the provisional candidate; all complete earlier definitions remain explicit variants for independent conflict review. Native cause of restart is not established.','scientificStatus':'Preserved proposal components only; no scientific admission or invented final tail.'};p=L/f'prefix-{family}.json';p.write_text(json.dumps(artifact,ensure_ascii=False,separators=(',',':'))+'\n');report={k:artifact[k] for k in ['schemaVersion','familyId','originalFailedReceiptSha256','retainedStreamSha256','sourcePacketSha256','jsonStartByte','offsetUnit','selectionBasis','scientificStatus']};report.update(prefixArtifactSha256=sha(p),prefixPath=str(p.relative_to(F.parent)),completeQuestions=len(selected['completeFields'].get('newQuestions',[])),completeDecisions=len(selected['completeFields'].get('decisions',selected['completeArrayPrefixes'].get('decisions',[]))),completePairConstraints=len(selected['completeArrayPrefixes'].get('pairConstraints',[])),earlierCompleteQuestionVariants=len(variants),attemptStartBytes=[a['jsonStartByte'] for a in attempts],exactValueRanges=selected['exactValueRanges']);reports.append(report)
(B/'prefix-audit.json').write_text(json.dumps({'schemaVersion':'q025-dual-canonical-prefix-audit/2','families':reports},indent=2)+'\n');print(json.dumps([{k:r[k] for k in ['familyId','completeQuestions','completeDecisions','completePairConstraints','earlierCompleteQuestionVariants']} for r in reports]))
