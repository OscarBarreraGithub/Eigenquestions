import test from 'node:test';
import assert from 'node:assert/strict';
import {assembleAccepted,provenanceRelationContentHash} from './accepted.mjs';
import {fixtureInput} from './fixture.mjs';
test('native narrows label can be retained as provenance without public containment',()=>{
  const input=fixtureInput(),baseline=assembleAccepted(fixtureInput());
  const row={id:'provenance:fixture',sourceReviewId:'review:fixture',sourceRef:'r',targetRef:'c0',proposedType:'narrows',interpretation:'review_batch_provenance',decisionId:'decision:provenance',evidenceRefs:[{kind:'child_review',id:'c0'}]};
  input.packet.provenanceRelations=[row];input.packet.decisions.push({id:row.decisionId,type:'provenance_link',status:'accepted',sourceReviewIds:['review:fixture'],evidenceRefs:row.evidenceRefs,relationUse:'provenance_only',provenanceRelationContentSha256:provenanceRelationContentHash(row)});
  const result=assembleAccepted(input);assert.deepEqual(result.catalog.relations,baseline.catalog.relations);assert.deepEqual(result.geometryInput,baseline.geometryInput);assert.equal(result.catalog.organizationProvenance.provenanceRelations[0].proposedType,'narrows');assert.equal(result.catalog.organizationProvenance.provenanceRelations[0].affectsContainment,false);
});
test('provenance interpretation cannot be silently promoted to public navigation',()=>{
  const x=fixtureInput(),decision=x.packet.decisions.find(d=>d.id===x.packet.relations[0].decisionId);decision.relationUse='provenance_only';assert.throws(()=>assembleAccepted(x),/explicit admitted semantic use/);
});
test('admitted comparison cannot be converted to narrower by a type mapping',()=>{
  const x=fixtureInput(),decision=x.packet.decisions.find(d=>d.id===x.packet.relations[0].decisionId);decision.relationType='comparison';assert.throws(()=>assembleAccepted(x),/exact type/);
});
