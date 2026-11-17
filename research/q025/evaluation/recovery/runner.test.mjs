import test from 'node:test';import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';import {mkdtempSync,readFileSync,rmSync} from 'node:fs';import {tmpdir} from 'node:os';import {dirname,resolve,join} from 'node:path';import {fileURLToPath} from 'node:url';
import {persistAgentDelta,validateReply,verifyPrepared} from './runner.mjs';
const here=dirname(fileURLToPath(import.meta.url));
const fixture=()=>JSON.parse(spawnSync('python3',['-c','import json;from test_compact import fixture;p,r=fixture();print(json.dumps({"packet":p,"reply":r}))'],{cwd:here,encoding:'utf8'}).stdout);
test('compact validator accepts reused card and two distinct fine singletons',()=>{const {packet,reply}=fixture();assert.equal(validateReply(reply,packet,{familyId:'test',stage:'challenge'}),true);});
test('actual validator rejects missing records despite valid cards',()=>{const {packet,reply}=fixture();reply.units=[];assert.throws(()=>validateReply(reply,packet,{familyId:'test',stage:'challenge'}),/missing\/duplicate unit coverage/);});
test('streamed partial scientific text is retained with bounded overflow',()=>{const d=mkdtempSync(join(tmpdir(),'q025-stream-'));try{const j={dir:d,req:{maxOutputCharacters:20},characters:0};persistAgentDelta(j,'{\"partial\":');persistAgentDelta(j,'x'.repeat(10000));const text=readFileSync(resolve(d,'reply.stream.raw.txt'),'utf8');assert.ok(text.startsWith('{\"partial\":'));assert.equal(text.length,8212);assert.equal(j.streamTruncated,true);assert.equal(j.characters,10011);}finally{rmSync(d,{recursive:true,force:true});}});
test('one pinned independent recovery challenge verifies without model turn',()=>assert.equal(verifyPrepared().jobs.length,1));
