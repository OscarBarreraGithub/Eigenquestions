/** Select display points from existing coordinates; this creates no scientific edges. */
export function detailOverviewFrontier({selectedId,points,metadataOnly,connections,childrenOf,parents,roots}) {
  const entries=metadataOnly?connections.filter(r=>r.navigationKind==='collection_access'&&r.traversal==='outgoing').map(r=>r.destinationId):[];
  if(entries.length){const topics=[...new Set(entries)];return {topics,plotted:topics.filter(id=>points.has(id)),collection:true};}
  const children=childrenOf(selectedId).filter(id=>points.has(id));
  let ids=points.has(selectedId)?[selectedId,...(children.length?children:parents.flatMap(childrenOf))]:roots;
  if(points.has(selectedId))ids.push(...connections.filter(r=>!['broader','narrower'].includes(r.navigationKind)).map(r=>r.destinationId));
  ids=[...new Set(ids)].filter(id=>points.has(id));
  return {topics:ids,plotted:ids,collection:false};
}
