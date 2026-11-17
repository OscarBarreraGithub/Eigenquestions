import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {loadAtlas,createAtlasNavigator} from '../../lib/geometry/prepared-atlas.mjs';
import {createCapsule} from '../../lib/protocol/capsule.mjs';
import {createRuntime} from '../../lib/protocol/runtime.mjs';
const fineId='source-question:'+'b'.repeat(64);
const sha=text=>createHash('sha256').update(text).digest('hex');
function fixture({alterMembership,alterDetail}={}){
  const files=new Map(),reads=[],hydratedIds=[];
  const save=(path,data)=>{const body=JSON.stringify(data);files.set('/fixture/'+path,body);return{path,sha256:sha(body),bytes:Buffer.byteLength(body)};};
  const source=id=>({id,paperId:id,title:`Synthetic ${id}`,year:id==='a'?2020:2024,evidence:{text:'Synthetic source; no scientific claim.',lens:'physical_question',date:id==='a'?'2020':'2024'}});
  const record=(id,metadataOnly=false)=>({id,kind:metadataOnly?'region':'question',title:`Synthetic ${id}`,question:`Synthetic ${id}`,summary:'Synthetic scope.',scope:{assumptions:[]},evidenceIds:[metadataOnly?'vocabulary':'a'],scientificStatus:'test_only',placementStatus:'test_only',membershipStatus:'complete',metadataOnly,provenance:{test:true}});
  const root=record('root',true),coarse=record('coarse'),fine={...record(fineId),evidenceIds:['b']};
  const row=(id,unitId)=>({destinationId:id,unitId,browserVectorRow:unitId==='a'?0:1,sourceRow:unitId==='a'?0:1,weight:1,lens:'physical_question',year:unitId==='a'?2020:2024,role:unitId==='a'?'on':'using'});
  const coarseRows=[row('coarse','a'),row('coarse','b')],fineRows=[row(fineId,'b')];
  const membership=save('memberships.json',{schemaVersion:'1.0.0',kind:'eigenquestions-destination-memberships',destinations:{coarse:{primaryCount:2,contextCount:0,items:coarseRows},[fineId]:{primaryCount:1,contextCount:0,items:alterMembership?alterMembership(fineRows):fineRows}}});
  const edge=(id,source,target)=>({id,source,target,type:'narrower',rationale:'Synthetic containment.',status:'test_only',evidenceIds:['a']});
  const rootEdge=edge('root-coarse','root','coarse'),fineEdge=edge('coarse-fine','coarse',fineId);
  const index=(d,count,connections,shardId)=>({id:d.id,kind:d.kind,title:d.title,metadataOnly:d.metadataOnly,evidenceIds:d.evidenceIds,membershipCount:count,contextMembershipCount:0,paperCount:count,connectionCount:connections,detail:{shardId}});
  const rootIndex=index(root,0,1,'root'),coarseIndex=index(coarse,2,2,'coarse'),fineIndex=index(fine,1,1,'fine');
  const item=(destination,sources,rows)=>({destination,sources,membershipSample:rows,memberships:membership});
  const rootItem=item(root,[{id:'vocabulary',kind:'vocabulary',title:'Synthetic vocabulary',evidence:{text:'Test'}}],[]);delete rootItem.memberships;
  const coarseItem={...item(coarse,[source('a')],[coarseRows[0]]),navigation:{destinations:[fineIndex],relations:[fineEdge]}},fineItem=item(fine,[source('b')],fineRows);
  if(alterDetail)alterDetail(fineItem);
  const detail=(id,value)=>save(id+'.json',{schemaVersion:'1.0.0',kind:'eigenquestions-destination-details',destinations:{[value.destination.id]:value}});
  const fineData={schemaVersion:'1.0.0',kind:'eigenquestions-fine-index',destinations:[fineIndex],relations:[fineEdge]};
  const catalog={storage:'lazy-destinations-v1',destinations:[rootIndex,coarseIndex],sources:[],memberships:[],relations:[rootEdge],detailShards:{root:detail('root',rootItem),coarse:detail('coarse',coarseItem),fine:detail('fine',fineItem)},fineIndex:save('fine-index.json',fineData),fineLookup:{kind:'source-question-hash-prefix',prefixLength:2,shards:{bb:save('fine-bb.json',fineData)}}};
  const manifest={schemaVersion:'1.1.0',kind:'eigenquestions-atlas',atlasId:'fixture',atlasVersion:'v1',corpusId:'fixture',corpusContentHash:'a'.repeat(64),entryDestinationId:'root',scope:{description:'Synthetic test only'},files:{catalog:save('catalog.json',catalog)}};save('manifest.json',manifest);
  const readText=async path=>{reads.push(path);if(!files.has(path))throw new Error('Missing test file '+path);return files.get(path);};
  return{files,reads,hydratedIds,async open(){const atlas=await loadAtlas('/fixture',{readText});return{atlas,nav:createAtlasNavigator(atlas,{readSources:async rows=>{hydratedIds.push(...rows.map(row=>row.unitId));return rows.map(row=>({...row,source:source(row.unitId)}));}})};}};
}
test('lazy entry and direct fine URL read only exact bounded records; replay is independent of cache history',async()=>{
  const f=fixture(),{nav}=await f.open();await nav.prepareState(nav.initialState);const home=nav.createSession(),before=nav.computeView(home.states[0]);createCapsule({session:home,view:before});
  assert.deepEqual(f.reads,['/fixture/manifest.json','/fixture/catalog.json','/fixture/root.json']);
  await nav.prepareDestination(fineId);const fineSession=nav.createSession({selector:{...nav.initialState.selector,destinationId:fineId}});createCapsule({session:fineSession,view:nav.computeView(fineSession.states[0])});assert.ok(f.reads.includes('/fixture/fine-bb.json'));assert.ok(!f.reads.includes('/fixture/fine-index.json'));assert.ok(!f.reads.includes('/fixture/memberships.json'));
  await nav.prepareSearch();assert.equal(nav.search(fineId)[0].id,fineId);assert.deepEqual(nav.computeView(home.states[0]),before);
  assert.deepEqual(await nav.validateCompleteMemberships(),{destinations:3,completeMemberships:2,checkedContainment:1,primaryRows:3,contextRows:0});
});
test('local fine drilldown avoids global search; filters and paging require complete membership',async()=>{
  const f=fixture(),{nav}=await f.open();await nav.prepareDestination('coarse');const state=nav.createSession({selector:{...nav.initialState.selector,destinationId:'coarse'}}).states[0],before=nav.computeView(state);
  assert.equal(before.atlas.matchingSourceCount,2);assert.deepEqual(before.atlas.matchingSourceIds,['a']);assert.equal(before.atlas.connectionCount,2);
  await nav.prepareDestination(fineId);const fineSession=nav.createSession({selector:{...nav.initialState.selector,destinationId:fineId}});createCapsule({session:fineSession,view:nav.computeView(fineSession.states[0])});assert.ok(!f.reads.some(p=>p.includes('fine-index')||p.includes('fine-bb')));
  const filtered=nav.createSession({...state,constraints:{yearMin:2023,excludeIds:[]}}).states[0];assert.throws(()=>nav.computeView(filtered),/complete membership/);
  await nav.prepareState(filtered);const result=nav.computeView(filtered);assert.equal(result.atlas.matchingSourceCount,1);assert.ok(result.nodes.some(node=>node.id==='b'&&node.atlasRole==='matching-source'));assert.deepEqual(result.atlas.matchingSourceIds,['b']);assert.deepEqual(nav.computeView(state),before);
  assert.equal(nav.sources('coarse',{constraints:{yearMin:2023},limit:20}).total,1);
});
test('lazy hashes, counts and canonical identity are checked before publication',async()=>{
  const changed=fixture(),{nav}=await changed.open();changed.files.set('/fixture/fine.json',changed.files.get('/fixture/fine.json')+' ');await assert.rejects(nav.prepareDestination(fineId),/byte count|checksum/);
  const identity=await fixture({alterDetail:item=>item.destination.question='Changed premise'}).open();await assert.rejects(identity.nav.prepareDestination(fineId),/canonical identity/);
  const count=await fixture({alterMembership:()=>[]}).open();await assert.rejects(count.nav.prepareSources(fineId),/count disagrees/);
});
test('an async prepared action cannot overwrite a newer accepted revision',async()=>{
  const {nav}=await fixture().open();await nav.prepareState(nav.initialState);let release;const gate=new Promise(resolve=>release=resolve),prepare=nav.prepareAction;
  nav.prepareAction=async(session,action)=>{if(action.selector?.destinationId==='coarse')await gate;await prepare(session,action);};
  const runtime=createRuntime(nav,'fixture'),slow=runtime.action({type:'navigate',selector:{...nav.initialState.selector,destinationId:'coarse'}});
  const first=await runtime.action({type:'navigate',selector:{...nav.initialState.selector,destinationId:fineId}});assert.equal(first.revision,1);release();await assert.rejects(slow,/Revision conflict/);assert.equal(runtime.snapshot().view.atlas.destination.id,fineId);
});

test('lazy preparation honors the shared implicit USING action before hydrating selected rows',async()=>{
  const f=fixture(),{nav}=await f.open();await nav.prepareDestination('coarse');const runtime=createRuntime(nav,'fixture',{selector:{...nav.initialState.selector,destinationId:'coarse'}});
  const result=await runtime.action({type:'navigate',intent:'using'});assert.equal(result.view.atlas.matchingSourceCount,1);assert.deepEqual(result.view.atlas.matchingSourceIds,['b']);assert.deepEqual(f.hydratedIds,['b']);
});

test('cold runtime connection reads hydrate exact coarse and fine links without changing the session',async()=>{
  const {nav}=await fixture().open();await nav.prepareState(nav.initialState);const runtime=createRuntime(nav,'fixture'),before=structuredClone(runtime.snapshot());
  const fine=await runtime.connections({destinationId:fineId});assert.equal(fine.total,1);assert.deepEqual(await runtime.connections({destinationId:fineId}),fine);
  const coarse=await runtime.connections({destinationId:'coarse'});assert.equal(coarse.total,2);assert.deepEqual(await runtime.connections({destinationId:'coarse'}),coarse);assert.deepEqual(runtime.snapshot(),before);
});
