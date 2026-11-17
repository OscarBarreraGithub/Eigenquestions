/** Prepared source-backed destinations. Uses the shared session/view contract;
 * no embedding, clustering, semantic interpretation or new scientific inference. */
import {normalizeState, createSession} from '../protocol/session.mjs';
import {PREPARED_SOURCE_SHA256} from './prepared-identity.mjs';

export const PREPARED_VERSION = '1.0.0';
export const PREPARED_BUILDER = 'eigenquestions-prepared-atlas';
const MAX = {destinations: 18000, sources: 30000, memberships: 500000, relations: 50000, destinationEvidence: 256, contextEvidence: 100, membershipSample: 36};
const fail = message => { throw new Error(`Prepared atlas: ${message}`); };
const object = (value, name) => { if (!value || typeof value !== 'object' || Array.isArray(value) || ![Object.prototype,null].includes(Object.getPrototypeOf(value))) fail(`${name} must be a JSON object`); return value; };
const text = (value, name, max = 8000) => { if (typeof value !== 'string' || value.length > max) fail(`invalid ${name}`); return value; };
const identifier = (value, name) => { text(value, name, 200); if (!/^[a-zA-Z0-9][a-zA-Z0-9._:-]*$/.test(value)) fail(`invalid ${name}`); return value; };
const list = (value, name, max) => { if (!Array.isArray(value) || value.length > max) fail(`invalid ${name}`); return value; };
const strings = (value, name, max = 1000) => list(value, name, max).forEach(item => text(item, name));
const unique = (items, name) => { const map = new Map(); for (const item of items) { object(item,name); identifier(item.id,`${name} ID`); if (map.has(item.id)) fail(`duplicate ${name} ID ${item.id}`); map.set(item.id,item); } return map; };
const clone = value => structuredClone(value);
function validateRouteTitles(relation){for(const key of ['title','incomingTitle'])if(relation[key]!==undefined)text(relation[key],`reviewed route ${key}`,4000);}
const stableJson=value=>JSON.stringify(value&&typeof value==='object'?(Array.isArray(value)?value.map(item=>JSON.parse(stableJson(item))):Object.fromEntries(Object.keys(value).sort().filter(key=>value[key]!==undefined).map(key=>[key,JSON.parse(stableJson(value[key]))]))):value);

const lazyCatalog = catalog => catalog.storage === 'lazy-destinations-v1';
function fileDescriptor(value) {
  object(value,'file descriptor');
  if(!/^[a-zA-Z0-9][a-zA-Z0-9._/-]*\.json$/.test(value.path||'')||value.path.split('/').includes('..')||!/^[a-f0-9]{64}$/.test(value.sha256||'')||!Number.isSafeInteger(value.bytes)||value.bytes<1||value.bytes>25*1024*1024)fail('invalid lazy file descriptor');
  return value;
}
function validateLazyCatalog(manifest,catalog) {
  if(manifest.schemaVersion!=='1.1.0'||manifest.kind!=='eigenquestions-atlas')fail('unsupported lazy manifest');
  for(const key of ['atlasId','atlasVersion','corpusId','entryDestinationId'])identifier(manifest[key],key);
  for(const hash of [manifest.corpusContentHash,manifest.files?.catalog?.sha256])if(!/^[a-f0-9]{64}$/.test(hash||''))fail('missing content hash');
  object(manifest.scope,'scope');text(manifest.scope.description,'scope description');strings(manifest.scope.limitations||[],'limitations');
  const destinations=unique(list(catalog.destinations,'destinations',18000),'destination');
  if(!destinations.has(manifest.entryDestinationId))fail('entry destination is absent');
  if(catalog.fineIndex)fileDescriptor(catalog.fineIndex);
  if(catalog.fineLookup){if(catalog.fineLookup.kind!=='source-question-hash-prefix'||catalog.fineLookup.prefixLength!==2)fail('unsupported fine lookup partition');object(catalog.fineLookup.shards,'fine index buckets');for(const [prefix,descriptor] of Object.entries(catalog.fineLookup.shards)){if(!/^[a-f0-9]{2}$/.test(prefix))fail('invalid fine index bucket');fileDescriptor(descriptor);}}
  object(catalog.detailShards,'detail shards');for(const descriptor of Object.values(catalog.detailShards))fileDescriptor(descriptor);
  if((catalog.sources||[]).length||(catalog.memberships||[]).length)fail('lazy catalog must not inline source or membership payloads');
  for(const d of destinations.values()){
    if(!['question','region','method','landmark'].includes(d.kind))fail('invalid destination kind');
    text(d.title,'title',4000);text(d.question??d.title,'question',4000);if(d.summary!==undefined)text(d.summary,'summary');strings(d.aliases||[],'aliases',100);
    for(const key of ['membershipCount','contextMembershipCount','paperCount'])if(!Number.isSafeInteger(d[key])||d[key]<0||d[key]>30000)fail('invalid indexed source count');
    if((catalog.fineIndex||d.connectionCount!==undefined)&&(!Number.isSafeInteger(d.connectionCount)||d.connectionCount<0||d.connectionCount>100000))fail('invalid indexed connection count');
    if(!catalog.detailShards[d.detail?.shardId])fail('destination detail shard is absent');
  }
  const children=new Map();
  for(const r of unique(list(catalog.relations,'relations',100000),'relation').values()){
    validateRouteTitles(r);
    if(!destinations.has(r.source)||!destinations.has(r.target)||r.source===r.target)fail('invalid relation endpoints');identifier(r.type,'relation type');text(r.rationale,'relation rationale');text(r.status,'relation status');strings(r.evidenceIds,'relation evidence',100);if(!r.evidenceIds.length)fail('relation has no evidence');
    if(r.type==='narrower'){if(!children.has(r.source))children.set(r.source,[]);children.get(r.source).push(r.target);}
  }
  const visiting=new Set(),visited=new Set();function visit(id){if(visiting.has(id))fail('cyclic containment');if(visited.has(id))return;visiting.add(id);for(const child of children.get(id)||[])visit(child);visiting.delete(id);visited.add(id);}for(const id of destinations.keys())visit(id);
  return {manifest,catalog};
}

export function expandAtlasIndex(catalog){
  if(!catalog.indexTemplates)return catalog;
  const expanded={...catalog};
  for(const section of ['destinations','relations'])expanded[section]=catalog[section].map(row=>{if(row.indexTemplate===undefined)return row;const template=catalog.indexTemplates[section]?.[row.indexTemplate];object(template,'index template');if(['id','source','target','indexTemplate'].some(key=>Object.hasOwn(template,key)))fail('index template cannot provide identity or endpoints');const result={...template,...row};delete result.indexTemplate;return result;});
  return expanded;
}

