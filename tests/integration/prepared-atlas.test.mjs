import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile} from 'node:fs/promises';
import {gzipSync} from 'node:zlib';
import {createAtlasNavigator,loadAtlas,validateAtlas,atlasAddress,createAtlasSourceReader,validateSourceContext,createAtlasContextReader} from '../../lib/geometry/prepared-atlas.mjs';
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

test('lookup is explicitly lexical and prepared runtime uses existing shared transitions',async()=>{
  const atlas=atlasFixture(),nav=createAtlasNavigator(atlas),runtime=createRuntime(nav,atlas.manifest.corpusId);
  assert.equal(runtime.search('shared alias')[0].selector.destinationId,'shared');
  assert.equal(runtime.search('alternate alias')[0].matchKind,'title-and-alias-lookup');
  assert.equal(runtime.search('unrepresented wording').length,0);
  assert.equal((await runtime.sources({destinationId:'shared',limit:1})).total,2);assert.equal(runtime.connections({destinationId:'shared'}).total,3);assert.equal((await runtime.context({unitId:'source-a'})).availability,'not-exported');assert.equal(runtime.snapshot().revision,0);
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

test('complete containment requires membership subset; vocabulary parents carry an explicit exemption',()=>{
  const atlas=atlasFixture({largeMembership:true});for(const d of atlas.catalog.destinations)d.membershipStatus='complete';
  assert.throws(()=>validateAtlas(atlas.manifest,atlas.catalog),/child membership escapes parent/);
  for(const id of ['left','right']){const d=atlas.catalog.destinations.find(x=>x.id===id);d.membershipStatus='metadata-only';d.metadataOnly=true;}
  assert.doesNotThrow(()=>validateAtlas(atlas.manifest,atlas.catalog));
});

test('source science preserves exact object endpoints, semantic status and attachment scope',async()=>{
  const atlas=atlasFixture(),context={coverage:{description:'Two synthetic objects only'},sourceObjects:[{id:'claim-a',kind:'claim',paperId:'paper-a',text:'Synthetic claim',evidenceScope:'direct',provenance:{sourceSha256:'a'.repeat(64)}},{id:'method-b',kind:'method',paperId:'paper-b',text:'Synthetic method',evidenceScope:'inherited',provenance:{sourceSha256:'b'.repeat(64)}}],sourceRelations:[{id:'source-use',source:'claim-a',target:'method-b',type:'uses_method',semanticStatus:'reviewed_scoped',premises:['Only the declared synthetic limit'],provenance:{review:'fixture'}}],sourceAttachments:[{unitId:'source-a',scope:'shared_extraction_window_context',objectIds:['claim-a','method-b'],relationIds:['source-use']}],sourceAssessments:[]};
  const body=JSON.stringify(context),index={schemaVersion:'1.0.0',kind:'eigenquestions-source-context-index',coverage:{description:'Fixture coverage'},units:{'source-a':{path:'context-0.json',sha256:createHash('sha256').update(body).digest('hex')}}},indexBody=JSON.stringify(index);
  atlas.manifest.files.sourceContextIndex={path:'source-context-index.json',sha256:createHash('sha256').update(indexBody).digest('hex')};
  const reader=createAtlasContextReader(atlas,{readText:async filename=>filename.endsWith('source-context-index.json')?indexBody:body});
  const result=await reader('source-a');assert.equal(result.sourceRelations[0].source,'claim-a');assert.equal(result.sourceAttachments[0].scope,'shared_extraction_window_context');assert.deepEqual(result.sourceRelations[0].premises,['Only the declared synthetic limit']);
  const compressed=gzipSync(body),gzipIndex=structuredClone(index);gzipIndex.units['source-a']={path:'context-0.json.gz',encoding:'gzip',uncompressedBytes:Buffer.byteLength(body),sha256:createHash('sha256').update(compressed).digest('hex')};const gzipIndexBody=JSON.stringify(gzipIndex),gzipAtlas=structuredClone(atlas);gzipAtlas.manifest.files.sourceContextIndex.sha256=createHash('sha256').update(gzipIndexBody).digest('hex');
  const gzipResult=await createAtlasContextReader(gzipAtlas,{readText:async()=>gzipIndexBody,readBinary:async()=>compressed})('source-a');assert.equal(gzipResult.sourceContextFile.encoding,'gzip');assert.deepEqual({...gzipResult,sourceContextFile:undefined},{...result,sourceContextFile:undefined});
  await assert.rejects(createAtlasContextReader(gzipAtlas,{readText:async()=>gzipIndexBody,readBinary:async()=>new Uint8Array([1,2,3])})('source-a'),/checksum mismatch/);
  assert.equal((await reader('unrepresented-unit')).availability,'not-exported');assert.match((await reader('unrepresented-unit')).notice,/does not establish/);
  const bad=structuredClone(context);bad.sourceRelations[0].source='root';assert.throws(()=>validateSourceContext(bad),/endpoint/);bad.sourceRelations[0].source='claim-a';delete bad.sourceRelations[0].semanticStatus;assert.throws(()=>validateSourceContext(bad),/semanticStatus/);
  assert.equal(atlas.catalog.relations.length,5,'source-science relation never becomes a destination arrow');
});

test('same-paper methods remain contextual associations, outside primary containment and USING',()=>{
  const atlas=atlasFixture(),question=atlas.catalog.destinations.find(d=>d.id==='shared');question.membershipStatus='complete';
  const methodId='context-method';atlas.catalog.sources.push({id:methodId,paperId:'source-a',title:'Synthetic method from the same paper',year:2024,evidence:{text:'Contextual method; applicability is not established.',lens:'method'}});
  atlas.catalog.memberships.push({destinationId:'shared',unitId:methodId,weight:1,year:2024,lens:'method',role:'evidence',associationScope:'same_paper_context',placementStatus:'context_only',paperId:'source-a',associationProvenance:{kind:'same_paper_join',questionUnitIds:['source-a']}});
  // Complete parent contains the primary question units; contextual associations
  // are not silently added to the scientific containment set.
  for(const id of ['left','right'])atlas.catalog.destinations.find(d=>d.id===id).membershipStatus='complete';
  const nav=createAtlasNavigator(atlas),selector={...nav.initialState.selector,destinationId:'shared'};
  assert.equal(nav.sources('shared').total,2);assert.equal(nav.sources('shared',{includeContext:true}).contextTotal,1);
  assert.equal(nav.sources('shared',{lens:'method'}).primaryTotal,0);assert.equal(nav.sources('shared',{intent:'derive'}).contextTotal,1);
  assert.equal(nav.sources('shared',{lens:'method',workRelation:'using'}).total,0);
  const view=nav.computeView(currentState(nav.createSession({selector,lens:'method'})));assert.equal(view.atlas.membershipCount,2);assert.equal(view.atlas.contextMembershipCount,1);assert.equal(view.atlas.matchingSourceCount,0);assert.equal(view.atlas.matchingContextCount,1);
  const method=view.nodes.find(n=>n.id===methodId);assert.equal(method.atlasRole,'context-evidence');assert.equal(method.atlasContextScope,'same_paper_context');
  const bad=structuredClone(atlas);bad.catalog.memberships.at(-1).role='using';assert.throws(()=>validateAtlas(bad.manifest,bad.catalog),/contextual methods require/);
});


test('typed contributions stay outside membership, navigation and USING, with exact role and scope binding',()=>{
  const atlas=atlasFixture(),record=atlas.catalog.destinations.find(d=>d.id==='shared');
  const source={...atlas.catalog.sources[0],id:'source-c'};atlas.catalog.sources.push(source);
  const baseline=createAtlasNavigator(structuredClone(atlas)),selector={...baseline.initialState.selector,destinationId:'shared'};
  const row={unitId:'source-c',destinationId:'shared',role:'method',basis:'description_checked',evidenceRefs:['fixture:source-c'],decisionId:'decision:fixture',scopeContentSha256:'c'.repeat(64),browserVectorRow:2,sourceRow:2,paperId:source.paperId,lens:'physical_question',contributionStatus:'accepted_typed_contribution',provenance:{doesNotAssertDirectHome:true,doesNotAssertEquivalence:true,doesNotAssertMethodApplicability:true}};
  record.sourceContributions=[row];const nav=createAtlasNavigator(atlas),state=currentState(nav.createSession({selector})),view=nav.computeView(state);
  assert.equal(view.atlas.membershipCount,2);assert.equal(nav.sources('shared',{workRelation:'using'}).total,1);assert.deepEqual(nav.connections('shared'),baseline.connections('shared'));assert.ok(!view.nodes.some(n=>n.id==='source-c'));assert.deepEqual(view.atlas.destination.sourceContributions,[row]);createCapsule({session:nav.createSession({selector}),view});
  for(const change of [{role:'using'},{workRelation:'using'},{destinationId:'left'},{scopeContentSha256:'not-a-hash'},{provenance:{doesNotAssertMethodApplicability:false}}]){const bad=structuredClone(atlas);Object.assign(bad.catalog.destinations.find(d=>d.id==='shared').sourceContributions[0],change);assert.throws(()=>validateAtlas(bad.manifest,bad.catalog),/contribution|scope binding/);}
});
