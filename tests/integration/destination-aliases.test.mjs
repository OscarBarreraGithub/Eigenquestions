import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {createAtlasNavigator,validateAtlas,atlasAddress} from '../../lib/geometry/prepared-atlas.mjs';
import {createRuntime} from '../../lib/protocol/runtime.mjs';
const sha=x=>createHash('sha256').update(JSON.stringify(x)).digest('hex');
function fixture(){
 const source={id:'unit:fixture',paperId:'paper',title:'Synthetic alias test',evidence:{text:'Synthetic test. No scientific admission.'}};
 const full={id:'canonical',kind:'question',title:'Canonical scoped question',question:'What is the canonical scoped target?',summary:'Current source-scoped summary',scope:{targets:['Target']},scientificStatus:'test',placementStatus:'test',readingCoverage:'Current reading limit',evidenceIds:[source.id],provenance:{test:true},scopeContentSha256:'a'.repeat(64)};
 const original={...full,id:'former',title:'Earlier reviewed wording',readingCoverage:{readingLimit:'Earlier reading limit retained exactly.'},scopeContentSha256:'b'.repeat(64)};
 full.scopedIdentity={groupId:'group:test',canonicalDestinationId:full.id,identityInventorySha256:'c'.repeat(64),decisionId:'decision:identity',originalDefinitions:[original,{...full}],retainedReadingLimits:[{destinationId:original.id,readingCoverage:original.readingCoverage},{destinationId:full.id,readingCoverage:full.readingCoverage}],sourceStatementEquivalence:false};
 const detail={schemaVersion:'1.0.0',kind:'eigenquestions-destination-details',destinations:{canonical:{destination:full,sources:[source],membershipSample:[]}}};const descriptor={path:'detail.json',sha256:sha(detail),bytes:JSON.stringify(detail).length};
 const catalog={storage:'lazy-destinations-v1',destinations:[{id:full.id,kind:full.kind,title:full.title,question:full.question,membershipCount:0,contextMembershipCount:0,paperCount:1,detail:{shardId:'one'}}],destinationAliases:{former:'canonical'},detailShards:{one:descriptor},sources:[],memberships:[],relations:[]};
 const manifest={schemaVersion:'1.1.0',kind:'eigenquestions-atlas',atlasId:'alias-fixture',atlasVersion:'v1',corpusId:'fixture',corpusContentHash:'d'.repeat(64),entryDestinationId:'canonical',scope:{description:'Synthetic alias fixture'},files:{catalog:{path:'catalog.json',sha256:sha(catalog)}}},reads=[];
 return {manifest,catalog,manifestSha256:'e'.repeat(64),readShard:async file=>{reads.push(file.path);return structuredClone(detail);},detail,reads};
}
test('former and canonical IDs produce one state and bounded detail load while retaining exact earlier definitions',async()=>{
 const x=fixture(),nav=createAtlasNavigator(x),oldSelector={...nav.initialState.selector,destinationId:'former'};
 const former=nav.createSession({selector:oldSelector}),canonical=nav.createSession();assert.deepEqual(former,canonical);assert.equal(former.states[0].selector.destinationId,'canonical');
 await nav.prepareDestination('former');await nav.prepareDestination('canonical');await nav.prepareSources('former');assert.deepEqual(x.reads,['detail.json']);
 assert.deepEqual(nav.destination('former'),nav.destination('canonical'));assert.equal(nav.destination('former').scopedIdentity.originalDefinitions[0].readingCoverage.readingLimit,'Earlier reading limit retained exactly.');assert.equal(nav.destination('former').scopeContentSha256,'a'.repeat(64));assert.equal(nav.sources('former').total,0);assert.equal(nav.sources('former',{workRelation:'using'}).total,0);assert.deepEqual(nav.connections('former'),nav.connections('canonical'));assert.match(atlasAddress(former.states[0]),/destination=canonical/);
 const runtime=createRuntime(nav,'fixture'),before=JSON.stringify(runtime.snapshot());assert.deepEqual(await runtime.connections({destinationId:'former'}),await runtime.connections({destinationId:'canonical'}));assert.equal(JSON.stringify(runtime.snapshot()),before);assert.equal(nav.computeView(former.states[0]).atlas.selector.destinationId,'canonical');
});
test('aliases reject cycles, chains, active-ID overwrites and unknown targets',()=>{
 for(const aliases of [{canonical:'former',former:'canonical'},{former:'another',another:'canonical'},{canonical:'canonical'},{former:'missing'}]){const x=fixture();x.catalog.destinationAliases=aliases;assert.throws(()=>validateAtlas(x.manifest,x.catalog),/aliases/);}
});
test('canonical detail must retain each aliased original and its exact reading coverage',async()=>{
 for(const mutate of [x=>x.detail.destinations.canonical.destination.scopedIdentity.originalDefinitions.shift(),x=>x.detail.destinations.canonical.destination.scopedIdentity.retainedReadingLimits[0].readingCoverage='changed',x=>x.detail.destinations.canonical.destination.scopedIdentity.sourceStatementEquivalence=true]){const x=fixture();mutate(x);const nav=createAtlasNavigator(x);await assert.rejects(nav.prepareDestination('former'),/aliased original|reading limit|identity binding/);}
});
