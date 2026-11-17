/** Verify a direct-home / exact-source-positive-role composition, never containment. */
import {sha256} from './corpus.mjs';
const sorted=v=>Array.isArray(v)?v.map(sorted):v&&typeof v==='object'?Object.fromEntries(Object.keys(v).sort().map(k=>[k,sorted(v[k])])):v;
export const certificateHash=record=>sha256(JSON.stringify(sorted(Object.fromEntries(Object.entries(record).filter(([k])=>k!=='certificateSha256')))));
const positive=new Set(['addresses','instantiates','specializes']);
const exception=['q025-candidate-region:88fa8687d2ded4f0a4462ab0','q025-candidate-region:953776ce2227c9ba181efcad'];
export function validateOrganizationalAccess({row,record,destinations,placements,contributions,decisions,identityResolution,scopeHash}){
  const fail=m=>{throw Error('Organizational access: '+m);};
  const meta=row.organizationalAccess;
  if(row.type!=='related_question'||row.provenance?.navigationBasis!=='same_source_organizational_access'||!meta||meta.countScope!=='scope_wide')fail('wrong semantic discriminator');
  if(!record||record.id!==row.id||meta.supportCertificate.recordId!==row.id||record.source!==row.source||record.target!==row.target||record.certificateSha256!==meta.certificateSha256||certificateHash(record)!==meta.certificateSha256)fail('certificate or exact route binding changed');
  const ds=new Map(destinations.map(d=>[d.id,d])),source=ds.get(row.source),target=ds.get(row.target);
  if(!['region','question'].includes(source?.kind)||!target||source.id===target.id)fail('source must be a distinct admitted scientific scope');
  if(target.kind!=='question'&&!(source.id===exception[0]&&target.id===exception[1]))fail('unapproved nonquestion target');
  const policyClass=source.kind==='question'?'fine_home_to_question':target.kind==='question'?'broad_home_to_question':'explicit_region_exception';
  // Historical broad certificates predate this additive discriminator. Fine
  // homes require an explicit new class on both the route and its certificate;
  // their source attribution never becomes containment or allocation.
  if(source.kind==='question'&&(record.policyClass!==policyClass||meta.policyClass!==policyClass))fail('fine home requires explicit approved policy class');
  if(record.policyClass!==undefined&&record.policyClass!==policyClass||meta.policyClass!==undefined&&meta.policyClass!==policyClass)fail('policy class disagrees with exact endpoint kinds');
  for(const [key,d]of [['source',source],['target',target]])if(record.endpointBindings[key].scopeContentSha256!==scopeHash(d)||record.endpointBindings[key].id!==d.id||record.endpointBindings[key].kind!==d.kind)fail('current endpoint scope binding changed');
  const alias=new Map();for(const g of identityResolution.groups)for(const id of g.memberIds)alias.set(id,g.destinationId);
  const canonical=id=>alias.get(id)||id,homes=new Map(placements.map(p=>[p.decisionId+'\n'+p.unitId,p])),roles=new Map(contributions.map(r=>[r.decisionId+'\n'+r.unitId+'\n'+r.destinationId+'\n'+r.role,r]));
  const seen=new Set();
  for(const w of record.witnesses){
    if(seen.has(w.unitId))fail('duplicate source witness');seen.add(w.unitId);
    const h=homes.get(w.home.decisionId+'\n'+w.unitId);
    if(!h||h.status!=='accepted'||!['member','overlap'].includes(h.role)||!(h.allocationWeight>0)||h.destinationId!==source.id||JSON.stringify(h)!==JSON.stringify(w.home))fail('not an exact direct accepted home');
    if(JSON.stringify(decisions.get(h.decisionId))!==JSON.stringify(w.homeDecision))fail('home proof changed');
    if(!w.observations?.length)fail('missing positive observation');
    for(const o of w.observations){const raw=o.contribution,r=roles.get(raw.decisionId+'\n'+w.unitId+'\n'+raw.destinationId+'\n'+raw.role);if(!r||!positive.has(r.role)||canonical(r.destinationId)!==target.id||JSON.stringify(r)!==JSON.stringify(raw))fail('not an exact same-unit positive contribution');if(JSON.stringify(decisions.get(r.decisionId))!==JSON.stringify(o.contributionDecision))fail('contribution proof changed');}
  }
  if(!seen.size||seen.size!==meta.uniqueWitnessCount||seen.size!==record.uniqueWitnessCount)fail('scope-wide witness inventory differs');
  if(row.evidenceIds.length!==seen.size||row.evidenceIds.some(id=>!seen.has(id)))fail('route evidence differs from complete witness inventory');
  return {uniqueWitnessCount:seen.size,observationCount:record.witnesses.reduce((n,w)=>n+w.observations.length,0)};
}
