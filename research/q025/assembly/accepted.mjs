/** Deterministic compilation of explicit adjudicated organization decisions. */
import {hydrateSources,sha256} from './corpus.mjs';
import {validateCanonicalIdentity} from './fine-identities.mjs';
import {isPrimaryReference,primaryLocatorFingerprint} from './primary-evidence.mjs';

const fail=message=>{throw new Error(`Accepted assembly: ${message}`);};
const setHash=ids=>sha256([...new Set(ids)].sort().join('\n'));
export const rehearsalCohortHash=setHash;
const mapUnique=(rows,name)=>{const out=new Map();for(const row of rows){if(!row?.id||out.has(row.id))fail(`duplicate/missing ${name} ID`);out.set(row.id,row);}return out;};
const navigationTypes=new Set(['narrower','method_for','application_of','comparison','premise_check','related_question']);
export const scopeContentHash=d=>sha256(JSON.stringify(Object.fromEntries(['kind','title','question','summary','scope','scientificStatus','readingCoverage','evidenceIds'].map(k=>[k,d[k]]))));
export const acceptedContentHash=packet=>sha256(JSON.stringify(Object.fromEntries(Object.entries(packet).filter(([key])=>key!=='acceptance'))));
export const sourceContributionContentHash=(row,scopeContentSha256)=>sha256(JSON.stringify({unitId:row.unitId,destinationId:row.destinationId,role:row.role,basis:row.basis,evidenceRefs:row.evidenceRefs,scopeContentSha256,...(row.qualification!==undefined?{qualification:row.qualification}:{})}));
export const provenanceRelationContentHash=row=>sha256(JSON.stringify({sourceReviewId:row.sourceReviewId,sourceRef:row.sourceRef,targetRef:row.targetRef,proposedType:row.proposedType,interpretation:row.interpretation,evidenceRefs:row.evidenceRefs}));
export const placementContentHash=(row,scopeContentSha256)=>sha256(JSON.stringify({unitId:row.unitId,destinationId:row.destinationId,role:row.role,status:row.status,basis:row.basis,allocationWeight:row.allocationWeight,associationScope:row.associationScope,workRelation:row.workRelation,reason:row.reason,qualification:row.qualification,evidenceRefs:row.evidenceRefs,scopeContentSha256}));

export function validateAdmittedScope(d,{decision,verifiedReceiptHashes=new Set()}) {
    const accepted=decision(d.scopeDecisionId,['scope_acceptance']);
    if(!accepted.subjectIds?.includes(d.id))fail(`scope decision does not name destination ${d.id}`);
    if(accepted.scopeContentSha256!==scopeContentHash(d))fail(`scope changed after its admission decision: ${d.id}`);
    const supported=accepted.challengerAgreement==='supported_as_written'&&accepted.scopeAgreement==='unchanged';
    const adjudicated=accepted.adjudication?.status==='accepted_explicit_scope'&&verifiedReceiptHashes.has(accepted.adjudication.receipt?.sha256);
    if(!supported&&!adjudicated)fail(`scope is rewritten, unsupported or awaiting review: ${d.id}`);
}

