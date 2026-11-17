import test from 'node:test';
import assert from 'node:assert/strict';
import {assembleAccepted,compileSourceContributions,scopeContentHash,sourceContributionContentHash} from './accepted.mjs';
import {fixtureInput} from './fixture.mjs';

function explicitContribution(){
  const x=fixtureInput(),d=x.packet.destinations.find(d=>d.id==='destination:fine'),u=x.corpus.unitMap.get('unit:q3');
  const row={unitId:u.id,destinationId:d.id,role:'instantiates',basis:'description_checked',evidenceRefs:[{kind:'description',unitId:u.id,textSha256:u.evidence.textSha256}],qualification:'Synthetic source-specific test only.',decisionId:'decision:explicit-contribution'};
  const proof={id:row.decisionId,type:'source_contribution',status:'accepted',subjectIds:[u.id,d.id],sourceReviewIds:['review:fixture'],evidenceRefs:structuredClone(row.evidenceRefs),scopeContentSha256:scopeContentHash(d),contributionContentSha256:sourceContributionContentHash(row,scopeContentHash(d)),challengerAgreement:'coordinator_adjudicated_source_contribution',adjudication:{status:'accepted_explicit_source_contribution',receipt:{path:'synthetic-root-receipt.json',sha256:'a'.repeat(64)}}};
  x.packet.sourceContributions=[row];x.packet.decisions.push(proof);x.verifiedReceiptHashes=new Set(['a'.repeat(64),'e'.repeat(64)]);return x;
}
test('explicit source contribution preserves its real admission mode without adding allocation or USING',()=>{
  const before=assembleAccepted(fixtureInput()),after=assembleAccepted(explicitContribution());
  assert.deepEqual(after.geometryInput.allocations,before.geometryInput.allocations);
  assert.deepEqual(after.catalog.memberships,before.catalog.memberships);
  const row=after.catalog.sourceContributions[0];assert.equal(row.provenance.challengerAgreement,'coordinator_adjudicated_source_contribution');assert.equal(row.provenance.reviewAgreement,undefined);
  assert.equal(row.provenance.doesNotAssertDirectHome,true);assert.equal(row.provenance.doesNotAssertEquivalence,true);assert.equal(row.provenance.doesNotAssertMethodApplicability,true);
});
test('production component gate does not depend on fixture bypass',()=>{
  const x=explicitContribution(),proof=x.packet.decisions.at(-1);
  const rows=compileSourceContributions({rows:x.packet.sourceContributions,destinations:x.packet.destinations,units:x.corpus.unitMap,decision:()=>proof,reviewRecords:new Map(x.packet.reviewRegistry.map(r=>[r.id,r])),verifiedReceiptHashes:x.verifiedReceiptHashes});
  assert.equal(rows.length,1);assert.equal(rows[0].qualification,'Synthetic source-specific test only.');
});
for(const [name,mutate,error] of [
  ['wrong scope',x=>{x.packet.decisions.at(-1).scopeContentSha256='f'.repeat(64);},/different scope/],
  ['changed exact contribution',x=>{x.packet.sourceContributions[0].role='addresses';},/changed after admission/],
  ['changed qualification',x=>{x.packet.sourceContributions[0].qualification='Different premise';},/changed after admission/],
  ['wrong receipt hash',x=>{x.packet.decisions.at(-1).adjudication.receipt.sha256='b'.repeat(64);},/receipt is not verified/],
  ['missing receipt verification',x=>{x.verifiedReceiptHashes.delete('a'.repeat(64));},/receipt is not verified/],
  ['wrong receipt purpose',x=>{x.packet.decisions.at(-1).adjudication.status='accepted_explicit_placement';},/receipt is not verified/],
  ['unverified native review',x=>{x.verifiedReceiptHashes.delete('e'.repeat(64));},/verified source review evidence/],
  ['coordinator receipt recycled as source review',x=>{x.packet.reviewRegistry[0].sha256='a'.repeat(64);},/verified source review evidence/],
  ['unbound decision evidence',x=>{x.packet.decisions.at(-1).evidenceRefs=[{kind:'description',unitId:'unit:q1'}];},/bind its source evidence/],
  ['fictional independent agreement',x=>{x.packet.decisions.at(-1).reviewAgreement={proposalReviewId:'review:fixture',challengeReviewId:'review:fixture'};},/fictional dual review/],
  ['excerpt claim without exact primary locator',x=>{x.packet.sourceContributions[0].basis='source_excerpt_checked';},/exact source\/basis/],
])test(`explicit contribution rejects ${name}`,()=>{const x=explicitContribution();mutate(x);assert.throws(()=>assembleAccepted(x),error);});