export function validateAtlas(manifest, catalog) {
  object(manifest, 'manifest'); object(catalog, 'catalog');
  if(lazyCatalog(catalog))return validateLazyCatalog(manifest,catalog);
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
    strings(d.aliases ?? [],'aliases',100); strings(d.evidenceIds,'evidence IDs',MAX.destinationEvidence);
    strings(d.contextSourceIds ?? [],'context source IDs',MAX.contextEvidence);
    if (!d.evidenceIds.length && !d.metadataOnly) fail(`destination ${d.id} has no evidence`);
    for (const id of d.evidenceIds) if (!sources.has(id)) fail(`missing representative source ${id}`);
    for (const id of d.contextSourceIds || []) if (!sources.has(id)) fail(`missing contextual source ${id}`);
    text(d.scientificStatus,'scientific status'); text(d.placementStatus,'placement status');
    object(d.provenance,'destination provenance');
    const contributions=d.sourceContributions||[];list(contributions,'source contributions',5000);if(d.metadataOnly&&contributions.length)fail('metadata-only destination cannot claim source contributions');const contributionKeys=new Set();
    for(const row of contributions){
      object(row,'source contribution');if(row.destinationId!==d.id)fail('source contribution has a foreign destination');text(row.unitId,'contribution unit ID',300);text(row.paperId,'contribution paper ID',300);text(row.decisionId,'contribution decision ID',500);if(!row.unitId.trim()||!row.paperId.trim()||!row.decisionId.trim())fail('source contribution has an empty reference');
      if(!['addresses','instantiates','specializes','method','boundary','comparison'].includes(row.role)||!['description_checked','source_excerpt_checked'].includes(row.basis)||row.contributionStatus!=='accepted_typed_contribution')fail('invalid typed contribution role, basis or status');
      if(row.workRelation!==undefined||row.primary!==undefined||row.weight!==undefined)fail('a contribution cannot declare membership or USING');
      if(!['physical_question','method'].includes(row.lens)||!['sourceRow','browserVectorRow'].every(key=>Number.isSafeInteger(row[key])&&row[key]>=0))fail('source contribution lacks exact frozen rows');
      if(!/^[a-f0-9]{64}$/.test(row.scopeContentSha256||''))fail('source contribution lacks scope binding');list(row.evidenceRefs,'contribution evidence references',1000);if(row.qualification!==undefined)text(row.qualification,'contribution qualification');
      if(!['doesNotAssertDirectHome','doesNotAssertEquivalence','doesNotAssertMethodApplicability'].every(key=>row.provenance?.[key]===true))fail('source contribution lacks semantic qualifications');
      const key=`${row.unitId}\n${row.role}`;if(contributionKeys.has(key))fail('duplicate typed source contribution');contributionKeys.add(key);
    }

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
    if(m.associationScope!==undefined){if(m.associationScope!=='same_paper_context'||m.placementStatus!=='context_only'||m.role!=='evidence'||m.lens!=='method')fail('contextual methods require same-paper scope, context_only placement, evidence role and method lens');text(m.paperId,'context association paper',300);object(m.associationProvenance,'context association provenance');}
    const key = `${m.destinationId}\n${m.unitId}`; if (seen.has(key)) fail('duplicate membership'); seen.add(key);
    for (const key of ['sourceRow','browserVectorRow']) if (m[key] !== undefined && (!Number.isSafeInteger(m[key]) || m[key] < 0)) fail(`invalid ${key}`);
  }
  const relations = unique(list(catalog.relations,'relations',MAX.relations),'relation');
  const fullMemberships=new Map();
  for(const d of destinations.values())if(d.membershipStatus==='complete'||d.membershipComplete===true)fullMemberships.set(d.id,new Set());
  for(const m of memberships)if(!m.associationScope)fullMemberships.get(m.destinationId)?.add(m.unitId);
  const children = new Map();
  for (const r of relations.values()) {
    validateRouteTitles(r);
    if (!destinations.has(r.source) || !destinations.has(r.target) || r.source === r.target) fail(`invalid relation endpoints ${r.id}`);
    identifier(r.type,'relation type'); text(r.rationale,'relation rationale'); text(r.status,'relation status');
    strings(r.evidenceIds,'relation evidence',100);
    if (!r.evidenceIds.length) fail(`relation ${r.id} has no evidence`);
    for (const id of r.evidenceIds) if (!sources.has(id)) fail(`missing relation source ${id}`);
    if (r.type === 'narrower') {
      if (!children.has(r.source)) children.set(r.source,[]); children.get(r.source).push(r.target);
      if(fullMemberships.has(r.source)&&fullMemberships.has(r.target))for(const id of fullMemberships.get(r.target))if(!fullMemberships.get(r.source).has(id))fail(`complete child membership escapes parent on ${r.id}`);
    }
  }
  const visiting = new Set(), visited = new Set();
  function visit(id) { if (visiting.has(id)) fail('cyclic containment'); if (visited.has(id)) return; visiting.add(id); for (const child of children.get(id) || []) visit(child); visiting.delete(id); visited.add(id); }
  for (const id of destinations.keys()) visit(id);
  if(catalog.sourceObjects||catalog.sourceRelations||catalog.sourceAttachments)validateSourceContext(catalog);
  return {manifest,catalog};
}

/** Source-science IDs and destination IDs belong to separate relation layers. */
export function validateSourceContext(context) {
  object(context,'source context');
  const objects=unique(list(context.sourceObjects||[],'source objects',30000),'source object');
  const relations=unique(list(context.sourceRelations||[],'source relations',50000),'source relation');
  for(const source of objects.values()){text(source.kind,'source object kind',200);text(source.paperId,'source object paper',300);text(source.text,'source object text',64000);object(source.provenance,'source object provenance');}
  const statuses=new Set(['reviewed_scoped','source_local_assertion','extraction_inference','local_nomination_only','unvalidated_mention','structural']);
  for(const relation of relations.values()){
    if(!objects.has(relation.source)||!objects.has(relation.target))fail('source-science relation endpoint is absent');
    text(relation.type,'source relation type',200);if(!statuses.has(relation.semanticStatus))fail('source relation needs an explicit semanticStatus');
    object(relation.provenance,'source relation provenance');
  }
  for(const attachment of list(context.sourceAttachments||[],'source attachments',30000)){
    text(attachment.unitId,'attachment unit ID',300);
    if(!['direct_record_relation','shared_extraction_window_context','same_paper_context'].includes(attachment.scope))fail('source attachment scope must distinguish direct relation from context');
    strings(attachment.objectIds||[],'attached objects',30000);strings(attachment.relationIds||[],'attached relations',50000);
    for(const id of attachment.objectIds||[])if(!objects.has(id))fail('attached source object is absent');
    for(const id of attachment.relationIds||[])if(!relations.has(id))fail('attached source relation is absent');
  }
  list(context.sourceAssessments||[],'source assessments',10000).forEach(value=>object(value,'source assessment'));
  list(context.sourceEvidence||[],'source evidence locators',200000).forEach(value=>{object(value,'source evidence locator');text(value.id,'namespaced evidence ID',500);});
  return context;
}

