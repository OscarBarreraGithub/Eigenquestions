import test from 'node:test';
import assert from 'node:assert/strict';
import {assembleAccepted,scopeContentHash,sourceContributionContentHash} from './accepted.mjs';
import {fixtureInput} from './fixture.mjs';
function input(){
  const x=fixtureInput(),d=x.packet.destinations.find(d=>d.id==='destination:fine'),u=x.corpus.unitMap.get('unit:q3');
  x.packet.reviewRegistry.push({id:'review:second',sha256:'b'.repeat(64)});
  x.packet.sourceContributions=['first qualification','separately admitted narrower reading limit'].map((qualification,i)=>{
    const row={unitId:u.id,destinationId:d.id,role:'addresses',basis:'description_checked',qualification,evidenceRefs:[{kind:'description',unitId:u.id,textSha256:u.evidence.textSha256}],decisionId:'decision:observation:'+i};
    x.packet.decisions.push({id:row.decisionId,type:'source_contribution',status:'accepted',subjectIds:[u.id,d.id],sourceReviewIds:['review:fixture','review:second'],evidenceRefs:row.evidenceRefs,scopeContentSha256:scopeContentHash(d),contributionContentSha256:sourceContributionContentHash(row,scopeContentHash(d)),challengerAgreement:'independently_agreed',reviewAgreement:{proposalReviewId:'review:fixture',challengeReviewId:'review:second'}});return row;
  });return x;
}
test('distinct admitted observations preserve qualifications without duplicate relationship or mass',()=>{
  const base=assembleAccepted(fixtureInput()),r=assembleAccepted(input()),d=r.catalog.destinations.find(d=>d.id==='destination:fine');
  assert.equal(d.sourceContributionObservationCount,2);assert.equal(d.sourceContributionRelationshipCount,1);
  assert.deepEqual(d.sourceContributions.map(r=>r.qualification),['first qualification','separately admitted narrower reading limit']);
  assert.equal(r.report.acceptedTypedContributions,1);assert.equal(r.report.acceptedContributionObservations,2);
  assert.deepEqual(r.geometryInput.allocations,base.geometryInput.allocations);assert.deepEqual(r.catalog.memberships,base.catalog.memberships);
});
test('repeated observation decision remains a duplicate',()=>{const x=input();x.packet.sourceContributions.push(x.packet.sourceContributions[0]);assert.throws(()=>assembleAccepted(x),/duplicate typed contribution observation/);});
