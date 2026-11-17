/** Bind root's exact A/B class and separate stellar-source adjudication. */
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {resolve,join,relative,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {scopeContentHash,placementContentHash} from '../accepted.mjs';
import {loadFrozenCorpus,sha256} from '../corpus.mjs';
import {verifyPrimaryEvidence} from '../primary-evidence.mjs';

const here=dirname(fileURLToPath(import.meta.url)),root=resolve(here,'../../../..'),evaluation=join(root,'research/q025/evaluation'),out=join(here,'admitted-v1');
const pin=(path,bytes)=>({path:relative(root,path),sha256:sha256(bytes),bytes:bytes.length});
async function read(path,expected){const bytes=await readFile(path);if(expected&&sha256(bytes)!==expected)throw Error(`Changed input ${path}`);return {value:JSON.parse(bytes),pin:pin(path,bytes)};}
async function save(name,value){const path=join(out,name),bytes=Buffer.from(JSON.stringify(value,null,2)+'\n');await writeFile(path,bytes);return pin(path,bytes);}
const proposal=await read(join(here,'placement-policy-proposal.json'),'9b9d6493839e3546792e771daf21f3523c46112a4e93e7a2eed64ac7d28b6574');
const input=async key=>{const p=proposal.value.inputs[key];return read(join(root,p.path),p.sha256);};
const candidates=await input('exactCandidateRows'),registry=await input('registry'),historicalComponent=await input('scopeRoleSupport');
const correction=await read(join(evaluation,'full-pass/admissions-v4/hash-correction-receipt.json'));
const component=await read(join(evaluation,'full-pass/admissions-v4/supported-scope-role-component-v4.json'),'98821c0544eb16b26584d65d5838a256bda54c2c65aebe377a834426579274cb');
if(correction.value.input.sha256!==historicalComponent.pin.sha256||correction.value.status!=='deterministic_representation_correction_no_scientific_change')throw Error('Correction does not bind original policy component');
const historicalScopes=new Map(historicalComponent.value.destinations.map(d=>[d.id,d]));
for(const d of component.value.destinations){const old=historicalScopes.get(d.id);const science=x=>JSON.stringify(Object.fromEntries(Object.entries(x).filter(([k])=>k!=='scopeContentSha256')));if(!old||science(old)!==science(d))throw Error('Hash correction changes scientific content');}
const correctedScopeHashes=new Map(correction.value.scopeCorruptionEvidence.map(r=>[r.destinationId,r]));
if(candidates.value.pendingPlacements.length!==4703)throw Error('Unexpected approved class size');
const corpus=await loadFrozenCorpus(join(root,'data/navigation'));
const scopes=new Map(component.value.destinations.map(d=>[d.id,d])),reviews=new Map(registry.value.reviews.map(r=>[r.reviewId,r]));
const assessments=new Map(registry.value.unitAssessments.map(a=>[a.reviewId+'\n'+a.unitId,a]));
const sourceReviews=new Map(),verifiedFiles=new Map(),cache=new Map();
async function verified(path,hash){const previous=verifiedFiles.get(path);if(previous){if(previous.sha256!==hash)throw Error('Conflicting artifact pin');return previous.value;}const x=await read(path,hash);verifiedFiles.set(path,{...x.pin,value:x.value});return x.value;}
async function review(rid){
  if(cache.has(rid))return cache.get(rid);
  const r=reviews.get(rid);if(!r)throw Error('Unknown review');
  const stages=[r.proposalDependency,{...r.challengeArtifact,reviewId:rid}];
  for(const stage of stages){
    const dir=join(evaluation,stage.artifactDirectory),reply=await verified(join(dir,'reply.json'),stage['reply.jsonSha256']),receipt=await verified(join(dir,'receipt.json'),stage['receipt.jsonSha256']);
    if(receipt.status!=='complete'||receipt.normalizedReplySha256!==stage['reply.jsonSha256'])throw Error('Incomplete or mismatched native review');
    sourceReviews.set(stage.reviewId,{id:stage.reviewId,kind:'pinned_native_source_review',path:relative(root,join(dir,'reply.json')),sha256:stage['reply.jsonSha256'],receipt:{path:relative(root,join(dir,'receipt.json')),sha256:stage['receipt.jsonSha256']}});
  }
  const dir=join(evaluation,r.artifactDirectory),p=await verified(join(dir,r.challengeArtifact.packetFile),r.pins.challengePacketSha256);
  const byUnit=new Map(p.units.map(u=>[p.refRegistry[u.descriptionRef].unitId,u]));
  const value={record:r,packet:p,byUnit};cache.set(rid,value);return value;
}

const rows=[],bindings=[];
const pending=[...candidates.value.pendingPlacements,{unitId:'unit:bd8c5b9a8b57126b3ca4cd9f8f106d4a591051d19ace30fd62d33141efb25f60',destinationId:'q025-candidate-question:fc582eff749d1936943465cf',proposedWeight:1,policyClass:'C_explicit_stellar_whole_compound_question',sourceReviewIds:['leaf-0403944f92af04eaed4a-challenge']},{unitId:'unit:0034b70ea953b9879b3d6034ad618cbfcb1be80a68ce1e19fa6ffa94793dec60',destinationId:'q025-candidate-region:839da90831bec9d6ef0a811b',proposedWeight:1,policyClass:'D_explicit_fourfold_placement_without_annotation_repair',sourceReviewIds:['leaf-f3d0ef8dd184e0ce2e9a-challenge']}];
for(const c of pending){
  const d=scopes.get(c.destinationId),source=corpus.unitMap.get(c.unitId);if(!d||!source||source.lens!=='physical_question')throw Error('Unknown source/scope');
  const scopeHash=scopeContentHash(d),fix=correctedScopeHashes.get(c.destinationId);if(scopeHash!==d.scopeContentSha256||c.scopeContentSha256&&scopeHash!==c.scopeContentSha256&&!(fix?.oldHash===c.scopeContentSha256&&fix.correctHash===scopeHash))throw Error('Changed admitted target');
  const evidenceRefs=[{kind:'description',unitId:c.unitId,paperId:source.paperId,textSha256:source.evidence.textSha256}],contexts=[],allReviewIds=new Set();
  let ownExcerpt=false;
  for(const rid of c.sourceReviewIds){
    const a=assessments.get(rid+'\n'+c.unitId),v=await review(rid),u=v.byUnit.get(c.unitId);if(!a||!u||sha256(u.description)!==source.evidence.textSha256||u.paperId!==source.paperId)throw Error('Source row/description mismatch');
    const p=a.proposalAttribution,q=a.challengeAttribution;
    if(c.policyClass.startsWith('A')||c.policyClass.startsWith('C')){
      if(!a.homeAgreement.sameExplicitScientificCard||!a.homeAgreement.proposalDefinitionMatchesPinnedOriginal||a.homeAgreement.challenge.candidateId!==c.destinationId)throw Error('Paired fine home changed');
    }else if(p.d!=='member'||q.d!=='member')throw Error('Whole-family member agreement changed');
    const shared=p.refs.filter(x=>q.refs.includes(x));
    for(const localRef of shared){const ref=v.packet.refRegistry[localRef];if(ref?.kind==='primary'&&ref.paperId===source.paperId&&p.b==='excerpt'&&q.b==='excerpt'){const value={localRef,...ref};if(!evidenceRefs.some(x=>JSON.stringify(x)===JSON.stringify(value)))evidenceRefs.push(value);ownExcerpt=true;}}
    allReviewIds.add(v.record.proposalDependency.reviewId);allReviewIds.add(rid);
    contexts.push({reviewId:rid,proposalReviewId:v.record.proposalDependency.reviewId,proposalNote:p.note,challengeNote:q.note,proposalReason:p.reason,challengeReason:q.reason,proposalDisposition:p.d,challengeDisposition:q.d,homeAgreement:a.homeAgreement,originalNotesSha256:{proposal:sha256(p.note),challenge:sha256(q.note)},originalProposal:v.record.proposalDependency,challengePins:v.record.pins});
  }
  const compound=c.policyClass.includes('compound'),qualification=c.policyClass.startsWith('D')?'Placement follows the intact source question and paired broad membership. Six specified constructions and exclusion of del Pezzo degree one remain explicit. The truncated challenger annotation is retained unresolved; its missing words are not reconstructed. The complete prior qualification remains attributed evidence, not a universal classification.':c.policyClass.startsWith('C')?'The whole compound stellar question covers plasmon/pion production and conditional visible-decay limits across its stated extra-dimensional settings. Pion uncertainty, conditional intra-tower dominance and unread rate/bound calculations remain attached. No five-dimensional threshold home is inferred.':compound?'The entire compound source question has one reviewed whole-family home. Distinct subtargets and their typed contributions remain visible; this does not certify atomic identity or equivalence, and does not split allocation automatically.':'The complete source question is organizationally placed within this admitted scope, retaining source-specific systems, regimes and reading limits. This does not assert question equivalence or method applicability.';
  const id='decision:approved-home-policy-v5:'+sha256(c.unitId+'\n'+c.destinationId).slice(0,24),row={unitId:c.unitId,destinationId:c.destinationId,role:'member',status:'accepted',basis:ownExcerpt?'source_excerpt_checked':'description_checked',allocationWeight:1,workRelation:'on',qualification,evidenceRefs,decisionId:id};
  rows.push(row);bindings.push({decisionId:id,policyClass:c.policyClass,scopeContentSha256:scopeHash,placementContentSha256:placementContentHash(row,scopeHash),sourceReviewIds:[...allReviewIds].sort(),sourceDescriptionSha256:source.evidence.textSha256,contexts,sourceEvidenceAgreement:'independently_agreed',placementAgreement:'coordinator_policy_adjudication_not_original_dual_placement_review'});
}
if(rows.length!==4705||new Set(rows.map(r=>r.unitId)).size!==4705)throw Error('New source duplication');
const contextRoot=join(root,'research/q025/geometry/source-context-v3-compact/pack'),context=await read(join(contextRoot,'manifest.json'),'c86bc90966007c28ce40523348e51e4ace4d20d62354f79928133d371f77c6f5');
const primary=await verifyPrimaryEvidence({references:rows.flatMap(r=>r.evidenceRefs),corpus,archiveRoot:'/Users/emmy/Developer/physics-atlas-swampland',contextRoot,contextManifest:context.value});
await mkdir(out,{recursive:true});
const rowHashes=await save('placement-bindings.local.json',bindings),receipts=[];
for(const [name,subset,authorization] of [
  ['policy-admission.json',bindings.slice(0,4703),'Root explicitly approved the exact 4,703 A/B rows after reading all ten descriptions, six positive full scopes, both annotations and four exception cases. A: 2,276 exact fine homes; B: 2,427 whole-family homes, including 1,155 compound originals. This is coordinator allocation policy, not fictional independent approval of H.'],
  ['stellar-admission.json',bindings.slice(4703,4704),'Root separately read and approved weight 1 for source 2510.18975 at the stellar production/cooling question fc582eff. That exact fine scope covers the whole compound source; broad-region overlap does not invalidate its fine coverage. No threshold-question home is approved.'],
  ['fourfold-admission.json',bindings.slice(4704),'Root separately read the complete source question, scope and both annotations and approved source 1608.07219 at compactification region839da908. Intact text and paired membership establish coverage independently of the severed final phrase. This is a placement-only exception; preserve the damaged challenger annotation and attributed complete prior limitation without claiming quotation repair.']
])receipts.push(await save(name,{schemaVersion:'q025-explicit-placement-policy-admission/1',status:'accepted_explicit_placement',adjudicator:'root',authorization,approvedProposal:proposal.pin,approvedCandidatePayload:candidates.pin,scopeComponent:component.pin,historicalScopeComponent:historicalComponent.pin,losslessHashCorrection:correction.pin,registry:registry.pin,exactBindings:rowHashes,approvedDecisionIds:subset.map(x=>x.decisionId),scopeChangePolicy:'A changed canonical scope requires placement revalidation. No automatic aliases, parent links, source equivalence or global scope uniqueness are approved.',fullAtlasAdmission:false}));
const decisions=rows.map((r,i)=>({id:r.decisionId,type:'placement',status:'accepted',subjectIds:[r.unitId,r.destinationId],scopeContentSha256:bindings[i].scopeContentSha256,placementContentSha256:bindings[i].placementContentSha256,challengerAgreement:'not_reviewed_as_placement',sourceEvidenceAgreement:'independently_agreed',adjudication:{status:'accepted_explicit_placement',receipt:receipts[i<4703?0:i===4703?1:2]},sourceReviewIds:bindings[i].sourceReviewIds,evidenceRefs:r.evidenceRefs,sourceAgreementBinding:{path:rowHashes.path,sha256:rowHashes.sha256,decisionId:r.decisionId}}));
const delta=await save('home-admission-delta.local.json',{schemaVersion:'q025-organization-admission-delta/1',baseComponent:component.pin,placements:rows,decisions,reviewRegistry:[...sourceReviews.values()],adjudicationReceipts:receipts,allocationPolicy:'explicit_normalized_weights',scopeChanges:[],relations:[],aliases:[],completeAtlasAdmission:false,canonicalRemapping:'Requires separately admitted mapping and unchanged scope or explicit placement revalidation.'});
const counts={};for(const b of bindings)counts[b.policyClass]=(counts[b.policyClass]||0)+1;
const report={schemaVersion:'q025-approved-home-policy-compilation/1',status:'passed_exact_source_scope_review_and_primary_checks',fixture:false,admittedSourceUnits:rows.length,admittedHomeRows:rows.length,distinctDestinations:new Set(rows.map(r=>r.destinationId)).size,policyClasses:counts,readingBasis:rows.reduce((a,r)=>(a[r.basis]=(a[r.basis]||0)+1,a),{}),verifiedNativeArtifacts:verifiedFiles.size,primaryEvidenceVerification:primary.report,component:delta,bindings:rowHashes,receipts,helperSha256:sha256(await readFile(join(here,'../accepted.mjs'))),scriptSha256:sha256(await readFile(fileURLToPath(import.meta.url))),fullAtlasAdmission:false,existingHomesDuplicated:false,scopeAndIdentityChanges:0};
await save('report.json',report);console.log(JSON.stringify(report,null,2));
