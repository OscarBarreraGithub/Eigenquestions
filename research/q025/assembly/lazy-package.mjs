/** Bounded representation of one fully validated logical atlas, not another engine. */
import {mkdir,writeFile} from 'node:fs/promises';
import {join} from 'node:path';
import {sha256} from './corpus.mjs';

const bytes=x=>Buffer.byteLength(JSON.stringify(x));
const contextual=r=>r.placementStatus==='context_only';
const setHash=ids=>sha256([...new Set(ids)].sort().join('\n'));
const MAX_FILE=25*1024*1024;
const indexFields=['id','kind','title','question','summary','aliases','metadataOnly','evidenceIds','scientificStatus','placementStatus','membershipStatus','identityStatus','sourceQuestionAccess'];

/** Lossless shallow defaults. Exact identity and endpoint fields are never templates. */
export function templateIndex(catalog){
  const value=structuredClone(catalog),templates={destinations:{},relations:{}};
  for(const [kind,groupKey] of [['destinations',r=>r.sourceQuestionAccess?'source_question':null],['relations',r=>r.type==='source_question'?'source_question':null]]){
    const groups=new Map();for(const row of value[kind]){const key=groupKey(row);if(key){if(!groups.has(key))groups.set(key,[]);groups.get(key).push(row);}}
    for(const [key,rows] of groups){if(rows.length<2)continue;const template={};for(const field of Object.keys(rows[0])){if(['id','source','target','title','question','detail','indexTemplate'].includes(field))continue;const expected=JSON.stringify(rows[0][field]);if(rows.every(row=>JSON.stringify(row[field])===expected))template[field]=rows[0][field];}if(!Object.keys(template).length)continue;templates[kind][key]=template;for(const row of rows){for(const field of Object.keys(template))delete row[field];row.indexTemplate=key;}}
  }
  value.indexTemplates=templates;return value;
}

export function validatePartition(logical,partition){
  const files=new Map(partition.files.map(f=>[f.descriptor.path,f]));
  const read=descriptor=>{const file=files.get(descriptor.path);if(!file||sha256(file.text)!==descriptor.sha256||Buffer.byteLength(file.text)!==descriptor.bytes)throw new Error(`Partition checksum mismatch ${descriptor.path}`);return JSON.parse(file.text);};
  for(const file of partition.files)read(file.descriptor);
  const fine=partition.catalog.fineIndex?read(partition.catalog.fineIndex):{destinations:[],relations:[]},expand=(row,kind)=>{const value={...(partition.catalog.indexTemplates?.[kind]?.[row.indexTemplate]||{}),...row};delete value.indexTemplate;return value;};
  const indexes=new Map([...partition.catalog.destinations,...fine.destinations].map(d=>{const value=expand(d,'destinations');return [value.id,value];})),relations=new Map([...partition.catalog.relations,...fine.relations].map(r=>{const value=expand(r,'relations');return [value.id,value];}));
  if(indexes.size!==logical.destinations.length||relations.size!==logical.relations.length)throw new Error('Partition index loses exact identities');
  for(const r of logical.relations)if(JSON.stringify(relations.get(r.id))!==JSON.stringify(r)){
    // Template expansion changes key insertion order but must preserve every value.
    const same=(a,b)=>JSON.stringify(Object.entries(a).sort(([x],[y])=>x.localeCompare(y)))===JSON.stringify(Object.entries(b).sort(([x],[y])=>x.localeCompare(y)));
    if(!same(relations.get(r.id),r))throw new Error('Partition relation changed');
  }
  const byDest=new Map(logical.destinations.map(d=>[d.id,[]]));for(const row of logical.memberships)byDest.get(row.destinationId).push(row);
  const loadedDetails=new Map(),loadedMemberships=new Map();let count=0;
  for(const d of logical.destinations){const index=indexes.get(d.id);if(!index)throw new Error('Destination absent from partition');const descriptor=partition.catalog.detailShards[index.detail.shardId];if(!loadedDetails.has(descriptor.path))loadedDetails.set(descriptor.path,read(descriptor));const detail=loadedDetails.get(descriptor.path).destinations[d.id];if(!detail||detail.destination.id!==d.id)throw new Error('Wrong detailed identity');let rows=[];if(detail.memberships){if(!loadedMemberships.has(detail.memberships.path))loadedMemberships.set(detail.memberships.path,read(detail.memberships));rows=loadedMemberships.get(detail.memberships.path).destinations[d.id].items;}if(JSON.stringify(rows)!==JSON.stringify(byDest.get(d.id)))throw new Error(`Membership round trip differs: ${d.id}`);count+=rows.length;
    const primary=rows.filter(r=>!contextual(r));if(index.membershipCount!==primary.length||index.contextMembershipCount!==rows.length-primary.length||index.paperCount!==new Set(primary.map(r=>r.paperId).filter(Boolean)).size)throw new Error('Pinned count mismatch');
    const incident=logical.relations.filter(r=>r.source===d.id||r.target===d.id);if(index.connectionCount!==incident.length)throw new Error('Pinned connection count mismatch');const localIds=new Set(detail.navigation.relations.map(r=>r.id)),globalIds=new Set(partition.catalog.relations.filter(r=>r.source===d.id||r.target===d.id).map(r=>r.id));if(incident.some(r=>!localIds.has(r.id)&&!globalIds.has(r.id)))throw new Error('Local navigation loses an incident link');
  }
  for(const [prefix,descriptor] of Object.entries(partition.catalog.fineLookup?.shards||{})){const bucket=read(descriptor);for(const d of bucket.destinations)if(d.id.slice(16,18)!==prefix||!indexes.has(d.id))throw new Error('Fine lookup prefix mismatch');}
  return {passed:true,filesChecked:files.size,completeMembershipRowsChecked:count,destinationsChecked:indexes.size,relationsChecked:relations.size,exactMembershipRoundTrip:true,exactSourceIdentityPreserved:true,pinnedCountsVerified:true,allIncidentNavigationAvailableBeforeView:true};
}

