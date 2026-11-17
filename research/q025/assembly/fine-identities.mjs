/** Preserve compact review identity proposals without semantic merges. */
import {sha256} from './corpus.mjs';
const fail=message=>{throw new Error(`Fine identity assembly: ${message}`);};
export const sourceQuestionId=unitId=>`source-question:${unitId.replace(/^unit:/,'')}`;

export function normalizeCompactIdentity({packet,reply,corpus,packetSha256,replySha256,reviewId}) {
  if(packet.version!=='q025-compact-packet/1'||reply.version!=='q025-compact-review/1'||packet.familyId!==reply.familyId||packet.stage!==reply.stage)fail('compact packet/reply identity mismatch');
  const map=new Map();
  for(const u of packet.units){
    const d=packet.refRegistry[u.descriptionRef],s=packet.refRegistry[u.sourceRef];
    if(d?.kind!=='description'||s?.kind!=='source_unit'||d.unitId!==s.unitId||d.unitIndex!==u.i||s.unitIndex!==u.i)fail('ambiguous packet unit mapping');
    const source=corpus.unitMap.get(d.unitId);if(!source||source.lens!=='physical_question'||source.paperId!==u.paperId||source.text!==u.description||sha256(source.text)!==d.textSha256)fail('compact source description differs from frozen source');
    if(map.has(u.i))fail('duplicate packet index');map.set(u.i,source.id);
  }
  const defs=new Map([...(packet.priorGroups||[]),...reply.identityGroups].map(g=>[g.id,g]));
  const rows=[],seen=new Set(),groups=new Map();
  for(const r of reply.units){
    if(!map.has(r.i)||seen.has(r.i))fail('missing/duplicate exact unit row');seen.add(r.i);
    if(!['s','?'].includes(r.identity)&&!defs.has(r.identity))fail('unknown proposed fine group');
    const status=r.identity==='s'?'proposed_singleton':r.identity==='?'?'unresolved':'candidate_group';
    if(status==='unresolved'&&!r.note)fail('unresolved identity lacks a reason');
    const groupId=status==='candidate_group'?`identity-proposal:${sha256(packet.familyId+'\n'+reviewId+'\n'+r.identity).slice(0,24)}`:null;
    if(groupId&&!groups.has(groupId)){const g=defs.get(r.identity);if(!map.has(g.representative))fail('group representative has no exact source');groups.set(groupId,{id:groupId,localId:r.identity,title:g.title,reason:g.reason,definingDifferences:g.definingDifferences,representativeUnitId:map.get(g.representative),memberIds:[],identityStatus:'candidate_equivalence_not_admitted',refs:g.refs,reviewId,packetSha256,replySha256});}
    if(groupId)groups.get(groupId).memberIds.push(map.get(r.i));
    rows.push({unitId:map.get(r.i),sourceQuestionDestinationId:sourceQuestionId(map.get(r.i)),identityStatus:status,candidateGroupId:groupId,proposedTitle:r.title,note:r.note,overviewContributions:r.q,placementDisposition:r.d,priorAssignmentAgreement:r.a,basis:r.b,reason:r.reason,alternateHome:r.home,refs:r.refs,factorRefs:r.f,reviewId,packetSha256,replySha256});
  }
  if(seen.size!==map.size)fail('compact reply drops source units');
  for(const g of groups.values())if(g.memberIds.length<2||!g.memberIds.includes(g.representativeUnitId))fail('candidate group lacks its representative or multiple sources');
  return {schemaVersion:'q025-normalized-fine-proposals/1',familyId:packet.familyId,reviewId,rows,groups:[...groups.values()],cardReviews:reply.cardReviews,groupReviews:reply.groupReviews,identityComparisons:reply.identityComparisons,limitations:reply.limitations,admissionMeaning:'These are proposals and explicit review assessments only. No group, alias, scope or placement is admitted by this normalization.'};
}

