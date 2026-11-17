import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {validateAtlas,loadAtlas,createAtlasNavigator} from '../../lib/geometry/prepared-atlas.mjs';
import {loadFrozenCorpus,hydrateSources} from '../../research/q025/assembly/corpus.mjs';
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');

test('exact admitted broad scopes retain all 103/122 evidence IDs through logical and lazy validation',async()=>{
  const fixture=JSON.parse(await readFile(new URL('../../research/q025/integration/source-endpoint-v1/scope-evidence-fixture.json',import.meta.url)));
  assert.deepEqual(fixture.records.map(d=>d.evidenceIds.length),[103,122]);
  const corpus=await loadFrozenCorpus(new URL('../../data/navigation/',import.meta.url).pathname);
  for(const original of fixture.records){
    const before=JSON.stringify(original),record={...structuredClone(original),placementStatus:'runtime_bound_regression_only',membershipStatus:'listed'};
    const sources=hydrateSources(corpus,record.evidenceIds),catalog={destinations:[record],sources,memberships:[],relations:[]};
    const manifest={schemaVersion:'1.0.0',kind:'eigenquestions-atlas',atlasId:'scope-bound-fixture',atlasVersion:'test',corpusId:corpus.manifest.corpusId,corpusContentHash:corpus.manifest.contentHash,entryDestinationId:record.id,scope:{description:'Test-only transport; no membership allocation.'},files:{catalog:{path:'catalog.json',sha256:sha(JSON.stringify(catalog))}}};
    assert.doesNotThrow(()=>validateAtlas(manifest,catalog));
    const files=new Map(),save=(path,value)=>{const text=JSON.stringify(value);files.set('/fixture/'+path,text);return {path,sha256:sha(text),bytes:Buffer.byteLength(text)};};
    const detail={schemaVersion:'1.0.0',kind:'eigenquestions-destination-details',destinations:{[record.id]:{destination:record,sources,membershipSample:[]}}};
    const indexed={id:record.id,kind:record.kind,title:record.title,question:record.question,membershipCount:0,contextMembershipCount:0,paperCount:0,detail:{shardId:'one'}};
    const lazy={storage:'lazy-destinations-v1',destinations:[indexed],sources:[],memberships:[],relations:[],detailShards:{one:save('detail.json',detail)}};
    save('manifest.json',{...manifest,schemaVersion:'1.1.0',files:{catalog:save('catalog.json',lazy)}});
    const nav=createAtlasNavigator(await loadAtlas('/fixture',{readText:async path=>files.get(path)}));await nav.prepareState(nav.initialState);
    const view=nav.computeView(nav.initialState);assert.equal(view.atlas.membershipCount,0);assert.ok(view.nodes.length<=30);assert.equal(view.atlas.destination.scopeContentSha256,original.scopeContentSha256);
    assert.equal(JSON.stringify(original),before);
    const missing=structuredClone(catalog);missing.sources.pop();assert.throws(()=>validateAtlas(manifest,missing),/missing representative source/);
    const over=structuredClone(catalog);over.destinations[0].evidenceIds=Array(257).fill(record.evidenceIds[0]);assert.throws(()=>validateAtlas(manifest,over),/invalid evidence IDs/);
  }
});
