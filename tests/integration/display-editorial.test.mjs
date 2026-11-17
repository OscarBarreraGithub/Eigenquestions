import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {destinationPresentation,destinationPreview,validateDisplayEditorial} from '../../lib/protocol/display-editorial.mjs';
import {renderAtlasPanel} from '../../web/atlas-panel.mjs';

const examples=JSON.parse(await readFile(new URL('../../research/q025/integration/presentation-v1/examples.json',import.meta.url),'utf8'));
const scientificHash=record=>createHash('sha256').update(JSON.stringify(Object.fromEntries(['kind','title','question','summary','scope','scientificStatus','readingCoverage','evidenceIds'].map(key=>[key,record[key]])))).digest('hex');

test('explicit admitted-record annotations preserve scientific definitions and reading limits',()=>{
  for(const record of examples.records){
    const original=JSON.stringify(record),before=scientificHash(record),presented=destinationPresentation(record);
    assert.equal(before,record.scopeContentSha256);assert.equal(JSON.stringify(record),original);assert.equal(scientificHash(record),before);
    for(const note of record.displayEditorial.relocations){const field=note.path.split('/')[2];assert.ok(!presented.scope[field].includes(note.originalText));assert.ok(presented.notes.some(row=>row.path===note.path&&row.originalText===note.originalText));}
    if(record.displayEditorial.readingLimit){const note=record.displayEditorial.readingLimit;assert.ok(presented.reading.includes(note.text));assert.ok(presented.notes.some(row=>row.originalText===note.originalText));}
    assert.deepEqual(presented.scope.regimes,record.scope.regimes);assert.deepEqual(presented.scope.excludes,record.scope.excludes);
  }
  const unchanged={summary:'Physics',scope:{conventions:[examples.unchangedPhysicsControl.text]}};
  assert.deepEqual(destinationPresentation(unchanged).scope,unchanged.scope);
});

test('stale scope bindings, moved text, source summaries and duplicate paths fail closed',()=>{
  const original=examples.records.find(record=>record.displayEditorial.summary&&record.displayEditorial.relocations.length);
  for(const change of [record=>record.scopeContentSha256='a'.repeat(64),record=>{const [,,field,index]=record.displayEditorial.relocations[0].path.split('/');record.scope[field][index]='Changed physics';},record=>record.summary+=' Changed',record=>record.displayEditorial.origin.artifactPath='../private.json',record=>record.displayEditorial.relocations.push(record.displayEditorial.relocations[0])]){
    const record=structuredClone(original);
    change(record);
    assert.throws(()=>validateDisplayEditorial(record),/Display editorial/);
  }
});

test('browser places workflow history outside physical assumptions in a closed disclosure',()=>{
  const previous={document:globalThis.document,localStorage:globalThis.localStorage},all=[];
  class Element{constructor(tag){this.tag=tag;this.children=[];this.handlers={};this.isConnected=true;all.push(this);}append(...children){this.children.push(...children);}replaceChildren(...children){this.children=children;}insertBefore(child){this.children.push(child);}after(){}setAttribute(){}addEventListener(type,fn){this.handlers[type]=fn;}}
  const elements=new Map([['atlas-panel',new Element('section')],['full-question-details',new Element('details')],['full-question-text',new Element('p')]]);
  try{
    globalThis.document={createElement:tag=>new Element(tag),getElementById:id=>elements.get(id),querySelector:()=>new Element('section')};globalThis.localStorage={getItem:()=>null};
    const record=examples.records.find(row=>row.displayEditorial.readingLimit),selector={kind:'atlas-destination',atlasId:'test',atlasVersion:'v1',destinationId:record.id};
    renderAtlasPanel({capsule:{snapshot:{view:{atlas:{selector,destination:record,membershipCount:0,connectionCount:0,connections:[]}}}},navigator:{},onError:error=>{throw new Error(error);}});
    const text=node=>[node.textContent||'',...node.children.map(text)].join('\n');
    const history=all.find(node=>node.tag==='details'&&node.children[0]?.textContent==='Reading and record history');
    assert.ok(history);assert.notEqual(history.open,true);assert.ok(text(history).includes(record.displayEditorial.relocations[0].originalText));
    const scope=all.find(node=>node.tag==='details'&&node.children[0]?.textContent==='Scope, assumptions and sources');
    assert.ok(!text(scope).includes(record.displayEditorial.relocations[0].originalText));assert.ok(text(scope).includes(record.displayEditorial.readingLimit.text));
    assert.ok(all.some(node=>node.textContent===record.displayEditorial.summary.text));
  }finally{for(const [key,value]of Object.entries(previous))if(value===undefined)delete globalThis[key];else globalThis[key]=value;}
});

test('compact navigation selects the unchanged scoped question and preserves raw review history',()=>{
  for(const record of examples.records){
    const original=JSON.stringify(record);
    assert.equal(destinationPreview(record).summary,record.question);
    assert.equal(JSON.stringify(record),original);
  }
  assert.equal(destinationPreview({title:'Physics',summary:'Classification vocabulary',metadataOnly:true}).summary,'Classification vocabulary');
  assert.equal(destinationPreview({title:'Exact question title',summary:'Original review history'}).summary,'Exact question title');
});
