"""Preserve nonincident disposition references as explicit context; never infer paths."""
import copy,hashlib,importlib.util,json
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent
spec=importlib.util.spec_from_file_location('canonical_recovery_v2',F/'canonical-recovery-v2/contract.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def separate_context(review):
 out=copy.deepcopy(review);ds={x['id']:x for x in out['decisions']};contexts=[]
 for row in out['scopeDispositions']:
  assert len(row['decisionIds'])==len(set(row['decisionIds'])),'Duplicate disposition reference'
  assert set(row['decisionIds'])<=set(ds),'Unknown disposition decision'
  direct=[];context=[]
  for ref in row['decisionIds']:
   (direct if row['ref'] in ds[ref]['members'] or row['ref']==ds[ref]['target'] else context).append(ref)
  if context:contexts.append({'scopeRef':row['ref'],'directDecisionIds':direct,'contextualDecisionIds':context,'originalDisposition':copy.deepcopy(row),'contextDecisions':[copy.deepcopy(ds[d]) for d in context],'interpretation':'Explicitly cited comparison/component context, not a direct endpoint decision. No connecting scientific path is inferred.'})
  row['decisionIds']=direct
 return out,contexts

def derive(job):
 p=json.loads((job/'packet.actual.json').read_text());raw=json.loads((job/'reply.raw.txt').read_text());prefix=p['preservedComponents'];review=copy.deepcopy(prefix['completeFields']);review['decisions']=copy.deepcopy(review.get('decisions',prefix['completeArrayPrefixes'].get('decisions',[])))+raw['additionalDecisions'];review['pairConstraints']=copy.deepcopy(review.get('pairConstraints',prefix['completeArrayPrefixes'].get('pairConstraints',[])))+raw['additionalPairConstraints'];review.update({k:raw[k] for k in ['scopeDispositions','sourceContributions','compoundSources','limitations','unresolved']});review['priorReviews']=[]
 old.structure(raw,old.SCHEMA);old.check_variants(p,raw['variantAssessments']);normal,contexts=separate_context(review);valid=old.base.evaluate(p,normal)
 pins={name:sha(job/name) for name in ['packet.actual.json','reply.raw.txt','receipt.json']};receipt={'schemaVersion':'q025-canonical-context-derivation/1','status':'valid_derived_representation','sourceArtifacts':pins,'originalFailedReceiptUnchanged':True,'originalAssembledValueSha256':old.base.vh(review),'normalizedReviewValueSha256':old.base.vh(normal),'contextualDispositionReferences':contexts,'originalScopeDispositions':review['scopeDispositions'],'streamVariantAssessments':raw['variantAssessments'],'streamVariants':p['streamVariants'],'preservedPrefixArtifactSha256':p['prefixArtifactSha256'],'validation':valid['validation'],'transform':'Separate existing known nonincident decision references into explicit contextualDecisionIds. Preserve every complete scientific definition, decision, pair constraint, source contribution, rationale and original disposition. Direct positive disposition coverage must still pass unchanged strict validation.','scientificContentChanged':False,'scopeDecisionEndpointsChanged':False,'inventedConnectingPaths':0,'discardedReferences':0,'acceptance':'Proposal representation only. Entire assembled result, original dispositions and contextual mappings require independent challenge.'};return p,normal,receipt
if __name__=='__main__':
 L=F/'native-local/canonical-recovery-v3';L.mkdir(parents=True,exist_ok=True);records=[]
 for family in ['mediation-scope','control-statistics']:
  source=F/'native-local/canonical-recovery-v2/jobs'/f'canonical-recovery-{family}-proposal';p,normal,receipt=derive(source);d=L/'derived'/family;d.mkdir(parents=True,exist_ok=True)
  for name,data in [('proposal.json',normal),('derivation.json',receipt)]: (d/name).write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
  records.append({'familyId':family,'sourceJobPath':str(source.relative_to(F.parent)),'sourceArtifacts':receipt['sourceArtifacts'],'proposalPath':str((d/'proposal.json').relative_to(F.parent)),'proposalSha256':sha(d/'proposal.json'),'derivationPath':str((d/'derivation.json').relative_to(F.parent)),'derivationSha256':sha(d/'derivation.json'),'contextualRefs':sum(len(x['contextualDecisionIds']) for x in receipt['contextualDispositionReferences']),'validation':receipt['validation']})
 out={'schemaVersion':'q025-canonical-context-recovery-index/1','families':records,'nativeTurns':0,'oldFailuresUnchanged':True};(B/'derivation-index.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
