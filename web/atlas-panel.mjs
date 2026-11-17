/** Text-first prepared destination details and local research notes. */
const element=(tag,text,className)=>{const node=document.createElement(tag);if(text!==undefined)node.textContent=text;if(className)node.className=className;return node;};
const noteKey=selector=>`eigenquestions:work-note:v1:${selector.atlasId}:${selector.atlasVersion}:${selector.destinationId}`;
const noteBuffers=new Map();
const readNote=selector=>{if(noteBuffers.has(noteKey(selector)))return noteBuffers.get(noteKey(selector));try{return JSON.parse(localStorage.getItem(noteKey(selector))||'null');}catch{return null;}};
const download=(name,value)=>{const url=URL.createObjectURL(new Blob([JSON.stringify(value,null,2)],{type:'application/json'}));const link=element('a');link.href=url;link.download=name;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};

const contributionLabels={addresses:'Addresses this scope',instantiates:'Example within this scope',specializes:'Specializes this scope',method:'Method contribution',boundary:'Boundary or limitation',comparison:'Comparison context'};
function sourceContributions(record,navigator,readSources,onError,contextForSource){
  const rows=record.sourceContributions||[];if(!rows.length)return null;
  const disclosure=element('details'),body=element('div'),more=element('button','Read source contributions'),progress=element('p'),groups=new Map();let offset=0,started=false;
  disclosure.className='source-contributions';disclosure.append(element('summary',`Source contributions (${rows.length})`),element('p','These roles describe how each source contributes to this scope. A shared source does not make questions equivalent, and a method contribution does not establish applicability to every case.'),body,progress,more);more.type='button';
  const load=async()=>{more.disabled=true;started=true;try{
    if(!readSources)throw new Error('Source reading is still loading. Try again after the atlas opens.');
    const selected=rows.slice(offset,offset+20).map(row=>{const source=navigator?.getEvidence?.([row.unitId])?.[0];return source&&!source.error?{...row,source}:row;});
    const page=await readSources(selected);if(!disclosure.isConnected)return;
    for(const row of page){const source=row.source;let group=groups.get(source.paperId);
      if(!group){const paper=element('details'),summary=element('summary');paper.append(summary);if(/^https?:\/\//.test(source.sourceUrl||'')){const link=element('a','Read paper');link.href=source.sourceUrl;link.target='_blank';link.rel='noopener noreferrer';paper.append(link);}group={paper,summary,title:source.title,count:0};groups.set(source.paperId,group);body.append(paper);}
      group.count++;group.summary.textContent=`${group.title} (${group.count} contribution${group.count===1?'':'s'})`;
      const item=element('article');item.append(element('h3',contributionLabels[row.role]||row.role),element('p',row.basis==='source_excerpt_checked'?'Source excerpt checked; see this destination’s reading limits.':'Extracted description checked; this does not claim a full-paper reading.'));
      if(row.qualification)item.append(element('p',row.qualification));item.append(element('p',source.evidence.text),element('small',`${row.lens} · ${row.unitId}`));
      const provenance=element('details');provenance.append(element('summary','Review and evidence references'),element('pre',JSON.stringify({role:row.role,basis:row.basis,decisionId:row.decisionId,scopeContentSha256:row.scopeContentSha256,evidenceRefs:row.evidenceRefs,provenance:row.provenance},null,2)));item.append(provenance);if(contextForSource)item.append(contextForSource(row.unitId));group.paper.append(item);
    }
    offset+=page.length;progress.textContent=`${offset} of ${rows.length} contributions loaded; these are separate from source membership.`;more.hidden=offset>=rows.length;more.textContent='Read next contributions';more.disabled=false;
  }catch(error){started=false;more.disabled=false;onError(error.message);}};
  more.addEventListener('click',load);disclosure.addEventListener('toggle',()=>{if(disclosure.open&&!started)return load();});return disclosure;
}

export function renderAtlasPanel({capsule,navigator,manifest,readSources,contextForSource,onNavigate,onNative,onError}) {
  let host=document.getElementById('atlas-panel');
  if(!host){host=element('section',undefined,'atlas-panel');host.id='atlas-panel';document.querySelector('.explorer').after(host);}
  host.replaceChildren();host.hidden=!capsule.snapshot.view.atlas;const previousSummary=document.getElementById('atlas-current-summary');if(previousSummary)previousSummary.hidden=host.hidden;if(host.hidden)return;
  const {atlas}=capsule.snapshot.view,record=atlas.destination,selector=atlas.selector;
  let currentSummary=document.getElementById('atlas-current-summary');if(!currentSummary){currentSummary=element('p',undefined,'atlas-summary');currentSummary.id='atlas-current-summary';document.getElementById('full-question-details').insertBefore(currentSummary,document.getElementById('full-question-text'));}currentSummary.textContent=record.summary;currentSummary.hidden=false;
  const scope=element('details'),summary=element('summary',record.metadataOnly?'Classification source and coverage':'Scope, assumptions and sources');scope.append(summary);
  if(record.whyItMatters)scope.append(element('p',record.whyItMatters));
  for(const [key,label]of[['includes','Includes'],['excludes','Distinctions and exclusions'],['assumptions','Assumptions'],['regimes','Regimes'],['conventions','Conventions']]){
    if(!record.scope[key]?.length)continue;scope.append(element('h3',label));const list=element('ul');for(const value of record.scope[key])list.append(element('li',value));scope.append(list);
  }
  if(record.methods?.length){scope.append(element('h3','Methods'));const list=element('ul');for(const method of record.methods)list.append(element('li',typeof method==='string'?method:method.label||method.description||JSON.stringify(method)));scope.append(list);}
  for(const reading of new Set([record.readingLimit,record.readingCoverage].filter(Boolean).map(value=>typeof value==='string'?value:JSON.stringify(value))))scope.append(element('p',reading));
  scope.append(element('p',`Scientific status: ${record.scientificStatus}. Placement: ${record.placementStatus}.`,'atlas-provenance'));
  if(!record.metadataOnly)scope.append(element('p',atlas.membershipNotice));
  if(record.metadataOnly)for(const source of navigator?.getEvidence?.(record.evidenceIds||[])||[]){if(!/^https?:\/\//.test(source.sourceUrl||''))continue;const link=element('a',source.title);link.href=source.sourceUrl;link.target='_blank';link.rel='noopener noreferrer';scope.append(link);}
  const coverage=element('div');
  for(const [key,label]of[['sourceContextSummary','Frozen source inventory and context coverage'],['unrepresentedPapers','Bibliographic records without source text']]){const file=manifest?.files?.[key];if(!file||!(/^[a-zA-Z0-9][a-zA-Z0-9._/-]*\.json$/.test(file.path))||file.path.split('/').includes('..'))continue;const line=element('p'),link=element('a',label);link.href=`/data/atlas/${encodeURIComponent(selector.atlasId)}/${encodeURIComponent(selector.atlasVersion)}/${file.path}`;line.append(link);coverage.append(line);}
  if(coverage.children.length){scope.append(element('h3','Coverage of the frozen source collection'),coverage);}
  const browse=element('button',`Browse all ${atlas.membershipCount.toLocaleString()} sources`);browse.type='button';const sourceList=element('div',undefined,'atlas-member-list');let offset=0;
  browse.hidden=atlas.membershipCount===0;
  browse.addEventListener('click',async()=>{browse.disabled=true;try{await navigator.prepareSources?.(selector.destinationId);const page=navigator.sources(selector.destinationId,{offset,limit:20});const rows=await readSources(page.items);if(!host.isConnected||capsule.snapshot.view.atlas.selector.destinationId!==selector.destinationId)return;for(const row of rows){const source=row.source,line=element('article');const title=element('a',source.title);let url;try{url=new URL(source.sourceUrl);}catch{}if(url&&['http:','https:'].includes(url.protocol)){title.href=url.href;title.target='_blank';title.rel='noopener noreferrer';}line.append(title,element('p',source.evidence.text),element('small',`${source.evidence.lens||'Source'} · ${source.evidence.date||'date unavailable'} · ${source.id}`));sourceList.append(line);}offset+=rows.length;browse.textContent=offset<page.total?`Show next sources (${offset} of ${page.total})`:`All ${page.total} sources shown`;browse.disabled=offset>=page.total;}catch(error){browse.disabled=false;onError(error.message);}});
  scope.append(browse,sourceList);
  if(atlas.contextMembershipCount){
    const methods=element('button',`Browse recorded methods (${atlas.contextMembershipCount} contextual associations)`),methodList=element('div',undefined,'atlas-member-list');methods.type='button';let methodOffset=0;
    methods.addEventListener('click',async()=>{methods.disabled=true;try{await navigator.prepareSources?.(selector.destinationId);const page=navigator.sources(selector.destinationId,{offset:methodOffset,limit:20,lens:'method',includeContext:true}),rows=await readSources(page.items);if(!methodList.isConnected)return;for(const row of rows){const source=row.source,line=element('article'),link=element('a',source.title);if(/^https?:\/\//.test(source.sourceUrl||'')){link.href=source.sourceUrl;link.target='_blank';link.rel='noopener noreferrer';}line.append(link,element('p',source.evidence.text),element('small',`${row.associationScope?'Same-paper context; applicability is not established':'Primary recorded source'} · ${source.id}`));methodList.append(line);}methodOffset+=rows.length;methods.textContent=methodOffset<page.total?`Show next methods (${methodOffset} of ${page.total})`:`All ${page.total} method descriptions shown`;methods.disabled=methodOffset>=page.total;}catch(error){methods.disabled=false;onError(error.message);}});
    scope.append(element('p','Contextual methods share a paper with primary sources. This association does not establish that the method applies to every question here.'),methods,methodList);
  }
  host.append(scope);
  const contributions=sourceContributions(record,navigator,readSources,onError,contextForSource);if(contributions)host.append(contributions);
  const connections=element('details'),connectionList=element('div',undefined,'atlas-connection-list');connections.append(element('summary',`All connections (${atlas.connectionCount})`));
  for(const relation of atlas.connections){const row=element('div'),button=element('button',relation.title);button.type='button';button.addEventListener('click',()=>onNavigate({type:'navigate',selector:relation.selector}));row.append(button,element('span',` ${relation.navigationKind.replaceAll('_',' ')} · ${relation.traversal} recorded relation`),element('p',relation.rationale));connectionList.append(row);}connections.append(connectionList);host.append(connections);
  const note=element('details'),textarea=element('textarea');note.append(element('summary','Your work on this question'));
  textarea.rows=4;textarea.maxLength=12000;textarea.placeholder='A private local work note, attached to this destination.';textarea.setAttribute('aria-label','Local research work note');textarea.value=readNote(selector)?.text||'';
  const notice=element('p','Saved on this browser only. Share destination links separately; your note is not included in them.'),actions=element('div',undefined,'tool-buttons'),feedback=element('p');
  const capture=()=>{const previous=readNote(selector),value={schemaVersion:'1.0.0',kind:'eigenquestions-work-note',id:previous?.id||crypto.randomUUID(),target:structuredClone(selector),text:textarea.value,createdAt:previous?.createdAt||new Date().toISOString(),modifiedAt:new Date().toISOString()};noteBuffers.set(noteKey(selector),value);return value;};
  const save=()=>{const value=capture();localStorage.setItem(noteKey(selector),JSON.stringify(value));return value;};
  textarea.addEventListener('input',()=>{try{save();feedback.textContent='Saved locally.';}catch{feedback.textContent='Local storage is unavailable. This edit is retained in this tab; export it before closing the tab.';}});
  for(const [label,handler]of[['Save note locally',()=>{save();feedback.textContent='Saved locally for this destination.';}],['Export note',()=>{download('eigenquestions-work-note.json',capture());feedback.textContent='Exported note. The file contains your note text.';}]]){const button=element('button',label);button.type='button';button.addEventListener('click',()=>{try{handler();}catch(error){onError(error.message);}});actions.append(button);}
  const input=element('input');input.type='file';input.accept='.json,application/json';input.hidden=true;const open=element('button','Import note');open.type='button';open.addEventListener('click',()=>input.click());input.addEventListener('change',async()=>{try{const file=input.files[0];if(!file||file.size>64000)throw new Error('Note file is absent or exceeds 64 KB.');const value=JSON.parse(await file.text());if(value.kind!=='eigenquestions-work-note'||value.schemaVersion!=='1.0.0'||typeof value.text!=='string'||value.text.length>12000||!['kind','atlasId','atlasVersion','destinationId'].every(key=>value.target?.[key]===selector[key]))throw new Error('This note belongs to a different destination or version. Open that destination before importing.');textarea.value=value.text;save();feedback.textContent='Imported and saved locally.';}catch(error){onError(error.message);}finally{input.value='';}});actions.append(open,input);note.append(notice,textarea,actions,feedback);host.append(note);
  const native=element('button','Start source exploration from this question');native.type='button';native.addEventListener('click',()=>onNative(record.question));host.append(native);
}