/** Exact method anchors and context; no text similarity or relation projection. */
export function resolveAtlasContextOverride(unitId,descriptor,payload) {
  const override=descriptor.attachmentOverride,policy='source_anchors_and_record_context_v1';
  if(override?.policy!==policy)fail('unsupported source attachment override policy');
  text(descriptor.shardId,'source-context paper ID',300);strings(override.anchorObjectIds||[],'anchor object IDs',500);strings(override.sourceRecordIds||[],'source record IDs',1000);
  const paper=descriptor.shardId,objects=new Map(payload.sourceObjects.map(o=>[o.id,o])),relations=new Map((payload.sourceRelations||[]).map(r=>[r.id,r])),requested=new Set(override.anchorObjectIds||[]),anchors=new Set([...requested].filter(id=>objects.has(id))),missing=[...requested].filter(id=>!objects.has(id)).sort();
  const directRelations=new Set([...relations.values()].filter(r=>anchors.has(r.source)||anchors.has(r.target)).map(r=>r.id)),directObjects=new Set(anchors);
  for(const id of directRelations){const r=relations.get(id);directObjects.add(r.source);directObjects.add(r.target);}
  const records=new Set(override.sourceRecordIds||[]);for(const id of anchors){const record=objects.get(id).provenance?.record?.record_id;if(record)records.add(record);}
  const windowKey=(record,window)=>JSON.stringify([record,window]),windows=new Map();
  for(const o of objects.values()){const r=o.provenance?.record||{};if(o.paperId===paper&&records.has(r.record_id)&&/^w\d+$/.test(r.source_unit_id||''))windows.set(windowKey(r.record_id,r.source_unit_id),{recordId:r.record_id,sourceUnitId:r.source_unit_id});}
  const windowObjects=new Set([...objects.values()].filter(o=>o.paperId===paper&&windows.has(windowKey(o.provenance?.record?.record_id,o.provenance?.record?.source_unit_id))).map(o=>o.id));
  const windowRelations=new Set([...relations.values()].filter(r=>!directRelations.has(r.id)&&windowObjects.has(r.source)&&windowObjects.has(r.target)).map(r=>r.id));
  const paperObjects=new Set([...objects.values()].filter(o=>o.paperId===paper).map(o=>o.id));
  const paperRelations=new Set([...relations.values()].filter(r=>!directRelations.has(r.id)&&!windowRelations.has(r.id)&&(paperObjects.has(r.source)||paperObjects.has(r.target))).map(r=>r.id));
  for(const id of paperRelations){const r=relations.get(id);paperObjects.add(r.source);paperObjects.add(r.target);}
  for(const a of payload.sourceAssessments||[])if(a.nodeIds?.some(id=>paperObjects.has(id)))for(const id of a.nodeIds)paperObjects.add(id);
  for(const id of [...directObjects,...paperObjects])if(!objects.has(id))fail('source-context override endpoint is absent');
  const sourceAttachments=[];
  if(directObjects.size)sourceAttachments.push({unitId,scope:'direct_record_relation',objectIds:[...directObjects].sort(),relationIds:[...directRelations].sort(),anchorObjectIds:[...anchors].sort(),statement:'Exact source anchors and exported incident relations. Each relation retains its own direction, semantic status and applicability; no question equivalence is inferred.'});
  const remainingWindow=[...windowObjects].filter(id=>!directObjects.has(id));
  if(remainingWindow.length||windowRelations.size)sourceAttachments.push({unitId,scope:'shared_extraction_window_context',objectIds:remainingWindow.sort(),relationIds:[...windowRelations].sort(),recordWindows:[...windows.values()].sort((a,b)=>a.recordId.localeCompare(b.recordId)||a.sourceUnitId.localeCompare(b.sourceUnitId)),statement:'Same exact extraction record and numbered window only. Co-occurrence does not establish this method’s premises.'});
  const other=[...paperObjects].filter(id=>!directObjects.has(id)&&!windowObjects.has(id));
  if(other.length||paperRelations.size)sourceAttachments.push({unitId,scope:'same_paper_context',objectIds:other.sort(),relationIds:[...paperRelations].sort(),statement:'Additional paper context and named endpoints of source relations. Whole-paper first-pass records are not narrow extraction windows and do not establish applicability.'});
  return {sourceAttachments,missingAnchorIds:missing,attachmentOverridePolicy:policy,coverage:{exactAnchorCount:anchors.size,requestedAnchorCount:requested.size,directExportedRelationCount:directRelations.size,directReviewedRelationCount:[...directRelations].filter(id=>relations.get(id).semanticStatus==='reviewed_scoped').length,windowRecordCount:windows.size,description:'Existing exported relations only. Zero exported incident relations is not evidence that the source has no method assumptions or relations. Shared-window and whole-paper context remain separately typed.'}};
}

