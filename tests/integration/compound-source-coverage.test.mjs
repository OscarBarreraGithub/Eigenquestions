import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile,mkdtemp,mkdir,writeFile,cp,copyFile,rm} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {createAtlasNavigator,createAtlasSourceReader,validateAtlas,sourceCoverage} from '../../lib/geometry/prepared-atlas.mjs';
import {createCapsule,validateCapsule} from '../../lib/protocol/capsule.mjs';
import {createRuntime} from '../../lib/protocol/runtime.mjs';
import {appendSourceCoverage} from '../../web/source-coverage.mjs';
const fixture=JSON.parse(await readFile(new URL('../fixtures/compound-source-coverage.json',import.meta.url),'utf8'));
const hash=value=>createHash('sha256').update(value).digest('hex');
function atlas(){
  const {unit,paper,placements}=fixture;
  const source={id:unit.id,paperId:paper.id,title:paper.title,sourceUrl:paper.url,year:paper.year,evidence:{...unit.evidence,text:unit.text,lens:unit.lens,date:paper.date||paper.year}};
  const memberships=placements.map(p=>({destinationId:p.destinationId,unitId:unit.id,paperId:paper.id,weight:p.allocationWeight,lens:unit.lens,year:paper.year,browserVectorRow:fixture.browserVectorRow,sourceRow:fixture.browserVectorRow,role:'on',placementStatus:p.status,decisionIds:[p.decisionId],placementQualification:p.qualification,coverageMode:p.coverageMode,targetCoverage:p.targetCoverage,wholeQuestionCoveredByEachHome:false}));
  const destinations=memberships.map((m,i)=>({id:m.destinationId,kind:'question',title:`Test harness component ${i+1}`,question:`Test harness component ${i+1}`,summary:'Regression scaffold around exact approved source placements.',scope:{},evidenceIds:[unit.id],scientificStatus:'test_scaffold',placementStatus:'test_scaffold',provenance:{fixture:true}}));
  const catalog={destinations,sources:[source],memberships,relations:[]};
  const manifest={schemaVersion:'1.0.0',kind:'eigenquestions-atlas',atlasId:'compound-test',atlasVersion:'v1',corpusId:fixture.corpusId,corpusContentHash:fixture.corpusContentHash,entryDestinationId:destinations[0].id,scope:{description:'Regression only; not a release atlas'},files:{catalog:{path:'catalog.json',sha256:hash(JSON.stringify(catalog))}}};
  return {manifest,catalog,manifestSha256:hash(JSON.stringify(manifest))};
}
test('real approved compound source retains both component homes and full map through hydration, view, capsule and source reads',async()=>{
  const data=atlas(),original=structuredClone(data),nav=createAtlasNavigator(data),uid=fixture.unit.id;
  assert.equal(hash(await readFile(new URL('../../'+fixture.provenance.componentPath,import.meta.url))),fixture.provenance.componentSha256);
  const read=createAtlasSourceReader(data,{base:new URL('../../data/navigation',import.meta.url).pathname,readText:file=>readFile(file,'utf8')});
  for(const membership of data.catalog.memberships){
    const [hydrated]=await read([{...membership,source:null}]);
    assert.equal(hydrated.source.evidence.text,fixture.unit.text);assert.deepEqual(hydrated.targetCoverage,membership.targetCoverage);assert.equal(hydrated.wholeQuestionCoveredByEachHome,false);assert.equal(hydrated.weight,.5);
    assert.equal(hydrated.coverageNotice,'This view covers one part of the source’s question.');
    const session=nav.createSession({selector:{...nav.initialState.selector,destinationId:membership.destinationId}}),view=nav.computeView(session.states[0]),node=view.nodes.find(s=>s.id===uid);
    assert.deepEqual(node.targetCoverage,membership.targetCoverage);assert.equal(node.evidence.text,fixture.unit.text);assert.equal(node.coverageNotice,hydrated.coverageNotice);
    const capsule=createCapsule({session,view});validateCapsule(capsule);assert.deepEqual(capsule.snapshot.view.nodes[0].targetCoverage,membership.targetCoverage);
    const page=nav.sources(membership.destinationId);assert.equal(page.total,1);assert.equal(page.items[0].weight,.5);assert.deepEqual(page.items[0].targetCoverage,membership.targetCoverage);assert.equal(page.items[0].coverageNotice,hydrated.coverageNotice);
    assert.equal(nav.sources(membership.destinationId,{workRelation:'using'}).total,0);
    assert.deepEqual(nav.getEvidence([uid],{destinationId:membership.destinationId})[0].targetCoverage,membership.targetCoverage);
  }
  nav.readSources=read;const runtime=createRuntime(nav,'compound-regression'),before=runtime.snapshot(),page=await runtime.sources();assert.deepEqual(page.items[0].targetCoverage,data.catalog.memberships[0].targetCoverage);assert.equal(page.items[0].source.evidence.text,fixture.unit.text);assert.deepEqual(runtime.snapshot(),before,'agent coverage reads are read-only');
  assert.equal(nav.getEvidence([uid])[0].targetCoverage,undefined,'unscoped source lookup cannot inherit a destination-specific assertion');assert.deepEqual(data,original,'source records and allocations remain immutable');
  const ancestor=sourceCoverage({...data.catalog.memberships[0],destinationId:'ancestor'});assert.equal(ancestor.coverageNotice,'This source combines several targets; see the qualified coverage in Source scope & provenance.');assert.deepEqual(ancestor.targetCoverage,data.catalog.memberships[0].targetCoverage);
  const invalid=atlas();invalid.catalog.memberships[0].wholeQuestionCoveredByEachHome=true;assert.throws(()=>validateAtlas(invalid.manifest,invalid.catalog),/partial whole-question/);
});
test('compound source coverage is readable in browser disclosure and static source pages',async()=>{
  const data=atlas(),row={...data.catalog.memberships[0],...sourceCoverage(data.catalog.memberships[0])},previous=globalThis.document,all=[];
  class Element{constructor(tag){this.tag=tag;this.children=[];this.handlers={};all.push(this);}addEventListener(name,handler){this.handlers[name]=handler;}append(...children){this.children.push(...children);}}
  try{globalThis.document={createElement:tag=>new Element(tag)};const host=new Element('article');const navigations=[];appendSourceCoverage(host,row,{navigator:{destination:id=>({title:'Reviewed topic '+id})},selector:{kind:'atlas-destination',atlasId:'compound-test',atlasVersion:'v1',destinationId:row.destinationId},onNavigate:action=>navigations.push(action)});const links=all.filter(n=>n.tag==='a');assert.equal(links.length,2);assert.ok(links.every(n=>n.textContent.startsWith('Reviewed topic ')));links[1].handlers.click({preventDefault(){}});assert.equal(navigations[0].selector.destinationId,row.targetCoverage[1].destinationIds[0]);assert.ok(all.some(n=>n.textContent===row.coverageNotice));const details=all.find(n=>n.tag==='details');assert.equal(details.open,undefined,'provenance is initially collapsed');for(const part of row.targetCoverage){assert.ok(all.some(n=>n.textContent===part.sourceSpan));assert.ok(all.some(n=>n.textContent===part.explanation));}assert.deepEqual(JSON.parse(all.find(n=>n.tag==='pre').textContent).targetCoverage,row.targetCoverage);}finally{if(previous===undefined)delete globalThis.document;else globalThis.document=previous;}
  const root=await mkdtemp(path.join(tmpdir(),'eigenquestions-compound-static-'));
  try{
    const directory=path.join(root,'data/atlas/compound-test/v1');await mkdir(directory,{recursive:true});await mkdir(path.join(root,'scripts'));await mkdir(path.join(root,'web'));await writeFile(path.join(root,'web/index.html'),'<p>Test fixture</p>');
    await copyFile(new URL('../../scripts/build-site.mjs',import.meta.url),path.join(root,'scripts/build-site.mjs'));await cp(new URL('../../lib',import.meta.url),path.join(root,'lib'),{recursive:true});
    await writeFile(path.join(root,'data/atlas/index.json'),JSON.stringify({schemaVersion:'1.0.0',atlases:[{atlasId:'compound-test',atlasVersion:'v1',entryDestinationId:data.manifest.entryDestinationId,title:'Regression'}]}));
    await writeFile(path.join(directory,'manifest.json'),JSON.stringify(data.manifest));await writeFile(path.join(directory,'catalog.json'),JSON.stringify(data.catalog));
    execFileSync(process.execPath,['scripts/build-site.mjs'],{cwd:root,stdio:'pipe'});
    const html=await readFile(path.join(root,'dist/atlas/compound-test/v1',row.destinationId+'.html'),'utf8');assert.ok(html.includes(row.coverageNotice));assert.match(html,/Source scope &amp; provenance/);assert.match(html,/organizational fractions, not confidence/);for(const part of row.targetCoverage){assert.ok(html.includes(part.sourceSpan));for(const id of part.destinationIds)assert.ok(html.includes(encodeURIComponent(id)+'.html'));}assert.ok(html.includes(fixture.unit.text));
  }finally{await rm(root,{recursive:true,force:true});}
});
