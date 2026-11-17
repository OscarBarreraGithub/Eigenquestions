import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile} from 'node:fs/promises';
import {createAtlasNavigator,loadAtlas,validateAtlas,atlasAddress,createAtlasSourceReader} from '../../lib/geometry/prepared-atlas.mjs';
import {PREPARED_SOURCE_SHA256} from '../../lib/geometry/prepared-identity.mjs';
import {createSession,normalizeState,currentState,applyAction,importSession,exportSession} from '../../lib/protocol/session.mjs';
import {createCapsule,capsuleCapabilities,encodeCapsuleBytes,decodeCapsuleBytes} from '../../lib/protocol/capsule.mjs';
import {createRuntime,agentSnapshot} from '../../lib/protocol/runtime.mjs';

export function atlasFixture({extraConnections=0,largeMembership=false}={}) {
  const source=(id)=>({id,paperId:id,title:`Synthetic source ${id}`,year:2024,sourceUrl:`https://example.org/${id}`,evidence:{text:`Synthetic acceptance fixture ${id}; no physics claim.`,lens:'physical_question',date:'2024',claimStatus:'synthetic fixture'}});
  const destination=(id,kind='region')=>({id,kind,title:`Fixture ${id}`,question:`What defines fixture ${id}?`,summary:`Synthetic scope for ${id}.`,scope:{assumptions:['Synthetic fixture only'],includes:[id],excludes:[],regimes:[],conventions:[]},aliases:id==='shared'?['shared alias','alternate alias']:[],evidenceIds:['source-a'],scientificStatus:'synthetic fixture',placementStatus:'test only',provenance:{builder:'test'}});
  const destinations=[destination('root'),destination('left'),destination('right'),destination('shared','question'),destination('contrast','question')];
  const relation=(id,source,target,type='narrower')=>({id,source,target,type,evidenceIds:['source-a'],rationale:'Synthetic navigation edge; no physics claim.',status:'test only'});
  const relations=[relation('root-left','root','left'),relation('root-right','root','right'),relation('left-shared','left','shared'),relation('right-shared','right','shared'),relation('shared-contrast','shared','contrast','related_question')];
  for(let i=0;i<extraConnections;i++){destinations.push(destination(`extra-${i}`));relations.push(relation(`extra-edge-${i}`,'shared',`extra-${i}`,'uses_method'));}
  const catalog={destinations,sources:[source('source-a'),source('source-b')],memberships:destinations.flatMap(d=>[{destinationId:d.id,unitId:'source-a',weight:1,role:'on'},{destinationId:d.id,unitId:'source-b',weight:.5,role:'using'}]),relations};
  if(largeMembership)for(let i=0;i<600;i++)catalog.memberships.push({destinationId:'shared',unitId:`unbundled-source-${i}`,weight:.1,role:'evidence',browserVectorRow:1000+i});
  const manifest={schemaVersion:'1.0.0',kind:'eigenquestions-atlas',atlasId:'acceptance-fixture',atlasVersion:'2026-11-17-test',corpusId:'fixture-corpus',corpusContentHash:'a'.repeat(64),entryDestinationId:'root',snapshotDate:'2026-11-17',scope:{description:'Synthetic acceptance data; no physics claims.',limitations:['Test fixture only']},files:{catalog:{path:'catalog.json',sha256:createHash('sha256').update(JSON.stringify(catalog)).digest('hex')}}};
  return {manifest,catalog,manifestSha256:createHash('sha256').update(JSON.stringify(manifest)).digest('hex')};
}
const select=(session,nav,target)=>applyAction(session,{type:'select',directionId:nav.computeView(currentState(session)).directions.find(d=>d.selector.destinationId===target).id},nav).session;

