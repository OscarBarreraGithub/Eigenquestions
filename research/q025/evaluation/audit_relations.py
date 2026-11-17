#!/usr/bin/env python3
"""Read-only reconstruction of current scientific admissions; writes only Q-025 evaluation."""
import argparse, collections, hashlib, json
from pathlib import Path
HERE=Path(__file__).resolve().parent
UPSTREAM=Path('/Users/emmy/Developer/physics-atlas-swampland')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--upstream',type=Path,default=UPSTREAM);a=ap.parse_args();root=a.upstream
 audit_path=root/'components/atlas_audit/snapshots/native-receipt-final-audit-81c4bb81bb01f18c.json'
 assert sha(audit_path)=='81c4bb81bb01f18ca98c29f9ad0bafaecb25effab6add102eab5aa8acb331381'
 audit=json.loads(audit_path.read_text()); state_path=root/'atlas-relations/state.json';state=json.loads(state_path.read_text())
 latest={x['task_id']:x for x in audit['records'] if x['latest_context']}
 records=[]
 for s in state['records']:
  task=s['task_id']; rev=s.get('context_revision',0)
  path=root/'atlas-relations/results'/task/f'context-{rev}.json' if rev else root/'atlas-relations/results'/f'{task}.json'
  r=json.loads(path.read_text());assert sha(path)==s['receipt_sha256']==latest[task]['receipt_sha256'];assert r['status']==latest[task]['status']==s['outcome']
  p=r.get('proposal',{});v=r.get('validation',{}); admitted=r['status']=='accepted_relation' and not r.get('promotion_withheld',False)
  if admitted: assert v['verdict']=='accept' and p['relation_category']==v['audited_category'] and p['direction']==v['audited_direction']
  packet_path=Path(s['proposal']['job_dir'])/'packet.json'; packet=json.loads(packet_path.read_text())
  endpoints=[]
  for n in packet.get('nodes',[]):
   if isinstance(n,dict):endpoints.append({k:n.get(k) for k in ['id','paper_id','paper_key','type','text','evidence_ids']})
  records.append(dict(taskId=task,contextRevision=rev,receiptPath=str(path.relative_to(root)),receiptSha256=sha(path),status=r['status'],promotionWithheld=r.get('promotion_withheld',False),admittedScientificEdge=admitted,relationCategory=p.get('relation_category'),direction=p.get('direction'),nodeIds=r['node_ids'],endpoints=endpoints,exactAssertion=p.get('exact_assertion'),applicability=p.get('applicability'),conventionDictionary=p.get('convention_dictionary'),evidenceIds=p.get('evidence_ids',[]),limitations=p.get('limitations',[]),readerNote=r.get('reader_note'),withholdingReason=r.get('coordinator_withholding',{}).get('expected_error'),reviewExposure=r.get('review_exposure'),sourcePacketPath=str(packet_path.relative_to(root)),sourcePacketSha256=sha(packet_path)))
 counts=dict(collections.Counter(r['status'] for r in records));cats=dict(collections.Counter(r['relationCategory'] for r in records if r['admittedScientificEdge']))
 assert counts==audit['latest_context_counts'];assert sum(r['promotionWithheld'] for r in records)==5
 output=dict(schemaVersion='q025-current-relation-ledger/1',upstreamRoot=str(root),auditPath=str(audit_path.relative_to(root)),auditSha256=sha(audit_path),stateSha256=sha(state_path),admissionRule='Use latest_context receipt pinned by immutable audit, require status accepted_relation and promotionWithheld false; retain exact category, direction, premises, conventions, limits and readerNote. Accepted dossiers are bounded reconstructions, not pair edges. Every other status produces no positive edge.',counts=counts,acceptedCategories=cats,withheldCurrent=5,records=sorted(records,key=lambda x:x['taskId']))
 (HERE/'current-relation-ledger.json').write_text(json.dumps(output,indent=2)+'\n')
 print(json.dumps({k:output[k] for k in ['counts','acceptedCategories','withheldCurrent']},indent=2))
if __name__=='__main__':main()
