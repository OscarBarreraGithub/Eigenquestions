/** Prepared source-backed destinations. Uses the shared session/view contract;
 * no embedding, clustering, semantic interpretation or new scientific inference. */
import {normalizeState, createSession} from '../protocol/session.mjs';
import {PREPARED_SOURCE_SHA256} from './prepared-identity.mjs';

export const PREPARED_VERSION = '1.0.0';
export const PREPARED_BUILDER = 'eigenquestions-prepared-atlas';
const MAX = {destinations: 10000, sources: 30000, memberships: 500000, relations: 50000};
const fail = message => { throw new Error(`Prepared atlas: ${message}`); };
const object = (value, name) => { if (!value || typeof value !== 'object' || Array.isArray(value) || ![Object.prototype,null].includes(Object.getPrototypeOf(value))) fail(`${name} must be a JSON object`); return value; };
const text = (value, name, max = 8000) => { if (typeof value !== 'string' || value.length > max) fail(`invalid ${name}`); return value; };
const identifier = (value, name) => { text(value, name, 200); if (!/^[a-zA-Z0-9][a-zA-Z0-9._:-]*$/.test(value)) fail(`invalid ${name}`); return value; };
const list = (value, name, max) => { if (!Array.isArray(value) || value.length > max) fail(`invalid ${name}`); return value; };
const strings = (value, name, max = 1000) => list(value, name, max).forEach(item => text(item, name));
const unique = (items, name) => { const map = new Map(); for (const item of items) { object(item,name); identifier(item.id,`${name} ID`); if (map.has(item.id)) fail(`duplicate ${name} ID ${item.id}`); map.set(item.id,item); } return map; };
const clone = value => structuredClone(value);

export function validateAtlas(manifest, catalog) {
  object(manifest, 'manifest'); object(catalog, 'catalog');
  if (manifest.schemaVersion !== '1.0.0' || manifest.kind !== 'eigenquestions-atlas') fail('unsupported manifest');
  for (const key of ['atlasId','atlasVersion','corpusId','entryDestinationId']) identifier(manifest[key],key);
  for (const value of [manifest.corpusContentHash, manifest.files?.catalog?.sha256]) if (!/^[a-f0-9]{64}$/.test(value || '')) fail('missing content hash');
  object(manifest.scope,'scope'); text(manifest.scope.description,'scope description');
  strings(manifest.scope.limitations ?? [],'limitations');
  const destinations = unique(list(catalog.destinations,'destinations',MAX.destinations),'destination');
  const sources = unique(list(catalog.sources,'sources',MAX.sources),'source');
  if (!destinations.has(manifest.entryDestinationId)) fail('entry destination is absent');
  for (const d of destinations.values()) {
    if (!['question','region','method','landmark'].includes(d.kind)) fail(`invalid destination kind ${d.id}`);
    text(d.title,'title',4000); text(d.question,'question',4000); text(d.summary,'summary');
    object(d.scope,'destination scope');
    for (const key of ['assumptions','includes','excludes','regimes','conventions']) strings(d.scope[key] ?? [],key);
    strings(d.aliases ?? [],'aliases',100); strings(d.evidenceIds,'evidence IDs',100);
    if (!d.evidenceIds.length && !d.metadataOnly) fail(`destination ${d.id} has no evidence`);
    for (const id of d.evidenceIds) if (!sources.has(id)) fail(`missing representative source ${id}`);
    text(d.scientificStatus,'scientific status'); text(d.placementStatus,'placement status');
    object(d.provenance,'destination provenance');
  }
  for (const s of sources.values()) { text(s.title,'source title',4000); if (s.kind !== 'vocabulary') text(s.paperId,'paper ID',300); object(s.evidence,'source evidence'); text(s.evidence.text,'source text',64000); }
  const memberships = list(catalog.memberships,'memberships',MAX.memberships), seen = new Set();
  for (const m of memberships) {
    object(m,'membership'); identifier(m.destinationId,'membership destination'); text(m.unitId,'unit ID',300);
    if (!destinations.has(m.destinationId)) fail('membership destination is absent');
    if (!Number.isFinite(m.weight) || m.weight < 0 || m.weight > 1) fail('membership weight must be in [0,1]');
    if (m.role !== undefined && !['on','using','evidence'].includes(m.role)) fail('unsupported membership role');
    if (m.year !== undefined && (!Number.isInteger(m.year) || m.year < 1000 || m.year > 3000)) fail('invalid membership year');
    if (m.lens !== undefined && !['physical_question','method'].includes(m.lens)) fail('invalid membership lens');
    if (m.perspectives !== undefined) strings(m.perspectives,'membership perspectives',20);
    const key = `${m.destinationId}\n${m.unitId}`; if (seen.has(key)) fail('duplicate membership'); seen.add(key);
    for (const key of ['sourceRow','browserVectorRow']) if (m[key] !== undefined && (!Number.isSafeInteger(m[key]) || m[key] < 0)) fail(`invalid ${key}`);
  }
  const relations = unique(list(catalog.relations,'relations',MAX.relations),'relation');
  const children = new Map();
  for (const r of relations.values()) {
    if (!destinations.has(r.source) || !destinations.has(r.target) || r.source === r.target) fail(`invalid relation endpoints ${r.id}`);
    identifier(r.type,'relation type'); text(r.rationale,'relation rationale'); text(r.status,'relation status');
    strings(r.evidenceIds,'relation evidence',100);
    if (!r.evidenceIds.length) fail(`relation ${r.id} has no evidence`);
    for (const id of r.evidenceIds) if (!sources.has(id)) fail(`missing relation source ${id}`);
    if (r.type === 'narrower') { if (!children.has(r.source)) children.set(r.source,[]); children.get(r.source).push(r.target); }
  }
  const visiting = new Set(), visited = new Set();
  function visit(id) { if (visiting.has(id)) fail('cyclic containment'); if (visited.has(id)) return; visiting.add(id); for (const child of children.get(id) || []) visit(child); visiting.delete(id); visited.add(id); }
  for (const id of destinations.keys()) visit(id);
  return {manifest,catalog};
}

