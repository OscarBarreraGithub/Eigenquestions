#!/usr/bin/env python3
"""Seal post-rule contrast expectations before inspecting the lexical factor draft."""
import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent;E=B.parent
ledger=json.loads((E/'current-relation-ledger.json').read_text())
choices=[('FC01','production-006','Compare the physical scope and differential-equation operations of these two source methods. Which navigation connections, if any, follow; which question identities or physical conclusions remain separate?'),('FC02','production-075','Compare the scalar-potential and spectrum procedures in these two source methods. Identify what can share a route and what needs a separate scope.'),('FC03','production-019','Compare the input data, calculated target and operations of these two source methods. Decide the justified navigation relationship without assuming a common method from shared vocabulary.')]
public=[];secret=[]
for cid,tid,prompt in choices:
 r=next(x for x in ledger['records'] if x['taskId']==tid)
 public.append({'id':cid,'sourceObjectIds':r['nodeIds'],'paperIds':[e['paper_id'] for e in r['endpoints']],'prompt':prompt})
 secret.append({'id':cid,'basis':'Existing admitted receipt, not new gold derived from numerical clusters','taskId':tid,'sourceRelation':r,'expectedNavigationCategory':r['relationCategory'],'expectedCanonicalMerge':False,'neededAbstention':'Do not promote this source-object judgment into universal question-level edges; exact Q attachments must be separately established.'})
local=B/'reserved-expectations.local.json'
if local.exists():raise SystemExit('Refusing to overwrite sealed expectations')
local.write_text(json.dumps({'schemaVersion':'q025-factor-controls/1','developmentStatus':'Newly reserved rule-check controls from previously exposed source receipts; not blind source holdouts and not population-generalization evidence. No final24 papers consumed.','records':secret},indent=2)+'\n')
(B/'controls.json').write_text(json.dumps({'schemaVersion':'q025-factor-controls-public/1','expectationsSha256':hashlib.sha256(local.read_bytes()).hexdigest(),'status':'expectations_sealed_before_factor_rules_inspection','evaluationLimit':'Controls are absent from the87-unit factor cohort, but their underlying receipts exist in the shared admitted ledger. This is a post-rule audit, not a blind-source test.','records':public},indent=2)+'\n')
print('Reserved3 post-rule controls; no primary source texts or expected labels exported.')