test('prepared destinations converge through different paths without changing v1 identity',()=>{
  assert.equal(normalizeState({corpusId:'fixture',computationId:'pinned',query:'comparison'}).id,'state-152f2c6c57334720');
  const nav=createAtlasNavigator(atlasFixture()),home=nav.createSession();
  const left=select(select(home,nav,'left'),nav,'shared'),right=select(select(home,nav,'right'),nav,'shared');
  assert.equal(currentState(left).selector.destinationId,'shared');
  assert.deepEqual(currentState(left),currentState(right));assert.deepEqual(nav.computeView(currentState(left)),nav.computeView(currentState(right)));
  assert.notEqual(currentState(left).id,currentState(select(left,nav,'contrast')).id);
  assert.deepEqual(importSession(exportSession(left)),left);
  assert.equal(applyAction(left,{type:'back'},nav).session.cursor,1);
  const replay=applyAction(left,{type:'replay',index:0},nav).session;
  assert.equal(select(replay,nav,'right').states.length,2);
  assert.throws(()=>applyAction(left,{type:'navigate',query:'A paragraph is not a destination.'},nav),/does not interpret paragraphs/);
  assert.throws(()=>applyAction(left,{type:'select',directionId:'stale'},nav),/absent/);
});

test('prepared capsule preserves exact selector, full membership counts and all cross-links beyond menu',async()=>{
  const nav=createAtlasNavigator(atlasFixture({extraConnections:18,largeMembership:true})),session=nav.createSession({selector:{...nav.initialState.selector,destinationId:'shared'}}),view=nav.computeView(currentState(session));
  assert.equal(view.directions.length,15);assert.equal(view.atlas.connectionCount,21);
  assert.equal(view.atlas.membershipCount,602);assert.ok(view.nodes.length<=500);assert.equal(nav.sources('shared',{offset:600,limit:10}).items.length,2);
  const capsule=createCapsule({session,view});assert.equal(capsuleCapabilities(capsule,nav.computationId).continue,true);
  assert.deepEqual(await decodeCapsuleBytes(await encodeCapsuleBytes(capsule)),capsule);
  assert.equal(view.atlas.connections.find(r=>r.id==='left-shared').traversal,'incoming');
  assert.equal(view.atlas.connections.find(r=>r.id==='left-shared').type,'narrower');
  assert.equal(nav.connections('shared').total,21);
});

test('prepared loader verifies exact content, containment, evidence and version',async()=>{
  const atlas=atlasFixture(),readText=async p=>JSON.stringify(p.endsWith('manifest.json')?atlas.manifest:atlas.catalog);
  assert.deepEqual(await loadAtlas('/fixture',{readText}),atlas);
  atlas.catalog.destinations[0].title='Modified';await assert.rejects(loadAtlas('/fixture',{readText}),/checksum/);
  const cycle=atlasFixture();cycle.catalog.relations.push({id:'cycle',source:'shared',target:'root',type:'narrower',evidenceIds:['source-a'],rationale:'fixture',status:'test'});assert.throws(()=>validateAtlas(cycle.manifest,cycle.catalog),/cyclic/);
  const unsupported=atlasFixture();unsupported.catalog.destinations[0].evidenceIds=['missing'];assert.throws(()=>createAtlasNavigator(unsupported),/source/);
  const nav=createAtlasNavigator(atlasFixture());assert.throws(()=>nav.createSession({selector:{...nav.initialState.selector,atlasVersion:'different'}}),/version mismatch/);
});

test('lookup is explicitly lexical and prepared runtime uses existing shared transitions',()=>{
  const atlas=atlasFixture(),nav=createAtlasNavigator(atlas),runtime=createRuntime(nav,atlas.manifest.corpusId);
  assert.equal(runtime.search('shared alias')[0].selector.destinationId,'shared');
  assert.equal(runtime.search('alternate alias')[0].matchKind,'title-and-alias-lookup');
  assert.equal(runtime.search('unrepresented wording').length,0);
  const first=runtime.snapshot();runtime.action({type:'navigate',selector:{...nav.initialState.selector,destinationId:'shared'}});
  assert.equal(runtime.snapshot().revision,1);assert.equal(agentSnapshot(runtime.snapshot()).view.chart,null);
  runtime.import(runtime.export());assert.equal(runtime.snapshot().revision,2);
  assert.equal(first.view.atlas.selector.destinationId,'root');
});

