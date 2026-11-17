/** Render only explicit scoped source coverage; never derive applicability. */
export function appendSourceCoverage(host,record,{provenance,navigator,selector,onNavigate}={}) {
  if(record?.coverageMode!=='explicit_compound_union')return;
  const el=(tag,text)=>{const node=document.createElement(tag);node.textContent=text;return node;};
  host.append(el('p',record.coverageNotice));
  const details=provenance||document.createElement('details');
  if(!provenance)details.append(el('summary','Source scope & provenance'));
  details.append(el('p','The source question remains one immutable description. The mapped components below qualify its coverage; weights are organizational fractions, not confidence.'));
  const list=document.createElement('ul');
  for(const part of record.targetCoverage){const item=document.createElement('li'),homes=el('p','Mapped topics: ');for(const [index,id]of part.destinationIds.entries()){if(index)homes.append(document.createTextNode('; '));let title=id;try{title=navigator?.destination(id)?.title||id;}catch{}if(selector){const target={...selector,destinationId:id},link=el('a',title);link.href='/#'+new URLSearchParams({atlas:target.atlasId,version:target.atlasVersion,destination:id});if(onNavigate)link.addEventListener('click',event=>{event.preventDefault();onNavigate({type:'navigate',selector:target});});homes.append(link);}else homes.append(el('span',title));}item.append(el('p',part.sourceSpan),homes,el('p',part.explanation));list.append(item);} 
  details.append(list,el('pre',JSON.stringify({coverageMode:record.coverageMode,wholeQuestionCoveredByEachHome:record.wholeQuestionCoveredByEachHome,targetCoverage:record.targetCoverage,...record.coverageProvenance},null,2)));
  if(!provenance)host.append(details);
}
