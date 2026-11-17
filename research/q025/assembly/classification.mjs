/** Pure packaging of the frozen vocabulary chart; no new classification inference. */
const scopeKeys=['assumptions','includes','excludes','regimes','conventions'];
export function attachClassification(catalog,{orientation,destinations,detailEntryDestinationId,reviewOnly=false}) {
  catalog=structuredClone(catalog);orientation=structuredClone(orientation);
  if(!catalog.destinations.some(d=>d.id===detailEntryDestinationId))throw new Error('Detailed portal target is absent');
  const vocabulary=[],classification=[];
  for(const raw of destinations){
    const sid=raw.sourceUri?`vocabulary:${raw.id}`:'vocabulary:physics-classification-root';
    vocabulary.push({id:sid,kind:'vocabulary',title:raw.title,sourceUrl:raw.sourceUri||'https://physh.org/releases',evidence:{text:raw.title,kind:'classification_vocabulary',sourceUri:raw.sourceUri,sourceTag:raw.provenance?.sourceTag,sourceCommit:raw.provenance?.sourceCommit,sourceSha256:raw.provenance?.sourceSha256}});
    classification.push({...raw,question:`Explore ${raw.title}`,summary:raw.scope?.description||'Classification vocabulary entrance; source-backed coverage uses a separate chart.',scope:{...Object.fromEntries(scopeKeys.map(k=>[k,[]])),...raw.scope},aliases:[],evidenceIds:[sid],scientificStatus:'classification_metadata_not_scientific_assertion',placementStatus:'recorded_vocabulary_classification',membershipStatus:'metadata-only',metadataOnly:true,provenance:{...raw.provenance,classificationLayoutId:orientation.layoutId,reviewOnly}});
  }
  const hepId='landmark:arxiv-hep-th',hepSource='vocabulary:arxiv:hep-th';
  vocabulary.push({id:hepSource,kind:'vocabulary',title:'arXiv High Energy Physics - Theory',sourceUrl:'https://arxiv.org/category_taxonomy#hep-th',evidence:{text:'arXiv category hep-th: High Energy Physics - Theory.',kind:'external_subject_category',sourceUri:'https://arxiv.org/category_taxonomy#hep-th'}});
  classification.push({id:hepId,kind:'landmark',title:'High Energy Physics — Theory',question:'Explore high energy theory',summary:'A subject-category landmark leading to the detailed Swampland collection. This portal is curator navigation, not an equivalence between classification systems.',scope:{...Object.fromEntries(scopeKeys.map(k=>[k,[]])),includes:['The detailed collection is Swampland-centered.'],excludes:['No complete empirical coverage of high energy theory or all physics is claimed.']},aliases:['hep-th'],evidenceIds:[hepSource],metadataOnly:true,membershipStatus:'metadata-only',scientificStatus:'subject_category_metadata',placementStatus:'curator_navigation_landmark',provenance:{sourceUri:'https://arxiv.org/category_taxonomy#hep-th',portalMeaning:'curator_collection_navigation',reviewOnly}});
  const existing=new Set(catalog.destinations.map(d=>d.id));for(const d of classification)if(existing.has(d.id))throw new Error(`Duplicate classification destination ${d.id}`);
  const sources=new Map(catalog.sources.map(s=>[s.id,s]));for(const s of vocabulary){if(sources.has(s.id))throw new Error('Duplicate vocabulary source');sources.set(s.id,s);}
  const destinationsById=new Map(classification.map(d=>[d.id,d]));
  const root='classification:physics';
  const edges=[...orientation.frontierDestinationIds.map(target=>({source:root,target,kind:'classification',predicate:'curator_frontier',directed:true})),...orientation.edges];
  const relations=edges.map((edge,i)=>({id:`classification-edge:${i}`,source:edge.source,target:edge.target,type:'narrower',rationale:edge.predicate==='curator_frontier'?'Active disciplines in the pinned classification vocabulary.':'Recorded discipline assignment in the Research Areas facet of the pinned vocabulary.',status:'classification_metadata',evidenceIds:destinationsById.get(edge.target).evidenceIds,provenance:{layer:'classification',predicate:edge.predicate,layoutId:orientation.layoutId,scientificImplication:false}}));
  const portals=classification.filter(d=>['Particles & Fields','Gravitation, Cosmology & Astrophysics','Strings & branes'].includes(d.title)).map(d=>({destinationId:d.id,target:'destination',entryDestinationId:hepId,label:'Explore high energy theory',provenance:{kind:'curator_navigation',classificationEquivalence:false}}));
  portals.push({destinationId:hepId,target:'detail',entryDestinationId:detailEntryDestinationId,label:reviewOnly?'Open the source-reading research draft':'Open the detailed Swampland atlas',provenance:{kind:'curator_collection_navigation',sharedCoordinateMetric:false,reviewOnly}});
  for(const [i,p] of portals.entries())relations.push({id:`classification-portal:${i}`,source:p.destinationId,target:p.entryDestinationId,type:'collection_portal',rationale:p.label,status:reviewOnly?'research_preview_portal':'curator_navigation',evidenceIds:[hepSource],provenance:p.provenance});
  catalog.destinations.push(...classification);catalog.sources=[...sources.values()];catalog.relations.push(...relations);catalog.orientation={...orientation,portals,entryDestinationId:root};
  return {catalog,entryDestinationId:root};
}
