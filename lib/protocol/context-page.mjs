/** Bounded agent reads over a complete, verified source-context record. */
export const CONTEXT_SECTIONS=['objects','relations','evidence','assessments'];
const fields={objects:'sourceObjects',relations:'sourceRelations',evidence:'sourceEvidence',assessments:'sourceAssessments'};
const scopes=['direct_record_relation','shared_extraction_window_context','same_paper_context'];
const ids=value=>value.objectIds||value.nodeIds||value.sourceObjectIds||[value.source,value.target].filter(Boolean);
const size=value=>new TextEncoder().encode(JSON.stringify(value)).byteLength;
const MAX_PAGE_BYTES=256*1024;
export const sourceRelationIsStructural=relation=>relation.semanticStatus==='structural'||relation.semanticStatus==='unvalidated_mention'||/^(contains|mentions|retrieval_hint|source_contains)$/.test(relation.type);
const relationStatuses=['reviewed_scoped','source_local_assertion','extraction_inference','local_nomination_only','unvalidated_mention','structural'];
export function compareSourceRelations(a,b,directIds=new Set()){return Number(sourceRelationIsStructural(a))-Number(sourceRelationIsStructural(b))||Number(!directIds.has(a.id))-Number(!directIds.has(b.id))||relationStatuses.indexOf(a.semanticStatus)-relationStatuses.indexOf(b.semanticStatus)||a.id.localeCompare(b.id);}

export function pageSourceContext(context,{section='objects',offset=0,limit=20,scope,kinds,objectIds}={}){
  if(!CONTEXT_SECTIONS.includes(section))throw new Error('Context section must be objects, relations, evidence or assessments');
  if(!Number.isInteger(offset)||offset<0||!Number.isInteger(limit)||limit<1||limit>40)throw new Error('Context page needs a nonnegative offset and limit between 1 and 40');
  if(scope!==undefined&&!scopes.includes(scope))throw new Error('Unknown source-context scope');
  for(const [name,values]of Object.entries({kinds,objectIds}))if(values!==undefined&&(!Array.isArray(values)||values.length>40||values.some(x=>typeof x!=='string'||x.length>500)))throw new Error(`${name} must contain at most 40 string identifiers`);
  const all=Object.fromEntries(CONTEXT_SECTIONS.map(key=>[key,context[fields[key]]||[]]));
  const attachments=context.sourceAttachments||[],selectedAttachments=attachments.filter(a=>!scope||a.scope===scope);
  const scopedObjects=new Set(selectedAttachments.flatMap(a=>a.objectIds||[])),scopedRelations=new Set(selectedAttachments.flatMap(a=>a.relationIds||[]));
  const structural=sourceRelationIsStructural;
  const rank=new Map();for(const attachment of attachments){const base=attachment.scope==='direct_record_relation'?(attachment.anchorObjectIds?.length?1.5:0):attachment.scope==='shared_extraction_window_context'?2:3;for(const id of attachment.objectIds||[])rank.set(id,Math.min(rank.get(id)??4,base));for(const id of attachment.anchorObjectIds||[])rank.set(id,0);}
  const directRelations=new Set(attachments.filter(a=>a.scope==='direct_record_relation').flatMap(a=>a.relationIds||[]));
  for(const relation of all.relations)if(directRelations.has(relation.id))for(const id of [relation.source,relation.target])rank.set(id,Math.min(rank.get(id)??4,structural(relation)?1.5:.5));
  const objects=all.objects.filter(o=>(!scope||scopedObjects.has(o.id))&&(!kinds?.length||kinds.includes(o.kind))&&(!objectIds?.length||objectIds.includes(o.id))).sort((a,b)=>(rank.get(a.id)??3)-(rank.get(b.id)??3)||a.id.localeCompare(b.id));
  const matchingObjects=new Set(objects.map(o=>o.id)),filteredObjects=Boolean(kinds?.length||objectIds?.length);
  const relations=all.relations.filter(r=>(!scope||scopedRelations.has(r.id))&&(!filteredObjects||matchingObjects.has(r.source)||matchingObjects.has(r.target))).sort((a,b)=>compareSourceRelations(a,b,directRelations));
  const assessments=all.assessments.filter(a=>(!scope&&!filteredObjects)||ids(a).some(id=>matchingObjects.has(id)));
  const evidenceIds=new Set([...objects,...relations,...assessments].flatMap(item=>item.evidenceRefs||[]));
  const evidence=all.evidence.filter(e=>(!scope&&!filteredObjects)||evidenceIds.has(e.id));
  const filtered={objects,relations,evidence,assessments},rows=filtered[section],items=[];let bytes=0;
  for(const row of rows.slice(offset,offset+limit)){const length=size(row);if(length>MAX_PAGE_BYTES)throw new Error(`Source record ${row.id||'(assessment)'} exceeds the 256 KiB inline page budget. Read its pinned static source-context shard; no record has been truncated.`);if(bytes+length>MAX_PAGE_BYTES)break;items.push(row);bytes+=length;}
  const pageObjectIds=new Set(section==='objects'?items.map(o=>o.id):section==='relations'?items.flatMap(r=>[r.source,r.target]):section==='assessments'?items.flatMap(ids):[]);
  const pageRelationIds=new Set(section==='relations'?items.map(r=>r.id):[]),nextOffset=offset+items.length<rows.length?offset+items.length:null;
  const result={unitId:context.unitId,availability:context.availability,coverage:context.coverage,notice:context.notice,
    page:{section,offset,limit,returned:items.length,total:rows.length,nextOffset,limitedBy:items.length<Math.min(limit,rows.length-offset)?'bytes':'records'},
    unfilteredTotals:Object.fromEntries(CONTEXT_SECTIONS.map(key=>[key,all[key].length])),filteredTotals:Object.fromEntries(CONTEXT_SECTIONS.map(key=>[key,filtered[key].length])),
    readingCoverage:{completeUnitContext:false,returnedSection:section,scope:scope||'all recorded scopes',notice:'This is one explicit page. Other sections, scopes and offsets remain available. Absence from a page or filter does not establish scientific absence; a directly attached source object is not automatically a premise of the retrieval question.'},
    attachmentCoverage:attachments.map(a=>({scope:a.scope,objectCount:(a.objectIds||[]).length,relationCount:(a.relationIds||[]).length,warning:a.warning})),
    sourceAttachments:selectedAttachments.map(a=>({...a,objectIds:(a.objectIds||[]).filter(id=>pageObjectIds.has(id)),relationIds:(a.relationIds||[]).filter(id=>pageRelationIds.has(id))})),
    sourceObjects:[],sourceRelations:[],sourceEvidence:[],sourceAssessments:[],
    assessmentNotice:{total:all.assessments.length,promotionWithheldCount:all.assessments.filter(a=>a.promotionWithheld).length,section:'assessments',notice:'Read applicable withheld and nonpositive assessments before interpreting a scientific source relation. Reader notes are returned in full in the assessments section.'},
    missingEvidenceCount:context.missingEvidenceIds?.length||0};
  result[fields[section]]=items;
  if(section==='relations')result.endpointObjects=all.objects.filter(o=>pageObjectIds.has(o.id)).map(o=>({id:o.id,kind:o.kind,paperId:o.paperId,evidenceScope:o.evidenceScope,sourceParentId:o.provenance?.sourceGraphNodeId||o.id,recordId:o.provenance?.record?.record_id,detailStatus:'endpoint reference; request objects with objectIds for full text'}));
  for(const key of ['attachmentOverridePolicy','missingAnchorIds','sourceContextFile','sourceLocator'])if(context[key]!==undefined)result[key]=context[key];
  return structuredClone(result);
}
