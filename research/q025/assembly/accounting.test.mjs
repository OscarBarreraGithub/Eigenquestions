import test from 'node:test';
import assert from 'node:assert/strict';
import {fixtureInput} from './fixture.mjs';
import {assembleAccepted,scopeContentHash,placementContentHash} from './accepted.mjs';
import {accountingContentHash} from './accounting.mjs';
import {attachFineSourceAccess,sourceQuestionId} from './fine-identities.mjs';
import {writeLazyPackage} from './lazy-package.mjs';

// Synthetic semantic-gate fixtures; these are not scientific admissions.
const receipt={path:'fixture-accounting.json',sha256:'c'.repeat(64)};
function bind(x,value,type,status){
  const id=value.decisionId;x.packet.decisions=x.packet.decisions.filter(d=>d.id!==id);x.packet.decisions.push({id,type,status:'accepted',sourceReviewIds:['review:fixture'],evidenceRefs:[{kind:'description',unitId:'unit:q3'}],contentSha256:accountingContentHash(value),adjudication:{status,receipt}});
}
function accounted(){
  const x=fixtureInput();x.verifiedReceiptHashes=new Set([receipt.sha256]);
  x.packet.placements=x.packet.placements.filter(p=>p.unitId!=='unit:q3');
  x.packet.coverage={kind:'accounted_question_corpus',reason:'complete_release',resolvedUnitIds:['unit:q1','unit:q2'],unresolved:[{unitId:'unit:q3',descriptionSha256:x.corpus.unitMap.get('unit:q3').evidence.textSha256,reason:'The supplied setting has no agreed whole-question scientific home.',sourceReviewIds:['review:fixture']}],reservedUnitIds:[],decisionId:'accounting'};
  bind(x,x.packet.coverage,'source_accounting','accepted_explicit_source_accounting');
  x.packet.publicEntryFrontier={kind:'curated_collection_frontier',landmark:{id:'collection:test',kind:'landmark',metadataOnly:true,title:'Test collection'},entries:['a','b'].map(id=>{const d=x.packet.destinations.find(d=>d.id===`destination:${id}`);return {destinationId:d.id,scopeContentSha256:scopeContentHash(d),type:'related_question',rationale:'Open this reviewed family; no scientific containment is asserted.'};}),decisionId:'frontier'};
  bind(x,x.packet.publicEntryFrontier,'collection_frontier','accepted_explicit_collection_frontier');x.packet.atlas.entryDestinationId='collection:test';
  x.packet.relations=x.packet.relations.filter(r=>r.source!=='destination:root');return x;
}
test('accounted unresolved source is readable with zero semantic mass and no invented family',()=>{
  const x=accounted(),r=assembleAccepted(x);assert.equal(r.report.sourceAccountingComplete,true);assert.equal(r.report.scientificCoverageComplete,false);assert.equal(r.report.unresolvedQuestionCount,1);
  assert.ok(!r.geometryInput.allocations.some(a=>a.unitId==='unit:q3'));assert.equal(r.geometryInput.units.reduce((n,u)=>n+u.paperBalancedMass,0),1);
  assert.equal(r.geometryInput.sourceMassInventory.length,3);assert.equal(r.geometryInput.coverage.sourceMass.renormalized,false);assert.ok(r.geometryInput.coverage.sourceMass.unresolved>0);assert.equal(r.geometryInput.coverage.sourceMass.global,r.geometryInput.coverage.sourceMass.allocated+r.geometryInput.coverage.sourceMass.unassigned);
  attachFineSourceAccess(r.catalog,{corpus:x.corpus,policyDecisionId:'source-access'});
  const d=r.catalog.destinations.find(d=>d.id===sourceQuestionId('unit:q3'));assert.equal(d.sourceHomeStatus,'unresolved');assert.match(d.sourceHomeReason,/no agreed/);assert.equal(r.catalog.sources.length,5);
  assert.equal(r.catalog.destinations.find(d=>d.id==='collection:test').memberIds.length,0);assert.ok(!r.geometryInput.baseDestinationIds.includes('collection:test'));
  assert.ok(r.catalog.relations.filter(r=>r.source==='collection:test').every(r=>r.type==='related_question'&&r.provenance.navigationBasis==='curated_collection_entry'));
});
test('accounting rejects disappeared, double-accounted and secretly allocated sources',()=>{
  for(const mutation of [x=>x.packet.coverage.unresolved=[],x=>x.packet.coverage.resolvedUnitIds.push('unit:q3')]){const x=accounted();mutation(x);bind(x,x.packet.coverage,'source_accounting','accepted_explicit_source_accounting');assert.throws(()=>assembleAccepted(x),/disappears|duplicate/);}
  const x=accounted();x.packet.placements.push(fixtureInput().packet.placements.find(p=>p.unitId==='unit:q3'));assert.throws(()=>assembleAccepted(x),/unresolved\/reserved source/);
});
test('approved frontier must bind exact scope and cannot conceal a disconnected allocated home',()=>{
  const x=accounted();x.packet.publicEntryFrontier.entries[0].scopeContentSha256='f'.repeat(64);bind(x,x.packet.publicEntryFrontier,'collection_frontier','accepted_explicit_collection_frontier');assert.throws(()=>assembleAccepted(x),/collection entry changed/);
  const y=accounted();y.packet.publicEntryFrontier.entries=y.packet.publicEntryFrontier.entries.filter(e=>e.destinationId!=='destination:b');bind(y,y.packet.publicEntryFrontier,'collection_frontier','accepted_explicit_collection_frontier');assert.throws(()=>assembleAccepted(y),/unreachable from the approved/);
});
test('reserved accounting blocks release and retained partial transport blocks installation',async()=>{
  const x=accounted();x.packet.coverage.reservedUnitIds=['unit:q3'];x.packet.coverage.unresolved=[];bind(x,x.packet.coverage,'source_accounting','accepted_explicit_source_accounting');assert.throws(()=>assembleAccepted(x),/reserved sources block/);
  x.packet.coverage.reason='pre_holdout_freeze';bind(x,x.packet.coverage,'source_accounting','accepted_explicit_source_accounting');const r=assembleAccepted(x);assert.equal(r.report.sourceAccountingComplete,false);assert.equal(r.report.reservedQuestionCount,1);
  await assert.rejects(writeLazyPackage({manifest:{scope:{accountingReason:'pre_holdout_freeze',reservedQuestionCount:1}},publicationStatus:'accepted_for_installation'}),/cannot be installed/);
});
function compound(){
  const x=accounted();x.packet.allocationPolicy='explicit_normalized_weights';
  const targetCoverage=[{sourceSpan:'Synthetic',destinationIds:['destination:a'],explanation:'First target is organizationally allocated to A.'},{sourceSpan:'fixture q2',destinationIds:['destination:b'],explanation:'Second target is organizationally allocated to B.'}];
  for(const p of x.packet.placements){p.allocationWeight=p.unitId==='unit:q2'?.5:1;if(p.unitId!=='unit:q2')continue;p.status='accepted';p.coverageMode='explicit_compound_union';p.targetCoverage=targetCoverage;p.coverageReason='The two partial targets jointly cover the immutable source; neither home alone is complete.';const proof=x.packet.decisions.find(d=>d.id===p.decisionId);proof.challengerAgreement='coordinator_adjudicated_placement';proof.adjudication={status:'accepted_explicit_placement',receipt};proof.scopeContentSha256=scopeContentHash(x.packet.destinations.find(d=>d.id===p.destinationId));proof.placementContentSha256=placementContentHash(p,proof.scopeContentSha256);}
  return x;
}
test('compound union conserves one source while preserving partial target maps and nonprobability meaning',()=>{
  const r=assembleAccepted(compound()),rows=r.geometryInput.allocations.filter(a=>a.unitId==='unit:q2');assert.equal(rows.reduce((n,a)=>n+a.weight,0),1);assert.equal(rows.length,2);assert.ok(rows.every(a=>a.coverageMode==='explicit_compound_union'&&a.wholeQuestionCoveredByEachHome===false&&a.targetCoverage.length===2));assert.ok(r.catalog.memberships.filter(m=>m.unitId==='unit:q2').every(m=>m.wholeQuestionCoveredByEachHome===false));
});
test('compound map is part of the admitted hash and cannot invent a source span',()=>{
  const x=compound();x.packet.placements.find(p=>p.unitId==='unit:q2').targetCoverage[0].sourceSpan='Invented text';assert.throws(()=>assembleAccepted(x),/compound union lacks explicit|unagreed accepted/);
  const y=compound();for(const p of y.packet.placements.filter(p=>p.unitId==='unit:q2')){p.targetCoverage[0].sourceSpan='Invented text';const proof=y.packet.decisions.find(d=>d.id===p.decisionId);proof.placementContentSha256=placementContentHash(p,proof.scopeContentSha256);}assert.throws(()=>assembleAccepted(y),/invented source span/);
});
