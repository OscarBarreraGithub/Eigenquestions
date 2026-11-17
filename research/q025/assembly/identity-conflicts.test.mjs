import test from 'node:test';
import assert from 'node:assert/strict';
import {assembleAccepted,scopeContentHash} from './accepted.mjs';
import {identityInventoryHash,canonicalIdentityGroupHash} from './fine-identities.mjs';
import {fixtureInput} from './fixture.mjs';

function fixtureIdentity(){
  const x=fixtureInput();x.packet.reviewRegistry.push({id:'review:challenge',sha256:'b'.repeat(64)});
  x.packet.identityResolution={registry:{path:'synthetic-registry.json',sha256:'c'.repeat(64)},records:['A','B','C'].map(id=>({id,contentSha256:id.toLowerCase().repeat(64)})),comparisons:[],canonicalGroups:[]};
  return x;
}
function compare(x,id,operation,members,differences=[]){x.packet.identityResolution.comparisons.push({id,operation,members,target:members.at(-1),definingDifferences:differences,sourceReviewIds:['review:fixture','review:challenge'],evidenceRefs:[{kind:'description',id:'unit:q1'}]});}
function group(x,memberIds=['A','B','C']){
  const r=x.packet.identityResolution,d=x.packet.destinations.find(d=>d.id==='destination:fine'),g={id:'identity:ABC',destinationId:d.id,memberIds,decisionId:'decision:identity'},scopeHash=scopeContentHash(d),inventoryHash=identityInventoryHash(r);
  r.canonicalGroups.push(g);x.packet.decisions.push({id:g.decisionId,type:'question_equivalence',status:'accepted',outcome:'equivalent_as_scoped',subjectIds:[d.id,...memberIds],sourceReviewIds:['review:fixture','review:challenge'],evidenceRefs:[{kind:'description',id:'unit:q1'}],challengerAgreement:'independently_agreed',changedPremises:[],canonicalDestinationId:d.id,scopeContentSha256:scopeHash,identityInventorySha256:inventoryHash,identityGroupContentSha256:canonicalIdentityGroupHash(g,scopeHash,inventoryHash),reviewAgreement:{proposalReviewId:'review:fixture',challengeReviewId:'review:challenge'}});
  return g;
}
test('A=B and B=C never automatically create a canonical union or alias',()=>{
  const x=fixtureIdentity();compare(x,'ab','same_scoped_question',['A','B']);compare(x,'bc','same_scoped_question',['B','C']);const r=assembleAccepted(x).catalog.organizationProvenance.identityResolution;assert.equal(r.groups.length,0);assert.equal(r.automaticUnions,0);
});
test('transitive A=B, B=C, A differs C remains an explicit unresolved conflict queue',()=>{
  const x=fixtureIdentity();compare(x,'ab','same_scoped_question',['A','B']);compare(x,'bc','same_scoped_question',['B','C']);compare(x,'ac','different',['A','C'],['Changed physical regime']);const r=assembleAccepted(x).catalog.organizationProvenance.identityResolution;assert.equal(r.unresolvedConflicts.length,1);assert.deepEqual(r.unresolvedConflicts[0].memberIds,['A','B','C']);assert.equal(r.groups.length,0);
  group(x);assert.throws(()=>assembleAccepted(x),error=>error.identityConflictQueue.transitiveConflicts.length===1);
});
test('specialization blocks equivalence even without any positive pair path',()=>{
  const x=fixtureIdentity();compare(x,'ac','specializes',['A','C'],['Extra controlled limit']);group(x);assert.throws(()=>assembleAccepted(x),/recorded distinction, specialization/);
});
test('common-target grouping is not an equivalence component',()=>{
  const x=fixtureIdentity();compare(x,'abc','common_target',['A','B','C']);compare(x,'ac','different',['A','C']);const r=assembleAccepted(x).catalog.organizationProvenance.identityResolution;assert.equal(r.groups.length,0);assert.equal(r.unresolvedConflicts.length,0);
});
test('explicit conflict-free whole group binds one admitted canonical scope without merging source statements or geometric mass',()=>{
  const x=fixtureIdentity();compare(x,'ab','same_scoped_question',['A','B']);compare(x,'bc','same_scoped_question',['B','C']);const g=group(x);x.packet.aliases=[{alias:'Synthetic alternate wording',sourceRecordId:'B',destinationId:g.destinationId,identityGroupId:g.id,decisionId:g.decisionId}];const result=assembleAccepted(x),base=assembleAccepted(fixtureInput());assert.deepEqual(result.geometryInput.allocations,base.geometryInput.allocations);assert.equal(result.catalog.organizationProvenance.identityResolution.groups[0].sourceStatementEquivalenceAsserted,false);assert.deepEqual(result.catalog.destinations.find(d=>d.id===g.destinationId).aliases,['Synthetic alternate wording']);
  x.packet.decisions.at(-1).scopeContentSha256='f'.repeat(64);assert.throws(()=>assembleAccepted(x),/one admitted final scope/);
});
test('pair proof or stale inventory cannot stand in for explicit whole-group admission',()=>{
  const x=fixtureIdentity();group(x);compare(x,'ab','comparison',['A','B']);assert.throws(()=>assembleAccepted(x),/exact complete-group decision/);
});
test('partial canonical groups cannot silently join by overlap',()=>{
  const x=fixtureIdentity(),g=group(x,['A','B']);x.packet.identityResolution.canonicalGroups.push({...g,id:'identity:BC',memberIds:['B','C']});assert.throws(()=>assembleAccepted(x),/overlapping canonical groups/);
});