function sampleRows(rows,d,primaryLimit=30,contextLimit=6){
  const preferred=new Set([...(d.evidenceIds||[]),...(d.contextSourceIds||[])]);
  const order=(a,b)=>Number(preferred.has(b.unitId))-Number(preferred.has(a.unitId))||(a.browserVectorRow??Infinity)-(b.browserVectorRow??Infinity)||a.unitId.localeCompare(b.unitId);
  return [...rows.filter(r=>!contextual(r)).sort(order).slice(0,primaryLimit),...rows.filter(contextual).sort(order).slice(0,contextLimit)];
}

function packEntries(entries,{kind,prefix,targetBytes,maxFileBytes=MAX_FILE}){
  const files=[],locations=new Map();let current={},currentBytes=0;
  function flush(){if(!Object.keys(current).length)return;const payload={kind,schemaVersion:'1.0.0',destinations:current},text=JSON.stringify(payload),size=Buffer.byteLength(text);if(size>maxFileBytes)throw new Error(`${kind} shard exceeds ${maxFileBytes} bytes (${size})`);const path=`${prefix}-${String(files.length).padStart(4,'0')}.json`,descriptor={path,sha256:sha256(text),bytes:size};files.push({descriptor,text});for(const id of Object.keys(current))locations.set(id,descriptor);current={};currentBytes=0;}
  for(const [id,value] of entries){const n=Buffer.byteLength(JSON.stringify(id))+bytes(value)+2;if(currentBytes&&currentBytes+n>targetBytes)flush();current[id]=value;currentBytes+=n;}
  flush();return {files,locations};
}