/** Shared production component gate; it never creates homes or allocations. */
export function compileSourceContributions({rows,destinations,units,decision,reviewRecords,verifiedPrimaryLocators=new Set(),verifiedReceiptHashes=new Set()}) {
  // A source's scientific contribution is independent of its direct home and
  // independent of whether multiple formulations denote one fine question.
  const dest=new Map(destinations.map(d=>[d.id,d])),reviews=new Set(reviewRecords.keys());
  const sourceContributions=[],contributionKeys=new Set(),contributionRoles=new Set(['addresses','instantiates','specializes','method','boundary','comparison']);
  for(const row of rows||[]){
    if(Object.keys(row).some(key=>!['unitId','destinationId','role','basis','evidenceRefs','decisionId','qualification'].includes(key)))fail('unbound typed contribution field');
    if(row.qualification!==undefined&&(typeof row.qualification!=='string'||row.qualification.length>8000))fail('invalid typed contribution qualification');
    const source=units.get(row.unitId),destination=dest.get(row.destinationId);if(!source||!destination)fail('unknown typed contribution endpoint');
    if(!contributionRoles.has(row.role)||!['description_checked','source_excerpt_checked'].includes(row.basis))fail('invalid typed contribution role/basis');
    if(!row.evidenceRefs?.length)fail('typed contribution lacks exact source evidence');
    for(const ref of row.evidenceRefs.filter(isPrimaryReference)){const fingerprint=primaryLocatorFingerprint(ref);if(!fingerprint||!verifiedPrimaryLocators.has(fingerprint))fail('typed contribution lacks an exact resolved primary locator');}
    const ownDescription=row.evidenceRefs.some(ref=>ref.kind==='description'&&ref.unitId===row.unitId&&ref.textSha256===source.evidence.textSha256),ownPrimary=row.evidenceRefs.some(ref=>isPrimaryReference(ref)&&ref.paperId===source.paperId&&verifiedPrimaryLocators.has(primaryLocatorFingerprint(ref)));
    if(!ownDescription&&!ownPrimary||row.basis==='source_excerpt_checked'&&!ownPrimary)fail('typed contribution evidence does not bind its exact source/basis');
    const proof=decision(row.decisionId,['source_contribution']),scopeHash=scopeContentHash(destination),agreement=proof.reviewAgreement;
    if(!proof.subjectIds?.includes(row.unitId)||!proof.subjectIds?.includes(row.destinationId))fail('typed contribution decision has wrong subjects');
    if(proof.scopeContentSha256!==scopeHash||proof.contributionContentSha256!==sourceContributionContentHash(row,scopeHash))fail('typed contribution changed after admission or names a different scope');
    const explicit=proof.challengerAgreement==='coordinator_adjudicated_source_contribution';
    if(explicit){
      const adjudication=proof.adjudication,receipt=adjudication?.receipt;
      if(adjudication?.status!=='accepted_explicit_source_contribution'||!receipt?.path||!/^[a-f0-9]{64}$/.test(receipt.sha256||'')||!verifiedReceiptHashes.has(receipt.sha256))fail('typed contribution explicit adjudication receipt is not verified');
      if(!proof.sourceReviewIds?.length||proof.sourceReviewIds.some(id=>!reviews.has(id)||!verifiedReceiptHashes.has(reviewRecords.get(id).sha256))||!proof.sourceReviewIds.some(id=>reviewRecords.get(id).sha256!==receipt.sha256))fail('typed contribution explicit adjudication lacks verified source review evidence');
      if(!row.evidenceRefs.every(ref=>(proof.evidenceRefs||[]).some(bound=>JSON.stringify(bound)===JSON.stringify(ref))))fail('typed contribution explicit adjudication does not bind its source evidence');
      if(agreement)fail('explicit contribution adjudication must not claim a fictional dual review agreement');
    }else{
      if(proof.challengerAgreement!=='independently_agreed'||!agreement?.proposalReviewId||!agreement.challengeReviewId||agreement.proposalReviewId===agreement.challengeReviewId||[agreement.proposalReviewId,agreement.challengeReviewId].some(id=>!reviews.has(id)||!proof.sourceReviewIds.includes(id)))fail('typed contribution lacks distinct pinned proposal and challenge evidence');
      if(!reviewRecords.get(agreement.proposalReviewId).sha256||reviewRecords.get(agreement.proposalReviewId).sha256===reviewRecords.get(agreement.challengeReviewId).sha256)fail('typed contribution repeats one review artifact under two IDs');
    }
    const key=[row.unitId,row.destinationId,row.role].join('\n');if(contributionKeys.has(key))fail('duplicate typed contribution');contributionKeys.add(key);
    sourceContributions.push({...row,scopeContentSha256:scopeHash,browserVectorRow:source.browserVectorRow,sourceRow:source.sourceRow,paperId:source.paperId,lens:source.lens,contributionStatus:'accepted_typed_contribution',provenance:{decisionId:row.decisionId,sourceReviewIds:proof.sourceReviewIds,...(explicit?{challengerAgreement:proof.challengerAgreement,adjudication:proof.adjudication}:{reviewAgreement:agreement}),doesNotAssertDirectHome:true,doesNotAssertEquivalence:true,doesNotAssertMethodApplicability:true}});
  }
  return sourceContributions;
}

