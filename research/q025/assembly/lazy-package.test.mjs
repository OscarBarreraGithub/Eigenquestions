import test from 'node:test';
import assert from 'node:assert/strict';
import {partitionCatalog,validatePartition,templateIndex} from './lazy-package.mjs';
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
