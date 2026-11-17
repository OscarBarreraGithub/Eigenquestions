/** Bounded whole-group audit; no group, home or screen disposition is admitted. */
import {readFile,writeFile,mkdir,readdir} from 'node:fs/promises';
import {join,resolve,relative,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {sha256,loadFrozenCorpus} from '../corpus.mjs';
import {scopeContentHash} from '../accepted.mjs';
import {validateCanonicalIdentity,identityInventoryHash} from '../fine-identities.mjs';
const here=dirname(fileURLToPath(import.meta.url)),root=resolve(here,'../../../..'),F=join(root,'research/q025/evaluation/full-pass'),out=join(here,'identity-current-v3');
async function read(path,expected){const raw=await readFile(path);if(expected&&sha256(raw)!==expected)throw Error('Changed pin '+path);return {value:JSON.parse(raw),pin:{path:relative(root,path),sha256:sha256(raw),bytes:raw.length}};}
const base=await read(join(here,'identity-screen-complete-v1/inventory.local.json'),'06489a700b826e0d4a96e97d764bf8aaaf3f34d298035f3ff0ca24ac325fbe49');
const packet=await read(join(here,'candidate-6117-connected-v5/aggregate.local.json'));
const components=[];for(const directory of ['navigation-admissions-v2','navigation-admissions-v4'])for(const name of (await readdir(join(F,directory))).filter(n=>n.endsWith('-component.json')).sort())components.push(await read(join(F,directory,name)));
const screenSuccessor=await read(join(F,'screen-conflict-admissions-v1/constraint-successors.json'),'c92a29ed2c2f2c6ca80ff4cd35251af3932c65b04fc0a3d09288017d0f10902c');
components.push(await read(join(F,'screen-conflict-admissions-v1/component.json'),'fddfbcad2699978fec6f424495256259031f5ec868c80e298d94a792a52c3d98'));
const destinations=packet.value.destinations,dest=new Map(destinations.map(d=>[d.id,d])),records=new Map(base.value.records.map(r=>[r.id,r])),reviews=new Map(packet.value.reviewRegistry.map(r=>[r.id,r]));
const screenPath=join(F,'native-local/navigation-wave-v2/combined-screen-intake.json'),screens=await read(screenPath,'0ef92b332f653470b6bd2583a0df8b3d8b5094d21c9805de35eb80141e9a005d');
for(const r of screens.value.inputReceipts)reviews.set(r.jobId,{id:r.jobId,path:r.reply.path,sha256:r.reply.sha256});
for(const d of destinations)records.set(d.id,{...records.get(d.id),id:d.id,contentSha256:sha256(JSON.stringify({id:d.id,scopeContentSha256:scopeContentHash(d)})),currentScopeContentSha256:scopeContentHash(d)});
const comparisons=[...base.value.comparisons],history=[...base.value.historicalConstraints],groups=[];
const mapOperation=r=>r==='same_scoped_question'?r:r.startsWith('specializes')?'specializes':r==='overlap'?'shared_parent_distinct':['changed_scope','distinct'].includes(r)?'different':r;
for(const c of components){
  for(const r of c.value.reviewRegistry||[])reviews.set(r.id,r);
  for(const d of c.value.destinations||[])if(!dest.has(d.id)){dest.set(d.id,d);records.set(d.id,{id:d.id,contentSha256:sha256(JSON.stringify({id:d.id,scopeContentSha256:scopeContentHash(d)})),currentScopeContentSha256:scopeContentHash(d),sourceComponent:c.pin});}
  // Rejected or superseded proposals still need an exact identity in the
  // conflict ledger. Register their component-bound local ref, never a public
  // destination or accepted scientific definition.
  for(const [localRef,id]of Object.entries(c.value.sourceScopeBindings||{}))if(!records.has(id))records.set(id,{id,contentSha256:sha256(JSON.stringify({id,localRef,componentSha256:c.pin.sha256})),registryOnly:true,admissionStatus:'not_admitted_by_identity_registration',sourceBinding:{localRef,component:c.pin}});
  for(const [i,x]of(c.value.completeLocalPairConstraints||[]).entries()){
    if(x.status!=='current'){history.push({...x,sourceComponent:c.pin});continue;}
    const operation=mapOperation(x.relation),members=[x.left,x.right];
    comparisons.push({id:'current:'+c.pin.path+':'+i,operation,members,...operation==='same_scoped_question'?{target:members[0]}:{},definingDifferences:operation==='same_scoped_question'?[]:[x.nativeConstraint?.reason||x.reason],sourceReviewIds:x.sourceReviewIds||c.value.reviewRegistry.map(r=>r.id),evidenceRefs:[{kind:'pinned_current_constraint',component:c.pin,index:i}],nativeConstraint:x});
  }
  for(const op of c.value.typedCanonicalOperations||[]){
    const operation=op.nativeOperation.operation,members=op.members;
    if(members.length<2)continue;
    comparisons.push({id:op.id,operation,members,target:op.target,definingDifferences:op.nativeOperation.definingDifferences,sourceReviewIds:op.sourceReviewIds,evidenceRefs:op.evidenceRefs,sourceComponent:c.pin,acceptedTypedOperationNotAutomaticUnion:true});
    if(operation==='same_scoped_question')groups.push({operationId:op.id,memberIds:members,canonicalDestinationId:op.target,canonicalScopeContentSha256:scopeContentHash(dest.get(op.target)),sourceReviewIds:op.sourceReviewIds,independentAssessment:op.independentAssessment,admissionBasis:op.admissionBasis,sourceComponent:c.pin,status:'requires_root_complete_group_admission'});
  }
}
if(groups.length!==3||base.value.screeningAccounting.length!==8282||base.value.withheldVariantConflicts.length!==6)throw Error('Unexpected group or complete-screen inventory');
for(const c of comparisons)for(const id of c.members)if(!records.has(id))throw Error('Missing exact identity record '+id);
await mkdir(out,{recursive:true});
const inventory={...base.value,inputs:[...base.value.inputs,packet.pin,...components.map(c=>c.pin),screenSuccessor.pin],records:[...records.values()],comparisons,historicalConstraints:history,connectionConflictSuccessors:screenSuccessor.value,currentVersusHistoricalPolicy:'V2 and authoritative V4 current challenge constraints plus effective admitted operations are additive. V4 replaces V3; no historical rejected DM equality or superseded bundle06 proposal enters current operations. All original identity screens remain accounted. Six connection-only disagreements have an exact successor ledger; their identity judgments are unchanged and no new equality is inferred.'};
const raw=JSON.stringify(inventory)+'\n',path=join(out,'inventory.local.json');await writeFile(path,raw);const pin={path:relative(root,path),sha256:sha256(raw),bytes:Buffer.byteLength(raw)};
const resolution={registry:pin,records:inventory.records,comparisons,canonicalGroups:[]},audit=validateCanonicalIdentity({resolution,destinations,scopeHash:scopeContentHash,reviewRecords:reviews,decision:()=>{throw Error('No group admission invented');}});
const corpus=await loadFrozenCorpus(join(root,'data/navigation')),decisions=new Map(packet.value.decisions.map(d=>[d.id,d]));
for(const g of groups){
  const members=new Set(g.memberIds);g.fullDefinitions=g.memberIds.map(id=>dest.get(id));
  g.screenHits=base.value.screeningAccounting.filter(r=>r.candidateIds.some(id=>members.has(id)));
  g.internalScreenHits=g.screenHits.filter(r=>r.candidateIds.every(id=>members.has(id)));
  g.variantConflicts=g.screenHits.filter(r=>r.variantConflictWithheld);
  g.currentConstraintConflicts=audit.unresolvedConflicts.filter(c=>c.memberIds.some(id=>members.has(id)));
  g.homeRevalidation=packet.value.placements.filter(h=>members.has(h.destinationId)).map(h=>{const u=corpus.unitMap.get(h.unitId);return {source:{unitId:u.id,paperId:u.paperId,wholeQuestion:u.text,textSha256:u.evidence.textSha256},currentHome:h,currentDecision:decisions.get(h.decisionId),canonicalDefinition:dest.get(g.canonicalDestinationId),canonicalScopeContentSha256:g.canonicalScopeContentSha256,proposedDestinationId:g.canonicalDestinationId,changesDestination:h.destinationId!==g.canonicalDestinationId,proposedWeight:h.allocationWeight,status:'requires_explicit_current_whole_scope_revalidation',sourceStatementEquivalence:false};});
  for(const h of g.homeRevalidation){const b=h.currentDecision.sourceAgreementBinding;if(b?.path){const source=await read(join(root,b.path),b.sha256),rows=Array.isArray(source.value)?source.value:source.value.bindings||source.value.placements||[];h.pairedHomeEvidence=rows.find(r=>r.decisionId===h.currentHome.decisionId);if(!h.pairedHomeEvidence)throw Error('Missing exact home attribution '+h.currentHome.decisionId);h.pairedHomeEvidencePin=source.pin;}}
}
const intake={schemaVersion:'q025-three-new-whole-group-intake/1',inputPins:[base.pin,packet.pin,screens.pin,...components.map(c=>c.pin)],completeInventory:pin,groups,automaticAliases:0,automaticMassTransfer:0,screenResolutionLedger:screenSuccessor.pin,connectionConflictsResolved:6,identityScreensChanged:0,readingLimitsPolicy:'Keep every exact original definition and readingCoverage under scopedIdentity. Whole-question equality is not source-statement equivalence; all existing placements require explicit unchanged-scope revalidation, with no implicit destination transfer.'};
await writeFile(join(out,'group-intake.json'),JSON.stringify(intake,null,2)+'\n');
const report={schemaVersion:'q025-three-new-whole-group-audit/1',status:'three_exact_internal_screen_constraints_require_root_group_admission',completeInventory:pin,identityInventorySha256:identityInventoryHash(resolution),inputPins:intake.inputPins,comparisons:comparisons.length,historicalConstraints:history.length,screenComparisons:8282,variantConflictsRetained:6,connectionConflictSuccessor:screenSuccessor.pin,connectionConflictsResolved:6,identityScreensChanged:0,groups:groups.map(g=>({operationId:g.operationId,members:g.memberIds,target:g.canonicalDestinationId,screenHits:g.screenHits.length,internalScreenHits:g.internalScreenHits.map(s=>({comparisonId:s.comparisonId,screens:s.screens,disposition:s.disposition})),variantConflicts:g.variantConflicts.length,currentConstraintConflicts:g.currentConstraintConflicts,homeRows:g.homeRevalidation.length,homeDestinationChanges:g.homeRevalidation.filter(h=>h.changesDestination).length})),groupIntake:{path:relative(root,join(out,'group-intake.json')),sha256:sha256(await readFile(join(out,'group-intake.json')))},automaticAliases:0,automaticMassTransfer:0,scriptSha256:sha256(await readFile(fileURLToPath(import.meta.url)))};
await writeFile(join(out,'report.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({status:report.status,comparisons:report.comparisons,groups:report.groups.map(g=>({members:g.members,internalScreens:g.internalScreenHits.length,conflicts:g.currentConstraintConflicts.length,homes:g.homeRows,changedHomes:g.homeDestinationChanges})),intake:report.groupIntake},null,2));
