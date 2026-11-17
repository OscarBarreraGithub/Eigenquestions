/** Exact dated post-test amendment; original candidate and score remain immutable. */
import {readFile,writeFile,mkdir,copyFile} from 'node:fs/promises';
import {dirname,join,resolve,relative} from 'node:path';
import {fileURLToPath} from 'node:url';
import {sha256,loadFrozenCorpus} from '../corpus.mjs';
import {acceptedContentHash,scopeContentHash,placementContentHash} from '../accepted.mjs';
import {accountingContentHash} from '../accounting.mjs';
import {preflight} from './preflight.mjs';
const here=dirname(fileURLToPath(import.meta.url)),root=resolve(here,'../../../..');
export function validateApprovedRow(row,original,source,destination,expectedScopeHash){
 for(const key of ['rowIndex','unitId','paperId','sourceRow','browserVectorRow','sourceQuestion','sourceTextSha256','originalMass','basis','coverageMode','allocationWeight','sourceReadingLimit'])if(JSON.stringify(row[key])!==JSON.stringify(original[key]))throw Error('Root amendment changed immutable source or coverage '+key);
 if(!source||source.text!==row.sourceQuestion||sha256(source.text)!==row.sourceTextSha256||source.paperId!==row.paperId||source.sourceRow!==row.sourceRow||source.browserVectorRow!==row.browserVectorRow)throw Error('Source differs from frozen corpus');
 if(row.basis!=='description_checked'||row.newScopeRequested||row.automaticAdmission)throw Error('Unauthorized admission basis');
 if(row.disposition==='approved_existing_whole_question_home'){
  if(!destination||destination.id!==row.destinationId||scopeContentHash(destination)!==expectedScopeHash||row.allocationWeight!==1||row.coverageMode!=='whole_immutable_source_target')throw Error('Wrong approved scope or whole-source allocation');
 }else if(row.disposition!=='approved_unresolved_source_facet'||row.destinationId!==null||row.allocationWeight!==0||row.coverageMode!=='no_scientific_H_allocation')throw Error('Unresolved source received allocation');
}
export async function compile(){
 const {proposal,base,result:preflightResult}=await preflight();
 const authorityPath='research/q025/evaluation/final-holdout/root-43-source-adjudication.json',authorityBytes=await readFile(join(root,authorityPath)),authorityHash=sha256(authorityBytes),authority=JSON.parse(authorityBytes);
 if(authorityHash!=='4fbc122ec2ad1053d3af2fcb9499e23984c736e3182e1ce92540f8b33d1e79ca'||authority.status!=='approved_for_dated_final_assembly'||authority.proposal.sha256!==proposal.pin.sha256||authority.scoredReportSha256!==proposal.value.scoredReportSha256)throw Error('Exact root post-test authorization is absent');
 const authorityPin={path:authorityPath,sha256:authorityHash,bytes:authorityBytes.length},out=join(here,'packet');await mkdir(out,{recursive:true});
 const save=async(name,v)=>{const raw=JSON.stringify(v,null,2)+'\n',path=join(out,name);await writeFile(path,raw);return {path:relative(root,path),sha256:sha256(raw),bytes:Buffer.byteLength(raw)};};
 const p=base.value,baseDir=dirname(join(root,base.pin.path)),rebase=path=>relative(out,resolve(baseDir,path));
 for(const r of p.reviewRegistry)r.path=rebase(r.path);
 for(const d of p.decisions)if(d.adjudication?.receipt?.path)d.adjudication.receipt.path=rebase(d.adjudication.receipt.path);
 p.originalCandidate.regionsPath=rebase(p.originalCandidate.regionsPath);
 for(const k of ['sourceContextRoot','sourceArchiveRoot'])p.assets[k]=rebase(p.assets[k]);
 for(const r of p.assets.deliveryAssets||[])r.sourcePath=rebase(r.sourcePath);
 for(const r of p.organizationalAccess.certificateFiles)r.sourcePath=rebase(r.sourcePath);
 // The registry descriptor is part of the admitted complete-group hash. Keep
 // its exact relative descriptor and copy the identical inventory bytes.
 await copyFile(resolve(baseDir,p.identityResolution.registry.path),join(out,p.identityResolution.registry.path));
 const corpus=await loadFrozenCorpus(join(root,'data/navigation')),dest=new Map(p.destinations.map(d=>[d.id,d])),byOriginal=new Map(proposal.value.rows.map(r=>[r.unitId,r])),reserved=new Set(p.coverage.reservedUnitIds),seen=new Set(),placements=[],bindings=[],unresolved=[];
 const sourceReviewId='post-test:43-source-descriptions',rootReviewId='root:43-source-adjudication';
 p.reviewRegistry.push({id:sourceReviewId,...proposal.pin,path:relative(out,join(root,proposal.pin.path)),kind:'complete_immutable_source_description_and_target_review'},{id:rootReviewId,...authorityPin,path:relative(out,join(root,authorityPin.path)),kind:'explicit_coordinator_post_test_adjudication'});
 const alternative=authority.additionalExistingTarget;
 if(scopeContentHash(dest.get(alternative.definition.id))!==alternative.scopeContentSha256||Object.entries(alternative.definition).filter(([k])=>k!=='scopeContentSha256').some(([k,v])=>JSON.stringify(dest.get(alternative.definition.id)[k])!==JSON.stringify(v)))throw Error('Approved H17 alternative changed');
 const described=await readFile(join(root,alternative.frozenDescribeReceipt.path));if(sha256(described)!==alternative.frozenDescribeReceipt.sha256)throw Error('H17 describe receipt changed');
 for(const row of authority.rows){
  if(!reserved.has(row.unitId)||seen.has(row.unitId))throw Error('Not the exact once-only reserved source set');seen.add(row.unitId);
  const original=byOriginal.get(row.unitId),d=dest.get(row.destinationId),scopeHash=row.destinationId===alternative.definition.id?alternative.scopeContentSha256:proposal.value.targets[row.destinationId]?.scopeContentSha256;
  validateApprovedRow(row,original,corpus.unitMap.get(row.unitId),d,scopeHash);
  const sourceBinding={unitId:row.unitId,paperId:row.paperId,sourceRow:row.sourceRow,browserVectorRow:row.browserVectorRow,textSha256:row.sourceTextSha256,rowIndex:row.rowIndex,proposal:proposal.pin,adjudication:authorityPin};
  if(row.disposition==='approved_unresolved_source_facet'){
   unresolved.push({unitId:row.unitId,descriptionSha256:row.sourceTextSha256,reason:row.reason,sourceHomeNotice:authority.newUnresolvedNotice,sourceReviewIds:[sourceReviewId,rootReviewId],provenance:{datedPostTestAmendment:true,sourceBinding,sourceReadingLimit:row.sourceReadingLimit,fineIdentityStatus:row.fineIdentityStatus}});continue;
  }
  const placement={unitId:row.unitId,destinationId:row.destinationId,role:'member',status:'accepted',basis:'description_checked',allocationWeight:1,reason:row.reason,qualification:row.sourceReadingLimit,evidenceRefs:[{kind:'description',unitId:row.unitId,paperId:row.paperId,textSha256:row.sourceTextSha256}],decisionId:'decision:dated43-home:'+row.rowIndex,provenance:{sourceBinding,coverageMode:row.coverageMode,fineIdentityStatus:row.fineIdentityStatus,coordinatorDecision:row.coordinatorDecision,originalProposedDestinationId:row.originalProposedDestinationId||row.destinationId,notAnIndependentRetest:true}};
  placements.push(placement);bindings.push({unitId:row.unitId,destinationId:row.destinationId,scopeContentSha256:scopeHash,placementContentSha256:placementContentHash(placement,scopeHash),sourceBinding});
 }
 if(seen.size!==43||placements.length!==37||unresolved.length!==6||authority.newUnresolvedNotice!=='A precise topic placement has not been established for this source.')throw Error('Approved exact 37/6 class changed');
 const homeReceipt=await save('placement-admission.json',{schemaVersion:'q025-dated-post-test-placement-admission/1',status:'accepted_explicit_placement',authority:authorityPin,proposal:proposal.pin,candidateFreeze:preflightResult.candidateFreeze,scoreFreeze:preflightResult.scoreFreeze,homeBindings:bindings,unresolved,originalsPreserved:true,readingLimit:authority.rootReading,noNewScopesRolesRoutesAliases:true,notAnIndependentRetest:true});
 const homeReceiptRef={path:'placement-admission.json',sha256:homeReceipt.sha256};
 p.reviewRegistry.push({id:'derived:43-home-binding',...homeReceiptRef});
 for(const placement of placements){const b=bindings.find(b=>b.unitId===placement.unitId);p.placements.push(placement);p.decisions.push({id:placement.decisionId,type:'placement',status:'accepted',subjectIds:[placement.unitId,placement.destinationId],scopeContentSha256:b.scopeContentSha256,placementContentSha256:b.placementContentSha256,challengerAgreement:'not_reviewed_as_allocation',sourceEvidenceAgreement:'coordinator_adjudicated_complete_source_and_target',sourceReviewIds:[sourceReviewId,rootReviewId,'derived:43-home-binding'],evidenceRefs:placement.evidenceRefs,adjudication:{status:'accepted_explicit_placement',receipt:homeReceiptRef}});}
 const oldCoverage=p.coverage;
 p.coverage={kind:'accounted_question_corpus',reason:'complete_release',resolvedUnitIds:[...oldCoverage.resolvedUnitIds,...placements.map(r=>r.unitId)].sort(),unresolved:[...oldCoverage.unresolved,...unresolved],reservedUnitIds:[],decisionId:'decision:source-accounting-post-test-complete'};
 if(p.coverage.resolvedUnitIds.length!==8436||p.coverage.unresolved.length!==37||new Set([...p.coverage.resolvedUnitIds,...p.coverage.unresolved.map(r=>r.unitId)]).size!==8473)throw Error('Final accounting is not conserved');
 const accounting=await save('source-accounting-admission.json',{schemaVersion:'q025-source-accounting-admission/1',status:'accepted_explicit_source_accounting',authority:authorityPin,previousPacket:base.pin,placementAdmission:homeReceipt,contentSha256:accountingContentHash(p.coverage),resolved:8436,unresolved:37,reserved:0,total:8473,globalMassConvention:'All global question-per-paper masses remain unchanged. Unresolved rows have zero H and retained source mass; no renormalization.',notAnIndependentRetest:true});
 p.reviewRegistry.push({id:'root:post-test-source-accounting',path:'source-accounting-admission.json',sha256:accounting.sha256});p.decisions.push({id:p.coverage.decisionId,type:'source_accounting',status:'accepted',subjectIds:[...p.coverage.resolvedUnitIds,...p.coverage.unresolved.map(r=>r.unitId)],contentSha256:accountingContentHash(p.coverage),sourceReviewIds:[rootReviewId,'root:post-test-source-accounting'],evidenceRefs:[{kind:'coordinator_source_accounting',path:'source-accounting-admission.json',sha256:accounting.sha256}],adjudication:{status:'accepted_explicit_source_accounting',receipt:{path:'source-accounting-admission.json',sha256:accounting.sha256}}});
 p.geometry.baseDestinationIds=[...new Set(p.placements.filter(r=>r.status==='accepted'&&r.role!=='context').map(r=>r.destinationId))].sort();
 p.atlas.atlasVersion='2026-11-17-post-test-accounted-v1';p.atlas.scope.partialRehearsal=false;p.atlas.scope.description='As of 17 November 2026, this Swampland-centered atlas includes all 8,473 source questions: 8,436 have reviewed topic placements and 37 remain source facets without a precise placement.';
 p.provenance={...p.provenance,datedPostTestAmendment:{authority:authorityPin,proposal:proposal.pin,previousPacket:base.pin,candidateFreeze:preflightResult.candidateFreeze,scoreFreeze:preflightResult.scoreFreeze,sourceBindings:bindings,unchangedScientificScopeRouteRoleIdentity:true,notAnIndependentRetest:true}};
 const receipt=await save('aggregate-admission.json',{schemaVersion:'q025-assembly-binding-receipt/1',status:'accepted_for_assembly',acceptedContentSha256:acceptedContentHash(p),input:base.pin,authority:authorityPin,placementAdmission:homeReceipt,sourceAccounting:accounting,sourceInventoryAccounted:true,fullReleaseAccounting:true,publicationStillRequiresIntegrationAcceptance:true});p.acceptance={status:'accepted_for_assembly',receipt:{path:'aggregate-admission.json',sha256:receipt.sha256}};
 const packet=await save('aggregate.local.json',p),report={packet,receipt,authority:authorityPin,placementAdmission:homeReceipt,sourceAccounting:accounting,counts:{resolved:8436,unresolved:37,reserved:0,sourceFacets:8473,newPlacements:37,newUnresolved:6,newScientificScopes:0,newScientificRoutes:0,newRoles:0,newAliases:0},existingScopesRoutesRolesUnchanged:true,originalUnresolvedRowsUnchanged:JSON.stringify(p.coverage.unresolved.slice(0,31))===JSON.stringify(oldCoverage.unresolved),scriptSha256:sha256(await readFile(fileURLToPath(import.meta.url)))};await save('binding.json',report);console.log(JSON.stringify(report,null,2));return report;
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url))await compile();
