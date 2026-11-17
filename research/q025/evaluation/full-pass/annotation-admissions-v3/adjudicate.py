"""Bind root's two annotation refinements and separate premise amendment."""
import collections,hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent;W=E.parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
textsha=lambda s:hashlib.sha256(s.encode()).hexdigest()
source=F/'native-local/annotation-adjudication-v2';records=[];pending=[]
for p in sorted(source.glob('*.json')):
 x=json.loads(p.read_text());cid=x['caseId'];c=x['originalCase'];r=x['challenge']
 if ':f28:' in cid:pending.append({'caseId':cid,'status':'abstention_retained_pending_expanded_local_source','packet':{'path':str(p.relative_to(W)),'sha256':sha(p)}});continue
 assert ':p3:' in cid or ':p4:' in cid or ':f41:' in cid
 premise=':f41:' in cid
 assert r['scopeImpact']==('premise_change' if premise else 'annotation_only')
 if premise:assert r['replacementText']==x['proposal']['replacementText']
 records.append({'caseId':cid,'status':'accepted_explicit_premise_amendment' if premise else 'accepted_annotation_refinement','adjudicator':'root','authorization':'Root independently read the exact exception packet and supplied primary windows, and explicitly approved this exact challenger text. The premise amendment separately withdraws unsupported hidden-sector insensitivity and a paper-wide F-term-only assertion.' if premise else 'Root independently read the exact exception packet and supplied primary windows, and explicitly approved the challenger wording as an annotation-only refinement.','originalText':c['originalText'],'originalTextSha256':textsha(c['originalText']),'replacementText':r['replacementText'],'replacementTextSha256':textsha(r['replacementText']),'meaningChange':r['meaningChange'],'scopeImpact':r['scopeImpact'],'sourcePacket':{'path':str(p.relative_to(W)),'sha256':sha(p)},'originalSourcePins':c['pins'],'reviewAgreement':x['reviewPins'],'challengeAssessment':x['challengeAssessment'],'evidenceRefs':[{'ref':ref,**c['refs'][ref]} for ref in r['refs']],'dependencyRevalidationRequired':premise,'noAutomaticPromotion':['scientific_scope','placement','canonical_identity','scientific_relation','physical_result'],'readingLimit':'Exact supplied descriptions and bounded primary passages only; source-reported calculations and missing arguments are not independently reproduced.'})
out={'schemaVersion':'q025-explicit-annotation-adjudication/3','rows':records,'pending':pending,'originalArtifactsUnchanged':True,'annotationRefinements':2,'separatePremiseAmendments':1,'scopeAdmissions':0,'placementAdmissions':0,'identityAdmissions':0}
p=B/'explicit-adjudications.json';p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'path':str(p.relative_to(W)),'sha256':sha(p),'annotations':2,'premiseAmendments':1,'abstentions':1}))
