import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {createAtlasNavigator,atlasAddress} from '../../lib/geometry/prepared-atlas.mjs';
import {createRuntime} from '../../lib/protocol/runtime.mjs';
import {currentState,normalizeState,exportSession} from '../../lib/protocol/session.mjs';
import {createCapsule,validateCapsule} from '../../lib/protocol/capsule.mjs';
const fixture=JSON.parse(await readFile(new URL('../../research/q025/integration/source-endpoint-v1/fixtures.json',import.meta.url),'utf8'));
const hash=value=>createHash('sha256').update(JSON.stringify(value)).digest('hex');
export function routeFixture({mapping=fixture.mapping,contexts=fixture.contexts,sources=fixture.sources,readContext}={}){
 const destination={id:'physics-fixture',kind:'region',metadataOnly:true,title:'Physics inspection fixture',question:'Which source method is being inspected?',summary:'Protocol fixture; no claim of a scientific home for the inspected source.',scope:{assumptions:[]},evidenceIds:[],scientificStatus:'synthetic test',placementStatus:'metadata-only',provenance:{fixture:true}};
 const catalog={destinations:[destination],sources:[],memberships:[],relations:[]},manifest={schemaVersion:'1.0.0',kind:'eigenquestions-atlas',atlasId:'endpoint-test',atlasVersion:'v1',corpusId:'fixture-corpus',corpusContentHash:'a'.repeat(64),entryDestinationId:destination.id,scope:{description:'Source endpoint protocol fixture'},files:{catalog:{path:'catalog.json',sha256:hash(catalog)}}};
 const nav=createAtlasNavigator({manifest,catalog,manifestSha256:hash(manifest)},{readSourceRoutes:async()=>structuredClone(mapping),readContext:readContext|| (async id=>structuredClone(contexts[id]||{unitId:id,availability:'not-exported',sourceRelations:[],sourceObjects:[]})),readSources:async rows=>rows.map(row=>({...row,source:structuredClone(sources[row.unitId])}))});
 return {nav,runtime:createRuntime(nav,manifest.corpusId),manifest};
}
const actionFor=(row,side='target')=>({type:'inspect-source',sourceInspection:{originUnitId:row.originUnitId,relationId:row.relationId,objectId:row[side+'ObjectId'],unitId:row[side+'UnitId']}});

test('three real reviewed method relations support both exact endpoints while preserving the physical destination',async()=>{
 for(const row of fixture.cases){const {runtime}=routeFixture(),initial=runtime.snapshot();
  for(const side of ['source','target']){const action=actionFor(row,side),result=await runtime.action(action,{expectedRevision:runtime.snapshot().revision}),inspection=result.view.atlas.sourceInspection;
   assert.deepEqual(currentState(result.session).selector,currentState(initial.session).selector);assert.equal(currentState(result.session).query,currentState(initial.session).query);assert.notEqual(result.view.stateId,initial.view.stateId);
   assert.deepEqual(result.view.nodes,initial.view.nodes);assert.deepEqual(result.view.directions,initial.view.directions);assert.equal(result.view.atlas.membershipCount,0);assert.equal(currentState(result.session).workRelation,'either');
   assert.equal(inspection.object.id,row[side+'ObjectId']);assert.equal(inspection.source.id,row[side+'UnitId']);assert.equal(inspection.endpointSide,side);assert.deepEqual(inspection.relation,fixture.contexts[row.originUnitId].sourceRelations[0]);
   assert.equal(inspection.relation.source,row.sourceObjectId);assert.equal(inspection.relation.target,row.targetObjectId);assert.ok(inspection.relation.premises);assert.match(inspection.notice,/leaves the physical destination/);
   validateCapsule(createCapsule(result));assert.throws(()=>atlasAddress(currentState(result.session)),/full view/);
  }
  const beforeBack=runtime.snapshot(),back=await runtime.action({type:'back'},{expectedRevision:beforeBack.revision});assert.equal(back.view.atlas.sourceInspection.endpointSide,'source');
  const replay=await runtime.action({type:'replay',index:2},{expectedRevision:back.revision});assert.equal(replay.view.atlas.sourceInspection.endpointSide,'target');
  const closed=await runtime.action({type:'close-source'},{expectedRevision:replay.revision});assert.equal(closed.view.stateId,initial.view.stateId);assert.equal(closed.view.atlas.sourceInspection,undefined);
  const imported=await runtime.import(exportSession(beforeBack.session),{expectedRevision:closed.revision});assert.deepEqual(imported.view.atlas.sourceInspection,beforeBack.view.atlas.sourceInspection);
 }
});