export function createAtlasContextReader(atlas,{base,readText,readBinary}={}) {
  const cache=new Map();
  const read=readText||(async url=>{const response=await fetch(url);if(!response.ok)fail(`source context unavailable (${response.status})`);return response.text();});
  const binary=readBinary||(async url=>{const response=await fetch(url);if(!response.ok)fail(`source context unavailable (${response.status})`);return new Uint8Array(await response.arrayBuffer());});
  const path=name=>`${String(base||`/data/atlas/${encodeURIComponent(atlas.manifest.atlasId)}/${encodeURIComponent(atlas.manifest.atlasVersion)}`).replace(/\/$/,'')}/${name}`;
  async function file(descriptor) {
    if(!descriptor||!/^[a-zA-Z0-9][a-zA-Z0-9._/-]*\.json(?:\.gz)?$/.test(descriptor.path)||descriptor.path.split('/').includes('..')||!/^[a-f0-9]{64}$/.test(descriptor.sha256||''))fail('invalid source context file');
    if(descriptor.encoding!==undefined&&descriptor.encoding!=='gzip')fail('unsupported source context encoding');
    if(!cache.has(descriptor.path))cache.set(descriptor.path,(async()=>{
      let bytes=descriptor.encoding==='gzip'?new Uint8Array(await binary(path(descriptor.path))):new TextEncoder().encode(await read(path(descriptor.path)));
      if(bytes.byteLength>16*1024*1024)fail('source context shard exceeds 16 MiB');
      const hash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(n=>n.toString(16).padStart(2,'0')).join('');if(hash!==descriptor.sha256)fail('source context checksum mismatch');
      if(descriptor.encoding==='gzip'){
        const stream=new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip')),reader=stream.getReader(),chunks=[];let size=0;
        try{while(true){const {done,value}=await reader.read();if(done)break;size+=value.byteLength;if(size>16*1024*1024){await reader.cancel();fail('decoded source context exceeds 16 MiB');}chunks.push(value);}}finally{reader.releaseLock();}
        if(descriptor.uncompressedBytes!==undefined&&size!==descriptor.uncompressedBytes)fail('source context decoded size mismatch');
        bytes=new Uint8Array(size);let offset=0;for(const chunk of chunks){bytes.set(chunk,offset);offset+=chunk.byteLength;}
      }
      return JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes));
    })());
    while(cache.size>12)cache.delete(cache.keys().next().value);
    return cache.get(descriptor.path);
  }
  return async unitId=>{
    text(unitId,'context unit ID',300);
    let data=atlas.catalog,coverage=data.sourceContextCoverage||null;
    const descriptor=atlas.manifest.files.sourceContextIndex;
    let sourceContextFile=null,sourceLocator=null;
    if(descriptor){
      const index=await file(descriptor);if(index.schemaVersion!=='1.0.0'||index.kind!=='eigenquestions-source-context-index')fail('unsupported source context index');coverage=index.coverage;
      let dictionary=index;
      if(index.unitIndex){if(index.unitIndex.kind!=='unit-hash-prefix'||index.unitIndex.prefixLength!==2)fail('unsupported unit-index partition');const match=/^unit:([a-f0-9]{2})[a-f0-9]{62}$/.exec(unitId);if(!match)fail('partitioned context lookup requires an exact frozen unit ID');const bucket=index.unitIndex.shards?.[match[1]];dictionary=bucket?await file(bucket):{};}
      const target=dictionary.units?.[unitId],targetFile=target?.shardId?dictionary.shards?.[target.shardId]:target;
      if(target&&!targetFile)fail('source-context shard reference is absent');
      if(targetFile){data=validateSourceContext(await file(targetFile));sourceContextFile=clone(targetFile);sourceLocator=target.sourceLocator?clone(target.sourceLocator):null;if(target.attachmentOverride){const resolved=resolveAtlasContextOverride(unitId,target,data);data={...data,...resolved,coverage:{...data.coverage,...resolved.coverage}};}}
    }
    const attachments=(data.sourceAttachments||[]).filter(a=>a.unitId===unitId),objectIds=new Set(attachments.flatMap(a=>a.objectIds||[])),relationIds=new Set(attachments.flatMap(a=>a.relationIds||[]));
    const relations=(data.sourceRelations||[]).filter(r=>relationIds.has(r.id));for(const r of relations){objectIds.add(r.source);objectIds.add(r.target);}
    const selectedObjects=(data.sourceObjects||[]).filter(o=>objectIds.has(o.id)),assessments=(data.sourceAssessments||[]).filter(a=>a.unitIds?.includes(unitId)||(a.objectIds||a.nodeIds||a.sourceObjectIds||[a.source,a.target]).some(id=>objectIds.has(id)));
    const evidenceIds=new Set([...selectedObjects,...relations,...assessments].flatMap(item=>item.evidenceRefs||[])),evidence=(data.sourceEvidence||[]).filter(e=>evidenceIds.has(e.id)),found=new Set(evidence.map(e=>e.id));
    return {unitId,...(sourceLocator?{sourceLocator}:{}),...(sourceContextFile?{sourceContextFile}:{}),...(data.attachmentOverridePolicy?{attachmentOverridePolicy:data.attachmentOverridePolicy,missingAnchorIds:clone(data.missingAnchorIds)}:{}),availability:attachments.length?'available':'not-exported',coverage:data.coverage||coverage||{description:'No source-context coverage statement was exported.'},notice:'Direct source relations and shared-extraction or same-paper context have different scopes. Missing exported context does not establish that a source has no assumptions, methods or related claims.',sourceAttachments:clone(attachments),sourceObjects:clone(selectedObjects),sourceRelations:clone(relations),sourceAssessments:clone(assessments),sourceEvidence:clone(evidence),missingEvidenceIds:[...evidenceIds].filter(id=>!found.has(id))};
  };
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
  const checked=validateAtlas(manifest,expandAtlasIndex(JSON.parse(bytes))),pending=new Map();
  const readShard=async descriptor=>{fileDescriptor(descriptor);const key=descriptor.sha256;if(!pending.has(key))pending.set(key,(async()=>{const body=await readText(path(descriptor.path)),encoded=new TextEncoder().encode(body);if(encoded.byteLength!==descriptor.bytes)fail('lazy shard byte count mismatch');const actual=[...new Uint8Array(await crypto.subtle.digest('SHA-256',encoded))].map(n=>n.toString(16).padStart(2,'0')).join('');if(actual!==descriptor.sha256)fail('lazy shard checksum mismatch');return JSON.parse(body);})().catch(error=>{pending.delete(key);throw error;}));while(pending.size>16)pending.delete(pending.keys().next().value);return pending.get(key);};
  return {...checked,manifestSha256,...(lazyCatalog(checked.catalog)||manifest.files.sourceMethodRoutes?{readShard}:{})};
}

