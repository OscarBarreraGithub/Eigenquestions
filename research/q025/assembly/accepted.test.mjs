import test from 'node:test';
import assert from 'node:assert/strict';
import {assembleAccepted,scopeContentHash} from './accepted.mjs';
import {fixtureInput} from './fixture.mjs';
import {validateAtlas,createAtlasNavigator} from '../../../lib/geometry/prepared-atlas.mjs';
import {sha256} from './corpus.mjs';

test('conserves sources, overlapping unit mass, rare-paper mass and unresolved family visibility',()=>{
  const result=assembleAccepted(fixtureInput());
  assert.equal(result.catalog.sources.length,5);assert.equal(result.report.questionAllocationMaxError,0);
  assert.equal(result.report.visibleAmbiguousPlacements.length,2);
  assert.equal(result.geometryInput.units.reduce((s,u)=>s+u.paperBalancedMass,0),2);
  assert.equal(result.catalog.destinations.find(d=>d.id==='destination:root').memberIds.length,3);
  assert.equal(result.catalog.memberships.find(m=>m.destinationId==='destination:root'&&m.unitId==='unit:q2').weight,1);
  assert.equal(result.report.unrepresentedPapers[0].id,'unavailable');
});
test('context methods remain outside primary containment/counts and USING',()=>{
  const {catalog}=assembleAccepted(fixtureInput()),manifest={schemaVersion:'1.0.0',kind:'eigenquestions-atlas',atlasId:'fixture',atlasVersion:'1',corpusId:'fixture-corpus',corpusContentHash:'a'.repeat(64),entryDestinationId:'destination:root',scope:{description:'Synthetic fixture'},files:{catalog:{path:'catalog.json',sha256:sha256(JSON.stringify(catalog))}}};
  validateAtlas(manifest,catalog);const nav=createAtlasNavigator({manifest,catalog,manifestSha256:sha256(JSON.stringify(manifest))});
  assert.equal(nav.sources('destination:root',{}).total,3);
  assert.equal(nav.sources('destination:root',{lens:'method'}).total,2);
  assert.equal(nav.sources('destination:root',{lens:'method',workRelation:'using'}).total,0);
  assert.ok(nav.sources('destination:root',{lens:'method'}).items.every(m=>m.placementStatus==='context_only'&&m.associationScope==='same_paper_context'));
});
for(const [name,mutate,pattern] of [
  ['raw review verdict',x=>{x.packet.acceptance.status='needs_revision';},/raw reviewer/],
  ['scope rewrite after agreement',x=>{x.packet.destinations[0].question='Changed scope';},/scope changed/],
  ['qualified rewrite is not unchanged acceptance',x=>{x.packet.decisions[0].challengerAgreement='supported_with_explicit_limits';},/awaiting review/],
  ['uncovered question',x=>{x.packet.placements=x.packet.placements.filter(p=>p.unitId!=='unit:q3');},/uncovered question/],
  ['unknown source identity',x=>{x.packet.placements[0].unitId='unit:invented';},/unknown placement/],
  ['unresolved canonical question',x=>{x.packet.placements[0].status='unresolved';x.packet.placements[0].reason='Unknown';},/broad family/],
  ['unadmitted alias',x=>{x.packet.destinations[0].aliases=['Same thing'];},/aliases must/],
  ['source science promoted as navigation',x=>{x.packet.relations[0].type='implies';},/cannot be promoted/],
  ['missing source review lineage',x=>{x.packet.reviewRegistry=[];},/review provenance/],
  ['cyclic containment',x=>{const r={...x.packet.relations[0],id:'cycle',source:'destination:a',target:'destination:root'};x.packet.relations.push(r);},/cyclic/],
  ['nonconserving allocation weights',x=>{x.packet.allocationPolicy='explicit_normalized_weights';x.packet.placements.forEach(p=>p.allocationWeight=.2);},/does not conserve/],
])test(`rejects ${name}`,()=>{const input=fixtureInput();mutate(input);assert.throws(()=>assembleAccepted(input),pattern);});
