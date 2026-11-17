/** Explicit source accounting and organizational entrances, independent of H. */
import {sha256} from './corpus.mjs';
const fail=m=>{throw Error(`Atlas accounting: ${m}`);};
const sorted=v=>Array.isArray(v)?v.map(sorted):v&&typeof v==='object'?Object.fromEntries(Object.keys(v).sort().map(k=>[k,sorted(v[k])])):v;
export const accountingContentHash=value=>sha256(JSON.stringify(sorted(Object.fromEntries(Object.entries(value).filter(([k])=>k!=='decisionId')))));
export const classificationDefinitionHash=value=>sha256(JSON.stringify(sorted(value)));
function explicitProof(value,type,status,{decision,verifiedReceiptHashes}){
  const proof=decision(value.decisionId,[type]);
  if(proof.contentSha256!==accountingContentHash(value)||proof.adjudication?.status!==status||!verifiedReceiptHashes.has(proof.adjudication.receipt?.sha256))fail(`${type} lacks its exact verified coordinator receipt`);
  return proof;
}
export function validateSourceAccounting(coverage,{allQuestions,...context}){
  if(coverage.kind!=='accounted_question_corpus'||!['pre_holdout_freeze','complete_release'].includes(coverage.reason))fail('unknown source accounting mode');
  explicitProof(coverage,'source_accounting','accepted_explicit_source_accounting',context);
  const all=new Map(allQuestions.map(u=>[u.id,u])),seen=new Set();
  const add=(id,kind)=>{if(!all.has(id)||seen.has(id))fail(`unknown/duplicate ${kind} source`);seen.add(id);};
  if(!Array.isArray(coverage.resolvedUnitIds)||!Array.isArray(coverage.unresolved)||!Array.isArray(coverage.reservedUnitIds))fail('missing complete source-accounting arrays');
  for(const id of coverage.resolvedUnitIds)add(id,'resolved');
  for(const row of coverage.unresolved){add(row.unitId,'unresolved');if(!row.reason?.trim()||row.descriptionSha256!==all.get(row.unitId).evidence.textSha256||!row.sourceReviewIds?.length)fail('unresolved source lacks exact description/reason/review lineage');for(const id of row.sourceReviewIds)if(!context.reviewRecords.has(id))fail('unresolved source review absent');}
  for(const id of coverage.reservedUnitIds)add(id,'reserved');
  if(seen.size!==all.size)fail('question source disappears from accounting');
  if(coverage.reason==='complete_release'&&coverage.reservedUnitIds.length)fail('reserved sources block complete release');
  return {resolved:new Set(coverage.resolvedUnitIds),unresolved:new Map(coverage.unresolved.map(r=>[r.unitId,r])),reserved:new Set(coverage.reservedUnitIds)};
}
export function validateCollectionFrontier(frontier,{destinations,scopeHash,classificationDestinations=new Map(),...context}){
  if(frontier.kind!=='curated_collection_frontier'||frontier.landmark?.kind!=='landmark'||frontier.landmark.metadataOnly!==true||!frontier.landmark.id||!frontier.landmark.title?.trim())fail('invalid metadata collection landmark');
  explicitProof(frontier,'collection_frontier','accepted_explicit_collection_frontier',context);
  if(!Array.isArray(frontier.entries)||!frontier.entries.length||frontier.entries.length>15)fail('collection frontier must name 1–15 reviewed entries');
  const seen=new Set();for(const e of frontier.entries){const d=destinations.get(e.destinationId);if(!d||seen.has(e.destinationId)||e.scopeContentSha256!==scopeHash(d)||e.type!=='related_question'||!e.rationale?.trim())fail('collection entry changed or lacks exact scoped organizational meaning');seen.add(e.destinationId);}
  for(const e of frontier.metadataEntries||[]){const s=classificationDestinations.get(e.sourceId),d=destinations.get(e.destinationId);if(!s?.metadataOnly||classificationDefinitionHash(s)!==e.sourceDefinitionSha256||!d||scopeHash(d)!==e.scopeContentSha256||e.type!=='related_question'||!e.rationale?.trim())fail('metadata portal lacks exact vocabulary and scientific endpoint binding');seen.add(e.destinationId);}
  return seen;
}
export function attachMetadataEntries(catalog,frontier){
  const ids=new Set(catalog.destinations.map(d=>d.id));for(const e of frontier?.metadataEntries||[]){if(!ids.has(e.sourceId)||!ids.has(e.destinationId))fail('approved metadata portal endpoint absent from installed classification');catalog.relations.push({id:`metadata-entry:${sha256(e.sourceId+'\n'+e.destinationId).slice(0,24)}`,source:e.sourceId,target:e.destinationId,type:'related_question',rationale:e.rationale,status:'accepted_organizational_access',evidenceIds:catalog.destinations.find(d=>d.id===e.destinationId).evidenceIds,provenance:{evidenceMeaning:'Inherited endpoint source support; no new source reading or physical relation.',navigationBasis:'curated_collection_entry',decisionId:frontier.decisionId,sourceDefinitionSha256:e.sourceDefinitionSha256,scopeContentSha256:e.scopeContentSha256,noScientificContainment:true,noGeometryAllocation:true,noMethodApplicability:true}});}
}
export function navigationReachability(catalog,entryIds){
  const adjacency=new Map(catalog.destinations.map(d=>[d.id,[]]));
  for(const r of catalog.relations){if(!adjacency.has(r.source)||!adjacency.has(r.target))fail('navigation endpoint absent');adjacency.get(r.source).push(r.target);adjacency.get(r.target).push(r.source);}
  const reached=new Set(entryIds),queue=[...entryIds];for(let i=0;i<queue.length;i++)for(const id of adjacency.get(queue[i])||[])if(!reached.has(id)){reached.add(id);queue.push(id);}
  return reached;
}
export function attachCollectionFrontier(catalog,frontier){
  const l=frontier.landmark;if(catalog.destinations.some(d=>d.id===l.id))fail('collection landmark collides with scientific destination');
  catalog.destinations.push({id:l.id,kind:'landmark',title:l.title,question:l.title,summary:'An organizational entrance to reviewed scientific scopes in this collection. This is not a physical parent or a scientific containment claim.',scope:{assumptions:[],includes:[],excludes:[],regimes:[],conventions:[]},metadataOnly:true,membershipStatus:'metadata-only',scientificStatus:'curated_collection_orientation',placementStatus:'metadata-only',aliases:[],evidenceIds:[],memberIds:[],provenance:{decisionId:frontier.decisionId,navigationBasis:'curated_collection_entry',noScientificContainment:true,noGeometryAllocation:true}});
  for(const e of frontier.entries){const target=catalog.destinations.find(d=>d.id===e.destinationId);catalog.relations.push({id:`collection-entry:${sha256(l.id+'\n'+target.id).slice(0,24)}`,source:l.id,target:target.id,type:'related_question',title:target.title,rationale:e.rationale,status:'accepted_organizational_access',evidenceIds:target.evidenceIds,provenance:{evidenceMeaning:'Inherited endpoint source support; no new source reading or physical relation.',navigationBasis:'curated_collection_entry',decisionId:frontier.decisionId,scopeContentSha256:e.scopeContentSha256,noScientificContainment:true,noGeometryAllocation:true,noMethodApplicability:true}});}
}
