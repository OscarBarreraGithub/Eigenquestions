"""Retain exact whitespace-loop failure; do not invent missing scientific records."""
import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;d=F/'native-local/full-leaf-wave-v3/jobs/leaf-54e3e83d0ccbf2700b0f-proposal';s=(d/'reply.stream.raw.txt').read_text();p=json.loads((d/'packet.json').read_text());r=json.loads((d/'receipt.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();decoder=json.JSONDecoder();i=1;fields={}
while i<len(s):
 while i<len(s) and (s[i].isspace() or s[i]==','):i+=1
 try:
  key,end=decoder.raw_decode(s,i);i=end
  while s[i].isspace():i+=1
  assert s[i]==':';i+=1
  while s[i].isspace():i+=1
  value,end=decoder.raw_decode(s,i);fields[key]=value;i=end
 except (json.JSONDecodeError,IndexError):break
report={'schemaVersion':'q025-native-whitespace-failure-audit/1','jobId':r['jobId'],'originalStatus':r['status'],'originalError':r['error'],'receiptSha256':sha(d/'receipt.json'),'retainedStreamSha256':sha(d/'reply.stream.raw.txt'),'sourcePacketSha256':sha(d/'packet.json'),'streamCharacters':len(s),'tabCharacters':s.count('\t'),'trailingWhitespaceCharacters':len(s)-len(s.rstrip()),'nonWhitespaceCharacters':sum(not x.isspace() for x in s),'completeTopLevelFieldNames':list(fields),'completeCardCount':0,'completeUnitAssessmentCount':0,'requiredUnitAssessments':len(p['units']),'rawFinalExists':(d/'reply.raw.txt').exists(),'interpretation':'The model stream enters a repeated-tab loop inside the first card after readingLimit; mandatory card fields and all42unit rows are absent. The broadregion text is a complete proposal component only. Trimming whitespace cannot repair missing scientific coverage.','recoveryPolicy':'Preserve original failed receipt and blocked descendant jobs. A separately pinned small proposal/challenge recovery may reread these same42rows; no automatic retry, invented aliases field, fabricated coverage or relabeling of the original failure.'};(B/'failure-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
