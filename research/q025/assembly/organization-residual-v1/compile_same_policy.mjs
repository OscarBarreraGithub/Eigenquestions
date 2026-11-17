/** Compile the264 confirmed same-policy homes and one explicit Reuter exception. */
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {resolve,join,relative,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {scopeContentHash,placementContentHash} from '../accepted.mjs';
import {loadFrozenCorpus,sha256} from '../corpus.mjs';
import {verifyPrimaryEvidence} from '../primary-evidence.mjs';
const here=dirname(fileURLToPath(import.meta.url)),root=resolve(here,'../../../..'),ev=join(root,'research/q025/evaluation'),out=join(here,'admitted-extension-v1');
async function read(path,expected){const raw=await readFile(path),hash=sha256(raw);if(expected&&hash!==expected)throw Error('Changed input '+path);return {value:JSON.parse(raw),pin:{path:relative(root,path),sha256:hash,bytes:raw.length}};}
async function save(name,value){const path=join(out,name);await writeFile(path,JSON.stringify(value,null,2)+'\n');return (await read(path)).pin;}
const proposal=await read(join(here,'same-policy-proposal.json'),'5bb3c69abd7d0b53963838c899f7e1e532330c760e2bed1e92a93e2100cad713');
const candidates=await read(join(root,proposal.value.candidatePayload.path),proposal.value.candidatePayload.sha256);
const input=async suffix=>{const pin=proposal.value.inputs.find(x=>x.path.endsWith(suffix));if(!pin)throw Error('Missing input');return read(join(root,pin.path),pin.sha256);};
const component=await input('supported-scope-role-component-v4.json'),registry=await input('authored-scope-registry-v5-20261117T135430Z.json'),old=await input('aggregate.local.json');
const scopes=new Map(component.value.destinations.map(d=>[d.id,d])),assessments=new Map(registry.value.unitAssessments.map(a=>[a.reviewId+'\n'+a.unitId,a])),reviews=new Map(registry.value.reviews.map(r=>[r.reviewId,r]));
const occupied=new Set(old.value.placements.filter(r=>r.role!=='context').map(r=>r.unitId));
const corpus=await loadFrozenCorpus(join(root,'data/navigation')),verified=new Map(),reviewRegistry=new Map(),cache=new Map();
async function artifact(path,hash){if(verified.has(path)){if(verified.get(path).pin.sha256!==hash)throw Error('Conflicting pin');return verified.get(path).value;}const x=await read(path,hash);verified.set(path,x);return x.value;}
async function review(id){
  if(cache.has(id))return cache.get(id);const r=reviews.get(id);if(!r)throw Error('Missing review');
  for(const stage of [r.proposalDependency,{...r.challengeArtifact,reviewId:id}]){
    const dir=join(ev,stage.artifactDirectory),reply=join(dir,'reply.json'),receipt=join(dir,'receipt.json');
    await artifact(reply,stage['reply.jsonSha256']);const rec=await artifact(receipt,stage['receipt.jsonSha256']);
    if(rec.status!=='complete'||rec.normalizedReplySha256!==stage['reply.jsonSha256'])throw Error('Incomplete native receipt');
    reviewRegistry.set(stage.reviewId,{id:stage.reviewId,path:relative(root,reply),sha256:stage['reply.jsonSha256'],receipt:{path:relative(root,receipt),sha256:stage['receipt.jsonSha256']}});
  }
  const packet=await artifact(join(ev,r.artifactDirectory,r.challengeArtifact.packetFile),r.pins.challengePacketSha256),byUnit=new Map(packet.units.map(u=>[packet.refRegistry[u.descriptionRef].unitId,u]));
  const result={record:r,packet,byUnit};cache.set(id,result);return result;
}
const exception='unit:0512c7d33fc01fba59af1556246131c61d9bdf866f46c10f0ecfb47637d374ab',rows=[],bindings=[];
if(candidates.value.rows.length!==265||new Set(candidates.value.rows.map(r=>r.unitId)).size!==265)throw Error('Wrong approved inventory');
for(const c of candidates.value.rows){
  if(occupied.has(c.unitId)||c.proposedRole!=='member'||c.proposedWeight!==1)throw Error('Duplicate source or changed approved weight');
  const d=scopes.get(c.destinationId),u=corpus.unitMap.get(c.unitId);if(!d||!u||u.lens!=='physical_question')throw Error('Unknown question/scope');
  const scopeHash=scopeContentHash(d);if(scopeHash!==c.scopeContentSha256||scopeHash!==d.scopeContentSha256||d.scopeDecisionId!==c.scopeDecisionId)throw Error('Changed admitted scope');
  const evidenceRefs=[{kind:'description',unitId:c.unitId,paperId:u.paperId,textSha256:u.evidence.textSha256}],contexts=[],reviewIds=new Set();let excerpt=false;
  for(const rid of c.sourceReviewIds){
    const a=assessments.get(rid+'\n'+c.unitId),declared=c.contexts.find(x=>x.reviewId===rid),r=await review(rid),unit=r.byUnit.get(c.unitId);
    if(!a||!declared||!unit||sha256(unit.description)!==u.evidence.textSha256||unit.paperId!==u.paperId)throw Error('Changed exact source');
    if(JSON.stringify(a.proposalAttribution)!==JSON.stringify(declared.proposal)||JSON.stringify(a.challengeAttribution)!==JSON.stringify(declared.challenge))throw Error('Changed paired annotation');
    const p=a.proposalAttribution,q=a.challengeAttribution;
    if(c.policyClass.startsWith('A')){if(!a.homeAgreement.sameExplicitScientificCard||!a.homeAgreement.proposalDefinitionMatchesPinnedOriginal||a.homeAgreement.challenge.candidateId!==d.id)throw Error('Changed fine attribution');}
    else if(!c.policyClass.startsWith('B')||p.d!=='member'||q.d!=='member')throw Error('Changed whole-family attribution');
    for(const localRef of p.refs.filter(x=>q.refs.includes(x))){const e=r.packet.refRegistry[localRef];if(p.b==='excerpt'&&q.b==='excerpt'&&e?.kind==='primary'&&e.paperId===u.paperId){const value={localRef,...e};if(!evidenceRefs.some(x=>JSON.stringify(x)===JSON.stringify(value)))evidenceRefs.push(value);excerpt=true;}}
    reviewIds.add(r.record.proposalDependency.reviewId);reviewIds.add(rid);contexts.push({...declared,proposalNoteSha256:sha256(p.note),challengeNoteSha256:sha256(q.note)});
  }
  const isException=c.unitId===exception;
  if(isException&&(u.paperId!=='2312.03831'||d.id!=='q025-candidate-question:7fc5f55b18f12ec4bbab14ee'||!contexts[0].challenge.note.endsWith('and vanishing')))throw Error('Changed exact annotation exception');
  const qualification=isException?'The intact source question covers the sixth-order minimal-essential fixed point, relevant directions and regulator robustness within this unchanged RG scope. The severed challenger phrase ending “and vanishing” remains unresolved historical annotation; no missing condition is guessed and no quotation or physical proof is repaired. Placement is separately coordinator-adjudicated.':c.policyClass.includes('compound')?'The entire compound source question retains one reviewed whole-family home. All stated targets, source-era conditions and typed contributions remain distinct; no atomic split, question equivalence or automatic mass division is asserted.':'The complete source question is placed within the exact unchanged admitted scope using the approved A/B policy. Source-specific conditions and reading limits remain attached; no equivalence or applicability is implied.';
  const row={unitId:c.unitId,destinationId:c.destinationId,role:'member',status:'accepted',basis:excerpt?'source_excerpt_checked':'description_checked',allocationWeight:1,workRelation:'on',qualification,evidenceRefs,decisionId:'decision:same-policy-extension:'+sha256(c.unitId+'\n'+c.destinationId).slice(0,24)};
  rows.push(row);bindings.push({decisionId:row.decisionId,policyClass:isException?'E_explicit_Reuter_placement_without_annotation_repair':c.policyClass,scopeContentSha256:scopeHash,placementContentSha256:placementContentHash(row,scopeHash),sourceDescriptionSha256:u.evidence.textSha256,sourceReviewIds:[...reviewIds].sort(),contexts,scopeDiagnosticRefresh:c.scopeDiagnosticRefresh,annotationDefectRetained:isException,placementAgreement:'explicit_coordinator_admission_not_original_dual_home_review'});
}
const contextRoot=join(root,'research/q025/geometry/source-context-v3-compact/pack'),context=await read(join(contextRoot,'manifest.json'),'c86bc90966007c28ce40523348e51e4ace4d20d62354f79928133d371f77c6f5');
const primary=await verifyPrimaryEvidence({references:rows.flatMap(r=>r.evidenceRefs),corpus,archiveRoot:'/Users/emmy/Developer/physics-atlas-swampland',contextRoot,contextManifest:context.value});
await mkdir(out,{recursive:true});const bound=await save('placement-bindings.local.json',bindings);
const common={schemaVersion:'q025-explicit-placement-policy-admission/1',status:'accepted_explicit_placement',adjudicator:'root',approvedProposal:proposal.pin,approvedCandidatePayload:candidates.pin,scopeComponent:component.pin,registry:registry.pin,priorCohort:old.pin,exactBindings:bound,scopeChangePolicy:'Changed or reconciled canonical scope requires explicit placement revalidation; no alias, route or source equivalence follows.',fullAtlasAdmission:false};
const policy=await save('policy-admission.json',{...common,authorization:'Root explicitly approved264 exact same-policy rows after reading all six descriptions, full target scopes, both annotations and diagnostic refreshes. Existing admitted scope status resolves only stale scope flags; no annotation-only or premise conflict is waived.',approvedDecisionIds:bindings.filter(x=>!x.annotationDefectRetained).map(x=>x.decisionId)});
const exceptionReceipt=await save('reuter-admission.json',{...common,authorization:'Root separately approved weight1 for exact source2312.03831 at the existing broad RG question after reading its intact stated targets, full scope and both annotations. The incomplete challenger ending remains unresolved history; no missing words, condition or proof claim are supplied.',approvedDecisionIds:bindings.filter(x=>x.annotationDefectRetained).map(x=>x.decisionId)});
const decisions=rows.map((r,i)=>({id:r.decisionId,type:'placement',status:'accepted',subjectIds:[r.unitId,r.destinationId],scopeContentSha256:bindings[i].scopeContentSha256,placementContentSha256:bindings[i].placementContentSha256,challengerAgreement:'not_reviewed_as_placement',sourceEvidenceAgreement:'independently_agreed',adjudication:{status:'accepted_explicit_placement',receipt:bindings[i].annotationDefectRetained?exceptionReceipt:policy},sourceReviewIds:bindings[i].sourceReviewIds,evidenceRefs:r.evidenceRefs,sourceAgreementBinding:{path:bound.path,sha256:bound.sha256,decisionId:r.decisionId}}));
const delta=await save('home-admission-delta.local.json',{schemaVersion:'q025-organization-admission-delta/1',baseComponent:component.pin,placements:rows,decisions,reviewRegistry:[...reviewRegistry.values()],adjudicationReceipts:[policy,exceptionReceipt],allocationPolicy:'explicit_normalized_weights',scopeChanges:[],relations:[],aliases:[],completeAtlasAdmission:false});
const b=bindings.find(x=>x.annotationDefectRetained);const defect=await save('annotation-defect-amendment.json',{schemaVersion:'q025-annotation-defect-amendment/1',status:'unresolved_historical_annotation_placement_separately_admitted',unitId:exception,reviewId:b.contexts[0].reviewId,originalChallengeNote:b.contexts[0].challenge.note,originalChallengeNoteSha256:b.contexts[0].challengeNoteSha256,reason:'Previously missed incomplete ending “and vanishing”. No text repair, active premise or universal claim inferred.',placementOnlyReceipt:exceptionReceipt,originalInventoryNotMutated:true});
const report={schemaVersion:'q025-same-policy-home-compilation/1',status:'passed_exact_source_scope_review_and_primary_checks',fixture:false,admittedSourceUnits:rows.length,policyRows:264,explicitAnnotationExceptionRows:1,previousAllocatedSources:occupied.size,resultingAllocatedSources:occupied.size+rows.length,remainingEligibleSources:8430-occupied.size-rows.length,reservedSources:43,distinctNewTargets:new Set(rows.map(r=>r.destinationId)).size,readingBasis:rows.reduce((o,r)=>(o[r.basis]=(o[r.basis]||0)+1,o),{}),verifiedNativeArtifacts:verified.size,primaryEvidenceVerification:primary.report,component:delta,bindings:bound,receipts:[policy,exceptionReceipt],annotationDefectAmendment:defect,scriptSha256:sha256(await readFile(fileURLToPath(import.meta.url))),helperSha256:sha256(await readFile(join(here,'../accepted.mjs'))),existingSourcesDuplicated:false,fullAtlasAdmission:false};
await save('report.json',report);console.log(JSON.stringify(report,null,2));
