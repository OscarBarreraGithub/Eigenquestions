/** Resolve a real admitted component through the production gates, no fixture. */
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {resolve,join,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {parseArgs} from 'node:util';
import {readPinnedJson,loadFrozenCorpus,sha256} from './corpus.mjs';
import {compileSourceContributions,validateAdmittedScope} from './accepted.mjs';
import {verifyPrimaryEvidence} from './primary-evidence.mjs';

export async function preflightContributions({root,componentPath,componentSha256,out}){
  const input=await readPinnedJson(componentPath,componentSha256),packet=input.value;
  const resolveInput=path=>path.startsWith('research/')?resolve(root,path):resolve(dirname(componentPath),path);
  const reviews=new Map(),verifiedReceiptHashes=new Set(),verifiedArtifacts=[];
  for(const r of packet.reviewRegistry){
    const path=resolveInput(r.path),bytes=await readFile(path);if(sha256(bytes)!==r.sha256)throw new Error(`Changed source review ${r.id}`);
    reviews.set(r.id,r);verifiedReceiptHashes.add(r.sha256);verifiedArtifacts.push({id:r.id,path:r.path,sha256:r.sha256,bytes:bytes.length});
  }
  for(const d of packet.decisions)if(d.adjudication?.receipt){const r=d.adjudication.receipt,p=await readPinnedJson(resolveInput(r.path),r.sha256);verifiedReceiptHashes.add(p.sha256);}
  const decisions=new Map(packet.decisions.map(d=>[d.id,d]));
  const decision=(id,types)=>{
    const d=decisions.get(id);if(!d||d.status!=='accepted'||!types.includes(d.type))throw new Error(`Not an admitted decision ${id}`);
    if(!d.evidenceRefs?.length||!d.sourceReviewIds?.length||d.sourceReviewIds.some(id=>!reviews.has(id)))throw new Error(`Missing pinned decision evidence ${id}`);
    return d;
  };
  const corpus=await loadFrozenCorpus(join(root,'data/navigation'));
  const contextRoot=join(root,'research/q025/geometry/source-context-v3-compact/pack');
  const context=await readPinnedJson(join(contextRoot,'manifest.json'),'c86bc90966007c28ce40523348e51e4ace4d20d62354f79928133d371f77c6f5');
  const primary=await verifyPrimaryEvidence({references:[...(packet.sourceContributions||[]),...packet.decisions].flatMap(r=>r.evidenceRefs||[]),corpus,archiveRoot:'/Users/emmy/Developer/physics-atlas-swampland',contextRoot,contextManifest:context.value});
  for(const d of packet.destinations)validateAdmittedScope(d,{decision,verifiedReceiptHashes});
  const args={rows:packet.sourceContributions,destinations:packet.destinations,units:corpus.unitMap,decision,reviewRecords:reviews,verifiedPrimaryLocators:primary.verifiedLocators,verifiedReceiptHashes};
  const compiled=compileSourceContributions(args),explicit=compiled.filter(r=>r.provenance.challengerAgreement==='coordinator_adjudicated_source_contribution');
  const negative=[];
  if(explicit.length){
    const row=packet.sourceContributions.find(r=>r.decisionId===explicit[0].decisionId),proof=decisions.get(row.decisionId);
    const reject=(name,changed)=>{let error;try{compileSourceContributions({...args,rows:[row],...changed});}catch(e){error=e.message;}if(!error)throw new Error(`Negative control admitted: ${name}`);negative.push({name,error,rejected:true});};
    reject('actual row mutated after its contribution hash',{rows:[{...row,role:row.role==='addresses'?'instantiates':'addresses'}]});
    reject('actual destination scope mutated after admission',{destinations:packet.destinations.map(d=>d.id===row.destinationId?{...d,question:d.question+' Changed.'}:d)});
    reject('actual adjudication receipt unverified',{verifiedReceiptHashes:new Set([...verifiedReceiptHashes].filter(h=>h!==proof.adjudication.receipt.sha256))});
  }
  const report={schemaVersion:'q025-real-contribution-component-preflight/1',status:'passed_component_gates_not_full_atlas_assembly',fixture:false,component:{path:componentPath,sha256:input.sha256},verifiedArtifacts,primaryEvidenceVerification:primary.report,scopeCount:packet.destinations.length,sourceContributionCount:compiled.length,explicitCoordinatorContributionCount:explicit.length,explicitRows:explicit.map(r=>({unitId:r.unitId,destinationId:r.destinationId,role:r.role,basis:r.basis,decisionId:r.decisionId,scopeContentSha256:r.scopeContentSha256,provenance:r.provenance})),negativeControls:negative,homesCreated:0,geometricAllocationsCreated:0,usingClaimsCreated:0,scopeOrAliasAdmissionsCreated:0,helperSha256:sha256(await readFile(fileURLToPath(new URL('./accepted.mjs',import.meta.url)))),scriptSha256:sha256(await readFile(fileURLToPath(import.meta.url))),meaning:'Exact frozen source identity, admitted scope/row hashes, native review bytes, coordinator receipt bytes and primary locators checked. This does not repeat or replace the coordinator scientific reading.'};
  await mkdir(dirname(out),{recursive:true});await writeFile(out,JSON.stringify(report,null,2)+'\n');return report;
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){
  const {values}=parseArgs({options:{component:{type:'string'},sha256:{type:'string'},out:{type:'string'}}});
  if(!values.component||!values.sha256||!values.out)throw new Error('--component --sha256 --out required');
  const root=resolve(fileURLToPath(new URL('../../../',import.meta.url)));
  const result=await preflightContributions({root,componentPath:resolve(values.component),componentSha256:values.sha256,out:resolve(values.out)});
  console.log(JSON.stringify({status:result.status,scopes:result.scopeCount,contributions:result.sourceContributionCount,explicit:result.explicitCoordinatorContributionCount,primaryLocators:result.primaryEvidenceVerification.distinctLocators,negativeControls:result.negativeControls.length}));
}
