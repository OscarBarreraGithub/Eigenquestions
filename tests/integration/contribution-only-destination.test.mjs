import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {fixtureInput} from '../../research/q025/assembly/fixture.mjs';
import {assembleAccepted,scopeContentHash,sourceContributionContentHash} from '../../research/q025/assembly/accepted.mjs';
import {partitionCatalog,validatePartition} from '../../research/q025/assembly/lazy-package.mjs';
import {createAtlasNavigator,validateAtlas} from '../../lib/geometry/prepared-atlas.mjs';
import {createRuntime} from '../../lib/protocol/runtime.mjs';
import {createCapsule} from '../../lib/protocol/capsule.mjs';
const sha=value=>createHash('sha256').update(JSON.stringify(value)).digest('hex');
function compiledFixture(){
  const input=fixtureInput(),destination=input.packet.destinations.find(d=>d.id==='destination:fine');
  input.packet.reviewRegistry.push({id:'review:independent-challenge',sha256:'b'.repeat(64)});
  const row={unitId:'unit:q3',destinationId:destination.id,role:'comparison',basis:'description_checked',evidenceRefs:[{kind:'description',unitId:'unit:q3',textSha256:input.corpus.unitMap.get('unit:q3').evidence.textSha256}],decisionId:'decision:contribution-only'};
  input.packet.sourceContributions=[row];input.packet.decisions.push({id:row.decisionId,type:'source_contribution',status:'accepted',subjectIds:[row.unitId,row.destinationId],sourceReviewIds:['review:fixture','review:independent-challenge'],evidenceRefs:row.evidenceRefs,challengerAgreement:'independently_agreed',scopeContentSha256:scopeContentHash(destination),contributionContentSha256:sourceContributionContentHash(row,scopeContentHash(destination)),reviewAgreement:{proposalReviewId:'review:fixture',challengeReviewId:'review:independent-challenge'}});
  const placement=input.packet.placements.find(p=>p.unitId==='unit:q1');placement.destinationId='destination:a';input.packet.decisions.find(d=>d.id===placement.decisionId).subjectIds=['unit:q1','destination:a'];
  return assembleAccepted(input);
}
test('an admitted contribution-only question loads with pinned empty membership and remains scientifically supported',async()=>{
  const compiled=compiledFixture(),manifest={schemaVersion:'1.0.0',kind:'eigenquestions-atlas',atlasId:'contribution-only-fixture',atlasVersion:'v1',corpusId:'fixture-corpus',corpusContentHash:'a'.repeat(64),entryDestinationId:'destination:root',scope:{description:'Synthetic contribution-only regression'},files:{catalog:{path:'catalog.json',sha256:sha(compiled.catalog)}}};
  validateAtlas(manifest,compiled.catalog);const partition=partitionCatalog(compiled.catalog,{entryDestinationId:manifest.entryDestinationId});assert.equal(validatePartition(compiled.catalog,partition).passed,true);
  const lazyManifest={...manifest,schemaVersion:'1.1.0',files:{catalog:{path:'catalog.json',sha256:sha(partition.catalog)}}};
  const navigatorFor=(mutate=()=>{})=>{const catalog=structuredClone(partition.catalog),files=partition.files.map(file=>({...file,payload:JSON.parse(file.text)}));mutate(catalog,files);return createAtlasNavigator({manifest:lazyManifest,catalog,manifestSha256:sha(lazyManifest),readShard:async descriptor=>structuredClone(files.find(file=>file.descriptor.path===descriptor.path).payload)});};
  const nav=navigatorFor();await nav.prepareDestination('destination:fine');await nav.prepareSources('destination:fine');
  const selector={...nav.initialState.selector,destinationId:'destination:fine'},session=nav.createSession({selector}),view=nav.computeView(session.states[0]);
  assert.equal(view.atlas.membershipCount,0);assert.equal(view.atlas.membershipReadMode,'complete-selection');assert.ok(view.nodes.every(node=>node.atlasMembershipChecked!==false));assert.equal(view.atlas.contextMembershipCount,0);assert.equal(view.atlas.destination.sourceContributions.length,1);assert.equal(view.atlas.destination.metadataOnly,undefined);assert.ok(view.nodes.length>0);assert.ok(view.nodes.every(node=>node.atlasRole==='context-evidence'));assert.equal(nav.sources('destination:fine').total,0);assert.equal(nav.sources('destination:fine',{workRelation:'using'}).total,0);createCapsule({session,view});
  await nav.prepareState(nav.initialState);
  const runtime=createRuntime({...nav,readSources:async rows=>rows.map(row=>({...row,source:compiled.catalog.sources.find(source=>source.id===row.unitId)}))},manifest.corpusId),before=JSON.stringify(runtime.snapshot());
  const contributions=await runtime.sources({destinationId:'destination:fine',collection:'contributions',limit:1});assert.equal(contributions.total,1);assert.equal(contributions.items[0].role,'comparison');assert.ok(contributions.items[0].source.evidence.text);assert.equal(contributions.items[0].destinationId,'destination:fine');assert.equal(JSON.stringify(runtime.snapshot()),before);
  assert.equal((await runtime.sources({destinationId:'destination:fine',collection:'contributions',offset:1})).items.length,0);assert.equal((await runtime.sources({destinationId:'destination:fine',workRelation:'using'})).total,0);await assert.rejects(runtime.sources({destinationId:'destination:fine',collection:'contributions',workRelation:'using'}),/membership filters/);
  for(const changed of ['positive-count','unexpected-sample']){
    const broken=navigatorFor((catalog,files)=>{const index=catalog.destinations.find(d=>d.id==='destination:fine'),item=files.find(file=>file.payload.destinations?.['destination:fine'])?.payload.destinations['destination:fine'];if(changed==='positive-count'){index.membershipCount=1;delete item.destination.membershipCount;}else item.membershipSample.push({destinationId:'destination:fine',unitId:'unit:q3',weight:1,role:'on'});});
    await assert.rejects(broken.prepareDestination('destination:fine'),/descriptor|count/);
  }
});