export function createAtlasNavigator(atlas,{readSources,readContext,readSourceRoutes}={}) {
  const {manifest,catalog} = validateAtlas(atlas.manifest,atlas.catalog);
  if (!/^[a-f0-9]{64}$/.test(atlas.manifestSha256 || '')) fail('load the checksummed manifest before creating a navigator');
  const lazy=lazyCatalog(catalog),indexes=new Map(catalog.destinations.map(d=>[d.id,d]));
  const contextReader=readContext||createAtlasContextReader(atlas),inspectionCache=new Map();let routeLoad;
  const inspectionKey=value=>JSON.stringify(['originUnitId','relationId','objectId','unitId'].map(key=>value[key]));
  async function routeData(){
    if(!manifest.files.sourceMethodRoutes&&!readSourceRoutes)return null;
    if(!routeLoad)routeLoad=(async()=>{const data=readSourceRoutes?await readSourceRoutes():await atlas.readShard(manifest.files.sourceMethodRoutes);if(data.schemaVersion!=='1.0.0'||data.kind!=='eigenquestions-exact-source-method-routes')fail('unsupported source method routes');object(data.routes,'source method routes');object(data.units,'source method units');return data;})().catch(error=>{routeLoad=null;throw error;});
    return routeLoad;
  }
  function exactRoute(data,relation){
    const route=data?.routes[relation.id];if(!route)return null;
    if(relation.semanticStatus!=='reviewed_scoped'||route.status!=='accepted_relation'||route.promotionWithheld!==false||route.sourceObjectId!==relation.source||route.targetObjectId!==relation.target||route.type!==relation.type||route.receiptSha256!==relation.provenance?.receiptSha256||route.questionEquivalenceInferred!==false||route.methodApplicabilityExtended!==false)fail('source route disagrees with exact reviewed relation');
    for(const side of ['source','target']){list(route[`${side}MethodUnitIds`],'mapped source units',100);for(const id of route[`${side}MethodUnitIds`]){const unit=data.units[id];if(!unit||unit.unitId!==id||unit.lens!=='method'||!unit.sourceNodeIds?.includes(route[`${side}ObjectId`])||!Number.isSafeInteger(unit.browserVectorRow)||unit.browserVectorRow<0||!/^[a-f0-9]{64}$/.test(unit.textSha256||''))fail('source route lacks an exact frozen method anchor');}}
    return route;
  }
  async function sourceRoutes(context){
    const data=await routeData();if(!data)return {status:'not-exported',items:[],notice:'No exact endpoint-to-method routes are exported; source relations remain readable.'};
    const items=[];for(const relation of context.sourceRelations||[]){const route=exactRoute(data,relation);if(!route)continue;items.push({relationId:relation.id,sourceObjectId:relation.source,targetObjectId:relation.target,type:relation.type,semanticStatus:relation.semanticStatus,endpoints:['source','target'].map(side=>({side,objectId:route[`${side}ObjectId`],choices:route[`${side}MethodUnitIds`].map(id=>({unitId:id,paperId:data.units[id].paperId,action:{type:'inspect-source',sourceInspection:{originUnitId:context.unitId,relationId:relation.id,objectId:route[`${side}ObjectId`],unitId:id}}}))})),notice:'Exact source-object inspection only. Traversing toward the source endpoint does not reverse the relation or establish applicability to the current question.'});}
    return {status:'available',items};
  }
  async function contextWithRoutes(unitId){const context=await contextReader(unitId);try{return {...context,sourceRoutes:await sourceRoutes(context)};}catch(error){return {...context,sourceRoutes:{status:'unavailable',items:[],notice:error.message}};}}
  async function prepareInspection(value){
    const key=inspectionKey(value);if(inspectionCache.has(key))return;
    const data=await routeData();if(!data)fail('exact source endpoint routes are not exported');
    const origin=await contextReader(value.originUnitId),relation=origin.sourceRelations?.find(row=>row.id===value.relationId);if(!relation)fail('reviewed relation is absent from the stated source context');
    const route=exactRoute(data,relation);if(!route)fail('source relation has no exact method route');
    const side=relation.source===value.objectId?'source':relation.target===value.objectId?'target':null;if(!side||!route[`${side}MethodUnitIds`].includes(value.unitId))fail('endpoint is not mapped to this exact method unit');
    const unit=data.units[value.unitId],context=await contextReader(value.unitId),target=context.sourceObjects?.find(row=>row.id===value.objectId);if(!target||target.paperId!==unit.paperId)fail('mapped method source object is absent or has a different paper');
    const [row]=await (readSources||createAtlasSourceReader(atlas))([{...unit}]),source=row?.source;if(source?.id!==unit.unitId||source.paperId!==unit.paperId)fail('mapped frozen method source identity changed');
    const textHash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(source.evidence.text)))].map(n=>n.toString(16).padStart(2,'0')).join('');if(textHash!==unit.textSha256)fail('mapped frozen method source text changed');
    const result={target:clone(value),endpointSide:side,source:clone(source),object:clone(target),relation:clone(relation),mapping:{basis:route.mappingBasis,receiptSha256:route.receiptSha256,sourceNodeIds:clone(unit.sourceNodeIds)},notice:'Inspecting this exact source object leaves the physical destination and its source membership unchanged. This route does not establish question equivalence or method applicability.'};
    if(new TextEncoder().encode(JSON.stringify(result)).byteLength>256*1024)fail('source inspection exceeds the inline view budget; read its pinned source context instead');inspectionCache.set(key,result);while(inspectionCache.size>32)inspectionCache.delete(inspectionCache.keys().next().value);
  }
  const destinations = new Map(catalog.destinations.map(d=>[d.id,{...d,question:d.question??d.title}])), sources = new Map(catalog.sources.map(s=>[s.id,s]));
  const memberships = new Map(), incident = new Map(),detailsReady=new Set(),membershipsReady=new Set(),detailLoads=new Map(),membershipLoads=new Map(),membershipDescriptors=new Map(),membershipSamples=new Map(),detailSources=new Map(),relationIndex=new Map(catalog.relations.map(r=>[r.id,r]));let searchReady=!catalog.fineIndex,searchLoad;
  for (const m of catalog.memberships) { if (!memberships.has(m.destinationId)) memberships.set(m.destinationId,[]); memberships.get(m.destinationId).push(m); }
  for (const rows of memberships.values()) rows.sort((a,b)=>Number(Boolean(a.associationScope))-Number(Boolean(b.associationScope))||b.weight-a.weight || a.unitId.localeCompare(b.unitId));
  for (const r of catalog.relations) for (const id of [r.source,r.target]) { if (!incident.has(id)) incident.set(id,[]); incident.get(id).push(r); }
  const defaultSelection=state=>(!state.intent||state.intent==='explore')&&(!state.lens||state.lens==='combined')&&(!state.workRelation||state.workRelation==='either')&&!state.constraints?.excludeIds?.length&&state.constraints?.yearMin===undefined&&state.constraints?.yearMax===undefined;
  const ordered=rows=>rows.sort((a,b)=>Number(Boolean(a.associationScope))-Number(Boolean(b.associationScope))||b.weight-a.weight||a.unitId.localeCompare(b.unitId));
  function validateLoaded(id,record,records,rows){
    if(record.id!==id)fail('detail destination ID mismatch');const indexed=indexes.get(id);
    if(record.title!==indexed.title||record.question!==(indexed.question??indexed.title)||record.kind!==indexed.kind||Boolean(record.metadataOnly)!==Boolean(indexed.metadataOnly))fail('detail changes indexed canonical identity');
    validateAtlas({...manifest,schemaVersion:'1.0.0',entryDestinationId:id},{destinations:[record],sources:records,memberships:rows,relations:[]});
    for(const row of rows)if(row.destinationId!==id)fail('membership shard has a foreign destination');
  }
  function mergeNavigation(input){
    const navigation=expandAtlasIndex({...input,indexTemplates:input.indexTemplates||catalog.indexTemplates});
    const added=[],links=[];
    for(const row of navigation.destinations||[]){if(indexes.has(row.id)){if(stableJson(indexes.get(row.id))!==stableJson(row))fail('inconsistent destination index across immutable shards');}else added.push(row);}
    for(const row of navigation.relations||[]){if(relationIndex.has(row.id)){if(stableJson(relationIndex.get(row.id))!==stableJson(row))fail('inconsistent navigation relation across immutable shards');}else links.push(row);}
    if(!added.length&&!links.length)return;
    validateLazyCatalog(manifest,{...catalog,destinations:[...catalog.destinations,...added],relations:[...catalog.relations,...links]});
    for(const id of detailsReady){const count=(incident.get(id)||[]).length+links.filter(r=>r.source===id||r.target===id).length;if(indexes.get(id).connectionCount!==undefined&&count!==indexes.get(id).connectionCount)fail('later index changes a prepared destination connection count');}
    for(const row of added){indexes.set(row.id,row);destinations.set(row.id,{...row,question:row.question??row.title});catalog.destinations.push(row);}
    for(const row of links){relationIndex.set(row.id,row);catalog.relations.push(row);for(const id of [row.source,row.target]){if(!incident.has(id))incident.set(id,[]);incident.get(id).push(row);}}
  }
  async function readFineIndex(descriptor){const data=await atlas.readShard(descriptor);if(data.schemaVersion!=='1.0.0'||data.kind!=='eigenquestions-fine-index')fail('unsupported fine index');mergeNavigation(data);}
  async function prepareSearch(){if(searchReady)return;if(!searchLoad)searchLoad=readFineIndex(catalog.fineIndex).then(()=>{searchReady=true;}).catch(error=>{searchLoad=null;throw error;});await searchLoad;}
  async function prepareDestination(id){
    identifier(id,'destination ID');
    if(!destinations.has(id)&&lazy){const prefix=/^source-question:([a-f0-9]{2})[a-f0-9]{62}$/.exec(id)?.[1],bucket=prefix&&catalog.fineLookup?.shards[prefix];if(bucket)await readFineIndex(bucket);else await prepareSearch();}
    if(!destinations.has(id))fail('unknown destination');if(!lazy||detailsReady.has(id))return;
    if(!detailLoads.has(id))detailLoads.set(id,(async()=>{
      if(!atlas.readShard)fail('lazy atlas must be loaded through its checksum reader');
      const data=await atlas.readShard(catalog.detailShards[indexes.get(id).detail.shardId]);
      if(data.schemaVersion!=='1.0.0'||data.kind!=='eigenquestions-destination-details')fail('unsupported destination detail shard');
      const item=data.destinations?.[id];if(!item)fail('destination detail is absent');
      if(item.navigation)mergeNavigation(item.navigation);
      if(indexes.get(id).connectionCount!==undefined&&(incident.get(id)||[]).length!==indexes.get(id).connectionCount)fail('destination navigation is incomplete');
      list(item.membershipSample,'membership sample',MAX.membershipSample);list(item.sources,'representative sources',MAX.destinationEvidence+MAX.contextEvidence+MAX.membershipSample);validateLoaded(id,item.destination,item.sources,item.membershipSample);
      const indexed=indexes.get(id);for(const key of ['membershipCount','contextMembershipCount'])if(item.destination[key]!==undefined&&item.destination[key]!==indexed[key])fail('detail source count disagrees with index');
      if(item.memberships){fileDescriptor(item.memberships);membershipDescriptors.set(id,item.memberships);}else if(indexed.membershipCount===0&&indexed.contextMembershipCount===0&&item.membershipSample.length===0)membershipsReady.add(id);else fail('destination lacks complete membership descriptor or declared empty membership');
      for(const source of item.sources){if(sources.has(source.id)&&(sources.get(source.id).paperId!==source.paperId||sources.get(source.id).evidence.text!==source.evidence.text))fail('inconsistent frozen source record');sources.set(source.id,source);}
      detailSources.set(id,new Map(item.sources.map(source=>[source.id,source])));destinations.set(id,item.destination);membershipSamples.set(id,ordered(clone(item.membershipSample)));memberships.set(id,membershipSamples.get(id));detailsReady.add(id);
    })().catch(error=>{detailLoads.delete(id);throw error;}));return detailLoads.get(id);
  }
  async function prepareSources(id){
    await prepareDestination(id);if(!lazy||membershipsReady.has(id))return;
    if(!membershipLoads.has(id))membershipLoads.set(id,(async()=>{
      const data=await atlas.readShard(membershipDescriptors.get(id));if(data.schemaVersion!=='1.0.0'||data.kind!=='eigenquestions-destination-memberships')fail('unsupported membership shard');
      const item=data.destinations?.[id];if(!item)fail('complete destination membership is absent');
      const rows=list(item.items,'complete memberships',30000),indexed=indexes.get(id),primary=rows.filter(row=>!row.associationScope).length,context=rows.length-primary;
      if(primary!==indexed.membershipCount||context!==indexed.contextMembershipCount||item.primaryCount!==primary||item.contextCount!==context)fail('complete membership count disagrees with pinned index');
      validateLoaded(id,destinations.get(id),[...new Set([...destinations.get(id).evidenceIds,...(destinations.get(id).contextSourceIds||[])])].map(key=>sources.get(key)),rows);
      const exact=new Map(rows.map(row=>[row.unitId,row]));for(const sample of memberships.get(id)||[])if(!exact.has(sample.unitId)||stableJson(exact.get(sample.unitId))!==stableJson(sample))fail('membership sample differs from complete record');
      memberships.set(id,ordered(clone(rows)));membershipsReady.add(id);
    })().catch(error=>{membershipLoads.delete(id);throw error;}));return membershipLoads.get(id);
  }
  async function validateCompleteMemberships(){
    await prepareSearch();
    for(const id of indexes.keys())await prepareSources(id);
    const complete=new Map();for(const [id,d]of destinations)if(!d.metadataOnly&&(d.membershipStatus==='complete'||d.membershipComplete===true))complete.set(id,new Set((memberships.get(id)||[]).filter(row=>!row.associationScope).map(row=>row.unitId)));
    let checkedContainment=0;for(const relation of catalog.relations)if(relation.type==='narrower'&&complete.has(relation.source)&&complete.has(relation.target)){checkedContainment++;for(const id of complete.get(relation.target))if(!complete.get(relation.source).has(id))fail(`complete child membership escapes parent on ${relation.id}`);}
    return {destinations:indexes.size,completeMemberships:complete.size,checkedContainment,primaryRows:[...memberships.values()].reduce((n,rows)=>n+rows.filter(row=>!row.associationScope).length,0),contextRows:[...memberships.values()].reduce((n,rows)=>n+rows.filter(row=>row.associationScope).length,0)};
  }
  async function prepareState(state){
    const id=state.selector.destinationId;await prepareDestination(id);if(!defaultSelection(state)){
      await prepareSources(id);const rows=sourceRows(id,state).slice(0,30).map(row=>({...row,source:sources.get(row.unitId)||null}));
      if(rows.some(row=>!row.source)){const hydrated=await (readSources||createAtlasSourceReader(atlas))(rows);if(hydrated.length!==rows.length)fail('source reader omitted selected rows');for(let i=0;i<rows.length;i++){const source=hydrated[i].source;if(source?.id!==rows[i].unitId)fail('selected source ID mismatch');text(source.title,'source title',4000);object(source.evidence,'source evidence');text(source.evidence.text,'source text',64000);sources.set(source.id,source);}}
    }
    if(state.sourceInspection)await prepareInspection(state.sourceInspection);
  }
  async function prepareAction(session,action){
    const before=session.states[session.cursor];let target=action.selector?.destinationId||before.selector.destinationId,fields={...before,...action,constraints:action.constraints?{...before.constraints,...action.constraints}:before.constraints};
    if(['back','forward','replay'].includes(action.type)){const cursor=action.type==='back'?Math.max(0,session.cursor-1):action.type==='forward'?Math.min(session.states.length-1,session.cursor+1):action.index;if(!Number.isInteger(cursor)||!session.states[cursor])fail('invalid replay index');fields=session.states[cursor];target=fields.selector.destinationId;}
    else if(action.type==='reset'){target=action.selector?.destinationId||manifest.entryDestinationId;fields={...initialState,...action};}
    else if(action.type==='select'){const link=connections(before.selector.destinationId).find(link=>`connection:${link.id}`===action.directionId);if(!link)fail('selected direction is absent');target=link.destinationId;fields=before;}
    if(!['inspect-source','back','forward','replay'].includes(action.type)){fields={...fields};delete fields.sourceInspection;}
    if(action.type!=='select'&&action.intent==='using'&&!Object.hasOwn(action,'workRelation'))fields={...fields,workRelation:'using'};
    await prepareState({...fields,selector:selector(target)});
  }
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
    if(lazy&&!detailsReady.has(id))fail('prepare the destination before reading its sources');
    if(lazy&&!membershipsReady.has(id)&&!defaultSelection(state))fail('complete membership must be loaded before filtering');
    const excluded = new Set(state.constraints?.excludeIds || []);
    if(state.includeContext!==undefined&&typeof state.includeContext!=='boolean')fail('includeContext must be a boolean');
    const includeContext=state.includeContext??(state.lens==='method'||state.intent==='derive');
    const yearOf = m => m.year ?? sources.get(m.unitId)?.year ?? (Number(String(sources.get(m.unitId)?.evidence?.date || '').slice(0,4)) || undefined);
    const rows = (memberships.get(id) || []).filter(m => {
      if (excluded.has(m.unitId)) return false;
      if(m.associationScope&&!includeContext)return false;
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
      return {...clone(r),...(r.title?{routeTitle:r.title}:{}),destinationId:target.id,title:target.title,choiceTitle:(outgoing?r.title:r.incomingTitle)||target.title,question:target.question,selector:selector(target.id),traversal:outgoing?'outgoing':'incoming',navigationKind:r.type === 'narrower' ? outgoing?'narrower':'broader':r.type};
    }).sort((a,b) => (a.type==='source_question'?3:a.navigationKind==='narrower'?0:a.navigationKind==='broader'?2:1)-(b.type==='source_question'?3:b.navigationKind==='narrower'?0:b.navigationKind==='broader'?2:1) || a.title.localeCompare(b.title) || a.id.localeCompare(b.id));
  }
  function computeView(input) {
    const state = normalizeState(input), canonical = normalizeState(resolveState(state)), d = destination(state.selector);
    if (state.id !== canonical.id || state.computationId !== computationId) fail('state does not match canonical prepared destination');
    if(lazy&&!detailsReady.has(d.id))fail('prepare the destination before computing its view');
    const inspection=state.sourceInspection&&inspectionCache.get(inspectionKey(state.sourceInspection));if(state.sourceInspection&&!inspection)fail('prepare the exact source inspection before computing its view');
    const links = connections(d.id), foreground = links.slice(0,d.metadataOnly ? 20 : 15), selected = new Set([...d.evidenceIds,...(d.contextSourceIds||[])].slice(0,30));
    for (const link of foreground) { for (const id of link.evidenceIds.slice(0,3)) selected.add(id); for (const id of ((lazy?indexes:destinations).get(link.destinationId).evidenceIds||[]).slice(0,3)) selected.add(id); }
    const sampled=lazy&&defaultSelection(state)&&(indexes.get(d.id).membershipCount+indexes.get(d.id).contextMembershipCount>0),rows=sampled?membershipSamples.get(d.id).filter(row=>!row.associationScope):sourceRows(d.id,state);
    for (const row of rows.slice(0,30)) if (sources.has(row.unitId)) selected.add(row.unitId);
    if(lazy&&!sampled&&rows.slice(0,30).some(row=>!sources.has(row.unitId)))fail('prepare complete selected source descriptions before computing');
    const visibleSourceIds=lazy?new Set([...detailSources.get(d.id).keys(),...rows.slice(0,30).map(row=>row.unitId)]):null;
    const primaryRows=rows.filter(row=>!row.associationScope),contextRows=rows.filter(row=>row.associationScope),matchingIds=new Set(primaryRows.map(row=>row.unitId)),contextIds=new Set(contextRows.map(row=>row.unitId)),associations=new Map((memberships.get(d.id)||[]).filter(row=>row.associationScope).map(row=>[row.unitId,row]));
    const nodes = [...selected].filter(id=>sources.has(id)&&(!lazy||visibleSourceIds.has(id))).map(id=>({...clone(lazy?detailSources.get(d.id).get(id)||sources.get(id):sources.get(id)),atlasRole:matchingIds.has(id)?'matching-source':'context-evidence',...(sampled?{atlasMembershipChecked:matchingIds.has(id)}:{}),...(associations.has(id)?{atlasContextScope:associations.get(id).associationScope,atlasContextMatchesFilters:contextIds.has(id)}:d.contextSourceIds?.includes(id)?{atlasContextScope:'same_paper_context'}:{})}));
    const visibleNodeIds=new Set(nodes.map(node=>node.id));
    const directions = foreground.map(link => {
      const target = (lazy?indexes:destinations).get(link.destinationId), ids = [...new Set([...link.evidenceIds,...(target.evidenceIds||[])])].filter(id=>visibleNodeIds.has(id));
      const classifiedChildren=target.metadataOnly?(catalog.orientation?.edges||[]).filter(edge=>edge.source===target.id).map(edge=>indexes.get(edge.target)?.title).filter(Boolean):[];
      const description=target.metadataOnly?(classifiedChildren.length?classifiedChildren.slice(0,3).join(' · '):target.kind==='landmark'?target.summary||'':''):target.summary||'';
      return {id:`connection:${link.id}`,label:link.choiceTitle,query:target.question??target.title,summary:description,...(target.metadataOnly?{metadataOnly:true}:{}),selector:link.selector,seedIds:[],memberIds:ids,evidenceIds:ids,intent:state.intent,lens:state.lens,workRelation:state.workRelation,sourceCount:lazy?indexes.get(target.id).membershipCount:(memberships.get(target.id)||[]).filter(row=>!row.associationScope).length,relationType:link.type,navigationKind:link.navigationKind,relation:link};
    });
    const warnings = [...(manifest.scope.limitations || [])];
    if (state.workRelation !== 'either') warnings.push('ON/USING source selection uses explicitly recorded membership roles. Unclassified sources are omitted from that selection.');
    if (state.intent === 'derive') warnings.push('Derivation reading selects recorded method facets. It does not perform or certify a new derivation.');
    if (state.intent === 'phenomenology') warnings.push('Phenomenology selects explicitly tagged memberships only. Untagged sources remain unclassified.');
    if (state.intent === 'recent') warnings.push('Recent orders recorded publication years within this frozen corpus; undated sources follow dated sources. This is not a live search.');
    return {schemaVersion:'1.1.0',corpusId:manifest.corpusId,computationId,stateId:state.id,query:d.question,nodes,directions,edges:[],chart:null,warnings,
      diagnostics:{scope:{...clone(manifest.scope),...(manifest.snapshotDate?{snapshotDate:manifest.snapshotDate}:{})},distinctPapers:new Set(nodes.filter(n=>n.kind!=='vocabulary'&&n.paperId).map(n=>n.paperId)).size,prepared:true},
      atlas:{atlasId:manifest.atlasId,atlasVersion:manifest.atlasVersion,selector:state.selector,destination:clone(d),...(inspection?{sourceInspection:clone(inspection)}:{}),membershipCount:lazy?indexes.get(d.id).membershipCount:(memberships.get(d.id)||[]).filter(row=>!row.associationScope).length,contextMembershipCount:lazy?indexes.get(d.id).contextMembershipCount:(memberships.get(d.id)||[]).filter(row=>row.associationScope).length,membershipReadMode:sampled?'pinned-counts-and-sample':'complete-selection',membershipStatus:d.metadataOnly?'metadata-only':d.membershipStatus||(d.membershipComplete?'complete':'unspecified'),matchingSourceCount:sampled?indexes.get(d.id).membershipCount:primaryRows.length,matchingContextCount:sampled?0:contextRows.length,matchingSourceIds:primaryRows.slice(0,30).map(row=>row.unitId),matchingContextIds:contextRows.slice(0,30).map(row=>row.unitId),displayedSourceCount:nodes.length,connectionCount:links.length,connections:links,membershipNotice:`Displayed source descriptions are a bounded sample. Recorded membership is pinned by this atlas version and destination.${d.membershipStatus==='complete'||d.membershipComplete?' This destination declares complete membership within its recorded scope.':' No exhaustive literature membership is claimed.'}`,contextEvidenceNotice:'Context evidence supports definitions or connections; same-paper method associations are reading context, not primary membership or established applicability. They are counted and labeled separately.'}};
  }
  return {computationId,initialState,resolveState,computeView,readContext:contextWithRoutes,sourceRoutes,...(lazy||manifest.files.sourceMethodRoutes||readSourceRoutes?{prepareDestination,prepareSources,prepareState,prepareAction,prepareSearch,validateCompleteMemberships}:{}),
    createSession:fields=>createSession(resolveState({...initialState,...fields})),
    destination:id=>clone(destination(selector(id))),
    connections:(id,{offset=0,limit=100}={})=>({total:connections(id).length,items:connections(id).slice(offset,offset+Math.min(100,limit))}),
    sources:(id,{offset=0,limit=30,collection='membership',...state}={})=>{if(!destinations.has(id))fail('unknown destination');if(!['membership','contributions'].includes(collection))fail('unknown source collection');if(!Number.isInteger(offset)||offset<0||!Number.isInteger(limit)||limit<1||limit>100)fail('invalid source page');if(collection==='contributions'){if(lazy&&!detailsReady.has(id))fail('load destination before paging contributions');if(Object.keys(state).length)fail('membership filters do not apply to typed contributions');const rows=destinations.get(id).sourceContributions||[];return {collection,destinationId:id,total:rows.length,offset,notice:'Typed source contributions are separate from membership, equivalence and established method applicability. Reading basis and qualifications remain attached to each row.',items:rows.slice(offset,offset+limit).map(row=>({...clone(row),source:sources.has(row.unitId)?clone(sources.get(row.unitId)):null}))};}if(lazy&&!membershipsReady.has(id))fail('load complete membership before paging sources');const rows=sourceRows(id,state);return {collection,total:rows.length,primaryTotal:rows.filter(row=>!row.associationScope).length,contextTotal:rows.filter(row=>row.associationScope).length,contextNotice:'Same-paper associations are context only, not established method use.',offset,items:rows.slice(offset,offset+limit).map(m=>({...clone(m),source:sources.has(m.unitId)?clone(sources.get(m.unitId)):null}))};},
    getEvidence:ids=>ids.map(id=>sources.has(id)?clone(sources.get(id)):{id,error:'Source description not bundled; read the frozen corpus source shard using its membership row.'}),
    search:(query,{limit=10}={})=>{
      if(lazy&&!searchReady)fail('prepare complete fine lookup before global title/alias search');
      text(query,'lookup query',4000); if(!Number.isInteger(limit)||limit<1||limit>30)fail('lookup limit must be 1–30');
      const normalized=query.trim().toLowerCase(),tokens=normalized.match(/[\p{L}\p{N}]+/gu)||[];
      if (!tokens.length) return [];
      return catalog.destinations.map(d=>{const names=[d.title,d.question??d.title,...(d.aliases||[])].map(s=>s.toLowerCase()),haystack=names.join(' ');const score=names.includes(normalized)?100:tokens.filter(t=>haystack.includes(t)).length/tokens.length;return {id:d.id,title:d.title,question:d.question??d.title,summary:d.summary||'',scope:d.scope?clone(d.scope):null,selector:selector(d.id),score,matchKind:'title-and-alias-lookup'};}).filter(d=>d.score>0).sort((a,b)=>b.score-a.score||a.id.localeCompare(b.id)).slice(0,limit);
    }};
}