test('prepared addresses contain scientific selector and perspective, never prose or notes',()=>{
  const nav=createAtlasNavigator(atlasFixture()),session=nav.createSession({intent:'recent',lens:'method'}),state=currentState(session),url=new URL(atlasAddress(state));
  assert.equal(new URLSearchParams(url.hash.slice(1)).get('destination'),'root');
  assert.ok(!url.href.includes(state.query));assert.equal(new URLSearchParams(url.hash.slice(1)).get('intent'),'recent');
  assert.throws(()=>atlasAddress(normalizeState({...state,constraints:{yearMin:2020}})),/capsule/);
  assert.throws(()=>createSession({...state,schemaVersion:'1.0.0'}),/schemaVersion/);
});

test('full-source paging verifies real frozen rows without loading any embedding files',async()=>{
  const corpus=new URL('../../data/navigation/',import.meta.url),manifest=JSON.parse(await readFile(new URL('manifest.json',corpus),'utf8')),units=JSON.parse(await readFile(new URL('units-000.json',corpus),'utf8')),reads=[];
  const reader=createAtlasSourceReader({manifest:{corpusId:manifest.corpusId,corpusContentHash:manifest.contentHash}},{base:corpus.href,readText:async filename=>{reads.push(filename);return readFile(new URL(filename),'utf8');}});
  const result=await reader([{unitId:units[0].id,browserVectorRow:0}]);assert.equal(result[0].source.evidence.text,units[0].text);assert.equal(result[0].source.paperId,units[0].paperId);
  assert.ok(reads.every(name=>name.endsWith('.json')));assert.equal(reads.length,3);
  await assert.rejects(reader([{unitId:'wrong-id',browserVectorRow:0}]),/row\/ID mismatch/);
});

test('prepared computation pins exact adapter source in addition to atlas bytes',async()=>{
  const bytes=await readFile(new URL('../../lib/geometry/prepared-atlas.mjs',import.meta.url));assert.equal(createHash('sha256').update(bytes).digest('hex'),PREPARED_SOURCE_SHA256);
  const first=atlasFixture(),changed=atlasFixture();changed.manifestSha256='f'.repeat(64);
  assert.notEqual(createAtlasNavigator(first).computationId,createAtlasNavigator(changed).computationId);
});

test('source filters cover unbundled memberships and distinguish context witnesses',()=>{
  const atlas=atlasFixture({largeMembership:true});
  for(const m of atlas.catalog.memberships){m.year=m.unitId==='source-a'?2020:2025;m.lens=m.unitId==='source-a'?'physical_question':'method';m.perspectives=m.unitId==='source-b'?['phenomenology']:[];}
  const nav=createAtlasNavigator(atlas),selector={...nav.initialState.selector,destinationId:'shared'},session=nav.createSession({selector,lens:'method',constraints:{yearMin:2024}}),view=nav.computeView(currentState(session));
  assert.equal(view.atlas.matchingSourceCount,601);assert.equal(view.nodes.find(n=>n.id==='source-a').atlasRole,'context-evidence');assert.equal(view.nodes.find(n=>n.id==='source-b').atlasRole,'matching-source');
  assert.equal(nav.sources('shared',{intent:'derive'}).total,601);assert.equal(nav.sources('shared',{intent:'phenomenology'}).total,1);
  const incomplete=createAtlasNavigator(atlasFixture({largeMembership:true}));assert.throws(()=>incomplete.sources('shared',{constraints:{yearMin:2024}}),/lacks year metadata/);assert.throws(()=>incomplete.sources('shared',{lens:'method'}),/lacks lens metadata/);
});
