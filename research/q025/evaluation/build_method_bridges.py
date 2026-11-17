#!/usr/bin/env python3
"""Export scoped source-object method controls, retaining evidence locators, not excerpts."""
import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent
UP=Path('/Users/emmy/Developer/physics-atlas-swampland')
ledger=json.loads((B/'current-relation-ledger.json').read_text())
choices={
 'production-020':{'label':'D4 flux interpolation across different external and wrapped-cycle dimensions','systems':['AdS4 with a D4 wrapping a contractible one-cycle in a two-cycle','AdS3 with a D4 wrapping a contractible two-cycle in a three-cycle'],'spans':['9c44a326cd0e679d37ed:p0007s001','43ed00b9bc39e2445e7b:p0019s001'],'preserve':'The proposed interpolation operation survives; the physical vacuum family, scalar metric and spontaneous-decay question do not merge.'},
 'production-026':{'label':'Einstein–DeTurck gauge fixing across different matter systems','systems':['Static axisymmetric AdS4 constructions with dilatonic and two-Maxwell matter','Static axisymmetric AdS4 Einstein–Maxwell theory with a massive charged complex scalar'],'spans':['81e90d90727ad688e2db:p0020s001','be6b2d2c22e403f85088:p0005s001'],'preserve':'Keep the common geometric gauge-fixing route; do not equate matter equations, solver algorithms or regular-solution existence.'},
 'production-097':{'label':'Forward dispersion for single and multiple photon species','systems':['3D single-photon amplitude represented by its scalar dual','3D multiple-photon amplitude projected onto real product species states'],'spans':['ebd908faa7eec3fc42c9:p0010s001','240fad48770cf4cf7a24:p0012s001'],'preserve':'Keep the conditional contour/positivity method route; do not equate theories, Wilson coefficients, spectral functions or unregulated limits.'}}
records=[]
for tid,choice in choices.items():
 r=next(x for x in ledger['records'] if x['taskId']==tid)
 assert r['admittedScientificEdge'] and not r['promotionWithheld'] and r['relationCategory']=='uses_method'
 packet=UP/r['sourcePacketPath'];assert hashlib.sha256(packet.read_bytes()).hexdigest()==r['sourcePacketSha256']
 p=json.loads(packet.read_text());spans={x['evidence_id']:x for x in p['spans']}
 locators=[{k:spans[s][k] for k in ['evidence_id','paper_id','source_sha256','page','start','end']} for s in choice['spans']]
 records.append({'id':tid,'label':choice['label'],'systems':choice['systems'],'expectedBehavior':choice['preserve'],
   'basis':'Prior admitted relation receipt; selected text spans reread in Q025. No new equation-image validation or independent scientific proof.',
   'sourceRelation':r,'selectedRereadLocators':locators,
   'questionAttachmentPolicy':'Endpoints are exact source objects, not Q-units. Same-paper question navigation is contextual unless an exact direct source-node join independently supports it.',
   'prohibitedInferences':['Cross-system implies cannot-link','Common method implies same scoped question','Source-object relation implies all questions in both papers are related']})
out={'schemaVersion':'q025-method-bridge-controls/1','status':'development_controls_from_existing_admitted_receipts','ledgerSha256':hashlib.sha256((B/'current-relation-ledger.json').read_bytes()).hexdigest(),'records':records}
(B/'method-bridge-controls.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'controls':len(records),'allAcceptedUsesMethod':True,'selectedSourceSpansReread':sum(len(r['selectedRereadLocators']) for r in records)}))
