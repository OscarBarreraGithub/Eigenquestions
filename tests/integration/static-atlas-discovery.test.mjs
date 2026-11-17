import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,writeFile,readFile,copyFile,rm,cp} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {gzipSync} from 'node:zlib';

test('plain atlas pages resolve bucketed source locators and link optional compressed detail',async()=>{
  const root=await mkdtemp(path.join(tmpdir(),'eigenquestions-static-atlas-'));
  try{
    const unitId='unit:ab'+'0'.repeat(62),directory=path.join(root,'data/atlas/fixture/v1');
    await mkdir(directory,{recursive:true});await mkdir(path.join(root,'scripts'));await mkdir(path.join(root,'web'));await mkdir(path.join(root,'research'));
    await writeFile(path.join(root,'research/private-note.txt'),'Must not be a site asset');await writeFile(path.join(root,'web/index.html'),'<p>Public explorer</p>');
    await copyFile(new URL('../../scripts/build-site.mjs',import.meta.url),path.join(root,'scripts/build-site.mjs'));
    await cp(new URL('../../lib',import.meta.url),path.join(root,'lib'),{recursive:true});
    const json=async(filename,value)=>{const body=JSON.stringify(value);await writeFile(path.join(directory,filename),body);return{path:filename,bytes:Buffer.byteLength(body),sha256:createHash('sha256').update(body).digest('hex')};};
    await writeFile(path.join(root,'data/atlas/index.json'),JSON.stringify({schemaVersion:'1.0.0',atlases:[{atlasId:'fixture',atlasVersion:'v1',entryDestinationId:'question',title:'Synthetic discovery fixture'}]}));
    const catalog={destinations:[{id:'question',kind:'question',title:'A scoped question',question:'What defines this test?',summary:'Synthetic only.',scope:{assumptions:['Test fixture']},evidenceIds:[unitId],scientificStatus:'test',placementStatus:'test',provenance:{test:true},methods:['A recorded method']}],sources:[{id:unitId,paperId:'paper',title:'Synthetic paper',sourceUrl:'https://example.org/paper',evidence:{text:'A sourced description'}}],memberships:[],relations:[]};
    await json('catalog.json',catalog);
    const compressed=gzipSync('{}');await writeFile(path.join(directory,'paper.json.gz'),compressed);
    const paperFile={path:'paper.json.gz',encoding:'gzip',bytes:compressed.length,sha256:createHash('sha256').update(compressed).digest('hex')};
    const bucket=await json('unit-index-ab.json',{units:{[unitId]:{shardId:'paper',sourceLocator:{paperId:'paper',pages:[3,4],sourceSha256:'a'.repeat(64)}}},shards:{paper:paperFile}});
    const contextFile=await json('context-index.json',{unitIndex:{kind:'unit-hash-prefix',prefixLength:2,shards:{ab:bucket}}});
    await json('manifest.json',{schemaVersion:'1.0.0',kind:'eigenquestions-atlas',atlasId:'fixture',atlasVersion:'v1',corpusId:'fixture-corpus',corpusContentHash:'a'.repeat(64),entryDestinationId:'question',scope:{description:'Synthetic test'},files:{catalog:{path:'catalog.json',sha256:createHash('sha256').update(JSON.stringify(catalog)).digest('hex')},sourceContextIndex:contextFile}});
    execFileSync(process.execPath,['scripts/build-site.mjs'],{cwd:root,stdio:'pipe'});
    const html=await readFile(path.join(root,'dist/atlas/fixture/v1/question.html'),'utf8');
    assert.match(html,/A recorded method/);assert.ok(html.includes(unitId));assert.match(html,/Archived source locator/);assert.match(html,/\/data\/atlas\/fixture\/v1\/paper.json.gz/);assert.match(html,/not claim exhaustive literature coverage/);
    await assert.rejects(readFile(path.join(root,'dist/research/private-note.txt')),/ENOENT/);
    await rm(path.join(directory,'unit-index-ab.json'));assert.throws(()=>execFileSync(process.execPath,['scripts/build-site.mjs'],{cwd:root,stdio:'pipe'}),/Command failed/);
    await rm(path.join(directory,'manifest.json'));assert.throws(()=>execFileSync(process.execPath,['scripts/build-site.mjs'],{cwd:root,stdio:'pipe'}),/Command failed/);
  }finally{await rm(root,{recursive:true,force:true});}
});
