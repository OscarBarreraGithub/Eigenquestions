/** Select display points from existing coordinates; this creates no scientific edges. */
export function detailOverviewFrontier({selectedId,points,metadataOnly,connections,childrenOf,parents,roots}) {
  const entries=metadataOnly?connections.filter(r=>r.navigationKind==='collection_access'&&r.traversal==='outgoing').map(r=>r.destinationId):[];
  if(entries.length){const topics=[...new Set(entries)];return {topics,plotted:[...(points.has(selectedId)?[selectedId]:[]),...topics.filter(id=>points.has(id))],collection:true};}
  const children=childrenOf(selectedId).filter(id=>points.has(id));
  let ids=points.has(selectedId)?[selectedId,...(children.length?children:parents.flatMap(childrenOf))]:roots;
  if(points.has(selectedId))ids.push(...connections.filter(r=>!['broader','narrower'].includes(r.navigationKind)).map(r=>r.destinationId));
  ids=[...new Set(ids)].filter(id=>points.has(id));
  return {topics:ids,plotted:ids,collection:false};
}

/** A schematic displays only exact recorded routes, with no metric interpretation. */
export function validateNavigationSchematic(chart,records,relations) {
  const points=new Set(chart.nodes.map(p=>p.destinationId)),recorded=new Map(relations.map(r=>[r.id,r]));
  for(const point of chart.nodes)if(point.coordinateBasis==='schematic_collection_anchor'&&(!records.get(point.destinationId)?.metadataOnly||point.mass!==0))throw new Error('A schematic collection anchor must remain metadata-only and zero mass');
  for(const edge of chart.edges||[]){const relation=recorded.get(edge.relationId);if(edge.kind!=='recorded_navigation'||!relation||relation.source!==edge.source||relation.target!==edge.target||relation.type!==edge.type||!points.has(edge.source)||!points.has(edge.target))throw new Error('Schematic edge lacks its exact recorded direction and endpoints');}
}
