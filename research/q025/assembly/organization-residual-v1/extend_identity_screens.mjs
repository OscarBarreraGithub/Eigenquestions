/** Carry all completed screening constraints into the whole-group audit. */
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {join,resolve,relative,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {sha256,loadFrozenCorpus} from '../corpus.mjs';
import {scopeContentHash} from '../accepted.mjs';
import {validateCanonicalIdentity} from '../fine-identities.mjs';
const here=dirname(fileURLToPath(import.meta.url)),root=resolve(here,'../../../..'),F=join(root,'research/q025/evaluation/full-pass'),out=join(here,'identity-screen-complete-v1');
async function read(path,expected){const raw=await readFile(path);if(expected&&sha256(raw)!==expected)throw Error('Changed inventory '+path);return {value:JSON.parse(raw),pin:{path:relative(root,path),sha256:sha256(raw)}};}
const base=await read(join(here,'identity-current-v2/inventory.json'),'1ac10dea4068dc4b16f87fef637985f8e6a91d692eacfa02e5544810aa286b8a');
const old=await read(join(here,'identity-current-v2/report.json'));
const screens=await read(join(F,'native-local/navigation-wave-v2/combined-screen-intake.json'),'0ef92b332f653470b6bd2583a0df8b3d8b5094d21c9805de35eb80141e9a005d');
const census=await read(join(F,'native-local/canonical-completion-census-v1/inventory.json'),'2c715b85a0987ddbb9c7a95f197a99645307fe1af8aec796416c1785e352ec5f');
const packet=await read(join(here,'candidate-6030-navigation-v2/aggregate.local.json'));
const rows=new Map(census.value.rows.map(r=>[r.comparisonId,r])),registered=new Set(base.value.records.map(r=>r.id)),reviewRecords=new Map(packet.value.reviewRegistry.map(r=>[r.id,r]));
let fileCount=0;for(const r of screens.value.inputReceipts){
  for(const key of ['reply','receipt','packet','normalization'])if(r[key]){await read(join(root,r[key].path),r[key].sha256);fileCount++;}
  reviewRecords.set(r.jobId,{id:r.jobId,sha256:r.reply.sha256,path:r.reply.path});
}
const comparisons=[...base.value.comparisons],screenRows=[];
for(const s of screens.value.comparisons){
  const c=rows.get(s.comparisonId);if(!c||JSON.stringify(c.recordIds)!==JSON.stringify(s.recordIds)||c.candidateIds.some(id=>!registered.has(id)))throw Error('Screen/current exact-ID mapping mismatch');
  const internal=old.value.groups.filter(g=>c.candidateIds.every(id=>g.memberIds.includes(id)));
  const resolving=internal.filter(g=>c.admittedOperations.some(o=>o.id===g.operationId&&o.operation==='same_scoped_question')&&!s.variantConflictWithheld);
  const r={comparisonId:s.comparisonId,candidateIds:c.candidateIds,recordIds:s.recordIds,workloadIds:s.workloadIds,screens:s.screens,variantConflictWithheld:s.variantConflictWithheld,
           disposition:resolving.length?'resolved_by_exact_root_admitted_whole_group_source_decision':'pending_screening_constraint_not_scientific_admission',resolvingOperationIds:resolving.map(g=>g.operationId),currentDecisionCoverage:c};screenRows.push(r);
  if(!resolving.length)comparisons.push({id:'pending-screen:'+s.comparisonId,operation:'unresolved',members:c.candidateIds,definingDifferences:s.screens.flatMap(x=>x.judgment.definingDifferences||[]),sourceReviewIds:[...new Set(s.screens.map(x=>x.jobId))],evidenceRefs:[{kind:'pinned_screening_nomination',comparisonId:s.comparisonId,intakeSha256:screens.pin.sha256}],screeningOnly:true,scientificAdmission:false,variantConflictWithheld:s.variantConflictWithheld});
}
if(screenRows.length!==8282||screens.value.withheldVariantConflicts.length!==6)throw Error('Incomplete authoritative screen inventory');
await mkdir(out,{recursive:true});
const inventory={...base.value,inputs:[...base.value.inputs,screens.pin,census.pin],comparisons,screeningAccounting:screenRows,withheldVariantConflicts:screens.value.withheldVariantConflicts,allScreenPositiveEquivalencesRemainNominations:true};
const raw=JSON.stringify(inventory)+'\n',path=join(out,'inventory.local.json');await writeFile(path,raw);const pin={path:relative(root,path),sha256:sha256(raw)};
const resolution={registry:pin,records:base.value.records,comparisons,canonicalGroups:[]};
const audit=validateCanonicalIdentity({resolution,destinations:packet.value.destinations,scopeHash:scopeContentHash,reviewRecords,decision:()=>{throw Error('No global group admission is invented');}});
const corpus=await loadFrozenCorpus(join(root,'data/navigation')),dest=new Map(packet.value.destinations.map(d=>[d.id,d]));
const groups=old.value.groups.map(g=>({...g,fullDefinitions:g.memberIds.map(id=>dest.get(id)),screenHits:screenRows.filter(r=>r.candidateIds.some(id=>g.memberIds.includes(id))),
  internalScreenHits:screenRows.filter(r=>r.candidateIds.every(id=>g.memberIds.includes(id))),
  relatedVariantConflicts:screenRows.filter(r=>r.variantConflictWithheld&&r.candidateIds.some(id=>g.memberIds.includes(id))),
  conflicts:audit.unresolvedConflicts.filter(c=>c.memberIds.some(id=>g.memberIds.includes(id))),
  homeRevalidation:g.currentHomeRows.map(h=>({source:{unitId:h.unitId,paperId:corpus.unitMap.get(h.unitId).paperId,wholeQuestion:corpus.unitMap.get(h.unitId).text,textSha256:corpus.unitMap.get(h.unitId).evidence.textSha256},currentHome:h,canonicalScopeContentSha256:scopeContentHash(dest.get(g.canonicalDestinationId)),proposedDestinationId:g.canonicalDestinationId,changesDestination:h.destinationId!==g.canonicalDestinationId,proposedWeight:h.allocationWeight,status:'pending_explicit_whole_scope_home_revalidation_no_mass_transferred'}))}));
const intake={schemaVersion:'q025-whole-group-screen-and-home-intake/1',inputs:[base.pin,old.pin,screens.pin,census.pin,packet.pin],completeInventory:pin,groups,
              sourceStatementEquivalence:false,automaticAliases:0,automaticHomeTransfer:0,readingLimitsPolicy:'All member readingCoverage objects remain explicitly attached to any future reusable destination; no overwritten limitation or new claim of primary/calc coverage.'};
await writeFile(join(out,'group-intake.json'),JSON.stringify(intake,null,2)+'\n');
const summary={schemaVersion:'q025-identity-complete-screen-audit/1',status:groups.some(g=>g.conflicts.length)?'group_conflict_queue_required':'three_groups_clear_of_all_current_admitted_and_pending_screen_constraints',completeInventory:pin,inputPins:[screens.pin,census.pin],verifiedOriginalScreenFiles:fileCount,logicalScreenCalls:screens.value.inputReceipts.length,screenComparisons:screenRows.length,originalNominationIds:new Set(screenRows.flatMap(r=>r.workloadIds)).size,variantConflictsRetained:screens.value.withheldVariantConflicts.length,screenConstraintsPending:screenRows.filter(r=>!r.resolvingOperationIds.length).length,currentAdmittedComparisons:base.value.comparisons.length,historicalConstraints:base.value.historicalConstraints.length,
               groups:groups.map(g=>({operationId:g.operationId,members:g.memberIds,screenHits:g.screenHits.length,internalScreenHits:g.internalScreenHits.map(x=>({comparisonId:x.comparisonId,disposition:x.disposition,resolvingOperationIds:x.resolvingOperationIds})),variantConflicts:g.relatedVariantConflicts.length,currentConstraintConflicts:g.conflicts.length,homeRows:g.homeRevalidation.length,homeDestinationChanges:g.homeRevalidation.filter(x=>x.changesDestination).length})),
               groupIntake:{path:relative(root,join(out,'group-intake.json')),sha256:sha256(await readFile(join(out,'group-intake.json')))},automaticAliases:0,automaticMassTransfer:0,scriptSha256:sha256(await readFile(fileURLToPath(import.meta.url)))};
await writeFile(join(out,'report.json'),JSON.stringify(summary,null,2)+'\n');console.log(JSON.stringify(summary,null,2));
