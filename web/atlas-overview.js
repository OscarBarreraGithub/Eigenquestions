import {loadAtlas,createAtlasNavigator,atlasAddress} from '/lib/geometry/prepared-atlas.mjs';
import {placeChartLabel} from '/chart-labels.mjs';
import {classificationChartDisplay} from '/classification-layout.mjs';
import {detailOverviewFrontier} from '/detail-frontier.mjs';
import {destinationPresentation} from '/lib/protocol/display-editorial.mjs';
const $=id=>document.getElementById(id),NS='http://www.w3.org/2000/svg';
const el=(tag,text)=>{const node=document.createElement(tag);if(text!==undefined)node.textContent=text;return node;};
const svg=(tag,attrs,text)=>{const node=document.createElementNS(NS,tag);for(const[k,v]of Object.entries(attrs))node.setAttribute(k,v);if(text!==undefined)node.textContent=text;return node;};
let loaded,navigator,records=new Map(),selectedId,classificationAnchor=null,space='classification',points=new Map(),visibleIds=[],topicIds=[],camera={x:0,y:0,width:100,height:100},baseCamera,request=0;
const map=$('atlas-map');
let displayPoints=new Map(),classificationDisplay;
const textMeasure=document.createElement('canvas').getContext('2d');textMeasure.font='14px Arial';
const layout=()=>space==='classification'?loaded.catalog.orientation:loaded.catalog.overview;
const selector=id=>({kind:'atlas-destination',atlasId:loaded.manifest.atlasId,atlasVersion:loaded.manifest.atlasVersion,destinationId:id});
function relations(id){const items=[];let offset=0,total;do{const page=navigator.connections(id,{offset,limit:100});items.push(...page.items);total=page.total;offset+=page.items.length;}while(offset<total);return items;}
function children(id){return space==='classification'?id===layout()?.entryDestinationId?roots():(layout()?.edges||[]).filter(e=>e.source===id).map(e=>e.target):relations(id).filter(r=>r.navigationKind==='narrower').map(r=>r.destinationId);}
function parents(id){return space==='classification'?(layout()?.edges||[]).filter(e=>e.target===id).map(e=>e.source):relations(id).filter(r=>r.navigationKind==='broader').map(r=>r.destinationId);}
function roots(){const values=[...points.values()];if(!values.length)return[];const minimum=Math.min(...values.map(p=>p.depth??0));return values.filter(p=>(p.depth??0)===minimum).map(p=>p.destinationId);}
function labelPositions(){
  if(space==='classification'||!points.size||!map.clientWidth)return;
  const scale=camera.width/map.clientWidth,minX=camera.x-camera.width/2,minY=camera.y-camera.height/2,markers=visibleIds.map(id=>points.get(id)).filter(Boolean).map(p=>({x:(p.x-minX)/scale,y:(p.y-minY)/scale,radius:14})),boxes=[];
  for(const group of map.querySelectorAll('.atlas-map-node')){
    const p=points.get(group.dataset.destinationId),label=group.querySelector('.atlas-map-label'),number=group.querySelector('.atlas-map-number');
    group.querySelector('.atlas-map-dot').setAttribute('r',6*scale);group.querySelector('.atlas-map-hit').setAttribute('r',22*scale);
    number.setAttribute('font-size',11*scale);number.setAttribute('y',p.y+3.5*scale);label.setAttribute('font-size',13*scale);label.removeAttribute('transform');label.style.display='block';
    const size=label.getBBox(),anchor={x:(p.x-minX)/scale,y:(p.y-minY)/scale,radius:14};
    const placed=placeChartLabel({anchor,width:size.width/scale+6,height:size.height/scale+6,bounds:{width:map.clientWidth,height:map.clientHeight},circles:markers,labels:boxes});
    if(placed){label.setAttribute('transform',`translate(${minX+(placed.x+3)*scale-size.x} ${minY+(placed.y+3)*scale-size.y})`);boxes.push(placed);}else label.style.display='none';
  }
}
function viewBox(){map.setAttribute('viewBox',`${camera.x-camera.width/2} ${camera.y-camera.height/2} ${camera.width} ${camera.height}`);labelPositions();}
function fit(){
  if(space==='classification'&&classificationDisplay){camera={x:classificationDisplay.width/2,y:classificationDisplay.height/2,width:classificationDisplay.width,height:classificationDisplay.height};baseCamera={...camera};viewBox();return;}
  const values=visibleIds.map(id=>points.get(id)).filter(Boolean);if(!values.length)return;
  const xs=values.map(p=>p.x),ys=values.map(p=>p.y),width=Math.max(.01,Math.max(...xs)-Math.min(...xs)),height=Math.max(.01,Math.max(...ys)-Math.min(...ys)),aspect=map.clientWidth/Math.max(1,map.clientHeight);
  camera={x:(Math.max(...xs)+Math.min(...xs))/2,y:(Math.max(...ys)+Math.min(...ys))/2,width:Math.max(width,height*aspect)*1.35,height:Math.max(height,width/aspect)*1.35};baseCamera={...camera};viewBox();
}
function zoom(factor){if(!baseCamera)return;const width=Math.min(baseCamera.width*3,Math.max(baseCamera.width/80,camera.width*factor));camera.height*=width/camera.width;camera.width=width;viewBox();}
function portalFor(id){return loaded.catalog.orientation?.portals?.filter(p=>p.destinationId===id)||[];}
function draw(){
  map.replaceChildren();const chart=layout();document.querySelector('.atlas-map-workspace').classList.toggle('classification-workspace',space==='classification');
  if(!chart){visibleIds=[];topicIds=[];map.style.display='none';$('atlas-map-caption').textContent=space==='classification'?'This release has no classification map. Recorded destinations remain readable in the list.':'This release has no detailed source chart. No coordinates have been invented.';return;}
  map.style.display='block';const childIds=children(selectedId).filter(id=>points.has(id));
  if(points.has(selectedId))visibleIds=[selectedId,...(childIds.length?childIds:parents(selectedId).flatMap(id=>children(id)))];else if(space==='classification'&&classificationAnchor&&points.has(classificationAnchor))visibleIds=[classificationAnchor,...children(classificationAnchor)];else visibleIds=roots();
  if(space==='detail'){const frontier=detailOverviewFrontier({selectedId,points,metadataOnly:records.get(selectedId)?.metadataOnly,connections:relations(selectedId),childrenOf:children,parents:parents(selectedId),roots:roots()});visibleIds=frontier.plotted;topicIds=frontier.topics;}else topicIds=visibleIds;
  visibleIds=[...new Set(visibleIds)].filter(id=>points.has(id));const visible=new Set(visibleIds);
  if(space==='classification'){drawClassification(chart);return;}
  classificationDisplay=null;displayPoints=points;map.style.height='';map.classList.remove('classification-display');document.querySelector('.atlas-map-workspace').classList.remove('classification-workspace');
  for(const edge of chart.edges||[]){if(!visible.has(edge.source)||!visible.has(edge.target))continue;const a=displayPoints.get(edge.source),b=displayPoints.get(edge.target);map.append(svg('line',{x1:a.x,y1:a.y,x2:b.x,y2:b.y,class:'atlas-map-edge'}));}
  visibleIds.forEach((id,index)=>{const p=displayPoints.get(id),record=records.get(id),group=svg('g',{class:'atlas-map-node',tabindex:0,role:'button','aria-label':record.title,'aria-current':String(id===selectedId)});group.dataset.destinationId=id;
    group.append(svg('circle',{cx:p.x,cy:p.y,r:1,fill:'transparent',class:'atlas-map-hit'}),svg('circle',{cx:p.x,cy:p.y,r:1,fill:id===selectedId?'#a52929':record.kind==='question'?'#754c4c':'#3f607c',class:'atlas-map-dot'}),svg('text',{x:p.x,y:p.y,'text-anchor':'middle',fill:'#fff',class:'atlas-map-number'},String(index+1)),svg('text',{x:0,y:0,fill:'#292929',class:'atlas-map-label'},record.title.length>62?record.title.slice(0,59)+'…':record.title),svg('title',{},record.title));
    group.addEventListener('click',()=>select(id));group.addEventListener('keydown',event=>{if(['Enter',' '].includes(event.key)){event.preventDefault();select(id);}});map.append(group);
  });
  fit();
  $('atlas-map-caption').textContent=space==='classification'?'Physics classification: links follow the recorded vocabulary hierarchy. Positions organize labels; distances are not physical or embedding distances. The detailed source atlas is a separate chart.':'Detailed source chart: positions use the recorded source geometry. Gray links are geometric affinities, not scientific implications. Unplotted destinations remain accessible in the list and text explorer. Broader classifications have a separate coordinate system.';
  $('atlas-map-provenance').textContent=JSON.stringify({layoutId:chart.layoutId,kind:chart.kind,provenance:chart.provenance,displayAdjustment:space==='classification'?'Full labels occupy nonoverlapping screen cards assigned near the recorded positions by minimum total displacement. Stored coordinates and classification links are unchanged; screen distances have no metric meaning.':undefined,diagnostics:chart.diagnostics,limitations:chart.limitations},null,2);
}
function drawClassification(chart){
  document.querySelector('.atlas-map-workspace').classList.add('classification-workspace');
  classificationDisplay=classificationChartDisplay([...points.values()].map(point=>({...point,title:records.get(point.destinationId).title})),{width:map.clientWidth,measureText:text=>textMeasure.measureText(text).width});
  displayPoints=new Map(classificationDisplay.points.map(point=>[point.destinationId,point]));map.style.height=`${classificationDisplay.height}px`;map.classList.add('classification-display');
  const focus=points.has(selectedId)?selectedId:classificationAnchor,parentsById=new Map();for(const edge of chart.edges){if(!parentsById.has(edge.target))parentsById.set(edge.target,[]);parentsById.get(edge.target).push(edge.source);}
  for(const frame of classificationDisplay.frames){map.append(svg('rect',{x:frame.x,y:frame.y,width:frame.width,height:frame.height,class:'classification-component-frame'}),svg('text',{x:frame.x+8,y:frame.y+15,class:'classification-component-label'},frame.label));}
  for(const edge of chart.edges){const a=displayPoints.get(edge.source),b=displayPoints.get(edge.target);if(!a||!b)continue;map.append(svg('line',{x1:a.x,y1:a.y,x2:b.x,y2:b.y,class:`atlas-map-edge classification-edge${edge.source===focus||edge.target===focus?' selected-edge':''}`}));}
  const activate=(group,id)=>{group.addEventListener('click',()=>select(id));group.addEventListener('keydown',event=>{if(['Enter',' '].includes(event.key)){event.preventDefault();select(id);}});};
  for(const point of classificationDisplay.points){const field=point.depth===0,shared=(parentsById.get(point.destinationId)||[]).length>1,group=svg('g',{class:`atlas-fixed-node${field?' classification-field':' classification-area'}${shared?' shared-area':''}${point.destinationId===focus?' active-point':''}`,'aria-label':records.get(point.destinationId).title,role:'button',tabindex:field&&classificationDisplay.mobile?0:-1});group.dataset.destinationId=point.destinationId;
    if(field&&classificationDisplay.mobile)group.classList.add('atlas-map-node');
    group.append(svg('circle',{cx:point.x,cy:point.y,r:field?22:7,fill:'transparent',class:'atlas-map-hit'}),svg('circle',{cx:point.x,cy:point.y,r:field?6:shared?3.5:2.5,class:'classification-fixed-dot'}),svg('title',{},records.get(point.destinationId).title+(shared?' · Classified under '+parentsById.get(point.destinationId).map(id=>records.get(id).title).join('; '):'')));activate(group,point.destinationId);map.append(group);
  }
  for(const box of classificationDisplay.callouts){
    const endX=box.side?box.x:box.x+box.width,endY=box.y+box.height/2;map.append(svg('line',{x1:box.anchor.x,y1:box.anchor.y,x2:endX,y2:endY,class:'classification-leader'}));
    const group=svg('g',{class:'atlas-map-node classification-card',tabindex:0,role:'button','aria-label':records.get(box.destinationId).title,'aria-current':String(box.destinationId===focus)});group.dataset.destinationId=box.destinationId;
    group.append(svg('rect',{x:box.x,y:box.y,width:box.width,height:box.height,rx:3,class:'atlas-map-hit'}));const label=svg('text',{x:box.x+14,y:box.y+box.height/2-(box.lines.length-1)*9+5,class:'atlas-map-label'});box.lines.forEach((line,i)=>label.append(svg('tspan',{x:box.x+14,dy:i?18:0},line)));group.append(label);activate(group,box.destinationId);map.append(group);
  }
  fit();$('atlas-map-caption').textContent='Physics classification: 17 fields, 194 research areas and their recorded classification links. Shared areas connect their actual parent fields. The detailed source atlas has a separate chart.';
  $('atlas-map-help').textContent=classificationDisplay.mobile?'Select a field below, or tap a point. Drag to pan; use +/− to zoom.':'Select a field label or an area point. Drag to pan; use +/− to zoom.';
  $('atlas-map-provenance').textContent=JSON.stringify({layoutId:chart.layoutId,kind:chart.kind,provenance:chart.provenance,displayAdjustment:'Coordinates within each recorded connected component are scaled uniformly and translated. Labels use separate callouts linked to unchanged anchors. Smaller disconnected components use a framed inset; its gap and scale are display choices, not intellectual distances.',diagnostics:chart.diagnostics,limitations:chart.limitations},null,2);
}
function button(label,handler){const node=el('button',label);node.type='button';node.addEventListener('click',handler);return node;}
async function select(id){
  const selection=++request;await navigator.prepareDestination?.(id);if(selection!==request)return;
  const record=navigator.destination(id);records.set(id,record);selectedId=id;if(space==='classification'&&points.has(id))classificationAnchor=id;const links=relations(id),childIds=children(id),panel=$('atlas-selected');panel.replaceChildren(el('h2',record.title));
  if(space==='classification'&&record.metadataOnly&&childIds.length)panel.append(el('p',`${childIds.length} ${id===layout()?.entryDestinationId?'fields':'research areas'} in this classification.`));else if(!record.metadataOnly||record.kind==='landmark')panel.append(el('p',destinationPresentation(record).summary));
  const open=el('a','Open this destination in the text explorer →');open.href=atlasAddress(navigator.createSession({selector:selector(id)}).states[0],location.origin);panel.append(open);
  for(const portal of portalFor(id))panel.append(button(portal.label||'Enter the detailed source atlas →',()=>portal.target==='destination'?select(portal.entryDestinationId):switchSpace('detail',portal.entryDestinationId)));
  const related=space==='classification'?parents(id).map(target=>({destinationId:target,title:records.get(target)?.title||target,navigationKind:'broader classification'})):links;
  if(related.length)panel.append(el('h3',space==='classification'?'Broader classifications':'Recorded connections'));
  for(const relation of related)panel.append(button(`${relation.title} · ${relation.navigationKind.replaceAll('_',' ')}`,()=>select(relation.destinationId)));
  if(!related.length&&space!=='classification')panel.append(el('p',record.metadataOnly?'Detailed source-backed navigation has not yet been prepared for this field.':'No additional recorded connection. Its source material remains available in the text explorer.'));
  const breadcrumb=$('atlas-map-breadcrumb');breadcrumb.replaceChildren(button('All physics fields',()=>switchSpace('classification',loaded.catalog.orientation?.entryDestinationId||loaded.manifest.entryDestinationId)),el('span',` › ${space==='classification'?'Classification':'Detailed sources'} › ${record.title}`));
  draw();renderTopics();const hash=new URLSearchParams({atlas:loaded.manifest.atlasId,version:loaded.manifest.atlasVersion,destination:id,space});history.replaceState(null,'',`#${hash}`);
}
function renderTopics(){
  const host=$('atlas-topics');host.replaceChildren();$('atlas-topics-heading').textContent=space==='classification'?(selectedId===layout()?.entryDestinationId?'Choose a field':'Topics in this view'):'Destinations in this view';
  const ids=topicIds.length?topicIds:[selectedId];ids.forEach((id,index)=>{const li=el('li');li.append(button(`${index+1}. ${records.get(id)?.title||id}`,()=>select(id)));host.append(li);});
}
function switchSpace(next,destination){
  space=next;classificationAnchor=null;$('atlas-space').value=space;const chart=layout();points=new Map();
  if(chart){const expected=space==='classification'?'classification_graph':'diffusion_chart';if(chart.kind!==expected||!Array.isArray(chart.nodes)||chart.nodes.length>1500)throw new Error('Unsupported or oversized map; use the static catalog.');for(const p of chart.nodes){if(!records.has(p.destinationId)||!Number.isFinite(p.x)||!Number.isFinite(p.y))throw new Error('Invalid map destination or coordinate');points.set(p.destinationId,p);}for(const edge of chart.edges||[])if(edge.kind!==(space==='classification'?'classification':'geometric_affinity'))throw new Error('Unexpected map relation type');}
  const fallback=space==='classification'?chart?.entryDestinationId||loaded.manifest.entryDestinationId:chart?.entryDestinationId||loaded.catalog.orientation?.portals?.find(p=>p.target==='detail')?.entryDestinationId||roots()[0]||loaded.manifest.entryDestinationId;
  select(destination&&records.has(destination)?destination:fallback);
}
async function open(entry,destination,requestedSpace){
  const ticket=++request;$('atlas-map-status').textContent='Opening the atlas…';const atlas=await loadAtlas(`/data/atlas/${encodeURIComponent(entry.atlasId)}/${encodeURIComponent(entry.atlasVersion)}`);if(ticket!==request)return;
  loaded=atlas;navigator=createAtlasNavigator(atlas);records=new Map(atlas.catalog.destinations.map(d=>[d.id,{...d,question:d.question??d.title}]));$('atlas-map-scope').textContent=atlas.manifest.scope.description;
  switchSpace(requestedSpace|| (atlas.catalog.orientation?'classification':'detail'),destination);$('atlas-map-status').textContent=`${atlas.catalog.destinations.length} recorded destinations. Source coverage and scientific status remain explicit on every destination.`;
}
$('atlas-space').addEventListener('change',()=>{try{switchSpace($('atlas-space').value);}catch(error){$('atlas-map-status').textContent=error.message;}});
$('atlas-zoom-in').addEventListener('click',()=>zoom(.8));$('atlas-zoom-out').addEventListener('click',()=>zoom(1.25));$('atlas-fit').addEventListener('click',fit);
let drag;map.addEventListener('pointerdown',event=>{if(event.target.closest('.atlas-map-node,.atlas-fixed-node'))return;drag={x:event.clientX,y:event.clientY,camera:{...camera}};map.setPointerCapture(event.pointerId);});map.addEventListener('pointermove',event=>{if(!drag)return;camera.x=drag.camera.x-(event.clientX-drag.x)/map.clientWidth*camera.width;camera.y=drag.camera.y-(event.clientY-drag.y)/map.clientHeight*camera.height;viewBox();});map.addEventListener('pointerup',()=>drag=null);map.addEventListener('pointercancel',()=>drag=null);map.addEventListener('wheel',event=>{event.preventDefault();zoom(event.deltaY>0?1.12:.89);},{passive:false});map.addEventListener('keydown',event=>{if(event.key==='+')zoom(.8);if(event.key==='-')zoom(1.25);if(event.key==='Home')fit();});
window.addEventListener('resize',()=>{if(loaded){if(space==='classification')draw();else fit();}});
$('atlas-find').addEventListener('input',async()=>{if(!navigator)return;const query=$('atlas-find').value.trim();if(!query){renderTopics();return;}await navigator.prepareSearch?.();if($('atlas-find').value.trim()!==query)return;const list=$('atlas-topics');list.replaceChildren();for(const result of navigator.search(query,{limit:15})){const li=el('li');li.append(button(result.title,()=>select(result.id)));list.append(li);}});
try{
  const response=await fetch('/data/atlas/index.json');if(!response.ok)throw new Error('No prepared atlas is installed in this retained release.');const index=await response.json(),fragment=new URLSearchParams(location.hash.slice(1));
  for(const entry of index.atlases||[]){const option=el('option',entry.title);option.value=`${entry.atlasId}/${entry.atlasVersion}`;$('atlas-select').append(option);}
  const entry=index.atlases.find(e=>e.atlasId===fragment.get('atlas')&&e.atlasVersion===fragment.get('version'))||index.atlases[0];if(!entry)throw new Error('The atlas catalog is empty.');$('atlas-select').value=`${entry.atlasId}/${entry.atlasVersion}`;
  $('atlas-select').addEventListener('change',()=>{const chosen=index.atlases.find(e=>`${e.atlasId}/${e.atlasVersion}`===$('atlas-select').value);open(chosen).catch(error=>$('atlas-map-status').textContent=error.message);});await open(entry,fragment.get('destination')||undefined,['classification','detail'].includes(fragment.get('space'))?fragment.get('space'):undefined);
}catch(error){$('atlas-map-status').textContent=error.message;$('atlas-map-scope').textContent='Atlas unavailable.';}
