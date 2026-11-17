/** Mechanical source/scope binding only. This does not admit the proposed amendment. */
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {dirname,join,resolve,relative} from 'node:path';
import {fileURLToPath} from 'node:url';
import {sha256,loadFrozenCorpus} from '../corpus.mjs';
import {scopeContentHash} from '../accepted.mjs';
const here=dirname(fileURLToPath(import.meta.url)),root=resolve(here,'../../../..');
const read=async(path,expected)=>{const raw=await readFile(join(root,path));if(expected&&sha256(raw)!==expected)throw Error('Changed input '+path);return {value:JSON.parse(raw),pin:{path,sha256:sha256(raw),bytes:raw.length}};};
export async function preflight(){
 const proposal=await read('research/q025/evaluation/final-holdout/dated-43-source-amendment-proposal.json','0a8396910883bdf3deefc4af987b570b6af9294e744e3c56038cb12dca0828eb');
 const base=await read('research/q025/assembly/final-preholdout-v1/packet/aggregate.local.json','6074b5a4b582e25984a8fd848cf4f77d12f4a60f865867e4905b1d97427b926c');
 const candidateFreeze=await read('research/q025/evaluation/final-holdout/candidate-freeze.json',proposal.value.candidateFreezeSha256),scoreFreeze=await read('research/q025/evaluation/final-holdout/score-freeze.json',proposal.value.scoreFreezeSha256);
 const frozen=join(root,'research/q025/assembly/outputs/final-preholdout-geometry-v1');
 for(const p of candidateFreeze.value.candidatePins)await read(p.path,p.sha256);
 const corpus=await loadFrozenCorpus(join(root,'data/navigation')),reserved=new Set(base.value.coverage.reservedUnitIds),seen=new Set(),destinations=new Map(base.value.destinations.map(d=>[d.id,d])),targetPins=[],sourceBindings=[];
 for(const [id,t]of Object.entries(proposal.value.targets)){
  const d=destinations.get(id);if(!d||scopeContentHash(d)!==t.scopeContentSha256||scopeContentHash(t.destination)!==t.scopeContentSha256)throw Error('Changed target scientific scope '+id);
  const shard=await read(relative(root,join(frozen,t.frozenDetailShard.path)),t.frozenDetailShard.sha256);if(Object.entries(t.destination).some(([key,value])=>JSON.stringify(shard.value.destinations[id].destination[key])!==JSON.stringify(value)))throw Error('Proposal differs from frozen target science/reading fields '+id);
  targetPins.push({destinationId:id,scopeContentSha256:t.scopeContentSha256,detail:shard.pin});
 }
 for(const r of proposal.value.rows){
  const u=corpus.unitMap.get(r.unitId);if(!u||!reserved.has(u.id)||seen.has(u.id)||u.text!==r.sourceQuestion||sha256(u.text)!==r.sourceTextSha256||u.paperId!==r.paperId||u.sourceRow!==r.sourceRow||u.browserVectorRow!==r.browserVectorRow||Math.abs(u.mass-r.originalMass)>1e-12)throw Error('Changed or duplicate reserved source '+r.unitId);
  if(r.basis!=='description_checked'||r.newScopeRequested||r.automaticAdmission)throw Error('Amendment claims an unauthorized basis or promotion');
  if(r.disposition==='proposed_existing_whole_question_home'){if(!destinations.has(r.destinationId)||!proposal.value.targets[r.destinationId]||r.allocationWeight!==1||r.coverageMode!=='whole_immutable_source_target')throw Error('Invalid proposed whole-source home');}
  else if(r.disposition!=='proposed_unresolved_source_facet'||r.destinationId||r.allocationWeight!==0)throw Error('Invalid unresolved source disposition');
  seen.add(u.id);sourceBindings.push({rowIndex:r.rowIndex,unitId:u.id,paperId:u.paperId,sourceRow:u.sourceRow,browserVectorRow:u.browserVectorRow,descriptionSha256:u.evidence.textSha256,originalMass:u.mass,disposition:r.disposition,destinationId:r.destinationId||null,scopeContentSha256:r.destinationId?proposal.value.targets[r.destinationId].scopeContentSha256:null});
 }
 if(seen.size!==43||reserved.size!==43)throw Error('Not the exact frozen 43-source set');
 const sourceReadingArtifacts=[];for(const p of proposal.value.sourceReadingArtifacts)sourceReadingArtifacts.push((await read(p.path,p.sha256)).pin);
 const result={schemaVersion:'q025-dated-amendment-preflight/1',status:'mechanically_validated_not_admitted',proposal:proposal.pin,base:base.pin,candidateFreeze:candidateFreeze.pin,scoreFreeze:scoreFreeze.pin,targetCount:targetPins.length,sourceCount:sourceBindings.length,counts:proposal.value.counts,targetPins,sourceBindings,sourceReadingArtifacts,expectedAccountingIfApproved:{resolved:8436,unresolved:37,reserved:0,total:8473},scientificApprovalPending:true,noNewScopesRoutesAliasesRoles:true,sourceHomeNotice:'A precise topic placement has not been established for this source.',scriptSha256:sha256(await readFile(fileURLToPath(import.meta.url)))};
 await mkdir(here,{recursive:true});const raw=JSON.stringify(result,null,2)+'\n';await writeFile(join(here,'preflight.json'),raw);console.log(JSON.stringify({path:relative(root,join(here,'preflight.json')),sha256:sha256(raw),sourceCount:seen.size,targetCount:targetPins.length,status:result.status}));return {proposal,base,result};
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url))await preflight();