export function partitionCatalog(logical,{entryDestinationId,detailTargetBytes=256*1024,membershipTargetBytes=1024*1024,maxFileBytes=MAX_FILE}={}){
  const sourceMap=new Map(logical.sources.map(s=>[s.id,s])),destMap=new Map(logical.destinations.map(d=>[d.id,d]));
  if(destMap.size!==logical.destinations.length||sourceMap.size!==logical.sources.length)throw new Error('Duplicate logical atlas identity');
  const byDestination=new Map(logical.destinations.map(d=>[d.id,[]]));
  for(const row of logical.memberships){if(!byDestination.has(row.destinationId)||!sourceMap.has(row.unitId))throw new Error('Unknown logical membership endpoint');byDestination.get(row.destinationId).push(row);}
  const membershipEntries=[],counts=new Map(),membershipHashes=new Map(),allMemberIds=new Set();
  for(const d of logical.destinations){const rows=byDestination.get(d.id),seen=new Set();for(const r of rows){if(seen.has(r.unitId))throw new Error(`Duplicate source membership ${d.id}`);seen.add(r.unitId);allMemberIds.add(r.unitId);}const primary=rows.filter(r=>!contextual(r)),count={primaryCount:primary.length,contextCount:rows.length-primary.length,paperCount:new Set(primary.map(r=>r.paperId).filter(Boolean)).size};counts.set(d.id,count);membershipHashes.set(d.id,setHash(primary.map(r=>r.unitId)));if(d.memberIdsSha256&&d.memberIdsSha256!==membershipHashes.get(d.id))throw new Error('Logical member hash changed before partition');if(rows.length)membershipEntries.push([d.id,{...count,items:rows}]);}
  const membershipPack=packEntries(membershipEntries,{kind:'eigenquestions-destination-memberships',prefix:'destination-memberships',targetBytes:membershipTargetBytes,maxFileBytes});
  const details={entry:[],metadata:[],authored:[],fine:[]};
  for(const d of logical.destinations){
    const rows=byDestination.get(d.id),sample=sampleRows(rows,d),sampleIds=new Set([...sample.map(r=>r.unitId),...(d.evidenceIds||[]).slice(0,30),...(d.contextSourceIds||[]).slice(0,6)]);
    const destination={...d,memberIdsExternal:rows.length>0};delete destination.memberIds;
    const sources=[...sampleIds].map(id=>{const s=sourceMap.get(id);if(!s)throw new Error(`Unknown representative source ${id}`);return s;});
    const detail={destination,sources,membershipSample:sample,...(rows.length?{memberships:membershipPack.locations.get(d.id)}:{}),coverage:{...counts.get(d.id),membershipSampleIsComplete:sample.length===rows.length,memberIdsSha256:membershipHashes.get(d.id)}};
    const category=d.id===entryDestinationId?'entry':d.metadataOnly?'metadata':d.sourceQuestionAccess?'fine':'authored';details[category].push([d.id,detail]);
  }
  const files=[...membershipPack.files],detailShards={},detailLocations=new Map();
  for(const [category,entries] of Object.entries(details)){
    const pack=packEntries(entries,{kind:'eigenquestions-destination-details',prefix:`destination-details-${category}`,targetBytes:category==='metadata'?64*1024:detailTargetBytes,maxFileBytes});
    for(const file of pack.files){const shardId=file.descriptor.path.replace(/\.json$/,'');detailShards[shardId]=file.descriptor;files.push(file);}for(const [id,descriptor] of pack.locations)detailLocations.set(id,descriptor.path.replace(/\.json$/,''));
  }
  const incident=new Map(logical.destinations.map(d=>[d.id,[]]));for(const r of logical.relations){if(!incident.has(r.source)||!incident.has(r.target))throw new Error('Unknown navigation endpoint during partition');incident.get(r.source).push(r);if(r.target!==r.source)incident.get(r.target).push(r);}
  const destinations=logical.destinations.map(d=>{const value=Object.fromEntries(indexFields.filter(k=>d[k]!==undefined).map(k=>[k,d[k]]));if(value.question===value.title)delete value.question;if(!value.aliases?.length)delete value.aliases;
    // The source-facet summary is invariant boilerplate and is present in the full detail.
    if(d.sourceQuestionAccess)delete value.summary;
    const n=counts.get(d.id);return {...value,membershipCount:n.primaryCount,contextMembershipCount:n.contextCount,paperCount:n.paperCount,connectionCount:incident.get(d.id).length,detail:{shardId:detailLocations.get(d.id)}};});
  let catalog={...logical,storage:'lazy-destinations-v1',destinations,sources:[],memberships:[],detailShards};
  if(catalog.sourceContributions){catalog.sourceContributionInventory={count:catalog.sourceContributions.length,sha256:sha256(JSON.stringify(catalog.sourceContributions)),access:'Complete exact typed contributions are stored in each destination detail; they are not primary membership or geometry allocations.'};delete catalog.sourceContributions;}
  const ancillary={};for(const key of ['fineIdentityProposals','unrepresentedPapers'])if(catalog[key]){const text=JSON.stringify(catalog[key]),descriptor={path:`${key.replace(/[A-Z]/g,x=>'-'+x.toLowerCase())}.json`,sha256:sha256(text),bytes:Buffer.byteLength(text)};if(descriptor.bytes>maxFileBytes)throw new Error(`Ancillary ${key} exceeds file bound`);files.push({descriptor,text});ancillary[key]=descriptor;delete catalog[key];}
  catalog.sourceInventory={sourceCount:logical.sources.filter(s=>s.kind!=='vocabulary').length,vocabularyCount:logical.sources.filter(s=>s.kind==='vocabulary').length,access:'Exact frozen browserVectorRow memberships; bounded source records in destination detail; full source context separately pinned.'};
  catalog=templateIndex(catalog);
  const fineIds=new Set(logical.destinations.filter(d=>d.sourceQuestionAccess).map(d=>d.id)),fineRelationIds=new Set(logical.relations.filter(r=>fineIds.has(r.source)||fineIds.has(r.target)).map(r=>r.id)),indexById=new Map(catalog.destinations.map(d=>[d.id,d])),indexedRelationById=new Map(catalog.relations.map(r=>[r.id,r]));
  // Details refer only to stable shard IDs, so this second pass introduces no
  // checksum cycle. A known parent's local fine links do not load global search.
  for(const file of files.filter(f=>f.descriptor.path.startsWith('destination-details-'))){
    const payload=JSON.parse(file.text);for(const [id,detail] of Object.entries(payload.destinations)){
      const relations=incident.get(id).filter(r=>fineRelationIds.has(r.id)),neighborIds=new Set();for(const r of relations)for(const endpoint of [r.source,r.target])if(endpoint!==id&&fineIds.has(endpoint))neighborIds.add(endpoint);
      detail.navigation={destinations:[...neighborIds].map(n=>indexById.get(n)),relations:relations.map(r=>indexedRelationById.get(r.id))};
    }
    file.text=JSON.stringify(payload);file.descriptor={...file.descriptor,sha256:sha256(file.text),bytes:Buffer.byteLength(file.text)};if(file.descriptor.bytes>maxFileBytes)throw new Error('Destination navigation detail exceeds file bound');detailShards[file.descriptor.path.replace(/\.json$/,'')]=file.descriptor;
  }
  catalog.detailShards=detailShards;
  if(fineIds.size){
    const fine={schemaVersion:'1.0.0',kind:'eigenquestions-fine-index',destinations:catalog.destinations.filter(d=>fineIds.has(d.id)),relations:catalog.relations.filter(r=>fineRelationIds.has(r.id)),indexTemplates:catalog.indexTemplates},text=JSON.stringify(fine),descriptor={path:'fine-index.json',sha256:sha256(text),bytes:Buffer.byteLength(text)};if(descriptor.bytes>maxFileBytes)throw new Error('Fine search index exceeds file bound');files.push({descriptor,text});catalog.fineIndex=descriptor;
    const buckets=new Map();for(const d of fine.destinations){if(!/^source-question:[a-f0-9]{64}$/.test(d.id))throw new Error('Fine lookup requires exact frozen question hash IDs');const prefix=d.id.slice('source-question:'.length,'source-question:'.length+2);if(!buckets.has(prefix))buckets.set(prefix,[]);buckets.get(prefix).push(d);}
    const shards={};for(const [prefix,rows] of [...buckets].sort(([a],[b])=>a.localeCompare(b))){const ids=new Set(rows.map(r=>r.id)),payload={...fine,destinations:rows,relations:fine.relations.filter(r=>ids.has(r.source)||ids.has(r.target))},text=JSON.stringify(payload),descriptor={path:`fine-lookup-${prefix}.json`,sha256:sha256(text),bytes:Buffer.byteLength(text)};if(descriptor.bytes>maxFileBytes)throw new Error('Fine lookup bucket exceeds file bound');shards[prefix]=descriptor;files.push({descriptor,text});}catalog.fineLookup={kind:'source-question-hash-prefix',prefixLength:2,shards};
    catalog.destinations=catalog.destinations.filter(d=>!fineIds.has(d.id));catalog.relations=catalog.relations.filter(r=>!fineRelationIds.has(r.id));
  }
  const report={schemaVersion:'q025-lazy-partition-validation/1',logicalDestinationCount:logical.destinations.length,initialDestinationCount:catalog.destinations.length,fineDestinationCount:fineIds.size,logicalSourceCount:logical.sources.length,logicalMembershipCount:logical.memberships.length,representedMembershipSourceCount:allMemberIds.size,navigationRelationCount:logical.relations.length,membershipShardCount:membershipPack.files.length,detailShardCount:Object.keys(detailShards).length,totalShardCount:files.length,totalShardBytes:files.reduce((s,f)=>s+f.descriptor.bytes,0),largestMembershipShardBytes:Math.max(0,...membershipPack.files.map(f=>f.descriptor.bytes)),largestDetailShardBytes:Math.max(0,...Object.values(detailShards).map(f=>f.bytes)),catalogBytes:bytes(catalog),fineIndexBytes:catalog.fineIndex?.bytes||0,catalogSourcesInitiallyLoaded:0,catalogMembershipsInitiallyLoaded:0,destinationCounts:Object.fromEntries(counts),membershipIdentityHashes:Object.fromEntries(membershipHashes),ancillary,limitations:['Partitioning preserves a separately validated logical assembly; it does not admit reviewer proposals.','Default bounded samples cannot answer complete filtered queries; load the pinned complete selected membership first.']};
  if(report.catalogBytes>maxFileBytes)throw new Error(`Lazy index exceeds file bound: ${report.catalogBytes}`);
  return {catalog,files,report,ancillary};
}