export function atlasAddress(state, origin = 'https://eigenquestions.com') {
  const normalized=normalizeState(state); if (!normalized.selector) fail('a prepared selector is required');
  if (normalized.sourceInspection) fail('Export the full view to share this source-object inspection; compact links identify the physical destination.');
  if (normalized.constraints.excludeIds.length || normalized.constraints.yearMin !== undefined || normalized.constraints.yearMax !== undefined) fail('filtered states require a capsule until compact filter addresses are supported');
  const hash=new URLSearchParams({atlas:normalized.selector.atlasId,version:normalized.selector.atlasVersion,destination:normalized.selector.destinationId,lens:normalized.lens,intent:normalized.intent,relation:normalized.workRelation});
  return `${origin.replace(/\/$/,'')}/#${hash}`;
}

/** Fetch only metadata/source shards, never vectors, to inspect full membership. */
export function createAtlasSourceReader(atlas, {base='/data',readText}={}) {
  const cache=new Map();
  const read=readText || (async url=>{const response=await fetch(url);if(!response.ok)fail(`source file unavailable (${response.status})`);return response.text();});
  const path=name=>`${String(base).replace(/\/$/,'')}/${name}`;
  let manifestPromise;
  async function file(descriptor) {
    if(!descriptor||!/^[a-zA-Z0-9._-]+$/.test(descriptor.path))fail('invalid source shard');
    if(!cache.has(descriptor.path))cache.set(descriptor.path,(async()=>{const body=await read(path(descriptor.path));const hash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(body)))].map(n=>n.toString(16).padStart(2,'0')).join('');if(hash!==descriptor.sha256)fail(`source checksum mismatch ${descriptor.path}`);return JSON.parse(body);})());
    return cache.get(descriptor.path);
  }
  return async rows=>{
    if(rows.every(row=>row.source))return rows;
    manifestPromise??=read(path('manifest.json')).then(JSON.parse).then(manifest=>{if(manifest.corpusId!==atlas.manifest.corpusId||manifest.contentHash!==atlas.manifest.corpusContentHash)fail('frozen source corpus identity mismatch');return manifest;});
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