test('agent context pages expose exact actions and unmapped source endpoints remain nonfollowable',async()=>{
 const {runtime}=routeFixture(),row=fixture.cases[0],before=runtime.snapshot();
 const page=await runtime.context({unitId:row.originUnitId,section:'relations'});assert.equal(page.sourceRoutes.items.length,1);const target=page.sourceRoutes.items[0].endpoints.find(item=>item.side==='target');assert.deepEqual(target.choices[0].action,actionFor(row));assert.equal(runtime.snapshot().revision,before.revision);
 const unmapped=await runtime.context({unitId:fixture.unmappedContext.unitId,section:'relations'});assert.equal(unmapped.sourceRelations.length,1);assert.ok(unmapped.sourceRoutes.items[0].endpoints.every(endpoint=>endpoint.choices.length===0));
 await assert.rejects(runtime.action({type:'inspect-source',sourceInspection:{originUnitId:fixture.unmappedContext.unitId,relationId:fixture.unmapped.route.id,objectId:fixture.unmapped.route.targetObjectId,unitId:row.targetUnitId}},{expectedRevision:0}),/not mapped/);assert.equal(runtime.snapshot().revision,0);
});

test('wrong endpoint, altered review or source text, and stale interpretation parents cannot commit',async()=>{
 const row=fixture.cases[0];
 for(const invalid of [r=>r.objectId='obj:wrong',r=>r.unitId=row.sourceUnitId,r=>r.originUnitId='unit:absent']){const {runtime}=routeFixture(),action=actionFor(row);invalid(action.sourceInspection);await assert.rejects(runtime.action(action,{expectedRevision:0}));assert.equal(runtime.snapshot().revision,0);}
 const mapping=structuredClone(fixture.mapping);mapping.routes[row.relationId].receiptSha256='b'.repeat(64);let {runtime}=routeFixture({mapping});await assert.rejects(runtime.action(actionFor(row),{expectedRevision:0}),/exact reviewed/);
 const sources=structuredClone(fixture.sources);sources[row.targetUnitId].evidence.text+=' Changed';({runtime}=routeFixture({sources}));await assert.rejects(runtime.action(actionFor(row),{expectedRevision:0}),/text changed/);
 ({runtime}=routeFixture());await runtime.action({type:'reset'},{expectedRevision:0});assert.throws(()=>runtime.action(actionFor(row),{expectedRevision:0}),/Revision conflict/);assert.equal(runtime.snapshot().revision,1);
 assert.throws(()=>normalizeState({corpusId:'native',computationId:'native',sourceInspection:actionFor(row).sourceInspection}),/physical atlas destination/);
});

test('an endpoint read delayed by a shard cannot overwrite a newer state, and foreign navigation fields are rejected',async()=>{
 const row=fixture.cases[0];let release,started;const gate=new Promise(resolve=>{release=resolve}),ready=new Promise(resolve=>{started=resolve});
 const {runtime}=routeFixture({readContext:async id=>{started();await gate;return structuredClone(fixture.contexts[id]);}});
 const pending=runtime.action(actionFor(row),{expectedRevision:0});await ready;const newer=await runtime.action({type:'reset'},{expectedRevision:0});release();await assert.rejects(pending,/Revision conflict/);assert.equal(runtime.snapshot().view.stateId,newer.view.stateId);assert.equal(runtime.snapshot().view.atlas.sourceInspection,undefined);
 await assert.rejects(runtime.action({...actionFor(row),workRelation:'using'},{expectedRevision:1}),/Unknown source inspection action field/);assert.equal(runtime.snapshot().revision,1);
});