export function attachFineSourceAccess(catalog,{corpus,proposalBundles=[],policyDecisionId}) {
  const rowMap=new Map(),groups=[];
  for(const b of proposalBundles){groups.push(...b.groups);for(const r of b.rows){if(!rowMap.has(r.unitId))rowMap.set(r.unitId,[]);rowMap.get(r.unitId).push(r);}}
  const destinations=new Map(catalog.destinations.map(d=>[d.id,d])),regionalMembership=new Map();
  for(const m of catalog.memberships)if(m.lens==='physical_question'&&!m.associationScope){if(!regionalMembership.has(m.unitId))regionalMembership.set(m.unitId,[]);regionalMembership.get(m.unitId).push(m.destinationId);}
  const narrowerParents=new Map(catalog.destinations.map(d=>[d.id,[]]));for(const r of catalog.relations)if(r.type==='narrower')narrowerParents.get(r.target)?.push(r.source);
  function isAncestor(parent,child){const todo=[...(narrowerParents.get(child)||[])],seen=new Set();while(todo.length){const x=todo.pop();if(x===parent)return true;if(seen.has(x))continue;seen.add(x);todo.push(...(narrowerParents.get(x)||[]));}return false;}
  for(const u of corpus.units.filter(u=>u.lens==='physical_question')){
    const id=sourceQuestionId(u.id);if(destinations.has(id))fail('source-question ID collision');
    const history=rowMap.get(u.id)||[];const unresolved=history.some(r=>r.identityStatus!=='proposed_singleton');
    const identityStatus=history.length?(unresolved?'unresolved_or_group_proposal':'proposed_singleton'):'unreviewed_source_facet';
    const d={id,kind:'question',title:u.text,question:u.text,summary:'This is one exact source-scoped extracted question. Its relationship to other formulations remains an explicit identity-review state; the source ID alone does not establish canonical equivalence.',scope:{assumptions:[],includes:[],excludes:[],regimes:[],conventions:[],sourceContextUnitId:u.id},aliases:[],evidenceIds:[u.id],scientificStatus:'source_scoped_extraction_not_canonical_equivalence',placementStatus:'source_facet_access',identityStatus,membershipStatus:'representative',representativeUnitId:u.id,sourceQuestionAccess:true,provenance:{policyDecisionId,frozenTextSha256:u.evidence.textSha256,browserVectorRow:u.browserVectorRow,sourceRow:u.sourceRow,identityReviewRefs:history.map(r=>({reviewId:r.reviewId,packetSha256:r.packetSha256,replySha256:r.replySha256,candidateGroupId:r.candidateGroupId,identityStatus:r.identityStatus}))}};
    catalog.destinations.push(d);destinations.set(id,d);
    const paper=corpus.papers.get(u.paperId);catalog.memberships.push({destinationId:id,unitId:u.id,paperId:u.paperId,weight:1,role:'evidence',lens:'physical_question',year:paper.year,browserVectorRow:u.browserVectorRow,sourceRow:u.sourceRow,placementStatus:'source_facet_access'});
    const homes=regionalMembership.get(u.id)||[];const nearest=homes.filter(p=>!homes.some(other=>p!==other&&isAncestor(p,other)));
    if(!nearest.length)fail('fine source has no meaningful authored family/card home');
    for(const home of nearest)catalog.relations.push({id:`source-access:${sha256(home+'\n'+u.id).slice(0,24)}`,source:home,target:id,type:'source_question',rationale:'Inspect the exact source question contributing to this authored family/card. This access link does not assert equivalence to the overview question.',status:'source_identity_access',evidenceIds:[u.id],provenance:{policyDecisionId,sourceUnitId:u.id,canonicalEquivalenceEstablished:false}});
  }
  catalog.fineIdentityProposals={groups,unitReviewStates:[...rowMap].map(([unitId,history])=>({unitId,history})),canonicalGroupsAutomaticallyCreated:0,meaning:'Candidate groups retain exact source-question destinations. Separate admitted equivalence decisions are required to create canonical groups or aliases.'};
  return catalog;
}
