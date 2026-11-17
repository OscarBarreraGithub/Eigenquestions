"""Bound the46 remaining immutable pilot-queue cases; no fresh semantic holdout."""
import collections,hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent;L=F/'native-local/clauses-wave-v2';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();oldindex=F/'repairs-v1/source-index.json';index=json.loads(oldindex.read_text());queuepath=F/'native-local/clause-repair-queue-v1.json';assert sha(queuepath)==index['queueSha256'];queue=json.loads(queuepath.read_text())['cases'];wanted=set(index['remainingCaseIds']);assert len(wanted)==46;groups=collections.defaultdict(list)
for c in queue:
 if c['caseId'] in wanted:groups[c['caseId'].split(':')[0].rsplit('-',1)[0]].append(c)
batches=[];current=[]
for group in groups.values():
 chunks=[group[i:i+6] for i in range(0,len(group),6)]
 for chunk in chunks:
  if current and len(current)+len(chunk)>8:batches.append(current);current=[]
  current+=chunk
if current:batches.append(current)
families=[]
for i,cases in enumerate(batches):
 key=f'remaining-clauses-{i+1:02}';packet={'schemaVersion':'q025-clause-source-packet/1','familyId':key,'stage':'proposal','cases':cases,'priorReview':None,'evidence':[],'refRegistry':{},'priorQueueSha256':sha(queuepath),'pilotIndexSha256':sha(oldindex),'readingLimit':'Only exact clauses, scope definitions and pertinent bounded primary/context evidence. Original proposal/challenge lineage retained per case. This is an annotation review, not a new whole-region read or a semantic holdout.'};path=L/'sources'/f'{key}.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(packet,ensure_ascii=False,separators=(',',':'))+'\n');families.append({'familyId':key,'sourcePacketPath':str(path.relative_to(E)),'sourcePacketSha256':sha(path),'caseIds':[c['caseId'] for c in cases],'caseCount':len(cases),'bytes':path.stat().st_size})
assert {x for f in families for x in f['caseIds']}==wanted;out={'schemaVersion':'q025-clause-continuation-intake/1','queueSha256':sha(queuepath),'priorPilotIndexSha256':sha(oldindex),'priorCompletedPilotCases':12,'remainingCases':46,'families':families,'nativeLaunches':0};(B/'source-index.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'batches':len(families),'cases':46,'sizes':[f['caseCount'] for f in families]}))
