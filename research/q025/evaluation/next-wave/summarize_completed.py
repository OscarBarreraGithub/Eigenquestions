#!/usr/bin/env python3
"""Summarize completed immutable reviews; never inspect partial scientific output or mutate jobs."""
import collections,hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent;L=B/'native-local';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
state=json.loads((L/'state.json').read_text());records=[];usage=collections.Counter()
for jid,s in state['jobs'].items():
 if s['status'] not in ['complete','failed','blocked']:continue
 d=L/'jobs'/jid
 if s['status']!='complete':
  records.append({'jobId':jid,'status':s['status'],'reason':json.loads((d/'receipt.json').read_text()).get('error') if (d/'receipt.json').exists() else s.get('reason'),'scientificInterpretation':'Operational failure/pending dependency is not a scientific membership verdict.'});continue
 r=json.loads((d/'reply.json').read_text());receipt=json.loads((d/'receipt.json').read_text());packet=json.loads((d/'packet.json').read_text())
 assert sha(d/'reply.raw.txt')==receipt['replySha256'] and json.loads((d/'reply.raw.txt').read_text())==r
 assert receipt['model']=='gpt-6-astra' and receipt['effort']=='xhigh' and not receipt['toolUseAttempted'];usage.update(receipt.get('usage') or {})
 units={u['unitIndex']:u for u in packet['units']};factors=r['factorDictionary'];counts=collections.Counter(a['disposition'] for a in r['unitAssessments']);agreements=collections.Counter(a['priorAssignmentAgreement'] for a in r['unitAssessments'])
 cards=[]
 for c in r['questionCards']:
  cards.append({k:c[k] for k in ['localId','title','question','summary','scope','methods','identityStatus','existingQuestionRef','scientificStatus','readingLimit'] }|{'contributionRoles':dict(collections.Counter(x['role'] for x in c['sourceContributions'])),'sourceExcerptPaperIds':sorted({units[x['unitIndex']]['paperId'] for x in c['sourceContributions'] if x['basis']=='source_excerpt_checked'}),'evidenceIds':c['evidenceIds']})
 records.append({'jobId':jid,'status':'complete','originalRegionVerdict':r['verdict'],'summary':r['summary'],'regionTitle':r['regionCard']['title'],'regionQuestion':r['regionCard']['question'],'coverage':r['coverage'],'dispositionCounts':dict(counts),'assignmentAgreementCounts':dict(agreements),'factorCounts':dict(collections.Counter(f['kind'] for f in factors)),'factorStatusCounts':dict(collections.Counter(f['status'] for f in factors)),'proposedQuestionCards':cards,'priorCardAssessments':r['priorCardAssessments'],'identityAssessments':r['identityAssessments'],'limitations':r['limitations'],'unresolvedQuestions':r['unresolvedQuestions'],'replyArtifactSha256':sha(d/'reply.json'),'rawReplySha256':receipt['replySha256'],'receiptSha256':sha(d/'receipt.json'),'elapsedSeconds':round((receipt['finishedAt']-receipt['startedAt'])/1000,1),'usage':receipt.get('usage')})
out={'schemaVersion':'q025-calibration-scientific-progress/1','status':'complete' if all(s['status'] in ['complete','failed','blocked'] for s in state['jobs'].values()) else 'in_progress','interpretation':'Completed source-only review proposals and explicit challenge agreement only. Original-basin needs_revision does not invalidate all new cards; rewritten challenger cards are not independently accepted. No scientific implication promoted. No raw primary excerpts included.','stateCounts':dict(collections.Counter(s['status'] for s in state['jobs'].values())),'completedUsage':dict(usage),'records':records}
(B/'scientific-progress.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n');print(json.dumps({'status':out['status'],'stateCounts':out['stateCounts'],'reportedStages':len(records),'usage':dict(usage)},indent=2))
