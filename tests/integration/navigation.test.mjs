import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,writeFile,readFile,rm} from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {spawn} from 'node:child_process';
import {createInterface} from 'node:readline';
import {loadLocalNavigator,createRuntime,bridgeCall,PROJECT_ROOT} from '../../lib/protocol/runtime.mjs';
import {startBridge} from '../../lib/protocol/bridge.mjs';
import {createSession,currentState,applyAction,exportSession,importSession} from '../../lib/protocol/session.mjs';
import {createNavigator} from '../../lib/geometry/index.mjs';

let loaded;
const data=()=>loaded??=(loadLocalNavigator());
const signature=view=>view.nodes.map(n=>n.id).join('|');
const positions=view=>JSON.stringify(view.nodes.map(n=>[n.id,n.x,n.y]));
const textOf=view=>view.nodes.slice(0,12).map(n=>`${n.title} ${n.evidence.text}`).join(' ');
function meaningful(view){
  assert.ok(view.nodes.length>0);assert.ok(view.directions.length>=3&&view.directions.length<=6);
  assert.ok(view.nodes.every(n=>Number.isFinite(n.x)&&Number.isFinite(n.y)&&Number.isFinite(n.residual)));
  assert.ok(view.directions.every(d=>d.evidenceIds.length&&d.seedIds.length));
  assert.equal(view.diagnostics.globalReentry,true);
}
test('owner journey changes real geometry, preserves multi-turn context and replays',async()=>{
  const {corpus,navigator}=await data();const runtime=createRuntime(navigator,corpus.manifest.corpusId);
  const kk=runtime.action({type:'navigate',query:'KK towers'});meaningful(kk.view);
  const dm=runtime.action({type:'refine',query:'what if they are dark matter?',intent:'phenomenology'});meaningful(dm.view);
  assert.deepEqual(currentState(dm.session).focusIds,[...kk.view.nodes.slice(0,5).map(n=>n.id)].sort());
  assert.match(textOf(dm.view),/dark dimension/i);assert.match(textOf(dm.view),/Kaluza.Klein|KK|graviton/i);
  assert.notEqual(signature(kk.view),signature(dm.view));assert.notEqual(positions(kk.view),positions(dm.view));
  const decay=runtime.action({type:'refine',query:'how do they decay?',intent:'phenomenology'});meaningful(decay.view);
  assert.deepEqual(currentState(decay.session).focusIds,[...dm.view.nodes.slice(0,5).map(n=>n.id)].sort());
  assert.match(textOf(decay.view),/decay/i);assert.match(textOf(decay.view),/dark dimension/i);
  const dark=runtime.action({type:'refine',query:'Dark Dimension swampland dark matter'});meaningful(dark.view);
  assert.match(textOf(dark.view),/dark dimension/i);
  const beforeIds=new Set(kk.view.nodes.map(n=>n.id));assert.ok(dm.view.nodes.some(n=>!beforeIds.has(n.id)),'context can re-enter globally outside earlier chart');
  const back=runtime.action({type:'back'});assert.deepEqual(back.view,decay.view);
  const restored=importSession(JSON.parse(JSON.stringify(runtime.export())),{corpusId:corpus.manifest.corpusId});
  assert.deepEqual(navigator.computeView(currentState(restored)),decay.view);
  const replay=runtime.action({type:'replay',index:1});assert.deepEqual(replay.view,kk.view);
  const branch=runtime.action({type:'pivot',query:'black hole evaporation'});assert.equal(branch.session.states.length,3);assert.deepEqual(currentState(branch.session).focusIds,[]);
});
test('derive, phenomenology, recent ON and recent USING are distinct computations',async()=>{
  const {corpus,navigator}=await data();const state=createSession({computationId:navigator.computationId,corpusId:corpus.manifest.corpusId,query:'KK towers'});
  const views={};for(const [name,intent,workRelation]of [['derive','derive','on'],['phenomenology','phenomenology','on'],['on','recent','on'],['using','recent','using']])views[name]=applyAction(state,{type:'navigate',intent,workRelation},navigator).view;
  for(const view of Object.values(views))meaningful(view);
  assert.notEqual(signature(views.derive),signature(views.phenomenology));
  assert.notEqual(signature(views.on),signature(views.using));assert.notEqual(positions(views.on),positions(views.using));
  assert.notDeepEqual(views.on.chart.basis,views.using.chart.basis);
  assert.ok(views.on.warnings.some(w=>/frozen|corpus/i.test(w)));
  assert.ok(views.on.nodes.some(n=>n.retrieval.workRelation.kind==='on'));
  assert.ok(views.using.nodes.some(n=>n.retrieval.workRelation.kind==='using'));
  const shorthand=applyAction(state,{type:'navigate',intent:'using'},navigator);
  assert.equal(currentState(shorthand.session).workRelation,'using');
  assert.ok(shorthand.view.nodes.some(n=>n.retrieval.workRelation.kind==='using'));
});
test('held-out evaporation → information → islands route re-enters outside original neighborhood',async()=>{
  const {corpus,navigator}=await data();const runtime=createRuntime(navigator,corpus.manifest.corpusId);
  const evaporation=runtime.action({type:'navigate',query:'black hole evaporation'});
  const information=runtime.action({type:'refine',query:'the information paradox'});
  const islands=runtime.action({type:'refine',query:'islands and replica wormholes',intent:'derive'});
  [evaporation,information,islands].forEach(x=>meaningful(x.view));
  assert.match(textOf(information.view),/information paradox/i);
  assert.match(textOf(islands.view),/replica wormhole|island/i);
  const startIds=new Set(evaporation.view.nodes.map(n=>n.id));assert.ok(islands.view.nodes.some(n=>!startIds.has(n.id)));
  assert.notEqual(positions(evaporation.view),positions(islands.view));
  assert.deepEqual(runtime.action({type:'back'}).view,information.view);
});
test('empty, unsupported, stale and malformed states fail honestly',async()=>{
  const {corpus,navigator}=await data();const session=createSession({computationId:navigator.computationId,corpusId:corpus.manifest.corpusId});
  const empty=navigator.computeView(currentState(session));assert.equal(empty.nodes.length,0);assert.ok(empty.warnings.length);
  const unsupported=applyAction(session,{type:'pivot',query:'flibbertigibbetquux'},navigator).view;assert.equal(unsupported.nodes.length,0);assert.ok(unsupported.warnings.length);
  assert.throws(()=>applyAction(session,{type:'select',directionId:'invented'},navigator),/absent/);
  assert.throws(()=>applyAction(session,{type:'navigate',intent:'prove'},navigator),/Unsupported intent/);
  assert.throws(()=>applyAction(session,{type:'navigate',constraints:{yearMin:2026,yearMax:2000}},navigator),/exceeds/);
  assert.throws(()=>importSession(exportSession(session),{corpusId:'stale'}),/Corpus mismatch/);
  assert.throws(()=>importSession(exportSession(session),{computationId:'changed-math'}),/Computation mismatch/);
  const malformed=exportSession(session);malformed.session.states[0].query='tampered';assert.throws(()=>importSession(malformed),/State ID/);
  assert.throws(()=>createSession(JSON.parse('{"corpusId":"x","__proto__":{}}')),/Unknown/);
});
test('same engine/session contract works on a separate small subfield fixture',()=>{
  const vectors=new Float32Array([1,0,0, .8,.6,0, 0,.8,.6, 0,0,1]);
  const units=['phonon scattering','phonon thermal conductivity','electron phonon coupling','superconducting pairing'].map((text,i)=>({id:`fixture:${i}`,paperId:`p${i}`,lens:i%2?'method':'physical_question',text,vectorRow:i,evidence:{kind:'test-fixture',claimStatus:'synthetic acceptance fixture; no physics claim'}}));
  const corpus={manifest:{schemaVersion:'1.0.0',corpusId:'condensed-matter-fixture',encoder:{dimensions:3},scope:{unitCount:4,latestYear:2024,recentMeaning:'test fixture'},snapshotDate:'2024-01-01'},units,vectors,papers:units.map((u,i)=>({id:u.paperId,title:u.text,year:2020+i,url:`https://example.org/${i}`})),adjacency:[[[1,.8]],[[0,.8],[2,.7]],[[1,.7],[3,.6]],[[2,.6]]]};
  const navigator=createNavigator(corpus),runtime=createRuntime(navigator,corpus.manifest.corpusId);
  const view=runtime.action({type:'navigate',query:'phonon'}).view;assert.ok(view.nodes.length);assert.equal(view.chart.dimension,3);assert.equal(view.corpusId,corpus.manifest.corpusId);
  assert.deepEqual(navigator.computeView(currentState(importSession(runtime.export()))),view);
});
test('MCP stdio action reaches bridge SSE and origin/session checks reject outsiders',async()=>{
  const {corpus,navigator}=await data(),directory=await mkdtemp(path.join(os.tmpdir(),'eigenquestions-test-'));
  await writeFile(path.join(directory,'index.html'),'<!doctype html><title>integration fixture</title>');
  const runtime=createRuntime(navigator,corpus.manifest.corpusId),bridge=await startBridge({runtime,staticDir:directory,port:0});
  const connection={url:bridge.url,token:bridge.token},connectionFile=path.join(directory,'connection.json');await writeFile(connectionFile,JSON.stringify(connection));
  const child=spawn(process.execPath,[path.join(PROJECT_ROOT,'bin/mcp-navigator.mjs'),'--connection',connectionFile],{stdio:['pipe','pipe','pipe']});
  const pending=new Map();let sequence=0;const lines=createInterface({input:child.stdout});
  lines.on('line',line=>{const value=JSON.parse(line);pending.get(value.id)?.(value);pending.delete(value.id);});
  const rpc=(method,params)=>new Promise((resolve,reject)=>{const id=++sequence;const timeout=setTimeout(()=>reject(new Error('MCP timeout')),10000);pending.set(id,value=>{clearTimeout(timeout);resolve(value);});child.stdin.write(JSON.stringify({jsonrpc:'2.0',id,method,params})+'\n');});
  let reader;
  try{
    assert.equal((await fetch(new URL('/api/session',bridge.url))).status,401);
    assert.equal((await fetch(new URL('/api/session',bridge.url),{headers:{Origin:'https://untrusted.example',Authorization:`Bearer ${bridge.token}`}})).status,403);
    const publicResponse=await fetch(new URL('/api/session',bridge.url),{headers:{Origin:'https://eigenquestions.com',Authorization:`Bearer ${bridge.token}`}});
    assert.equal(publicResponse.status,200);assert.equal(publicResponse.headers.get('access-control-allow-origin'),'https://eigenquestions.com');
    const preflight=await fetch(new URL('/api/action',bridge.url),{method:'OPTIONS',headers:{Origin:'https://eigenquestions.com','Access-Control-Request-Private-Network':'true'}});assert.equal(preflight.status,204);assert.equal(preflight.headers.get('access-control-allow-private-network'),'true');
    const events=await fetch(new URL(`/api/events?token=${bridge.token}`,bridge.url));reader=events.body.getReader();await reader.read();
    const init=await rpc('initialize',{protocolVersion:'2025-06-18',clientInfo:{name:'integration',version:'1'}});assert.equal(init.result.serverInfo.name,'eigenquestions-navigator');
    assert.equal((await rpc('tools/list',{})).result.tools.length,6);
    const response=await rpc('tools/call',{name:'navigator_navigate',arguments:{type:'navigate',query:'KK towers'}});assert.equal(response.result.isError,false);
    let streamText='';while(!streamText.includes('\n\n')){const chunk=await reader.read();streamText+=new TextDecoder().decode(chunk.value);}
    const event=JSON.parse(streamText.split('data: ')[1].split('\n\n')[0]);assert.equal(event.revision,1);assert.equal(event.view.query,'KK towers');
    const observed=await bridgeCall(connection,'/api/session');assert.deepEqual(observed.view,event.view);assert.equal(response.result.structuredContent.state.id,event.view.stateId);
    assert.equal(observed.browserStatus.acknowledgedCurrent,false);
    const acknowledgement=await bridgeCall(connection,'/api/viewer',{viewerId:'integration-viewer',stateId:event.view.stateId,revision:1});assert.equal(acknowledgement.acknowledgedCurrent,true);
    assert.equal((await bridgeCall(connection,'/api/session')).browserStatus.lastRenderedStateId,event.view.stateId);
    const exported=await bridgeCall(connection,'/api/export');assert.equal(exported.kind,'eigenquestions-session');assert.equal(JSON.stringify(exported).includes(bridge.token),false);
    const bad=await rpc('tools/call',{name:'navigator_navigate',arguments:{type:'select',directionId:'stale'}});assert.equal(bad.result.isError,true);assert.equal((await bridgeCall(connection,'/api/session')).revision,1);
  }finally{await reader?.cancel();child.stdin.end();child.kill();lines.close();await bridge.close();await rm(directory,{recursive:true,force:true});}
});
