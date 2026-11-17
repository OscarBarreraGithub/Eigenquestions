import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,writeFile,readFile,rm} from 'node:fs/promises';
import {spawn} from 'node:child_process';
import {createInterface} from 'node:readline';
import path from 'node:path';
import os from 'node:os';
import {createRuntime,bridgeCall,PROJECT_ROOT} from '../../lib/protocol/runtime.mjs';
import {startBridge} from '../../lib/protocol/bridge.mjs';

function navigator(){return {computationId:'revision-fixture',computeView:state=>({stateId:state.id,corpusId:state.corpusId,computationId:state.computationId,query:state.query,nodes:[],edges:[],directions:[],chart:null})};}
function execute(args){return new Promise((resolve,reject)=>{const child=spawn(process.execPath,args,{stdio:['ignore','pipe','pipe']});let stdout='',stderr='';child.stdout.on('data',x=>stdout+=x);child.stderr.on('data',x=>stderr+=x);child.on('error',reject);child.on('close',code=>resolve({code,stdout,stderr}));});}
test('captured revision zero works; stale actions and imports fail before preparation without changing drafts',async()=>{
 const nav=navigator();let prepared=0;nav.prepareAction=async()=>prepared++;nav.prepareState=async()=>prepared++;
 const runtime=createRuntime(nav,'revision-fixture'),draft={type:'navigate',query:'draft'},saved=runtime.export(),savedBytes=JSON.stringify(saved);
 await runtime.action({type:'navigate',query:'newer'}, {expectedRevision:0});const before=runtime.snapshot(),calls=prepared;
 assert.throws(()=>runtime.action(draft,{expectedRevision:0}),error=>error.code==='revision_conflict'&&error.current.revision===1);
 assert.throws(()=>runtime.import(saved,{expectedRevision:0}),error=>error.code==='revision_conflict');
 assert.equal(prepared,calls);assert.deepEqual(runtime.snapshot(),before);assert.deepEqual(draft,{type:'navigate',query:'draft'});assert.equal(JSON.stringify(saved),savedBytes);
 for(const expectedRevision of [null,-1,0.5,'1',Number.MAX_SAFE_INTEGER+1])assert.throws(()=>runtime.action(draft,{expectedRevision}),/nonnegative safe integer/);
 // Omission is the explicit legacy behavior, not an implicit re-read by the client.
 assert.equal((await runtime.action(draft)).revision,2);
});
test('captured parent also rejects action and import races during asynchronous preparation',async()=>{
 for(const operation of ['action','import']){
  const nav=navigator();let release;const gate=new Promise(resolve=>release=resolve);
  if(operation==='action')nav.prepareAction=async(_,action)=>{if(action.query==='slow')await gate;};else nav.prepareState=async()=>gate;
  const runtime=createRuntime(nav,'revision-fixture'),saved=runtime.export();
  const pending=operation==='action'?runtime.action({type:'navigate',query:'slow'},{expectedRevision:0}):runtime.import(saved,{expectedRevision:0});
  const accepted=await runtime.action({type:'navigate',query:'newer'},{expectedRevision:0});release();
  await assert.rejects(pending,error=>error.code==='revision_conflict'&&error.current.revision===1);
  assert.deepEqual(runtime.snapshot(),accepted);assert.equal(saved.session.states.length,1);
 }
});
test('real CLI and stdio MCP propagate captured parents, return conflict state, and guard import/back/replay',async()=>{
 const directory=await mkdtemp(path.join(os.tmpdir(),'revision-guard-'));await writeFile(path.join(directory,'index.html'),'revision test');
 const runtime=createRuntime(navigator(),'revision-fixture'),bridge=await startBridge({runtime,staticDir:directory,port:0}),connection={url:bridge.url,token:bridge.token};
 const connectionFile=path.join(directory,'connection.json');await writeFile(connectionFile,JSON.stringify(connection));
 const child=spawn(process.execPath,[path.join(PROJECT_ROOT,'bin/mcp-navigator.mjs'),'--connection',connectionFile],{stdio:['pipe','pipe','pipe']}),lines=createInterface({input:child.stdout}),pending=new Map();let seq=0;
 lines.on('line',line=>{const response=JSON.parse(line);pending.get(response.id)?.(response);pending.delete(response.id);});
 const rpc=(name,args)=>new Promise((resolve,reject)=>{const id=++seq,timer=setTimeout(()=>reject(Error('MCP timeout')),10000);pending.set(id,value=>{clearTimeout(timer);resolve(value.result);});child.stdin.write(JSON.stringify({jsonrpc:'2.0',id,method:'tools/call',params:{name,arguments:args}})+'\n');});
 const cli=(...args)=>execute([path.join(PROJECT_ROOT,'bin/navigate.mjs'),...args,'--connection',connectionFile]);
 try{
  const parent=await rpc('navigator_state',{});assert.equal(parent.structuredContent.revision,0);
  const accepted=await rpc('navigator_navigate',{type:'navigate',query:'first',expectedRevision:0});assert.equal(accepted.structuredContent.revision,1);
  const captured=accepted.structuredContent.revision,saved=runtime.export(),importFile=path.join(directory,'draft.json');await writeFile(importFile,JSON.stringify(saved));
  const external=await cli('navigate','--query','newer','--expected-revision','1');assert.equal(external.code,0);assert.equal(JSON.parse(external.stdout).revision,2);
  for(const [name,args]of [['navigator_navigate',{type:'back',expectedRevision:captured}],['navigator_import',{payload:saved,expectedRevision:captured}]]){
   const result=await rpc(name,args);assert.equal(result.isError,true);assert.equal(result.structuredContent.code,'revision_conflict');assert.equal(result.structuredContent.current.revision,2);assert.equal(result.structuredContent.current.state.query,'newer');
  }
  for(const args of [['back'],['import','--file',importFile]]){const result=await cli(...args,'--expected-revision','1');assert.equal(result.code,1);assert.equal(JSON.parse(result.stderr).code,'revision_conflict');}
  assert.equal(await readFile(importFile,'utf8'),JSON.stringify(saved));assert.equal(runtime.snapshot().revision,2);
  assert.equal((await cli('back','--expected-revision','2')).code,0);
  assert.equal((await cli('replay','--index','2','--expected-revision','3')).code,0);
  const imported=await rpc('navigator_import',{payload:saved,expectedRevision:4});assert.equal(imported.structuredContent.revision,5);
  const invalid=await rpc('navigator_navigate',{type:'reset',expectedRevision:null});assert.equal(invalid.isError,true);assert.equal(runtime.snapshot().revision,5);
  const readOnly=await bridgeCall(connection,'/api/session');assert.equal(readOnly.revision,5);
 }finally{child.stdin.end();child.kill();lines.close();await bridge.close();await rm(directory,{recursive:true,force:true});}
});
test('CLI sends an explicitly captured zero rather than treating it as absent',async()=>{
 const directory=await mkdtemp(path.join(os.tmpdir(),'revision-zero-'));await writeFile(path.join(directory,'index.html'),'revision test');const runtime=createRuntime(navigator(),'revision-fixture'),bridge=await startBridge({runtime,staticDir:directory,port:0});const file=path.join(directory,'connection.json');await writeFile(file,JSON.stringify({url:bridge.url,token:bridge.token}));
 try{const run=()=>execute([path.join(PROJECT_ROOT,'bin/navigate.mjs'),'reset','--expected-revision','0','--connection',file]);assert.equal((await run()).code,0);const stale=await run();assert.equal(stale.code,1);assert.equal(JSON.parse(stale.stderr).current.revision,1);assert.equal(runtime.snapshot().revision,1);}finally{await bridge.close();await rm(directory,{recursive:true,force:true});}
});
