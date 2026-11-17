"""Nine exact pilot cases and a bounded global scope nomination audit; no admission."""
import collections,hashlib,json,math,re
from pathlib import Path
B=Path(__file__).resolve().parent;ROOT=B.parents[3];R=ROOT/'research/q025/assembly/organization-residual-v1';F=ROOT/'research/q025/evaluation/full-pass';OUT=B

def read(p):
 b=p.read_bytes();return json.loads(b),{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def pin(p):
 b=p.read_bytes();return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
a,ap=read(R/'candidate-6030-canonical-v3/aggregate.local.json');intake,ip=read(ROOT/'research/q025/integration/placement-pilot-intake-v1/intake-20261117T153723Z.json');ds={d['id']:d for d in a['destinations']};science=('id','kind','title','question','summary','scope','methods','readingCoverage','scopeContentSha256')
def scoped(d):return {k:d[k]for k in science if k in d}
stop=set('the a an and of to in for is are with from by as on or can do does how what which at its their that these this under between whether'.split())
def tok(x):return set(w for w in re.findall(r'[a-z0-9]+',x.lower())if len(w)>2 and w not in stop)
docs={d['id']:tok(json.dumps({k:d.get(k)for k in ['title','question','scope']},ensure_ascii=False))for d in ds.values()};df=collections.Counter(w for t in docs.values()for w in t)
selection=[('competing','u2','challenger_revision'),('competing','u16','challenger_revision'),('absent','u0','new_scope'),('absent','u3','new_scope'),('absent','u5','new_scope'),('annotation','u0','unchanged_annotation'),('annotation','u1','unchanged_broad_composite'),('coverage','u0','unchanged_cross_context'),('coverage','u10','unchanged_whole_composite')]
cache={};cases=[];lookups=[]
for family,ref,kind in selection:
 if family not in cache:
  side,sp=read(R/f'pilot-inputs/placement-pilot-{family}.json');p,pp=read(F/f'native-local/placement-decisions-v1/jobs/placement-pilot-{family}-proposal/reply.json');c,cp=read(F/f'native-local/placement-decisions-v1/jobs/placement-pilot-{family}-challenge/reply.json');view,vp=read(R/f'pilot-inputs/placement-pilot-{family}.view.json');cache[family]=(side,p,c,view,{'sidecar':sp,'view':vp,'proposal':pp,'challenge':cp})
 side,p,c,view,pins=cache[family];u=next(x for x in side['units']if x['ref']==ref);v=next(x for x in view['units']if x['ref']==ref);pr=next(x for x in p['placements']if x['unitRef']==ref);cr=next(x for x in c['placements']if x['unitRef']==ref);refs={h['scopeRef']for row in [pr,cr]for h in row['homes']};definitions={s['ref']:scoped(s['destination'])for s in side['scopes']if s['ref']in refs};definitions.update({s['id']:s for s in p['newScopes']if s['id']in refs});cases.append({'case':family+'-'+ref,'class':kind,'unitId':u['unitId'],'paperId':u['paperId'],'description':u['description'],'descriptionSha256':u['descriptionSha256'],'oldContexts':v['priorContexts'],'fullTargetDefinitions':definitions,'proposalJudgment':pr,'challengeJudgment':cr,'challengePlacementReview':next((x for x in c['priorPlacementReviews']if x.get('unitRef',x.get('ref'))==ref),None),'challengeNewScopeReviews':[x for x in c['priorScopeReviews']if x['ref']in refs],'pins':pins})
 if kind!='new_scope':continue
 n=definitions[next(iter(refs))];query=tok(u['description']+' '+n['question']);exact=[r for r in a['sourceContributions']if r['unitId']==u['unitId']];eid={r['destinationId']for r in exact};rank=sorted(ds,key=lambda id:(-sum(math.log((len(ds)+1)/(df[w]+1))for w in query&docs[id])/math.sqrt(len(docs[id])),id));ids=list(sorted(eid))+[id for id in rank[:6]if id not in eid]
 # Include the explicit broad family control without asserting equivalence.
 broad='q025-candidate-region:46fc37476acf84e240866e4b'
 if broad not in ids:ids.append(broad)
 lookups.append({'case':family+'-'+ref,'unitId':u['unitId'],'proposedDefinition':n,'inventoryCount':len(ds),'exactSourceRoles':[{'destinationId':x['destinationId'],'role':x['role'],'decisionId':x['decisionId'],'qualification':x.get('qualification'),'basis':x['basis']}for x in exact],'nearestDefinitions':[{'nominationBasis':'exact_same_source'if id in eid else 'broad_family_control'if id==broad else 'idf_weighted_definition_token_overlap','destination':scoped(ds[id])}for id in ids],'noExactSpecializedTermInAdmittedDefinitions':{term:not any(term.lower()in json.dumps(d,ensure_ascii=False).lower()for d in docs.values())for term in []}})
notes={
 'absent-u0':'The exact-source existing role is boundary to discharge kinematics, not a whole-scale home. Global force/charge cards discuss inequalities, spectra and extremality; the admitted charged-object family is a plausible broad access route, but none of the inspected fine definitions states the M_W=M_P/e and N(W)=e^-2 scale-construction target. A new fine question is defensible; do not claim a new physics result or identify area with species number.',
 'absent-u3':'The exact-source existing roles are method/boundary to spectrum and emission questions. No admitted definition contains Krylov. Global entropy/diagnostic cards concern macroscopic entropy calculations or physical relaxation, not freezing/restoration of charged-state Krylov spreading. The new diagnostic question is distinct while remaining related to discharge; the proposed diagnostic is not established as a rate.',
 'absent-u5':'Global lookup reveals an important broader alternative absent from the pilot: 205a007c (Discharge, perturbative dynamics and censorship) covers absorption, dynamical horizon preservation and conditional discharge. It does not explicitly articulate the SDC-tower activation plus relaxed thermodynamic-WGC comparison. The existing b94e5d08 tower card covers that other part. Root can choose the broad 205a007c home if its whole-target interpretation is accepted, or retain the new, more specific composite GMGHS question. Do not claim global absence; do not reconstruct either truncated charged-tower annotation or equate third-order protection with tower discharge.'}
for x in lookups:x['scientificAssessment']=notes[x['case']]
report={'schemaVersion':'q025-placement-pilot-scientific-review/1','status':'pending_coordinator_admission','inputs':{'mechanicalIntake':ip,'currentAdmittedAggregate':ap},'coverage':{'allPilotUnits':87,'unchangedExistingScopePlacements':82,'challengerRevisions':2,'unchangedNewScopeProposals':3,'compoundUnions':0,'unresolvedPlacementRows':0},'cases':cases,'globalNewScopeLookup':lookups,'readingLimit':'Exact complete source descriptions, complete current scopes and both old/new judgments were read. No new primary-page reading. Lexical/source-overlap nominations do not establish equality or global uniqueness. Historical annotations and scientific uncertainties remain separate from allocation admission.'};write(B/'intake.json',report)
lines=['# Placement pilot: nine exact cases','',report['readingLimit'],'','82 unchanged existing-scope placements; two challenger revisions; three unchanged proposed scopes. All 87 retain whole source questions. No union or unresolved row was returned.','']
for x in cases:
 lines+=['## '+x['case']+' — '+x['paperId'],'',x['description'],'']
 for ref,d in x['fullTargetDefinitions'].items():lines+=['**'+ref+' — '+d['title']+'**',d['question'],d['summary'],'Scope: '+json.dumps(d['scope'],ensure_ascii=False),'Reading: '+json.dumps(d.get('readingCoverage'),ensure_ascii=False),'']
 for ctx in x['oldContexts']:lines+=['Old '+ctx['reviewRef']+' proposal: '+json.dumps(ctx['proposal'],ensure_ascii=False),'Old '+ctx['reviewRef']+' challenge: '+json.dumps(ctx['challenge'],ensure_ascii=False),'']
 for label,key in [('Proposal','proposalJudgment'),('Challenge','challengeJudgment')]:
  row=x[key];lines+=[label+' homes: '+json.dumps(row['homes'],ensure_ascii=False),label+' coverage: '+row['coverageReason'],label+' reason: '+row['reason'],'']
 if x['case']in notes:lines+=['Global lookup: '+notes[x['case']],'']
(B/'REVIEW.md').write_text('\n'.join(lines)+'\n');write(B/'manifest.json',{'script':pin(Path(__file__)),'intake':read(B/'intake.json')[1],'readable':pin(B/'REVIEW.md'),'inputs':report['inputs'],'status':report['status']});print(json.dumps(read(B/'manifest.json')[1],indent=2))