export function assembleAccepted({packet,corpus,originalBins,originalBinsSha256,verifiedReceiptHashes=new Set(),verifiedPrimaryLocators=new Set(),fixture=false}) {
  if(packet.schemaVersion!=='q025-accepted-atlas/1')fail('unsupported acceptance packet');
  if(packet.acceptance?.status!=='accepted_for_assembly')fail('raw reviewer proposals cannot be assembled as accepted');
  if(!fixture&&!verifiedReceiptHashes.has(packet.acceptance.receipt?.sha256))fail('assembly admission receipt is not verified');
  if(packet.corpus?.corpusId!==corpus.manifest.corpusId||packet.corpus?.contentHash!==corpus.manifest.contentHash)fail('frozen corpus identity mismatch');
  if(packet.originalCandidate?.regionsSha256!==originalBinsSha256)fail('original candidate hash mismatch');
  if(packet.allocationPolicy!=='equal_across_explicit_homes'&&packet.allocationPolicy!=='explicit_normalized_weights')fail('organizational allocation policy must be explicit');
  const units=corpus.unitMap,allQuestions=corpus.units.filter(u=>u.lens==='physical_question'),allMethods=corpus.units.filter(u=>u.lens==='method');let questions=allQuestions,methods=allMethods;
  const bins=mapUnique(originalBins,'original bin'),originalRows=[];const leaves=originalBins.filter(b=>!b.childIds?.length),priorByUnit=new Map();
  for(const bin of originalBins){
    if(bin.candidateId!==packet.originalCandidate.candidateId)fail('mixed original candidates');
    for(const uid of bin.memberIds)if(!units.has(uid)||units.get(uid).lens!=='physical_question')fail('original candidate contains an unknown/nonquestion source');
    originalRows.push({candidateId:bin.candidateId,regionId:bin.id,memberCount:bin.memberIds.length,memberIdsSha256:setHash(bin.memberIds),parentIds:bin.parentIds||[],childIds:bin.childIds||[]});
  }
  for(const bin of leaves)for(const uid of bin.memberIds){if(priorByUnit.has(uid))fail('original leaf partition is not unique');priorByUnit.set(uid,bin.id);}
  if(allQuestions.some(u=>!priorByUnit.has(u.id)))fail('original leaf partition does not conserve the question corpus');
  const decisions=mapUnique(packet.decisions||[],'decision'),reviewRecords=mapUnique(packet.reviewRegistry||[],'review'),reviews=new Set(reviewRecords.keys());
  function decision(id,types){
    const d=decisions.get(id);if(!d||d.status!=='accepted'||!types.includes(d.type))fail(`missing admitted decision ${id}`);
    if(!d.sourceReviewIds?.length||d.sourceReviewIds.some(r=>!reviews.has(r)))fail(`unresolved review provenance ${id}`);
    if(!d.evidenceRefs?.length)fail(`decision lacks evidence ${id}`);
    return d;
  }
  const partialRehearsal=packet.coverage?.kind==='admitted_rehearsal_cohort';
  if(packet.coverage&&!partialRehearsal)fail('unknown explicit coverage mode');
  const partialCandidateReason=partialRehearsal?(packet.coverage.reason||'scientific_rehearsal'):null;if(partialRehearsal&&!['scientific_rehearsal','pre_holdout_freeze'].includes(partialCandidateReason))fail('unknown partial candidate reason');
  if(partialRehearsal){
    const ids=packet.coverage.unitIds,proof=decision(packet.coverage.decisionId,['rehearsal_cohort']);
    if(!Array.isArray(ids)||!ids.length||new Set(ids).size!==ids.length||ids.some(id=>units.get(id)?.lens!=='physical_question')||proof.outcome!=='approve_explicit_partial_corpus_rehearsal'||proof.unitIdsSha256!==setHash(ids)||ids.some(id=>!proof.subjectIds?.includes(id)))fail('partial rehearsal requires an explicit exact cohort admission');
    const selected=new Set(ids);questions=allQuestions.filter(u=>selected.has(u.id));const papers=new Set(questions.map(u=>u.paperId));methods=allMethods.filter(u=>papers.has(u.paperId));
  }
  const destinations=structuredClone(packet.destinations||[]),dest=mapUnique(destinations,'destination');
  if(!dest.has(packet.atlas?.entryDestinationId))fail('detailed entry destination absent');
  for(const d of destinations){
    if(!['region','question','method'].includes(d.kind))fail(`unsupported scientific destination kind ${d.id}`);
    validateAdmittedScope(d,{decision,verifiedReceiptHashes});
    if(!d.title||!d.question||!d.summary||!d.scientificStatus||!d.readingCoverage)fail(`missing reviewed readable scope ${d.id}`);
    if(d.aliases?.length)fail('aliases must be separate equivalence decisions');
    if(!d.scope||typeof d.scope!=='object'||Array.isArray(d.scope))fail(`missing exact reviewed scope ${d.id}`);
    // Retain the exact admitted nested key order; even a harmless default-field
    // normalization would invalidate the shared content hash.
    d.scope={...d.scope};d.aliases=[];d.contextSourceIds=d.contextSourceIds||[];
    if(!d.evidenceIds?.length||d.evidenceIds.some(uid=>!units.has(uid)))fail(`invalid representative evidence ${d.id}`);
    if((d.originalBinIds||[]).some(id=>!bins.has(id)))fail(`unknown original bin provenance ${d.id}`);
    d.provenance={...d.provenance,scopeDecisionId:d.scopeDecisionId,readingCoverage:d.readingCoverage,originalCandidateId:packet.originalCandidate.candidateId,originalBinIds:d.originalBinIds||[]};
    d.membershipStatus=d.kind==='region'?'complete':'representative';
  }
  const sourceContributions=compileSourceContributions({rows:packet.sourceContributions,destinations,units,decision,reviewRecords,verifiedPrimaryLocators,verifiedReceiptHashes});
  for(const d of destinations){if(d.sourceContributions?.length)fail('typed contributions must use the separately admitted packet table');d.sourceContributions=sourceContributions.filter(row=>row.destinationId===d.id);}
  const relations=[],parents=new Map(destinations.map(d=>[d.id,[]])),children=new Map(destinations.map(d=>[d.id,[]]));
  for(const raw of packet.relations||[]){
    if(!dest.has(raw.source)||!dest.has(raw.target)||raw.source===raw.target)fail(`unknown/self navigation endpoint ${raw.id}`);
    if(!navigationTypes.has(raw.type))fail(`source-science relation cannot be promoted to destination navigation: ${raw.type}`);
    const proof=decision(raw.decisionId,raw.type==='narrower'?['reparent','navigation']:['navigation']);
    if(proof.relationUse!=='public_navigation'||proof.relationType!==raw.type)fail('public navigation needs its explicit admitted semantic use and exact type');
    if(!proof.subjectIds?.includes(raw.source)||!proof.subjectIds?.includes(raw.target))fail(`navigation decision has wrong subjects ${raw.id}`);
    if(!raw.rationale||!raw.evidenceIds?.length||raw.evidenceIds.some(uid=>!units.has(uid)))fail(`navigation lacks source rationale ${raw.id}`);
    relations.push({...raw,status:'accepted_navigation',provenance:{...raw.provenance,decisionId:raw.decisionId,sourceScienceLayerSeparate:true}});
    if(raw.type==='narrower'){parents.get(raw.target).push(raw.source);children.get(raw.source).push(raw.target);}
  }
  const provenanceRelations=[];
  for(const row of packet.provenanceRelations||[]){
    const proof=decision(row.decisionId,['provenance_link']);
    if(!reviews.has(row.sourceReviewId)||!row.sourceRef||!row.targetRef||!row.proposedType||row.interpretation!=='review_batch_provenance'||!row.evidenceRefs?.length)fail('invalid review-batch provenance link');
    if(proof.relationUse!=='provenance_only'||proof.provenanceRelationContentSha256!==provenanceRelationContentHash(row))fail('provenance link lacks explicit interpretation or exact binding');
    provenanceRelations.push({...row,publicNavigation:false,affectsContainment:false,affectsGeometry:false});
  }
  const visiting=new Set(),visited=new Set(),order=[];
  function visit(id){if(visiting.has(id))fail('cyclic accepted containment');if(visited.has(id))return;visiting.add(id);for(const child of children.get(id))visit(child);visiting.delete(id);visited.add(id);order.push(id);}
  for(const id of dest.keys())visit(id);
  function ancestors(id){const out=new Set(),todo=[...parents.get(id)];while(todo.length){const n=todo.pop();if(out.has(n))continue;out.add(n);todo.push(...parents.get(n));}return out;}
  const direct=new Map(),placementKeys=new Set(),ambiguous=[];
  for(const p of packet.placements||[]){
    if(!units.has(p.unitId)||!dest.has(p.destinationId))fail(`unknown placement identity ${p.unitId}`);
    if(!['member','overlap','context'].includes(p.role)||!['accepted','provisional','unresolved'].includes(p.status))fail('invalid placement role/status');
    const key=`${p.unitId}\n${p.destinationId}`;if(placementKeys.has(key))fail('duplicate direct placement');placementKeys.add(key);
    const proof=decision(p.decisionId,p.role==='overlap'?['overlap','placement']:['placement']);
    if(!proof.subjectIds?.includes(p.unitId)||!proof.subjectIds?.includes(p.destinationId))fail(`placement decision has wrong subjects ${key}`);
    const explicitPlacement=proof.adjudication?.status==='accepted_explicit_placement'&&verifiedReceiptHashes.has(proof.adjudication.receipt?.sha256)&&proof.scopeContentSha256===scopeContentHash(dest.get(p.destinationId))&&proof.placementContentSha256===placementContentHash(p,proof.scopeContentSha256);
    if(p.status==='accepted'&&proof.challengerAgreement!=='independently_agreed'&&!explicitPlacement)fail(`unagreed accepted placement ${key}`);
    if(partialRehearsal&&units.get(p.unitId).lens==='physical_question'&&!questions.some(u=>u.id===p.unitId))fail('rehearsal placement escapes the explicitly admitted cohort');
    if(p.status!=='accepted'){
      if(dest.get(p.destinationId).kind!=='region'||!p.reason||proof.outcome!=='retain_provisional_family_placement')fail('unresolved placement needs an explicitly admitted broad family and reason');
      ambiguous.push({...p});
    }
    if(p.role==='context'&&!p.associationScope)fail('context placement requires its attachment scope');
    if(p.workRelation==='using'&&!proof.sourceRelationRefs?.length&&!proof.sourceExcerptSupport)fail('using requires scoped evidence, not co-paper association');
    if(!direct.has(p.unitId))direct.set(p.unitId,[]);direct.get(p.unitId).push({...p});
  }
  const allocations=[];
  for(const u of questions){
    const rows=(direct.get(u.id)||[]).filter(p=>p.role!=='context');if(!rows.length)fail(`uncovered question; no catch-all is invented: ${u.id}`);
    for(const p of rows)for(const other of rows)if(p!==other&&ancestors(p.destinationId).has(other.destinationId))fail(`direct home duplicates its ancestor: ${u.id}`);
    const weights=rows.map(p=>packet.allocationPolicy==='equal_across_explicit_homes'?1/rows.length:p.allocationWeight);
    if(weights.some(w=>!Number.isFinite(w)||w<=0)||Math.abs(weights.reduce((a,b)=>a+b,0)-1)>1e-10)fail(`organizational allocation does not conserve unit ${u.id}`);
    rows.forEach((p,i)=>allocations.push({unitId:u.id,destinationId:p.destinationId,weight:weights[i],placementStatus:p.status,decisionId:p.decisionId,originalBinId:priorByUnit.get(u.id)}));
  }
  const members=new Map(destinations.map(d=>[d.id,new Map()]));
  function rowFor(uid,destinationId,weight,p){const u=units.get(uid),paper=corpus.papers.get(u.paperId);return {destinationId,unitId:uid,paperId:u.paperId,weight,lens:u.lens,year:paper.year,browserVectorRow:u.browserVectorRow,sourceRow:u.sourceRow,role:p.workRelation||'on',placementStatus:p.status||p.placementStatus,decisionIds:[p.decisionId],...(p.associationScope?{associationScope:p.associationScope}:{}),...(p.reason?{placementReason:p.reason}:{}),...(p.basis?{placementBasis:p.basis}:{}),...(p.qualification?{placementQualification:p.qualification}:{})};}
  function addRow(id,row){const prev=members.get(id).get(row.unitId);if(!prev||prev.placementStatus==='context_only'&&row.placementStatus!=='context_only')members.get(id).set(row.unitId,row);else if(row.placementStatus!=='context_only'){prev.weight=Math.min(1,prev.weight+row.weight);prev.decisionIds=[...new Set([...prev.decisionIds,...row.decisionIds])];if(prev.placementStatus!=='accepted'||row.placementStatus!=='accepted')prev.placementStatus='contains_provisional_placement';}}
  for(const a of allocations){const p=(direct.get(a.unitId)||[]).find(p=>p.destinationId===a.destinationId);for(const id of [a.destinationId,...ancestors(a.destinationId)])addRow(id,rowFor(a.unitId,id,a.weight,p));}
  for(const [uid,rows] of direct)for(const p of rows)if(units.get(uid).lens==='method'||p.role==='context'){
    for(const id of p.role==='context'?[p.destinationId]:[p.destinationId,...ancestors(p.destinationId)]){const r=rowFor(uid,id,p.allocationWeight??1,p);if(p.role==='context'){r.role='evidence';r.placementStatus='context_only';}addRow(id,r);}
  }
  // Methods from papers represented in a region are contextual source inventory,
  // not claims of method use; geometry never consumes these rows.
  if(['same_paper_context_at_regions','same_paper_context_at_scientific_destinations'].includes(packet.methodContextPolicy?.kind)){
    const policy=decision(packet.methodContextPolicy.decisionId,['context_policy']);
    if(policy.outcome!=='context_only_no_applicability')fail('method context policy must exclude applicability');
    const methodByPaper=new Map();for(const m of methods){if(!methodByPaper.has(m.paperId))methodByPaper.set(m.paperId,[]);methodByPaper.get(m.paperId).push(m);}
    for(const d of destinations.filter(d=>d.kind==='region'||packet.methodContextPolicy.kind==='same_paper_context_at_scientific_destinations'&&d.kind==='question')){
      const byPaper=new Map();for(const r of members.get(d.id).values())if(r.lens==='physical_question'&&r.placementStatus!=='context_only'){if(!byPaper.has(r.paperId))byPaper.set(r.paperId,[]);byPaper.get(r.paperId).push(r.unitId);}
      for(const [paperId,qids] of byPaper)for(const m of methodByPaper.get(paperId)||[]){if(members.get(d.id).has(m.id))continue;members.get(d.id).set(m.id,{...rowFor(m.id,d.id,1,{status:'context_only',decisionId:policy.id,associationScope:'same_paper_context'}),role:'evidence',associationProvenance:{join:'exact frozen paperId',paperId,sourceQuestionIds:qids.sort(),noMethodApplicabilityInferred:true}});}
    }
  }else if(methods.length)fail('method source visibility policy must be explicitly admitted');
  const memberships=[...members.values()].flatMap(rows=>[...rows.values()]);
  for(const d of destinations){
    const rows=[...members.get(d.id).values()],primary=rows.filter(r=>r.placementStatus!=='context_only');d.memberIds=primary.map(r=>r.unitId).sort();d.memberIdsSha256=setHash(d.memberIds);d.placementStatus=primary.some(r=>r.placementStatus!=='accepted')?'reviewed_scope_with_visible_provisional_placements':'reviewed_scope_and_placements';d.contextAssociationCount=rows.length-primary.length;
    const contextSample=[],samplePapers=new Set();for(const r of rows.filter(r=>r.placementStatus==='context_only'&&r.lens==='method').sort((a,b)=>a.browserVectorRow-b.browserVectorRow)){if(samplePapers.has(r.paperId))continue;contextSample.push(r.unitId);samplePapers.add(r.paperId);if(contextSample.length===6)break;}d.contextSourceIds=[...new Set([...d.contextSourceIds,...contextSample])].slice(0,100);
    if(d.completeMemberIds&&setHash(d.completeMemberIds)!==d.memberIdsSha256)fail(`declared complete membership differs from accepted containment closure ${d.id}`);
    delete d.completeMemberIds;
  }
  for(const r of relations.filter(r=>r.type==='narrower'))for(const uid of dest.get(r.target).memberIds)if(!members.get(r.source).has(uid)||members.get(r.source).get(uid).placementStatus==='context_only')fail('primary child escapes parent');
  const rootMembers=new Set(dest.get(packet.atlas.entryDestinationId).memberIds);
  if(!partialRehearsal&&questions.some(u=>!rootMembers.has(u.id)))fail('detailed entry does not reach every question through accepted containment');
  if(partialRehearsal){const independent=packet.coverage.independentEntryDestinationIds||[],proof=decision(packet.coverage.decisionId,['rehearsal_cohort']);if(new Set(independent).size!==independent.length||JSON.stringify(independent)!==JSON.stringify(proof.independentEntryDestinationIds||[])||independent.some(id=>!dest.has(id)||!proof.subjectIds.includes(id)))fail('independent rehearsal entry lacks exact admission');const reachable=new Set([packet.atlas.entryDestinationId,...independent]);let changed=true;while(changed){changed=false;for(const r of relations)if(reachable.has(r.source)||reachable.has(r.target)){for(const id of [r.source,r.target])if(!reachable.has(id)){reachable.add(id);changed=true;}}}if(allocations.some(a=>!reachable.has(a.destinationId)))fail('rehearsal home is unreachable through admitted navigation');}
  const methodVisible=new Set(memberships.filter(m=>m.lens==='method').map(m=>m.unitId));if(methods.some(u=>!methodVisible.has(u.id)))fail('method source has no source/context view');
  if(packet.identityResolution&&!fixture&&!verifiedReceiptHashes.has(packet.identityResolution.registry?.sha256))fail('identity comparison inventory is not verified');
  const identityResolution=validateCanonicalIdentity({resolution:packet.identityResolution,destinations,decision,scopeHash:scopeContentHash,reviewRecords});
  for(const a of packet.aliases||[]){const d=dest.get(a.destinationId),group=identityResolution.groups.find(g=>g.id===a.identityGroupId);if(!d||!group||group.destinationId!==d.id||group.decisionId!==a.decisionId||!group.memberIds.includes(a.sourceRecordId)||typeof a.alias!=='string'||!a.alias.trim())fail('alias lacks accepted conflict-free whole-group equivalence');d.aliases.push(a.alias);}
  const representedPapers=new Set(corpus.units.map(u=>u.paperId)),unrepresentedPapers=[...corpus.papers.values()].filter(p=>!representedPapers.has(p.id)).map(p=>({id:p.id,title:p.title,sourceUrl:p.url,sourceSha256:p.sourceSha256,sourceNotice:p.sourceNotice,scientificStatus:p.scientificStatus,reason:'No vector-covered question/method unit in this frozen navigation corpus; source availability is not inferred.'}));
  const catalog={destinations,sources:hydrateSources(corpus),memberships,relations,sourceContributions,unrepresentedPapers,organizationProvenance:{originalCandidate:{candidateId:packet.originalCandidate.candidateId,regionsSha256:packet.originalCandidate.regionsSha256},originalBins:originalRows,acceptance:{status:packet.acceptance.status,receipt:{sha256:packet.acceptance.receipt.sha256}},decisionIds:[...decisions.keys()],provenanceRelations,identityResolution,geometryMembershipsAreOrganizationalAllocations:true}};
  const paperCounts=new Map(),globalPaperCounts=new Map();for(const u of questions)paperCounts.set(u.paperId,(paperCounts.get(u.paperId)||0)+1);for(const u of allQuestions)globalPaperCounts.set(u.paperId,(globalPaperCounts.get(u.paperId)||0)+1);
  const paperMassPolicy=partialRehearsal?'cohort_renormalized_one_mass_per_represented_paper':'global_one_mass_per_paper_using_all_question_counts';
  const baseDestinationIds=packet.geometry?.baseDestinationIds||[];if(baseDestinationIds.some(id=>!['region','question'].includes(dest.get(id)?.kind)))fail('geometry base is not an admitted scientific destination');
  const geometryInput={schemaVersion:'q025-accepted-geometry-input/1',corpus:packet.corpus,coverage:{partialRehearsal,allocatedQuestionCount:questions.length,unallocatedQuestionCount:allQuestions.length-questions.length,cohortUnitIdsSha256:partialRehearsal?setHash(questions.map(u=>u.id)):null,independentEntryDestinationIds:packet.coverage?.independentEntryDestinationIds||[],paperMassPolicy,globalQuestionCount:allQuestions.length,globalPaperCount:globalPaperCounts.size},originalCandidate:packet.originalCandidate,acceptanceReceipt:packet.acceptance.receipt,allocations,units:questions.map(u=>({unitId:u.id,paperId:u.paperId,browserVectorRow:u.browserVectorRow,sourceRow:u.sourceRow,textSha256:u.evidence.textSha256,paperBalancedMass:1/paperCounts.get(u.paperId),globalPaperQuestionCount:globalPaperCounts.get(u.paperId),selectedPaperQuestionCount:paperCounts.get(u.paperId),inheritedGlobalPaperMass:1/globalPaperCounts.get(u.paperId)})),destinations:destinations.map(d=>({id:d.id,kind:d.kind,memberIds:d.memberIds.filter(id=>units.get(id).lens==='physical_question'),parentIds:parents.get(d.id)})),baseDestinationIds,allocationMeaning:'Organizational mass among explicit reviewed/provisional homes, not confidence or relevance.',contextMembershipRowsUsedAsAllocations:false};
  const allocationSums=new Map();for(const a of allocations)allocationSums.set(a.unitId,(allocationSums.get(a.unitId)||0)+a.weight);
  const report={paperMassPolicy,partialCandidateReason,partialRehearsal,scientificCoverageComplete:!partialRehearsal,allocatedQuestionCount:questions.length,unallocatedQuestionCount:allQuestions.length-questions.length,unallocatedQuestionIdsSha256:setHash(allQuestions.filter(u=>!allocationSums.has(u.id)).map(u=>u.id)),allSourceUnitsConserved:catalog.sources.length===corpus.units.length,sourceUnits:corpus.units.length,questionUnits:questions.length,methodUnits:methods.length,representedPaperCount:representedPapers.size,unrepresentedPapers,questionAllocationMaxError:Math.max(0,...questions.map(u=>Math.abs(allocationSums.get(u.id)-1))),visibleAmbiguousPlacements:ambiguous,originalLeafCount:leaves.length,originalBinCount:originalBins.length,sourceTextAndRowIdentity:'Exact frozen corpus hydration; no source rewrites.',methodAssociationMeaning:'Same-paper context is not primary membership or actual uses.',acceptedTypedContributions:sourceContributions.length,typedContributionsAffectAllocation:false,sourceScienceImportedAsNavigation:false};
  return {catalog,geometryInput,report};
}
