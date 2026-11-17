import test from 'node:test';
import assert from 'node:assert/strict';
import {assembleAccepted,rehearsalCohortHash,placementContentHash,scopeContentHash} from './accepted.mjs';
import {fixtureInput} from './fixture.mjs';
import {writeLazyPackage} from './lazy-package.mjs';
function cohort(){
  const x=fixtureInput(),unitIds=['unit:q1','unit:q2'];x.packet.coverage={kind:'admitted_rehearsal_cohort',unitIds,decisionId:'decision:cohort'};
  x.packet.decisions.push({id:'decision:cohort',type:'rehearsal_cohort',status:'accepted',subjectIds:unitIds,sourceReviewIds:['review:fixture'],evidenceRefs:[{kind:'description',id:'unit:q1'}],outcome:'approve_explicit_partial_corpus_rehearsal',unitIdsSha256:rehearsalCohortHash(unitIds)});
  x.packet.placements=x.packet.placements.filter(p=>p.unitId!=='unit:q3');return x;
}
test('explicit cohort conserves selected mass and reports unallocated corpus without deleting source inventory',()=>{
  const x=cohort(),r=assembleAccepted(x);assert.equal(r.report.partialRehearsal,true);assert.equal(r.report.scientificCoverageComplete,false);assert.equal(r.report.allocatedQuestionCount,2);assert.equal(r.report.unallocatedQuestionCount,1);assert.equal(r.report.questionAllocationMaxError,0);assert.equal(r.catalog.sources.length,5);assert.equal(r.geometryInput.units.length,2);
});
test('complete default coverage still rejects the same missing source without a cohort decision',()=>{
  const x=cohort();delete x.packet.coverage;assert.throws(()=>assembleAccepted(x),/uncovered question/);
});
test('cohort membership mutation and placements outside it are rejected',()=>{
  const x=cohort();x.packet.coverage.unitIds.push('unit:q3');assert.throws(()=>assembleAccepted(x),/exact cohort admission/);
  const y=cohort();y.packet.placements.push(fixtureInput().packet.placements.at(-1));assert.throws(()=>assembleAccepted(y),/escapes the explicitly admitted cohort/);
});
test('coordinator placement admission is distinct from independent source-role evidence and binds scope/row',()=>{
  const x=fixtureInput(),p=x.packet.placements[0],d=x.packet.destinations.find(d=>d.id===p.destinationId),proof=x.packet.decisions.find(d=>d.id===p.decisionId),receipt='c'.repeat(64);
  proof.challengerAgreement='not_reviewed_as_placement';proof.sourceEvidenceAgreement='independently_agreed';proof.scopeContentSha256=scopeContentHash(d);proof.placementContentSha256=placementContentHash(p,proof.scopeContentSha256);proof.adjudication={status:'accepted_explicit_placement',receipt:{path:'synthetic-placement.json',sha256:receipt}};
  assert.throws(()=>assembleAccepted(x),/unagreed accepted placement/);x.verifiedReceiptHashes=new Set([receipt]);assert.equal(assembleAccepted(x).report.questionAllocationMaxError,0);p.basis='changed';assert.throws(()=>assembleAccepted(x),/unagreed accepted placement/);
});
test('broad admitted questions can be declared geometry bases without promoting their contributions',()=>{
  const x=fixtureInput();x.packet.geometry.baseDestinationIds=['destination:fine','destination:a','destination:b'];const r=assembleAccepted(x);assert.deepEqual(r.geometryInput.baseDestinationIds,x.packet.geometry.baseDestinationIds);assert.equal(r.report.typedContributionsAffectAllocation,false);
});
test('a partial cohort cannot be labeled accepted for complete-atlas installation',async()=>{
  await assert.rejects(writeLazyPackage({manifest:{scope:{partialRehearsal:true}},publicationStatus:'accepted_for_installation'}),/cannot be installed as the complete accepted atlas/);
});

test('cohort masses expose both renormalized and inherited global paper mass',()=>{
  const x=cohort();x.packet.coverage.unitIds=['unit:q1'];const proof=x.packet.decisions.find(d=>d.id==='decision:cohort');proof.unitIdsSha256=rehearsalCohortHash(['unit:q1']);x.packet.placements=x.packet.placements.filter(p=>p.unitId==='unit:q1');const r=assembleAccepted(x),u=r.geometryInput.units[0];assert.equal(u.paperBalancedMass,1);assert.equal(u.inheritedGlobalPaperMass,.5);assert.equal(u.globalPaperQuestionCount,2);assert.equal(u.selectedPaperQuestionCount,1);assert.match(r.geometryInput.coverage.paperMassPolicy,/cohort_renormalized/);
  const full=assembleAccepted(fixtureInput());assert.match(full.geometryInput.coverage.paperMassPolicy,/global_one_mass/);assert.equal(full.geometryInput.units[0].paperBalancedMass,.5);
});
test('independent scientific rehearsal entries require an exact explicit admission, not an invented link',()=>{
  const x=cohort();x.packet.relations=[];x.packet.atlas.entryDestinationId='destination:fine';assert.throws(()=>assembleAccepted(x),/unreachable/);x.packet.coverage.independentEntryDestinationIds=['destination:a','destination:b'];assert.throws(()=>assembleAccepted(x),/independent rehearsal entry/);const proof=x.packet.decisions.find(d=>d.id==='decision:cohort');proof.independentEntryDestinationIds=[...x.packet.coverage.independentEntryDestinationIds];proof.subjectIds=[...proof.subjectIds,...proof.independentEntryDestinationIds];const r=assembleAccepted(x);assert.equal(r.catalog.relations.length,0);assert.equal(r.report.questionAllocationMaxError,0);
});

test('source-specific placement qualification survives membership transport without changing its weight',()=>{
  const x=fixtureInput(),p=x.packet.placements[0];p.basis='description_checked';p.qualification='Source target only; inherited context is not an additional home.';const r=assembleAccepted(x),row=r.catalog.memberships.find(m=>m.unitId===p.unitId&&m.destinationId===p.destinationId);assert.equal(row.placementQualification,p.qualification);assert.equal(row.placementBasis,p.basis);assert.equal(row.weight,1);
});

test('pre-holdout candidates use the same exact cohort gate with a distinct nonrelease reason',()=>{
  const x=cohort();x.packet.coverage.reason='pre_holdout_freeze';const r=assembleAccepted(x);assert.equal(r.report.partialCandidateReason,'pre_holdout_freeze');assert.equal(r.report.scientificCoverageComplete,false);assert.equal(r.report.unallocatedQuestionCount,1);x.packet.coverage.reason='complete';assert.throws(()=>assembleAccepted(x),/unknown partial candidate reason/);
});
