"""Post-hoc exact reference resolution; native failures and scientific rows stay intact."""
import copy,hashlib,importlib.util,json,shutil
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent;W=E.parents[2]
spec=importlib.util.spec_from_file_location('retained_navigation',F/'navigation-recovery-v2/contract.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def vh(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def derive(packet,reply,*,allow_one_destination_compound=False,require_equivalence_issue=False):
 p=copy.deepcopy(packet);r=copy.deepcopy(reply);original=copy.deepcopy(reply)
 prior=p.get('priorReview')or{};pd={x['id']:x for x in prior.get('decisions',[])};current={x['id']:x for x in r['decisions']};reviews={x['ref']:x for x in r['priorReviews']};resolved=[]
 for ref in sorted({ref for row in r['scopeDispositions']for ref in row['decisionIds']} - set(current)):
  assert ref in pd,'Unknown historical decision reference'
  assert reviews.get(ref,{}).get('verdict')=='supported_as_written','Referenced historical decision lacks explicit unchanged support'
  r['decisions'].append(copy.deepcopy(pd[ref]));resolved.append({'ref':ref,'exactPriorObjectSha256':vh(pd[ref]),'explicitAssessmentSha256':vh(reviews[ref]),'createsNewLogicalObject':False})
 known={s['ref']for s in p['scopes']}|{q['id']for q in prior.get('newQuestions',[])}|{q['id']for q in r['newQuestions']};refs=p['refRegistry'];compounds=[]
 for row in r['compoundSources']:
  assert row['unitRef']in refs and refs[row['unitRef']]['kind']=='description','Compound annotation needs exact source description'
  targets=row['questionRefs'];assert targets and len(targets)==len(set(targets)) and set(targets)<=known,'Unknown/empty/duplicate compound destination'
  assert row['reason']and row['refs']and len(row['refs'])==len(set(row['refs']))and set(row['refs'])<=set(refs),'Invalid compound annotation evidence'
  if len(targets)==1:
   assert allow_one_destination_compound,'One-destination compound annotation needs the explicit derived policy'
   assert row['unitRef']=='u33'and targets==['pq0'],'This adjudication covers only the exact supplied u33→pq0 annotation'
  compounds.append({'unitRef':row['unitRef'],'questionRefs':targets,'annotationSha256':vh(row),'wholeSourceUnchanged':True,'atomicIdentitiesEstablished':False,'logicalDestinationCount':len(targets)})
 # Compound annotations are validated above, then omitted only from the old
 # validator's projection. The returned scientific artifact retains them exactly.
 r['compoundSources']=[]
 d=old.classify_retained(p,r,require_equivalence_issue)
 d.update({'schemaVersion':'q025-navigation-reference-recovery/3','status':'valid_derived_prior_reference_representation','normalizedReview':original,'originalReplyValueSha256':vh(original),'normalizedReplyValueSha256':vh(original),'resolvedPriorDecisionReferences':resolved,'compoundAnnotationsChecked':compounds,'scientificContentChanged':False,'logicalObjectsDuplicated':0,'acceptance':'Representation validation only. Exact prior references and compound annotations are retained; this receipt admits no scope equivalence, new source role, public route or organizational home.'})
 return d

def adopt(name,relative,**opts):
 src=F/'native-local'/relative;p=json.loads((src/'packet.actual.json').read_text());r=json.loads((src/'reply.raw.txt').read_text());original=json.loads((src/'receipt.json').read_text());assert original['status']=='failed'
 derived=derive(p,r,**opts);out=F/'native-local/navigation-recovery-v3/adopted'/name;out.mkdir(parents=True,exist_ok=True)
 for filename in ['packet.actual.json','reply.raw.txt']:
  shutil.copyfile(src/filename,out/filename)
 (out/'reply.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
 derived.update({'originalFailedReceipt':{'path':str((src/'receipt.json').relative_to(W)),'sha256':sha(src/'receipt.json')},'originalRawSha256':sha(src/'reply.raw.txt'),'packetSha256':sha(src/'packet.actual.json'),'normalizerSha256':sha(__file__),'explicitStructuralAdjudication':{'authority':'root','policy':'Retain exact u33→[pq0] as a compound annotation: internal EFT/dispersive stages may share one broader public destination; atomic identities remain unresolved.'}if opts.get('allow_one_destination_compound')else None})
 (out/'normalization.json').write_text(json.dumps(derived,ensure_ascii=False,indent=2)+'\n')
 receipt={**original,'schemaVersion':'q025-derived-navigation-receipt/3','jobId':name,'status':'complete','error':None,'originalNativeStatus':'failed','originalFailedReceipt':derived['originalFailedReceipt'],'normalizedReplySha256':sha(out/'reply.json'),'normalizationReceiptSha256':sha(out/'normalization.json'),'representationStatus':derived['status'],'nativeReviewRepeated':False,'scientificContentChanged':False,'logicalObjectsDuplicated':0}
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
 return {'name':name,'adoptedDirectory':str(out.relative_to(E)),'originalFailedReceipt':derived['originalFailedReceipt'],'packetSha256':sha(out/'packet.actual.json'),'replySha256':sha(out/'reply.json'),'normalizationSha256':sha(out/'normalization.json'),'receiptSha256':sha(out/'receipt.json'),'coverage':derived['validation'],'counts':{k:len(v)for k,v in r.items()if isinstance(v,list)},'resolvedPriorDecisionReferences':derived['resolvedPriorDecisionReferences'],'retainedPriorObjects':derived['retainedPriorObjects'],'compoundAnnotationsChecked':derived['compoundAnnotationsChecked'],'nativeTurns':0,'scientificAdmission':False}
if __name__=='__main__':
 reports=[adopt('amplitude-compound-challenge','navigation-recovery-v2/jobs/amplitude-explicit-equivalence-challenge',allow_one_destination_compound=True,require_equivalence_issue=True),adopt('kk-prior-reference-challenge','navigation-kk-v1/jobs/kk-cross-field-routes-challenge')]
 (B/'recovery-report.json').write_text(json.dumps({'schemaVersion':'q025-navigation-recovery-report/3','recoveries':reports,'originalFailuresPreserved':True,'nativeTurns':0},indent=2)+'\n');print(json.dumps({'recoveries':[{k:r[k]for k in ['name','receiptSha256','coverage','counts']}for r in reports]}))
