import test from 'node:test';
import assert from 'node:assert/strict';
import {renderAtlasPanel} from '../../web/atlas-panel.mjs';
test('private note export survives storage quota failure and accepted reading coverage stays visible',async()=>{
  const originals=Object.fromEntries(['document','localStorage','setTimeout'].map(key=>[key,globalThis[key]])),create=URL.createObjectURL,revoke=URL.revokeObjectURL,all=[],blobs=[];
  class Element{constructor(tag){this.tag=tag;this.children=[];this.handlers={};this.isConnected=true;all.push(this);}append(...nodes){this.children.push(...nodes);}replaceChildren(...nodes){this.children=nodes;}insertBefore(node){this.children.push(node);}after(){}setAttribute(){}addEventListener(type,handler){this.handlers[type]=handler;}click(){this.handlers.click?.();}}
  const elements=new Map([['atlas-panel',new Element('section')],['full-question-details',new Element('details')],['full-question-text',new Element('p')]]);
  try{
    globalThis.document={createElement:tag=>new Element(tag),getElementById:id=>elements.get(id),querySelector:()=>new Element('section')};
    globalThis.localStorage={getItem:()=>null,setItem:()=>{throw new Error('QuotaExceededError');}};globalThis.setTimeout=()=>0;URL.createObjectURL=blob=>{blobs.push(blob);return 'blob:note-test';};URL.revokeObjectURL=()=>{};
    const errors=[],selector={kind:'atlas-destination',atlasId:'quota-test',atlasVersion:'v1',destinationId:'q'},coverage='Only descriptions were read; the section 4 derivation remains unread.';
    renderAtlasPanel({capsule:{snapshot:{view:{atlas:{selector,destination:{summary:'Synthetic test',scope:{},scientificStatus:'test',placementStatus:'test',readingCoverage:coverage,sourceHomeStatus:'unresolved',sourceHomeReason:'Two distinct regimes remain unreconciled.'},membershipCount:0,membershipNotice:'Test',connectionCount:0,connections:[]}}}},navigator:{},onError:error=>errors.push(error)});
    assert.ok(all.some(element=>element.textContent===coverage));
    assert.ok(all.some(element=>element.textContent==='More source context is needed for precise topic placement.'));
    assert.ok(all.some(element=>element.textContent==='Two distinct regimes remain unreconciled.'));
    const textarea=all.find(element=>element.tag==='textarea');textarea.value='Private work retained despite quota failure';textarea.handlers.input();all.find(element=>element.textContent==='Export note').click();
    assert.deepEqual(errors,[]);assert.equal(blobs.length,1);const note=JSON.parse(await blobs[0].text());assert.equal(note.text,textarea.value);assert.deepEqual(note.target,selector);assert.equal(all.find(element=>element.tag==='a').download,'eigenquestions-work-note.json');
  }finally{for(const [key,value]of Object.entries(originals)){if(value===undefined)delete globalThis[key];else globalThis[key]=value;}URL.createObjectURL=create;URL.revokeObjectURL=revoke;}
});
