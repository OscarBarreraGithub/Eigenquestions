import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,writeFile,readFile,copyFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {gzipSync} from 'node:zlib';

test('plain atlas pages resolve bucketed source locators and link optional compressed detail',async()=>{
  const root=await mkdtemp(path.join(tmpdir(),'eigenquestions-static-atlas-'));
  try{
    const unitId='unit:ab'+'0'.repeat(62),directory=path.join(root,'data/atlas/fixture/v1');
    await mkdir(directory,{recursive:true});await mkdir(path.join(root,'scripts'));await mkdir(path.join(root,'web'));await mkdir(path.join(root,'research'));
    await writeFile(path.join(root,'research/private-note.txt'),'Must not be a site asset');await writeFile(path.join(root,'web/index.html'),'<p>Public explorer</p>');
    await copyFile(new URL('../../scripts/build-site.mjs',import.meta.url),path.join(root,'scripts/build-site.mjs'));
    const json=(filename,value)=>writeFile(path.join(directory,filename),JSON.stringify(value));
    await writeFile(path.join(root,'data/atlas/index.json'),JSON.stringify({schemaVersion:'1.0.0',atlases:[{atlasId:'fixture',atlasVersion:'v1',entryDestinationId:'question',title:'Synthetic discovery fixture'}]}));
    await json('manifest.json',{files:{catalog:{path:'catalog.json'},sourceContextIndex:{path:'context-index.json'}}});
    await json('catalog.json',{destinations:[{id:'question',title:'A scoped question',question:'What defines this test?',summary:'Synthetic only.',scope:{assumptions:['Test fixture']},evidenceIds:[unitId],scientificStatus:'test',placementStatus:'test',methods:['A recorded method']}],sources:[{id:unitId,title:'Synthetic paper',sourceUrl:'https://example.org/paper',evidence:{text:'A sourced description'}}],relations:[]});
    await json('context-index.json',{unitIndex:{kind:'unit-hash-prefix',prefixLength:2,shards:{ab:{path:'unit-index-ab.json'}}}});
    await json('unit-index-ab.json',{units:{[unitId]:{shardId:'paper',sourceLocator:{paperId:'paper',pages:[3,4],sourceSha256:'a'.repeat(64)}}},shards:{paper:{path:'paper.json.gz',encoding:'gzip',sha256:'b'.repeat(64)}}});
    await writeFile(path.join(directory,'paper.json.gz'),gzipSync('{}'));
    execFileSync(process.execPath,['scripts/build-site.mjs'],{cwd:root,stdio:'pipe'});
    const html=await readFile(path.join(root,'dist/atlas/fixture/v1/question.html'),'utf8');
    assert.match(html,/A recorded method/);assert.ok(html.includes(unitId));assert.match(html,/Archived source locator/);assert.match(html,/\/data\/atlas\/fixture\/v1\/paper.json.gz/);assert.match(html,/not claim exhaustive literature coverage/);
    await assert.rejects(readFile(path.join(root,'dist/research/private-note.txt')),/ENOENT/);
  }finally{await rm(root,{recursive:true,force:true});}
});
