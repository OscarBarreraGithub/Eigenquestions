"""Exact completed-screen coverage and prioritization; no scientific admission."""
import collections, hashlib, json
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;W=F.parents[3];L=F/'native-local/canonical-triage-v1/jobs'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
counts={k:collections.Counter() for k in ['identityScreen','priority','scientificConnections']};jobs=[];scopes=set();comparisons=set();workloads=set()
for d in sorted(L.glob('*-screen')):
 receipt=json.loads((d/'receipt.json').read_text());assert receipt['status']=='complete'
 r=json.loads((d/'reply.json').read_text());p=json.loads((d/'packet.actual.json').read_text())
 assert sha(d/'reply.json')==receipt['normalizedReplySha256']
 assert {x['ref'] for x in r['scopeReviews']}=={x['ref'] for x in p['scopes']}
 assert {x['ref'] for x in r['comparisonReviews']}=={x['ref'] for x in p['nominations']}
 assert len(r['scopeReviews'])==len(p['scopes']);assert len(r['comparisonReviews'])==len(p['nominations'])
 scopes.update(x['ref'] for x in p['scopes']);comparisons.update(x['ref'] for x in p['nominations'])
 for row in r['comparisonReviews']:
  counts['identityScreen'][row['identityScreen']]+=1;counts['priority'][row['priority']]+=1;counts['scientificConnections'].update(row['scientificConnections'])
 jobs.append({'jobId':d.name,'scopeReviews':len(r['scopeReviews']),'comparisonReviews':len(r['comparisonReviews']),'rawResponseCharacters':len((d/'reply.raw.txt').read_text()),'pins':{name:sha(d/name) for name in ['packet.actual.json','reply.json','reply.raw.txt','receipt.json']},'artifactDirectory':str(d.relative_to(W)),'summary':r['summary'],'independence':receipt['independence']})
 out={'schemaVersion':'q025-screen-pilot-assessment/1','status':'four_single_pass_screens_complete_no_admission','jobs':jobs,'scopeExposures':sum(j['scopeReviews'] for j in jobs),'uniqueScopeRefs':len(scopes),'comparisonJudgments':sum(j['comparisonReviews'] for j in jobs),'uniqueComparisonRefs':len(comparisons),'judgmentCounts':{k:dict(v) for k,v in counts.items()},'completedComparisonRefs':sorted(comparisons),'completedScopeRefs':sorted(scopes),'coverageAmendment':{'path':str((F/'canonical-triage-v1/coverage-amendment.md').relative_to(W)),'sha256':sha(F/'canonical-triage-v1/coverage-amendment.md')},'reviewedEvidence':'Whole supplied scope definitions and source descriptions, scope-level prior assessment notes and paired-role metadata. Both per-unit attribution notes were absent. No fresh primary reading.','admissions':{'identities':0,'scopes':0,'homes':0,'scientificRelations':0},'nextDecisionPolicy':'An escalation category is not a request to reread every pair. Group shared exact scopes and existing review context. Add both per-unit notes for source attribution. Use primary evidence only when resolving consequential premise uncertainty, changing scope meaning or asserting a substantive scientific relation.'}
(B/'pilot-assessment.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:out[k] for k in ['scopeExposures','uniqueScopeRefs','comparisonJudgments','uniqueComparisonRefs','judgmentCounts']}))
