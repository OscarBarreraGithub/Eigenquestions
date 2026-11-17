import test from 'node:test';
import assert from 'node:assert/strict';
import {assembleAccepted,scopeContentHash,sourceContributionContentHash} from './accepted.mjs';
import {fixtureInput} from './fixture.mjs';
import {partitionCatalog,validatePartition} from './lazy-package.mjs';
import {primaryLocatorFingerprint} from './primary-evidence.mjs';

function withContribution(role='comparison'){
  const x=fixtureInput(),destination=x.packet.destinations.find(d=>d.id==='destination:fine');
  destination.scope={systems:['Synthetic source scope'],...destination.scope};const scopeHash=scopeContentHash(destination);x.packet.decisions.find(d=>d.id===destination.scopeDecisionId).scopeContentSha256=scopeHash;
  x.packet.reviewRegistry.push({id:'review:independent-challenge',sha256:'b'.repeat(64)});
  const source=x.corpus.unitMap.get('unit:q3'),row={unitId:source.id,destinationId:destination.id,role,basis:'description_checked',evidenceRefs:[{kind:'description',unitId:source.id,textSha256:source.evidence.textSha256}],decisionId:'decision:contribution'};
  x.packet.sourceContributions=[row];x.packet.decisions.push({id:row.decisionId,type:'source_contribution',status:'accepted',subjectIds:[row.unitId,row.destinationId],sourceReviewIds:['review:fixture','review:independent-challenge'],evidenceRefs:row.evidenceRefs,scopeContentSha256:scopeHash,contributionContentSha256:sourceContributionContentHash(row,scopeHash),challengerAgreement:'independently_agreed',reviewAgreement:{proposalReviewId:'review:fixture',challengeReviewId:'review:independent-challenge'}});
  return x;
}
test('typed comparison is preserved without a new home, geometric mass or USING membership',()=>{
  const base=assembleAccepted(fixtureInput()),result=assembleAccepted(withContribution());
  assert.deepEqual(result.geometryInput.allocations,base.geometryInput.allocations);assert.deepEqual(result.catalog.memberships,base.catalog.memberships);
  const d=result.catalog.destinations.find(d=>d.id==='destination:fine');assert.equal(d.sourceContributions[0].role,'comparison');assert.equal(d.sourceContributions[0].browserVectorRow,2);assert.ok(!d.memberIds.includes('unit:q3'));
  assert.equal(d.sourceContributions[0].scopeContentSha256,scopeContentHash(d));
});
test('method contribution alone does not grant method applicability or USING',()=>{
  const x=withContribution('method'),result=assembleAccepted(x);assert.ok(!result.catalog.memberships.some(r=>r.role==='using'));assert.equal(result.catalog.sourceContributions[0].provenance.doesNotAssertMethodApplicability,true);
});
test('resolved primary locators and explicitly bound qualifications remain intact',()=>{
  const x=withContribution(),row=x.packet.sourceContributions[0],proof=x.packet.decisions.at(-1);row.basis='source_excerpt_checked';row.qualification='Synthetic source-specific qualification.';const ref={kind:'primary',paperId:'p2',sourceId:'ev:abcdef',sourceSha256:'a'.repeat(64),sourceContext:{path:'synthetic-reading-order.json',fileSha256:'b'.repeat(64),pdfPage:2,start:0,end:10,textSha256:'d'.repeat(64)}};row.evidenceRefs.push(ref);x.verifiedPrimaryLocators=new Set([primaryLocatorFingerprint(ref)]);proof.contributionContentSha256=sourceContributionContentHash(row,proof.scopeContentSha256);assert.equal(assembleAccepted(x).catalog.sourceContributions[0].qualification,row.qualification);row.qualification='Changed';assert.throws(()=>assembleAccepted(x),/changed after admission/);
});
test('typed contributions survive lazy detail while remaining absent from initial source payload',()=>{
  const {catalog}=assembleAccepted(withContribution()),p=partitionCatalog(catalog,{entryDestinationId:'destination:root'});assert.equal(p.catalog.sourceContributions,undefined);assert.equal(p.catalog.sourceContributionInventory.count,1);assert.equal(validatePartition(catalog,p).passed,true);const index=p.catalog.destinations.find(d=>d.id==='destination:fine'),descriptor=p.catalog.detailShards[index.detail.shardId],detail=JSON.parse(p.files.find(f=>f.descriptor.path===descriptor.path).text).destinations[index.id];assert.equal(detail.destination.sourceContributions[0].unitId,'unit:q3');
});
for(const [name,mutate,error] of [
  ['rewritten role',x=>{x.packet.sourceContributions[0].role='addresses';},/changed after admission/],
  ['single review recycled as two',x=>{x.packet.decisions.at(-1).reviewAgreement.challengeReviewId='review:fixture';},/distinct pinned/],
  ['same artifact under two names',x=>{x.packet.reviewRegistry[1].sha256=x.packet.reviewRegistry[0].sha256;},/one review artifact/],
  ['wrong scope binding',x=>{x.packet.decisions.at(-1).scopeContentSha256='c'.repeat(64);},/different scope/],
  ['claimed excerpt without primary source',x=>{x.packet.sourceContributions[0].basis='source_excerpt_checked';},/exact source\/basis/],
  ['wrong source evidence',x=>{x.packet.sourceContributions[0].evidenceRefs[0].unitId='unit:q2';},/exact source\/basis/],
  ['unadmitted USING field',x=>{x.packet.sourceContributions[0].workRelation='using';},/unbound typed contribution field/],
])test(`rejects contribution ${name}`,()=>{const x=withContribution();mutate(x);assert.throws(()=>assembleAccepted(x),error);});