export async function loadAtlas(base, {readJson, readText} = {}) {
  const path = file => `${String(base).replace(/\/$/,'')}/${file}`;
  const fetchText = async file => { const response = await fetch(file); if (!response.ok) fail(`cannot read ${file} (${response.status})`); const body = await response.text(); if (body.length > 64 * 1024 * 1024) fail('catalog exceeds 64 MiB'); return body; };
  readText ??= fetchText;
  // Exact bytes bind metadata as well as the separately checksummed catalog.
  // readJson remains accepted for callers sharing the native loader options.
  const manifestText = await readText(path('manifest.json'));
  const manifest = JSON.parse(manifestText), file = manifest.files?.catalog;
  if (!file || !/^[a-zA-Z0-9][a-zA-Z0-9._-]*\.json$/.test(file.path)) fail('invalid catalog file');
  const bytes = await readText(path(file.path));
  const hash = [...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(bytes)))].map(n=>n.toString(16).padStart(2,'0')).join('');
  if (hash !== file.sha256) fail('catalog checksum mismatch');
  const manifestSha256 = [...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(manifestText)))].map(n=>n.toString(16).padStart(2,'0')).join('');
  return {...validateAtlas(manifest,JSON.parse(bytes)),manifestSha256};
}

export function createAtlasNavigator(atlas) {
  const {manifest,catalog} = validateAtlas(atlas.manifest,atlas.catalog);
  if (!/^[a-f0-9]{64}$/.test(atlas.manifestSha256 || '')) fail('load the checksummed manifest before creating a navigator');
  const destinations = new Map(catalog.destinations.map(d=>[d.id,d])), sources = new Map(catalog.sources.map(s=>[s.id,s]));
  const memberships = new Map(), incident = new Map();
  for (const m of catalog.memberships) { if (!memberships.has(m.destinationId)) memberships.set(m.destinationId,[]); memberships.get(m.destinationId).push(m); }
  for (const rows of memberships.values()) rows.sort((a,b)=>b.weight-a.weight || a.unitId.localeCompare(b.unitId));
  for (const r of catalog.relations) for (const id of [r.source,r.target]) { if (!incident.has(id)) incident.set(id,[]); incident.get(id).push(r); }
  const computationId = `prepared:${PREPARED_VERSION}:${PREPARED_SOURCE_SHA256}:${atlas.manifestSha256}:${manifest.files.catalog.sha256}`;
  const selector = id => ({kind:'atlas-destination',atlasId:manifest.atlasId,atlasVersion:manifest.atlasVersion,destinationId:id});
  function destination(input) {
    if (!input || input.kind !== 'atlas-destination' || input.atlasId !== manifest.atlasId || input.atlasVersion !== manifest.atlasVersion) fail('atlas version mismatch; load the exact prepared atlas');
    const result = destinations.get(input.destinationId); if (!result) fail(`unknown destination ${input.destinationId}`); return result;
  }
  function resolveState(input, action) {
    const d = destination(input.selector);
    if (input.focusIds?.length) fail('prepared membership is pinned by destination; source anchors require an explicit native exploration');
    if (action && Object.hasOwn(action,'query') && action.query !== d.question) fail('prepared navigation needs a destination ID; title/alias lookup does not interpret paragraphs');
    if (action?.type === 'broaden') fail('choose an explicit broader connection; overlapping regions can have multiple parents');
    return {...input,schemaVersion:'1.1.0',corpusId:manifest.corpusId,computationId,query:d.question,focusIds:[],selector:selector(d.id)};
  }
  const initialState = resolveState({selector:selector(manifest.entryDestinationId)});
  function sourceRows(id, state = {}) {
    const excluded = new Set(state.constraints?.excludeIds || []);
    const yearOf = m => m.year ?? sources.get(m.unitId)?.year ?? (Number(String(sources.get(m.unitId)?.evidence?.date || '').slice(0,4)) || undefined);
    const rows = (memberships.get(id) || []).filter(m => {
      if (excluded.has(m.unitId)) return false;
      if (state.workRelation && state.workRelation !== 'either' && m.role !== state.workRelation) return false;
      const source = sources.get(m.unitId), year = yearOf(m), lens=m.lens ?? source?.evidence?.lens;
      const selectedLens = state.lens && state.lens !== 'combined' ? state.lens : state.intent === 'derive' ? 'method' : null;
      if (selectedLens && !lens) fail(`source ${m.unitId} lacks lens metadata; this perspective cannot cover the complete membership`);
      if (selectedLens && lens !== selectedLens) return false;
      if (state.intent === 'phenomenology' && !m.perspectives?.includes('phenomenology')) return false;
      if ((state.constraints?.yearMin !== undefined || state.constraints?.yearMax !== undefined) && !year) fail(`source ${m.unitId} lacks year metadata; this filter cannot cover the complete membership`);
      if (state.constraints?.yearMin !== undefined && !(year >= state.constraints.yearMin)) return false;
      if (state.constraints?.yearMax !== undefined && !(year <= state.constraints.yearMax)) return false;
      return true;
    });
    if (state.intent === 'recent') rows.sort((a,b)=>(yearOf(b)||0)-(yearOf(a)||0)||b.weight-a.weight||a.unitId.localeCompare(b.unitId));
    return rows;
  }
  function connections(id) {
    if (!destinations.has(id)) fail('unknown destination');
    return (incident.get(id) || []).map(r => {
      const outgoing = r.source === id, target = destinations.get(outgoing ? r.target : r.source);
      return {...clone(r),destinationId:target.id,title:target.title,question:target.question,selector:selector(target.id),traversal:outgoing?'outgoing':'incoming',navigationKind:r.type === 'narrower' ? outgoing?'narrower':'broader':r.type};
    }).sort((a,b) => (a.navigationKind==='narrower'?0:a.navigationKind==='broader'?2:1)-(b.navigationKind==='narrower'?0:b.navigationKind==='broader'?2:1) || a.title.localeCompare(b.title) || a.id.localeCompare(b.id));
  }
  function computeView(input) {
    const state = normalizeState(input), canonical = normalizeState(resolveState(state)), d = destination(state.selector);
    if (state.id !== canonical.id || state.computationId !== computationId) fail('state does not match canonical prepared destination');
    const links = connections(d.id), foreground = links.slice(0,15), selected = new Set(d.evidenceIds.slice(0,20));
    for (const link of foreground) { for (const id of link.evidenceIds.slice(0,3)) selected.add(id); for (const id of destinations.get(link.destinationId).evidenceIds.slice(0,3)) selected.add(id); }
    const rows = sourceRows(d.id,state);
    for (const row of rows.slice(0,30)) if (sources.has(row.unitId)) selected.add(row.unitId);
    const matchingIds=new Set(rows.map(row=>row.unitId));
    const nodes = [...selected].filter(id=>sources.has(id)).map(id=>({...clone(sources.get(id)),atlasRole:matchingIds.has(id)?'matching-source':'context-evidence'}));
    const directions = foreground.map(link => {
      const target = destinations.get(link.destinationId), ids = [...new Set([...link.evidenceIds,...target.evidenceIds])].filter(id=>selected.has(id));
      return {id:`connection:${link.id}`,label:target.title,query:target.question,summary:target.summary,selector:link.selector,seedIds:[],memberIds:ids,evidenceIds:ids,intent:state.intent,lens:state.lens,workRelation:state.workRelation,sourceCount:memberships.get(target.id)?.length || 0,relationType:link.type,navigationKind:link.navigationKind,relation:link};
    });
    const warnings = [...(manifest.scope.limitations || [])];
    if (state.workRelation !== 'either') warnings.push('ON/USING source selection uses explicitly recorded membership roles. Unclassified sources are omitted from that selection.');
    if (state.intent === 'derive') warnings.push('Derivation reading selects recorded method facets. It does not perform or certify a new derivation.');
    if (state.intent === 'phenomenology') warnings.push('Phenomenology selects explicitly tagged memberships only. Untagged sources remain unclassified.');
    if (state.intent === 'recent') warnings.push('Recent orders recorded publication years within this frozen corpus; undated sources follow dated sources. This is not a live search.');
    return {schemaVersion:'1.1.0',corpusId:manifest.corpusId,computationId,stateId:state.id,query:d.question,nodes,directions,edges:[],chart:null,warnings,
      diagnostics:{scope:{...clone(manifest.scope),snapshotDate:manifest.snapshotDate},distinctPapers:new Set(nodes.filter(n=>n.kind!=='vocabulary'&&n.paperId).map(n=>n.paperId)).size,prepared:true},
      atlas:{atlasId:manifest.atlasId,atlasVersion:manifest.atlasVersion,selector:state.selector,destination:clone(d),membershipCount:(memberships.get(d.id)||[]).length,matchingSourceCount:rows.length,matchingSourceIds:rows.slice(0,30).map(row=>row.unitId),displayedSourceCount:nodes.length,connectionCount:links.length,connections:links,membershipNotice:'Displayed source descriptions are a bounded sample. Exact membership is pinned by this atlas version and destination.',contextEvidenceNotice:'Context evidence supports destination definitions and connections. It may fall outside the selected source filters and is labeled separately.'}};
  }
  return {computationId,initialState,resolveState,computeView,
    createSession:fields=>createSession(resolveState({...initialState,...fields})),
    destination:id=>clone(destination(selector(id))),
    connections:(id,{offset=0,limit=100}={})=>({total:connections(id).length,items:connections(id).slice(offset,offset+Math.min(100,limit))}),
    sources:(id,{offset=0,limit=30,...state}={})=>{if(!Number.isInteger(offset)||offset<0||!Number.isInteger(limit)||limit<1||limit>100)fail('invalid source page');const rows=sourceRows(id,state);return {total:rows.length,offset,items:rows.slice(offset,offset+limit).map(m=>({...clone(m),source:sources.has(m.unitId)?clone(sources.get(m.unitId)):null}))};},
    getEvidence:ids=>ids.map(id=>sources.has(id)?clone(sources.get(id)):{id,error:'Source description not bundled; read the frozen corpus source shard using its membership row.'}),
    search:(query,{limit=10}={})=>{
      text(query,'lookup query',4000); if(!Number.isInteger(limit)||limit<1||limit>30)fail('lookup limit must be 1–30');
      const normalized=query.trim().toLowerCase(),tokens=normalized.match(/[\p{L}\p{N}]+/gu)||[];
      if (!tokens.length) return [];
      return catalog.destinations.map(d=>{const names=[d.title,d.question,...(d.aliases||[])].map(s=>s.toLowerCase()),haystack=names.join(' ');const score=names.includes(normalized)?100:tokens.filter(t=>haystack.includes(t)).length/tokens.length;return {id:d.id,title:d.title,question:d.question,summary:d.summary,scope:clone(d.scope),selector:selector(d.id),score,matchKind:'title-and-alias-lookup'};}).filter(d=>d.score>0).sort((a,b)=>b.score-a.score||a.id.localeCompare(b.id)).slice(0,limit);
    }};
}

