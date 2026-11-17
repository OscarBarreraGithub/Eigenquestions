import test from 'node:test';
import assert from 'node:assert/strict';
import {pageSourceContext} from '../../lib/protocol/context-page.mjs';
const fixture=()=>({unitId:'unit:fixture',availability:'available',coverage:{description:'Synthetic paging fixture'},notice:'Source-scoped records; not universal question premises.',sourceObjects:Array.from({length:60},(_,i)=>({id:`object-${String(i).padStart(2,'0')}`,kind:i%2?'method':'assumption',paperId:'paper',text:`Full object ${i}`,evidenceScope:'direct_record_anchor',evidenceRefs:[`source-graph:ev:${i}`],provenance:{sourceGraphNodeId:`object-${String(i).padStart(2,'0')}`}})),sourceRelations:[{id:'relation-a',source:'object-59',target:'object-58',type:'uses_method',semanticStatus:'reviewed_scoped',premises:['Exact recorded regime'],evidenceRefs:['source-graph:ev:59']}],sourceAttachments:[{unitId:'unit:fixture',scope:'direct_record_relation',objectIds:['object-59'],relationIds:['relation-a']},{unitId:'unit:fixture',scope:'same_paper_context',objectIds:Array.from({length:59},(_,i)=>`object-${String(i).padStart(2,'0')}`),relationIds:[]}],sourceAssessments:[{id:'withheld-a',nodeIds:['object-59'],promotionWithheld:true,status:'deferred',readerNote:'Full mandatory reader note: conventions are unresolved; do not promote this relation.',evidenceRefs:['source-graph:ev:59']}],sourceEvidence:Array.from({length:60},(_,i)=>({id:`source-graph:ev:${i}`,page:i+1,sourceSha256:'a'.repeat(64)})),missingEvidenceIds:[]});

test('bounded context pages prioritize direct anchors and expose complete/filtered coverage',()=>{
  const source=fixture(),page=pageSourceContext(source);
  assert.equal(page.sourceObjects.length,20);assert.equal(page.sourceObjects[0].id,'object-59');assert.equal(page.page.nextOffset,20);assert.equal(page.unfilteredTotals.objects,60);assert.equal(page.unfilteredTotals.assessments,1);assert.equal(page.assessmentNotice.promotionWithheldCount,1);assert.match(page.readingCoverage.notice,/not automatically a premise/);
  const collected=[];let offset=0;do{const next=pageSourceContext(source,{offset});collected.push(...next.sourceObjects.map(o=>o.id));offset=next.page.nextOffset;}while(offset!==null);
  assert.equal(new Set(collected).size,60);assert.deepEqual(new Set(collected),new Set(source.sourceObjects.map(o=>o.id)));
  const methods=pageSourceContext(source,{kinds:['method'],scope:'same_paper_context'});assert.equal(methods.filteredTotals.objects,29);assert.equal(methods.unfilteredTotals.objects,60);assert.ok(methods.sourceObjects.every(o=>o.kind==='method'));assert.equal(methods.filteredTotals.relations,0);
});

test('relation endpoints remain exact outside object pages, and withheld reader notes are never shortened',()=>{
  const source=fixture(),objects=pageSourceContext(source,{limit:1}),relations=pageSourceContext(source,{section:'relations'});
  assert.ok(!objects.sourceObjects.some(o=>o.id==='object-58'));assert.equal(relations.sourceRelations[0].target,'object-58');assert.ok(relations.endpointObjects.some(o=>o.id==='object-58'&&o.kind==='assumption'));assert.deepEqual(relations.sourceRelations[0].premises,['Exact recorded regime']);
  const target=pageSourceContext(source,{objectIds:['object-58']});assert.deepEqual(target.sourceObjects,[source.sourceObjects[58]]);
  const assessments=pageSourceContext(source,{section:'assessments',objectIds:['object-59']});assert.equal(assessments.sourceAssessments[0].readerNote,source.sourceAssessments[0].readerNote);assert.equal(assessments.sourceAssessments[0].promotionWithheld,true);
  const evidence=pageSourceContext(source,{section:'evidence',objectIds:['object-59']});assert.deepEqual(evidence.sourceEvidence.map(e=>e.id),['source-graph:ev:59']);
});

test('large records stop at explicit byte-budget continuation and never truncate scientific text',()=>{
  const source=fixture();for(const o of source.sourceObjects)o.text='source '.repeat(4000);
  const first=pageSourceContext(source,{limit:40});assert.equal(first.page.limitedBy,'bytes');assert.ok(first.page.returned>0&&first.page.returned<40);assert.equal(first.sourceObjects[0].text,source.sourceObjects[0].text);assert.equal(first.page.nextOffset,first.page.returned);
  assert.throws(()=>pageSourceContext(source,{limit:41}),/between 1 and 40/);assert.throws(()=>pageSourceContext(source,{section:'all'}),/section/);
  source.sourceObjects[59].text='x'.repeat(300000);assert.throws(()=>pageSourceContext(source),/no record has been truncated/);
});

test('structural links remain inspectable without displacing substantive direct relations',()=>{
  const source=fixture();source.sourceAttachments[0].anchorObjectIds=['object-59'];
  for(let i=0;i<50;i++){const id=`structural-${i}`;source.sourceRelations.unshift({id,source:'object-59',target:`object-${String(i).padStart(2,'0')}`,type:'contains',semanticStatus:'structural'});source.sourceAttachments[0].relationIds.push(id);}
  const first=pageSourceContext(source,{section:'relations'});assert.equal(first.sourceRelations[0].id,'relation-a');assert.equal(first.unfilteredTotals.relations,51);assert.equal(first.page.nextOffset,20);
  const objects=pageSourceContext(source,{limit:2});assert.deepEqual(objects.sourceObjects.map(o=>o.id),['object-59','object-58']);
  const ids=[];let offset=0;do{const page=pageSourceContext(source,{section:'relations',offset});ids.push(...page.sourceRelations.map(r=>r.id));offset=page.page.nextOffset;}while(offset!==null);assert.equal(new Set(ids).size,51);
});
