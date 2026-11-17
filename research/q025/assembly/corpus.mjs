import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {join} from 'node:path';
import {gunzipSync} from 'node:zlib';

export const sha256 = bytes => createHash('sha256').update(bytes).digest('hex');
export async function readPinnedJson(path, expected) {
  const bytes=await readFile(path),hash=sha256(bytes);
  if(expected&&hash!==expected)throw new Error(`Input checksum mismatch: ${path}`);
  return {value:JSON.parse(path.endsWith('.gz')?gunzipSync(bytes):bytes),sha256:hash,bytes:bytes.length,path};
}
export async function loadFrozenCorpus(directory) {
  const manifestInput=await readPinnedJson(join(directory,'manifest.json')),manifest=manifestInput.value;
  const p=await readPinnedJson(join(directory,manifest.files.papers.path),manifest.files.papers.sha256);
  const papers=new Map(p.value.map(x=>[x.id,x])),units=[],inputs=[manifestInput,p];
  for(const descriptor of manifest.files.units){
    if(descriptor.start!==units.length)throw new Error('Frozen unit shards are not contiguous');
    const input=await readPinnedJson(join(directory,descriptor.path),descriptor.sha256);inputs.push(input);
    if(input.value.length!==descriptor.count)throw new Error('Frozen shard row count changed');
    for(const [offset,unit] of input.value.entries()){
      const browserVectorRow=descriptor.start+offset;
      if(unit.vectorRow!==browserVectorRow)throw new Error(`Frozen row mismatch ${unit.id}`);
      const layer=manifest.layers[unit.lens];if(!layer||browserVectorRow<layer.start||browserVectorRow>=layer.start+layer.count)throw new Error('Unit is outside its declared lens rows');
      if(!papers.has(unit.paperId))throw new Error(`Unit paper absent ${unit.id}`);
      if(sha256(Buffer.from(unit.text))!==unit.evidence.textSha256)throw new Error(`Frozen text mismatch ${unit.id}`);
      units.push({...unit,browserVectorRow,sourceRow:browserVectorRow-manifest.layers[unit.lens].start});
    }
  }
  if(new Set(units.map(u=>u.id)).size!==units.length)throw new Error('Duplicate frozen unit ID');
  return {manifest,papers,units,unitMap:new Map(units.map(u=>[u.id,u])),inputs:inputs.map(({value,...descriptor})=>descriptor)};
}
export function hydrateSources(corpus,unitIds=corpus.units.map(u=>u.id)) {
  return unitIds.map(id=>{
    const u=corpus.unitMap.get(id);if(!u)throw new Error(`Unknown frozen source ${id}`);
    const p=corpus.papers.get(u.paperId);
    return {id:u.id,paperId:u.paperId,title:p.title,sourceUrl:p.url,year:p.year,evidence:{...u.evidence,id:u.id,text:u.text,lens:u.lens,date:p.date}};
  });
}
