import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,cp,mkdir,writeFile,readFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
const wrapper=new URL('./read.mjs',import.meta.url),root=new URL('../../../../',import.meta.url),sha=x=>createHash('sha256').update(x).digest('hex');
test('read-only adapter uses the real prepared runtime/CLI, exposes exact scopes, and rejects mutations and changed pins',async()=>{
 const temp=await mkdtemp(path.join(tmpdir(),'atlas-preholdout-test-'));
 try{
  const app=path.join(temp,'app'),atlas=path.join(app,'atlas');await mkdir(atlas,{recursive:true});await cp(new URL('lib',root),path.join(app,'lib'),{recursive:true});await cp(new URL('bin',root),path.join(app,'bin'),{recursive:true});
  const catalog={destinations:[{id:'test-q',kind:'question',title:'Synthetic scoped destination',question:'Synthetic test question',summary:'Test scaffold only.',scope:{assumptions:['Synthetic condition']},evidenceIds:['source-test'],scientificStatus:'test',placementStatus:'test',provenance:{test:true}}],sources:[{id:'source-test',paperId:'synthetic',title:'Synthetic source',evidence:{text:'Synthetic test description',lens:'physical_question'}}],memberships:[{destinationId:'test-q',unitId:'source-test',weight:1,lens:'physical_question',role:'on'}],relations:[]};
  const body=JSON.stringify(catalog);await writeFile(path.join(atlas,'catalog.json'),body);
  const manifest={schemaVersion:'1.0.0',kind:'eigenquestions-atlas',atlasId:'synthetic',atlasVersion:'v1',corpusId:'synthetic',corpusContentHash:'a'.repeat(64),entryDestinationId:'test-q',scope:{description:'Synthetic mechanics fixture; no scientific counts inferred.',deliveryState:'partial_pre_holdout_candidate',sourceAccountingComplete:false,reservedQuestionCount:43},files:{catalog:{path:'catalog.json',sha256:sha(body)}}};const manifestBody=JSON.stringify(manifest);await writeFile(path.join(atlas,'manifest.json'),manifestBody);
  const access=path.join(temp,'access.json');await writeFile(access,JSON.stringify({kind:'q025-preholdout-readonly-access',application:app,atlas,manifestSha256:sha(manifestBody),runtimeCommit:'synthetic',staticEntry:path.join(atlas,'manifest.json'),publicationStatus:'test only'}));
  const invoke=(...args)=>spawnSync(process.execPath,[wrapper.pathname,access,...args],{encoding:'utf8'}),read=(...args)=>{const result=invoke(...args);assert.equal(result.status,0,result.stderr);return JSON.parse(result.stdout);};
  assert.equal(read('info').result.liveBrowserMutation,false);
  assert.equal(read('search','--query','Synthetic scoped').result[0].id,'test-q');
  const description=read('describe','--destination','test-q');assert.deepEqual(description.result.destination.scope.assumptions,['Synthetic condition']);assert.equal(description.result.selector.destinationId,'test-q');
  assert.equal(read('compute','--destination','test-q').result.view.atlas.destination.id,'test-q');assert.equal(read('sources','--destination','test-q').result.items[0].source.evidence.text,'Synthetic test description');assert.equal(read('connections','--destination','test-q').result.total,0);
  for(const command of ['navigate','action','import','serve','inspect-source','reset'])assert.notEqual(invoke(command).status,0);
  assert.notEqual(invoke('search','--connection','foreign').status,0);
  assert.equal(await readFile(path.join(atlas,'manifest.json'),'utf8'),manifestBody);await writeFile(path.join(atlas,'manifest.json'),manifestBody+' ');assert.match(invoke('info').stderr,/Frozen manifest changed/);
 }finally{await rm(temp,{recursive:true,force:true});}
});
