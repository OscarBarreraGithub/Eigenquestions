#!/usr/bin/env python3
"""Summarize immutable local pilot results without publishing primary-source packets."""
import collections, hashlib, json
from pathlib import Path
B=Path(__file__).resolve().parent
J=B/'native-review/native-local/jobs'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
records=[]; usage=collections.Counter(); papers=set(); assessments=collections.Counter()
for family in ['compactification3127','inflation729']:
 for stage in ['proposal','challenge','fresh']:
  job=f'{family}-{stage}'; d=J/job
  receipt=json.loads((d/'receipt.json').read_text()); reply=json.loads((d/'reply.json').read_text()); packet=json.loads((d/'packet.json').read_text())
  assert receipt['status']=='complete' and receipt['model']=='gpt-6-astra' and receipt['effort']=='xhigh'
  assert not receipt['toolUseAttempted'] and receipt['sourceOnly'] and receipt['sandbox']=='read-only'
  assert sha(d/'reply.raw.txt')==receipt['replySha256']
  assert json.loads((d/'reply.raw.txt').read_text())==reply
  assert not reply['fullMembershipCertified'] and reply['sampledOnly']
  assert len(reply['membershipAssessments'])==len(packet['samples'])
  assert {x['unitId'] for x in reply['membershipAssessments']}=={x['unitId'] for x in packet['samples']}
  usage.update(receipt['usage']); papers.update(x['paperId'] for x in packet['samples'])
  assessments.update(x['disposition'] for x in reply['membershipAssessments'])
  sample_papers={x['unitId']:x['paperId'] for x in packet['samples']}
  records.append({'jobId':job,'verdict':reply['verdict'],'title':reply['title'],'summary':reply['summary'],
    'replyArtifactSha256':sha(d/'reply.json'),'rawReplySha256':receipt['replySha256'],'receiptSha256':sha(d/'receipt.json'),
    'inputPins':receipt['inputPins'],'elapsedSeconds':round((receipt['finishedAt']-receipt['startedAt'])/1000,1),'usage':receipt['usage'],
    'membershipAssessments':[dict(a,paperId=sample_papers[a['unitId']]) for a in reply['membershipAssessments']],
    'identityAssessments':reply['identityAssessments'],'limitations':reply['limitations'],
    'fullMembershipCertified':False,'sampledOnly':True})
out={'schemaVersion':'q025-pilot-review-summary/2','status':'pilot_complete_scientific_revision_required',
 'interpretation':'Six completed source-only sampled reviews; no accepted full-region map. Exclusion from a narrow conjecture-testing question does not remove a source from a broader inflation family. Candidate memberships and numerical hierarchy remain proposals. Frozen requests and outputs unchanged.',
 'operationalValidation':{'jobs':len(records),'model':'gpt-6-astra','effort':'xhigh','sourceOnly':True,'toolUseAttempts':0,'allRawReplyHashesMatch':True,'allParsedRepliesMatchRaw':True,'fullMembershipCertified':False},
 'coverage':{'distinctSourcePapers':len(papers),'assessmentOccurrences':sum(assessments.values()),'dispositions':dict(assessments),'verdicts':dict(collections.Counter(x['verdict'] for x in records))},
 'usage':dict(usage),'records':records}
(B/'pilot-review-summary.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({k:out[k] for k in ['status','operationalValidation','coverage','usage']},indent=2))
