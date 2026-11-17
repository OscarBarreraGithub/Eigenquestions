#!/usr/bin/env python3
"""Validate evidence identities and final-status handling, not scientific correctness."""
import json,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
WORK=HERE.parents[2]
def main():
 suite=json.loads((HERE/'journeys.json').read_text());ledger=json.loads((HERE/'current-relation-ledger.json').read_text())
 units={u['id']:u for f in (WORK/'data/navigation').glob('units-*.json') for u in json.loads(f.read_text())}
 receipts={r['taskId']:r for r in ledger['records']}
 assert len(suite['cases'])==12
 checks=0;witnesses=set();papers=set()
 for c in suite['cases']:
  assert len(c['questionPrompts'])>=2 and len(c['entryRoutes'])>=2 and c['boundaryPrompts'] and c['failureConditions']
  represented=set()
  for w in c['witnesses']:
   u=units[w['unitId']];assert w['paperId']==u['paperId']; assert w['text']==u['text'];assert w['nodeIds']==u['evidence']['sourceNodeIds'];assert w['evidenceIds']==u['evidence']['anchors'];assert w['sourceSha256']==u['evidence']['sourceSha256']
   witnesses.add(w['unitId']);papers.add(w['paperId']);represented.add(w['paperId']);checks+=1
  assert set(c['requiredWitnessPaperIds'])<=represented
  if 'reviewWitness' in c:
   r=c['reviewWitness'];current=receipts[r['taskId']]
   for k,v in r.items(): assert current[k]==v,(c['id'],k)
 assert sum(r['admittedScientificEdge'] for r in receipts.values())==97
 assert sum(r['promotionWithheld'] for r in receipts.values())==5
 assert all(not r['admittedScientificEdge'] for r in receipts.values() if r['promotionWithheld'] or r['status']!='accepted_relation')
 raw=HERE/'witness-evidence.local.json';anchor_count=None
 if raw.exists():
  ev={e['id']:e for e in json.loads(raw.read_text())};want={e for w in witnesses for e in units[w]['evidence']['anchors']};assert want<=ev.keys();anchor_count=len(want)
  for uid in witnesses:
   u=units[uid]
   for aid in u['evidence']['anchors']:assert ev[aid]['paper_id']==u['paperId'] and ev[aid]['source_sha256']==u['evidence']['sourceSha256']
 reservation=HERE/'final-holdout-reservation.local.json';commit=json.loads((HERE/'holdout-commitment.json').read_text());assert hashlib.sha256(reservation.read_bytes()).hexdigest()==commit['reservationSha256']
 result=dict(schemaVersion='q025-suite-validation/1',status='pass',cases=12,witnessOccurrencesChecked=checks,uniqueWitnessUnits=len(witnesses),uniqueWitnessPapers=len(papers),resolvedPrimaryEvidenceAnchors=anchor_count,currentAdmittedScientificRelations=97,withheldExcluded=5,reservedHoldoutPapers=commit['paperCount'],scientificJudgment='Not certified by these structural checks',runtimeJourneys='Not yet executed',readingLimits='Archived text/excerpt reading and existing scoped reviews; no new full-paper reproduction or image verification')
 (HERE/'suite-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__': main()
