import test from 'node:test';
import assert from 'node:assert/strict';
import {partitionCatalog,validatePartition,templateIndex,relationRecordHash} from './lazy-package.mjs';
import {assembleAccepted} from './accepted.mjs';
import {fixtureInput} from './fixture.mjs';

test('lazy export roundtrips complete memberships and excludes context from pinned primary counts',()=>{
  const {catalog}=assembleAccepted(fixtureInput()),p=partitionCatalog(catalog,{entryDestinationId:'destination:root',detailTargetBytes:2000,membershipTargetBytes:2000});
  assert.equal(p.catalog.sources.length,0);assert.equal(p.catalog.memberships.length,0);
  const root=p.catalog.destinations.find(d=>d.id==='destination:root');assert.equal(root.membershipCount,3);assert.equal(root.contextMembershipCount,2);assert.equal(root.paperCount,2);
  assert.equal(validatePartition(catalog,p).exactMembershipRoundTrip,true);
});
test('partition validation rejects modified shard bytes even when logical catalog is intact',()=>{
  const {catalog}=assembleAccepted(fixtureInput()),p=partitionCatalog(catalog,{entryDestinationId:'destination:root'});p.files[0].text+=' ';
  assert.throws(()=>validatePartition(catalog,p),/checksum mismatch/);
});
test('template defaults preserve every value and never supply identities or endpoints',()=>{
  const raw={destinations:[{id:'a',kind:'question',title:'A',sourceQuestionAccess:true},{id:'b',kind:'question',title:'B',sourceQuestionAccess:true}],relations:[{id:'r1',source:'x',target:'a',type:'source_question',rationale:'Exact source access'},{id:'r2',source:'x',target:'b',type:'source_question',rationale:'Exact source access'}]};
  const packed=templateIndex(raw);for(const kind of ['destinations','relations']){const unpacked=packed[kind].map(row=>{const value={...packed.indexTemplates[kind][row.indexTemplate],...row};delete value.indexTemplate;return value;});assert.deepEqual(unpacked,raw[kind]);for(const t of Object.values(packed.indexTemplates[kind]))assert.ok(!['id','source','target'].some(k=>Object.hasOwn(t,k)));}
});
test('compact relation index preserves scientific qualifications and resolves the exact full proof',()=>{
  const {catalog}=assembleAccepted(fixtureInput());const relation=catalog.relations[0];relation.qualification='Conditional on the stated field content.';relation.premises=['Specified background'];relation.evidenceRefs=[{kind:'description',unitId:catalog.sources[0].id}];
  const p=partitionCatalog(catalog,{entryDestinationId:'destination:root'}),index=p.catalog.relations.find(r=>r.id===relation.id);assert.equal(index.qualification,relation.qualification);assert.deepEqual(index.premises,relation.premises);assert.equal(index.evidenceCount,relation.evidenceIds.length);assert.equal(index.evidenceIds,undefined);assert.equal(index.evidenceRefs,undefined);assert.equal(index.detail.recordSha256,relationRecordHash(relation));
  const descriptor=p.catalog.relationDetailShards[index.detail.shardId],full=JSON.parse(p.files.find(f=>f.descriptor.path===descriptor.path).text).relations[relation.id];assert.deepEqual(full,relation);assert.equal(validatePartition(catalog,p).exactRelationProofRoundTrip,true);assert.equal(p.catalog.organizationProvenance,undefined);assert.ok(p.ancillary.organizationProvenance);
});
test('compact index cannot silently change a qualification or proof record hash',()=>{
  const {catalog}=assembleAccepted(fixtureInput());for(const change of [r=>r.qualification='Unconditional',r=>r.detail.recordSha256='0'.repeat(64)]){const p=partitionCatalog(catalog,{entryDestinationId:'destination:root'});change(p.catalog.relations[0]);assert.throws(()=>validatePartition(catalog,p),/relation changed/);}
});
