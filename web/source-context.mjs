const el=(tag,value)=>{const node=document.createElement(tag);if(value!==undefined)node.textContent=value;return node;};
const scopes={direct_record_relation:'Direct recorded source relation',shared_extraction_window_context:'Shared extraction window — applicability is not established',same_paper_context:'Same-paper context — applicability is not established'};

// Detail records are built progressively, including their provenance. A large
// paper shard may be complete without putting every object into the DOM at once.
function progressive(host,items,render,label,batch=20){
  let offset=0;const more=el('button');more.type='button';
  function append(){more.remove();for(const item of items.slice(offset,offset+batch))host.append(render(item));offset+=batch;if(offset<items.length){more.textContent=`Show ${Math.min(batch,items.length-offset)} more ${label} (${items.length-offset} remaining)`;host.append(more);}}
  more.addEventListener('click',append);append();
}
function provenance(record,value){let populated=false;record.addEventListener('toggle',()=>{if(record.open&&!populated){populated=true;record.append(el('pre',JSON.stringify(value,null,2)));}});}

export function sourceContextDisclosure(load) {
  const details=el('details');details.className='source-scientific-context';details.append(el('summary','Methods, assumptions and scientific source connections'));
  let requested=false;
  details.addEventListener('toggle',async()=>{
    if(!details.open||requested)return;requested=true;
    const body=el('div');body.append(el('p','Loading pinned source context…'));details.append(body);
    try{
      const context=await load();if(!details.isConnected)return;body.replaceChildren();
      body.append(el('p',context.notice));
      if(context.coverage)body.append(el('p',typeof context.coverage.description==='string'?context.coverage.description:JSON.stringify(context.coverage)));
      if(context.availability!=='available'){body.append(el('p','No context was exported for this source in this atlas version. Read the paper for its assumptions and methods.'));return;}
      const objects=new Map(context.sourceObjects.map(item=>[item.id,item])),relations=new Map(context.sourceRelations.map(item=>[item.id,item]));
      for(const attachment of context.sourceAttachments){
        const group=el('section');group.append(el('h4',scopes[attachment.scope]||attachment.scope));
        if(attachment.warning)group.append(el('p',attachment.warning));
        const objectRows=(attachment.objectIds||[]).map(id=>objects.get(id)).filter(Boolean);
        group.append(el('p',`${objectRows.length} source objects · ${(attachment.relationIds||[]).length} recorded relations`));
        const objectList=el('div');progressive(objectList,objectRows,object=>{const record=el('details');record.append(el('summary',`${object.kind} · ${object.paperId}`),el('p',object.text));provenance(record,{id:object.id,evidenceScope:object.evidenceScope,evidenceRefs:object.evidenceRefs,provenance:object.provenance});return record;},'source objects');group.append(objectList);
        const relationList=el('div');progressive(relationList,(attachment.relationIds||[]).map(id=>relations.get(id)).filter(Boolean),relation=>{
          const record=el('details'),source=objects.get(relation.source),target=objects.get(relation.target);record.append(el('summary',`${relation.type.replaceAll('_',' ')} · ${relation.semanticStatus.replaceAll('_',' ')}`),el('p',`${source?.kind||'Object'} ${source?.paperId||relation.source} → ${target?.kind||'object'} ${target?.paperId||relation.target}`));
          if(relation.statement)record.append(el('p',relation.statement));if(relation.readerNote)record.append(el('p',relation.readerNote));
          if(relation.premises?.length){record.append(el('h4','Premises'));const list=el('ul');for(const premise of relation.premises)list.append(el('li',typeof premise==='string'?premise:JSON.stringify(premise)));record.append(list);}
          record.append(el('p','This relation concerns these source objects under their recorded scope. It is not an implication between their entire topics.'));provenance(record,relation);return record;
        },'source relations');group.append(relationList);body.append(group);
      }
      if(context.sourceAssessments?.length){const assessment=el('details');assessment.append(el('summary',`${context.sourceAssessments.length} withheld or nonpositive assessments`));progressive(assessment,context.sourceAssessments,item=>{const record=el('details');record.append(el('summary',item.status||'Recorded assessment'),el('p',item.readerNote||item.statement||'Recorded assessment'));provenance(record,item);return record;},'assessments');body.append(assessment);}
      if(context.sourceEvidence?.length){const locators=el('details');locators.append(el('summary',`${context.sourceEvidence.length} original evidence locators`));let populated=false;locators.addEventListener('toggle',()=>{if(locators.open&&!populated){populated=true;progressive(locators,context.sourceEvidence,item=>{const record=el('details');record.append(el('summary',`${item.id}${item.page!==undefined?` · page ${item.page}`:''}`));provenance(record,item);return record;},'locators');}});body.append(locators);}
      if(context.missingEvidenceIds?.length)body.append(el('p',`${context.missingEvidenceIds.length} referenced evidence locators are not included in this export. The exact IDs remain in the source records.`));
    }catch(error){requested=false;body.replaceChildren(el('p',`Source context unavailable: ${error.message}. The displayed source is unchanged.`));}
  });
  return details;
}
