/** Bind root's three exact groups against the complete current screen inventory. */
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {join,resolve,relative,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {sha256} from '../corpus.mjs';
import {scopeContentHash,acceptedContentHash,placementContentHash} from '../accepted.mjs';
import {identityInventoryHash,canonicalIdentityGroupHash,validateCanonicalIdentity} from '../fine-identities.mjs';
const here=dirname(fileURLToPath(import.meta.url)),root=resolve(here,'../../../..'),base=join(here,'candidate-6030-navigation-v2'),out=join(here,'candidate-6030-canonical-v3');
async function read(path,expected){const raw=await readFile(path);if(expected&&sha256(raw)!==expected)throw Error('Changed input '+path);return {value:JSON.parse(raw),pin:{path:relative(root,path),sha256:sha256(raw)}};}
async function save(name,value){const path=join(out,name),raw=JSON.stringify(value,null,2)+'\n';await writeFile(path,raw);return {path:relative(root,path),sha256:sha256(raw)};}
const input=await read(join(base,'aggregate.local.json')),intake=await read(join(here,'identity-screen-complete-v1/group-intake.json'),'aef0d6c57a8c5fd2559e37bf75c46e9b41c0cf283fbc93140de869e212c25508'),report=await read(join(here,'identity-screen-complete-v1/report.json'));
const inv=await read(join(root,intake.value.completeInventory.path),intake.value.completeInventory.sha256),screenPin=intake.value.inputs.find(p=>p.path.endsWith('combined-screen-intake.json')),screens=await read(join(root,screenPin.path),screenPin.sha256);
const p=input.value,dest=new Map(p.destinations.map(d=>[d.id,d]));
if(report.value.screenComparisons!==8282||report.value.variantConflictsRetained!==6||report.value.groups.some(g=>g.currentConstraintConflicts||g.variantConflicts))throw Error('Whole group has unresolved inventory conflict');
for(const r of p.reviewRegistry)r.path=relative(out,resolve(base,r.path));
for(const d of p.decisions)if(d.adjudication?.receipt?.path)d.adjudication.receipt.path=relative(out,resolve(base,d.adjudication.receipt.path));
p.originalCandidate.regionsPath=relative(out,resolve(base,p.originalCandidate.regionsPath));
for(const key of ['sourceContextRoot','sourceArchiveRoot'])p.assets[key]=relative(out,resolve(base,p.assets[key]));
const seen=new Set(p.reviewRegistry.map(r=>r.id));for(const r of screens.value.inputReceipts)if(!seen.has(r.jobId)){p.reviewRegistry.push({id:r.jobId,kind:'screening_constraint_not_scientific_admission',path:relative(out,join(root,r.reply.path)),sha256:r.reply.sha256});seen.add(r.jobId);}
const resolution={registry:{path:relative(out,join(root,inv.pin.path)),sha256:inv.pin.sha256},records:inv.value.records,comparisons:inv.value.comparisons,canonicalGroups:[]};
const inventoryHash=identityInventoryHash(resolution),operations=new Map(inv.value.comparisons.filter(c=>c.id.startsWith('operation:')).map(c=>[c.id,c]));
await mkdir(out,{recursive:true});
const homes=intake.value.groups.flatMap(g=>g.homeRevalidation);if(homes.length!==4||homes.some(h=>h.changesDestination))throw Error('Unexpected home transfer');
const admission=await save('canonical-group-admission.json',{schemaVersion:'q025-explicit-whole-group-admission/1',status:'accepted_exact_scoped_question_groups',adjudicator:'root',authority:'Root read all full definitions, four source-home questions, internal screen contrasts and category census, then approved these three complete scoped-question identity groups after complete8282-screen and six-conflict accounting.',inputs:[input.pin,intake.pin,report.pin,inv.pin],groups:intake.value.groups.map(g=>({operationId:g.operationId,members:g.memberIds,canonicalDestinationId:g.canonicalDestinationId,canonicalScopeContentSha256:g.canonicalScopeContentSha256,retainedReadingLimits:g.retainedReadingLimits})),revalidatedUnchangedHomes:homes.map(h=>({unitId:h.source.unitId,paperId:h.source.paperId,destinationId:h.currentHome.destinationId,weight:h.currentHome.allocationWeight,placementContentSha256:placementContentHash(h.currentHome,h.canonicalScopeContentSha256),scopeContentSha256:h.canonicalScopeContentSha256})),policy:'Original definitions/reading limits remain inspectable; equality concerns scoped question identity only. External pending nominations and all six variants remain pending. Original route/role receipts are retained before exact endpoint projection; self-routes are archived, not asserted. No source allocation destination or weight changes.'});
p.reviewRegistry.push({id:'root:canonical-three-groups',path:'canonical-group-admission.json',sha256:admission.sha256});
for(const g of intake.value.groups){
  const op=operations.get(g.operationId);if(!op||op.operation!=='same_scoped_question'||op.definingDifferences.length||g.canonicalScopeContentSha256!==scopeContentHash(dest.get(g.canonicalDestinationId)))throw Error('Changed exact local equality or scope');
  const row={id:'identity-group:'+sha256(g.operationId).slice(0,24),destinationId:g.canonicalDestinationId,memberIds:g.memberIds,decisionId:'decision:whole-group:'+sha256(g.operationId).slice(0,24)};
  const decision={id:row.decisionId,type:'question_equivalence',status:'accepted',outcome:'equivalent_as_scoped',challengerAgreement:'independently_agreed',changedPremises:[],canonicalDestinationId:row.destinationId,subjectIds:[...new Set([row.destinationId,...row.memberIds])],scopeContentSha256:scopeContentHash(dest.get(row.destinationId)),identityInventorySha256:inventoryHash,identityGroupContentSha256:canonicalIdentityGroupHash(row,scopeContentHash(dest.get(row.destinationId)),inventoryHash),sourceReviewIds:[...op.sourceReviewIds,'root:canonical-three-groups'],reviewAgreement:{proposalReviewId:op.sourceReviewIds[0],challengeReviewId:op.sourceReviewIds[1]},evidenceRefs:op.evidenceRefs,coordinatorAdmissionReceipt:admission,originalOperationId:g.operationId};
  p.decisions.push(decision);resolution.canonicalGroups.push(row);
  for(const id of row.memberIds)if(id!==row.destinationId)p.aliases.push({alias:dest.get(id).title,destinationId:row.destinationId,sourceRecordId:id,identityGroupId:row.id,decisionId:row.decisionId});
}
const decisions=new Map(p.decisions.map(d=>[d.id,d]));
const gate=validateCanonicalIdentity({resolution,destinations:p.destinations,decision:id=>decisions.get(id),scopeHash:scopeContentHash,reviewRecords:new Map(p.reviewRegistry.map(r=>[r.id,r]))});
if(gate.groups.length!==3||gate.unresolvedConflicts.length)throw Error('Exact whole-group gate failed');
p.identityResolution=resolution;p.atlas.atlasVersion='2026-11-17-cohort-6030-canonical-v3';p.provenance={...p.provenance,canonicalGroupsCreated:3,canonicalGroupAdmission:admission,completeIdentityInventory:inv.pin,globalCanonicalReconciliationComplete:false};
const receipt=await save('aggregate-admission.json',{schemaVersion:'q025-assembly-binding-receipt/1',status:'accepted_for_assembly',acceptedContentSha256:acceptedContentHash(p),authority:'Mechanical binding of root-approved exact groups and unchanged homes to current admitted organization; no other identity, source home or scientific route admitted.',input:input.pin,canonicalAdmission:admission,fullAtlasAdmission:false});
p.acceptance={status:'accepted_for_assembly',receipt:{path:'aggregate-admission.json',sha256:receipt.sha256}};
const packet=await save('aggregate.local.json',p);await save('binding.json',{schemaVersion:'q025-canonical-candidate-binding/1',packet,receipt,canonicalAdmission:admission,groups:3,redirects:p.aliases.length,sourceHomeDestinationChanges:0,weightChanges:0,allOriginalReadingLimitsRetained:true,fullAtlasAdmission:false,scriptSha256:sha256(await readFile(fileURLToPath(import.meta.url)))});
console.log(JSON.stringify({packet,receipt,canonicalAdmission:admission,groups:gate.groups.length,aliases:p.aliases.length,inventoryComparisons:resolution.comparisons.length,homeChanges:0},null,2));
