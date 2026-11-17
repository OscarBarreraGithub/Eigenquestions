"""Verify pinned scientific views/sidecars and attach only a completed actual proposal."""
import copy,hashlib,json,sys
from pathlib import Path
import contract
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent;W=E.parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
def read(p):return json.loads(Path(p).read_text())
def verified_pin(pin):
 p=(W/pin['path']).resolve();assert p.is_relative_to(W.resolve()),'pin leaves workspace';assert sha(p)==pin['sha256'],'changed pin '+pin['path'];return p

def check_sources(view,side):
 assert view['familyId']==side['familyId'];su={u['ref']:u for u in side['units']};vs={u['ref']:u for u in view['units']}
 assert len(su)==len(vs)==len(view['units']) and su.keys()==vs.keys(),'source inventory changed'
 ids={s['id']:s['ref'] for s in side['scopes']};aliases=read(verified_pin(side['machineBindings']['canonicalProjection'])).get('destinationAliases',{})
 def scope_ref(ident):return ids.get(aliases.get(ident,ident))
 qside={s['ref']:s for s in side['scopes']};qview={s['ref']:s for s in view['scopes']}
 assert qside.keys()==qview.keys() and len(qview)==len(view['scopes']),'scope inventory changed'
 for ref,s in qside.items():
  expected={'ref':ref,**{k:s['destination'][k]for k in ['kind','title','question','summary','scope','readingCoverage','methods','aliases','scientificStatus']if k in s['destination']}}
  assert qview[ref]==expected,'scope projection changed'
 for ref,u in vs.items():
  s=su[ref];assert u['description']==s['description'] and hashlib.sha256(u['description'].encode()).hexdigest()==s['descriptionSha256'],'source description changed'
  assert u['paperId']==s['paperId'] and u['candidateHomeRefs']==s['candidateHomeRefs'] and u['existingHomeRefs']==s['existingHomeRefs'] and u['originalSourceQuestionMustRemainWhole'] is True,'source identity changed'
  prior={x['reviewId']:x for x in s['proposalAttributions']};challenge={x['reviewId']:x for x in s['challengeAttributions']}
  assert prior.keys()==challenge.keys() and len(u['priorContexts'])==len(prior),'missing old attribution'
  seen=set()
  for c in u['priorContexts']:
   rid=view['reviewNamespaces'][c['reviewRef']];assert rid in prior and rid not in seen;seen.add(rid);p=prior[rid];h=p['homeAgreement']
   expected={'reviewRef':c['reviewRef'],'sourceOrigin':p['sourceOrigin'],'proposal':p['original'],'challenge':challenge[rid]['original'],'resolvedContributions':p['resolvedTypedContributions'],'resolvedProposalHomeRef':scope_ref(h['proposal'].get('candidateId')),'resolvedChallengeHomeRef':scope_ref(h['challenge'].get('candidateId')),'sameExplicitScientificCard':h['sameExplicitScientificCard'],'proposalDefinitionMatchesPinnedOriginal':h['proposalDefinitionMatchesPinnedOriginal'],'unchangedSupportedScope':h['unchangedSupportedScope'],'placementAlreadyAdmitted':False}
   assert c==expected,'old attribution or resolved context changed'
  expected_issues={'bucket':s['coverageIssue']['bucket'],'contexts':[{'reviewRef':next(k for k,v in view['reviewNamespaces'].items() if v==x['reviewId']),'candidateHomeRef':scope_ref(x['destinationId']),'exclusionReasons':x['exclusionReasons']}for x in s['coverageIssue']['priorCensus']]}
  assert u['coverageIssue']==expected_issues,'coverage issues changed'
 assert view['readingLimits'][:len(side['readingLimits'])]==side['readingLimits'] and view['selection']==side['selection'],'reading/sampling limits changed'
 return {'sourceCount':len(vs),'scopeCount':len(qview),'priorContexts':sum(len(u['priorContexts'])for u in vs.values()),'primaryPagesSupplied':0}

def source_pins(side):
 """Resolve every actual historical artifact via explicit paths; never guess siblings."""
 out=[]
 for k in ['registry','scopeComponent','residualInventory','eligibleInventory','canonicalProjection']:out.append(side['machineBindings'][k])
 out.extend(side['machineBindings']['additionalComponents'])
 for u in side['machineBindings']['units']:
  for c in u['reviewContexts']:
   for key in ['proposalDependency','challengeArtifact']:
    a=c[key];base=E/a['artifactDirectory']
    for k,v in a.items():
     if k.endswith('Sha256'):out.append({'path':str((base/k[:-6]).relative_to(W)),'sha256':v})
    if a.get('resolvedFromRequest'):out.append(a['resolvedFromRequest'])
 unique={}
 for p in out:
  assert p['path'] not in unique or unique[p['path']]['sha256']==p['sha256'],'conflicting historical artifact pins'
  unique[p['path']]=p
 return list(unique.values())

def materialize(request_path,runtime):
 d=Path(request_path).resolve().parent;assert not(d/'dispatch-request.json').exists(),'already materialized; no redispatch';req=read(request_path)
 for pin in req['sourcePins']:verified_pin(pin)
 source=E/req['originalPacketPath'];assert sha(source)==req['originalPacketSha256'];view=read(source);side=read(verified_pin(view['sidecar']));check_sources(view,side)
 p={**view,'stage':req['stage'],'priorReview':None};actual={**req,'baseRequestSha256':sha(request_path)}
 if req['dependsOn']:
  prior=Path(runtime)/'jobs'/req['dependsOn'];receipt=read(prior/'receipt.json');assert receipt['status']=='complete' and receipt['sourceOnly'] and not receipt['toolUseAttempted'],'prior did not complete source-only'
  assert receipt['normalizedReplySha256']==sha(prior/'reply.json') and receipt['inputPins']['packetSha256']==sha(prior/'packet.actual.json'),'prior receipt mismatch'
  pp=read(prior/'packet.actual.json');assert pp['stage']=='proposal' and {k:v for k,v in pp.items() if k not in ['stage','priorReview']}==view,'prior has different scientific packet'
  proposal=read(prior/'reply.json');contract.evaluate(pp,proposal);p['priorReview']=proposal;actual.update(priorReceiptSha256=sha(prior/'receipt.json'),priorReplySha256=sha(prior/'reply.json'),priorPacketSha256=sha(prior/'packet.actual.json'))
 assert (p['stage']=='proposal')==(p['priorReview'] is None),'stage dependency mismatch'
 dump(d/'packet.actual.json',p);text=(B/'INSTRUCTIONS.md').read_text();assert text.count('{{MAX_OUTPUT_CHARACTERS}}')==1
 # Keep machine provenance in packet/sidecar; the model sees complete scientific content.
 public={k:v for k,v in p.items() if k not in ['sidecar','reviewNamespaces']};public['reviewNamespaces']={k:'review-scoped prior annotation context' for k in p['reviewNamespaces']}
 (d/'prompt-base.actual.txt').write_text(text.replace('{{MAX_OUTPUT_CHARACTERS}}',str(req['maxOutputCharacters']))+'\n\nEXACT PLACEMENT DECISION PACKET\n'+json.dumps(public,ensure_ascii=False,separators=(',',':'))+'\n')
 actual.update(packetSha256=sha(d/'packet.actual.json'),promptBaseSha256=sha(d/'prompt-base.actual.txt'));dump(d/'dispatch-request.json',actual);return actual
if __name__=='__main__':print(json.dumps({'materialized':materialize(sys.argv[1],sys.argv[2])['jobId']}))
