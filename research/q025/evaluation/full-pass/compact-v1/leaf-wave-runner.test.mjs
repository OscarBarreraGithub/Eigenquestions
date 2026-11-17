import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,writeFileSync,readFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join,resolve} from 'node:path';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {materializeChallenge,verifyPrepared} from './leaf-wave-runner.mjs';
const hash=x=>createHash('sha256').update(x).digest('hex');
function setup(){
 const dir=mkdtempSync(join(tmpdir(),'q025-leaf-challenge-'));const previous=join(dir,'jobs','fixture-proposal'),current=join(dir,'jobs','fixture-challenge');mkdirSync(previous,{recursive:true});mkdirSync(current,{recursive:true});
 const py=spawnSync('python3',['-c',"import sys,json;sys.path.insert(0,'research/q025/evaluation/full-pass/compact-v1');from test_pipeline import fixture;o,p,r=fixture();print(json.dumps({'original':o,'reply':r}))"],{cwd:resolve(import.meta.dirname,'../../../../..'),encoding:'utf8'});if(py.status!==0)throw Error(py.stderr);const f=JSON.parse(py.stdout);const original=join(dir,'source.json'),raw=JSON.stringify(f.reply);writeFileSync(original,JSON.stringify(f.original));writeFileSync(join(previous,'reply.raw.txt'),raw);writeFileSync(join(previous,'reply.json'),JSON.stringify(f.reply,null,2));writeFileSync(join(previous,'receipt.json'),JSON.stringify({status:'complete',toolUseAttempted:false,replySha256:hash(raw)}));const req={jobId:'fixture-challenge',familyId:'test',stage:'challenge',dependsOn:'fixture-proposal',originalPacketPath:original,originalPacketSha256:hash(readFileSync(original))};writeFileSync(join(current,'request.json'),JSON.stringify(req));return {dir,current,previous,req};
}
test('materializes independent challenge with exact dependency and explicit family review',()=>{const x=setup();try{const m=materializeChallenge(x.current,x.req,x.dir),p=JSON.parse(readFileSync(m.packetPath));assert.equal(p.stage,'challenge');assert.equal(p.units.length,2);assert.deepEqual(p.priorCards.map(c=>c.id),['p0','r']);assert.equal(m.request.priorReceiptSha256,hash(readFileSync(join(x.previous,'receipt.json'))));assert.equal(m.request.packetSha256,hash(readFileSync(m.packetPath)));assert.throws(()=>materializeChallenge(x.current,x.req,x.dir),/already materialized/);}finally{rmSync(x.dir,{recursive:true,force:true});}});
test('rejects altered raw proposal before compilation',()=>{const x=setup();try{writeFileSync(join(x.previous,'reply.raw.txt'),'{}');assert.throws(()=>materializeChallenge(x.current,x.req,x.dir),/raw reply changed/);}finally{rmSync(x.dir,{recursive:true,force:true});}});
test('rejects failed proposer without model call',()=>{const x=setup();try{writeFileSync(join(x.previous,'receipt.json'),JSON.stringify({status:'failed'}));assert.throws(()=>materializeChallenge(x.current,x.req,x.dir),/not valid/);}finally{rmSync(x.dir,{recursive:true,force:true});}});
test('complete372-job preparation preserves all dependencies',()=>{const p=verifyPrepared();assert.equal(p.jobs.length,372);assert.equal(p.jobs.filter(x=>x.dependsOn).length,186);});