export async function writeLazyPackage({directory,manifest,catalog:logical,provenance,publicationStatus,validateLogical,externalAssets=[],ordinarySiteAssetReserve=500}){
  if(!validateLogical)throw new Error('Lazy export requires full logical atlas validation');
  const validation=await validateLogical(logical);
  const partition=partitionCatalog(logical,{entryDestinationId:manifest.entryDestinationId});await mkdir(directory,{recursive:true});
  const roundTrip=validatePartition(logical,partition);
  for(const file of partition.files)await writeFile(join(directory,file.descriptor.path),file.text);
  const receipt={...partition.report,fullLogicalValidation:validation,partitionRoundTrip:roundTrip},receiptText=JSON.stringify(receipt),validationDescriptor={path:'partition-validation.json',sha256:sha256(receiptText),bytes:Buffer.byteLength(receiptText)};
  await writeFile(join(directory,validationDescriptor.path),receiptText);
  const catalogText=JSON.stringify(partition.catalog),catalogDescriptor={path:'catalog.json',sha256:sha256(catalogText),bytes:Buffer.byteLength(catalogText)};
  const deliveryFiles=[...partition.files.map(f=>f.descriptor),catalogDescriptor,validationDescriptor,...externalAssets.map(({path,sha256,bytes})=>({path,sha256,bytes}))];
  if(new Set(deliveryFiles.map(f=>f.path)).size!==deliveryFiles.length)throw new Error('Duplicate delivery asset path');
  const projectedFileCount=deliveryFiles.length+2+logical.destinations.length+ordinarySiteAssetReserve;if(projectedFileCount>20000)throw new Error(`Projected full static delivery exceeds 20000 assets: ${projectedFileCount}`);
  for(const f of deliveryFiles)if(!Number.isSafeInteger(f.bytes)||f.bytes>MAX_FILE||f.bytes<1)throw new Error(`Delivery asset violates25MiB bound: ${f.path}`);
  const delivery={schemaVersion:'q025-delivery-assets/1',files:deliveryFiles,gate:{maxFileBytes:MAX_FILE,maxFileCount:20000,staticDestinationPages:logical.destinations.length,ordinarySiteAssetReserve,projectedFileCount,passed:true},sourceGeometryChanged:false},deliveryText=JSON.stringify(delivery),deliveryDescriptor={path:'delivery-assets.json',sha256:sha256(deliveryText),bytes:Buffer.byteLength(deliveryText)};await writeFile(join(directory,deliveryDescriptor.path),deliveryText);
  manifest={...manifest,schemaVersion:'1.1.0',files:{...manifest.files,catalog:catalogDescriptor,logicalValidation:validationDescriptor,deliveryAssets:deliveryDescriptor,...partition.ancillary}};
  const manifestText=JSON.stringify(manifest);await writeFile(join(directory,'catalog.json'),catalogText);await writeFile(join(directory,'manifest.json'),manifestText);
  const handoff={schemaVersion:'q025-assembly-handoff/1',publicationStatus,notApprovedForSiteRelease:publicationStatus!=='accepted_for_installation',packageDirectory:directory,manifestSha256:sha256(manifestText),catalogSha256:catalogDescriptor.sha256,catalogBytes:catalogDescriptor.bytes,counts:{destinations:logical.destinations.length,sources:logical.sources.length,memberships:logical.memberships.length,navigationRelations:logical.relations.length,orientationNodes:logical.orientation?.nodes.length||0,detailOverviewNodes:logical.overview?.nodes.length||0},partition:{validation:validationDescriptor,deliveryAssets:deliveryDescriptor,assetCount:partition.files.length+4,totalShardBytes:partition.report.totalShardBytes,largestMembershipShardBytes:partition.report.largestMembershipShardBytes,largestDetailShardBytes:partition.report.largestDetailShardBytes,fileCountGate:delivery.gate},provenance};
  await writeFile(join(directory,'handoff.json'),JSON.stringify(handoff,null,2)+'\n');return {handoff,partition};
}