export function atlasAddress(state, origin = 'https://eigenquestions.com') {
  const normalized=normalizeState(state); if (!normalized.selector) fail('a prepared selector is required');
  if (normalized.constraints.excludeIds.length || normalized.constraints.yearMin !== undefined || normalized.constraints.yearMax !== undefined) fail('filtered states require a capsule until compact filter addresses are supported');
  const hash=new URLSearchParams({atlas:normalized.selector.atlasId,version:normalized.selector.atlasVersion,destination:normalized.selector.destinationId,lens:normalized.lens,intent:normalized.intent,relation:normalized.workRelation});
  return `${origin.replace(/\/$/,'')}/#${hash}`;
}

/** Fetch only metadata/source shards, never vectors, to inspect full membership. */
export function createAtlasSourceReader(atlas, {base='/data',readText}={}) {
  const cache=new Map();
  const read=readText || (async url=>{const response=await fetch(url);if(!response.ok)fail(`source file unavailable (${response.status})`);return response.text();});
  const path=name=>`${String(base).replace(/\/$/,'')}/${name}`;
  const manifestPromise=read(path('manifest.json')).then(JSON.parse).then(manifest=>{if(manifest.corpusId!==atlas.manifest.corpusId||manifest.contentHash!==atlas.manifest.corpusContentHash)fail('frozen source corpus identity mismatch');return manifest;});
  async function file(descriptor) {
    if(!descriptor||!/^[a-zA-Z0-9._-]+$/.test(descriptor.path))fail('invalid source shard');
    if(!cache.has(descriptor.path))cache.set(descriptor.path,(async()=>{const body=await read(path(descriptor.path));const hash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(body)))].map(n=>n.toString(16).padStart(2,'0')).join('');if(hash!==descriptor.sha256)fail(`source checksum mismatch ${descriptor.path}`);return JSON.parse(body);})());
    return cache.get(descriptor.path);
  }
  return async rows=>{
    const manifest=await manifestPromise;
    const papers=await file(manifest.files.papers),byPaper=new Map(papers.map(p=>[p.id,p]));
    return Promise.all(rows.map(async row=>{
      if(row.source)return row;
      if(!Number.isSafeInteger(row.browserVectorRow))fail(`membership ${row.unitId} lacks its frozen source row`);
      const descriptor=manifest.files.units.find(s=>row.browserVectorRow>=s.start&&row.browserVectorRow<s.start+s.count);
      const units=await file(descriptor),unit=units[row.browserVectorRow-descriptor.start];
      if(unit?.id!==row.unitId)fail('source row/ID mismatch');
      const paper=byPaper.get(unit.paperId);if(!paper)fail('source paper is absent');
      return {...row,source:{id:unit.id,paperId:unit.paperId,title:paper.title,sourceUrl:paper.url,year:paper.year,label:unit.text,evidence:{...unit.evidence,id:unit.id,text:unit.text,lens:unit.lens,date:paper.date||paper.year}}};
    }));
  };
}
