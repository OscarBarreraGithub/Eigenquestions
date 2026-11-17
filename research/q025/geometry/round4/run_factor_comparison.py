#!/usr/bin/env python3
"""Same-cohort geometry versus typed source-span navigation, without merging Q IDs."""
import argparse, hashlib, json
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()

def dump(path,x):Path(path).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')

def common(a,b,role,specific=None):
 aa={x['value'] for x in a['factors'] if x['role']==role and (specific is None or x['specific']==specific)}
 bb={x['value'] for x in b['factors'] if x['role']==role and (specific is None or x['specific']==specific)}
 return sorted(aa&bb)

def classify(a,b):
 systems=common(a,b,'system',True);frameworks=common(a,b,'framework',True);targets=common(a,b,'target',True);broadtargets=common(a,b,'target');broadframework=common(a,b,'framework')
 ar={x['value'] for x in a['factors'] if x['role']=='regime'};br={x['value'] for x in b['factors'] if x['role']=='regime'}
 af={x['value'] for x in a['factors'] if x['role']=='framework'};bf={x['value'] for x in b['factors'] if x['role']=='framework'}
 contrast=('no_inflation' in ar and 'inflation' in bf) or ('no_inflation' in br and 'inflation' in af)
 types=[]
 if systems:types.append('shared_system')
 if frameworks:types.append('shared_specific_framework')
 if targets:types.append('shared_specific_target')
 elif broadtargets:types.append('shared_target')
 if contrast and broadtargets:types.append('target_bridge_across_regimes')
 if broadframework and not frameworks:types.append('shared_broad_framework')
 if not types:types.append('retrieval_only')
 tier=0 if systems else 1 if frameworks else 2 if targets else 3 if broadtargets else 4 if broadframework else 5
 return {'types':types,'priorityTier':tier,'sharedSystems':systems,'sharedSpecificFrameworks':frameworks,'sharedTargets':broadtargets,'explicitRegimeContrast':bool(contrast),'questionEquivalenceEstablished':False,'scientificImplicationEstablished':False}

def source_relation(record):
 left,right=record['nodeIds'];direction=record['direction'];source,target=(right,left) if direction=='right_to_left' else (left,right)
 return {'id':'scientific:'+record['taskId'],'source':source,'target':target,'kind':'reviewed_scoped_source_relation','type':record['relationCategory'],'originalDirection':direction,'exactAssertion':record['exactAssertion'],'applicability':record['applicability'],'conventionDictionary':record['conventionDictionary'],'readerNote':record.get('readerNote'),'provenance':{'receiptPath':record['receiptPath'],'receiptSha256':record['receiptSha256']},'questionEquivalenceEstablished':False}

def main():
 p=argparse.ArgumentParser();p.add_argument('--inputs',type=Path,required=True);p.add_argument('--geometry-inputs',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 cohort=json.loads((a.inputs/'cohort-v1.json').read_text());factorfile=json.loads((a.inputs/'factors-v1.json').read_text());rows=cohort['units'];factors=factorfile['factors'];n=len(rows)
 assert len(factors)==n and all(x['unitId']==y['unitId'] for x,y in zip(rows,factors));assert factorfile['cohortSha256']==sha(a.inputs/'cohort-v1.json')
 freeze=json.loads((a.inputs/'freeze-v1.json').read_text())
 for name,digest in freeze['files'].items():assert sha(a.inputs/name)==digest
 graphs={};sourcefiles={}
 for encoder in ['minilm','qwen-4b-raw']:
  root=a.geometry_inputs/f'geometry-{encoder}-physical_question';ids=[json.loads(line)['unit_id'] for line in (root/'units.jsonl').open()];lookup={u:i for i,u in enumerate(ids)};indices=[lookup[u['unitId']] for u in rows];V=np.load(root/'vectors.npy',mmap_mode='r');X=np.array(V[indices]);X/=np.maximum(np.linalg.norm(X,axis=1,keepdims=True),1e-30);S=X@X.T;np.fill_diagonal(S,-np.inf);graphs[encoder]=S
  sourcefiles[encoder]={'unitIdOrderSha256':hashlib.sha256('\n'.join(ids).encode()).hexdigest(),'unitsFileSha256':sha(root/'units.jsonl'),'vectorsSha256':sha(root/'vectors.npy'),'dimensions':V.shape[1],'selectedSourceRows':indices}
 pairs={};types=Counter();question_edges=[]
 for i in range(n):
  for j in range(i+1,n):
   c=classify(factors[i],factors[j]);pairs[(i,j)]=c;types.update(c['types'])
   question_edges.append({'source':rows[i]['unitId'],'target':rows[j]['unitId'],'kind':'scope_or_retrieval_proposal','scope':c,'cosine':{e:float(S[i,j]) for e,S in graphs.items()}})
 factor_nodes={};factor_edges=[]
 for u,ff in zip(rows,factors):
  for f in ff['factors']:
   fid='scope:'+f['role']+':'+f['value'];factor_nodes[fid]={'id':fid,'kind':'scope_factor','role':f['role'],'label':f['value'],'status':'source_span_nomination'};factor_edges.append({'source':u['unitId'],'target':fid,'kind':'scope_annotation','spans':f['spans'],'scientificImplication':False})
 neighbors={};metric={}
 for encoder,S in graphs.items():
  nr=[];retrieval_before=0;retrieval_after=0;new_counts=[]
  for i in range(n):
   raw=[int(j) for j in np.argsort(S[i])[::-1] if j!=i][:5]
   ranked=sorted([j for j in range(n) if j!=i],key=lambda j:(pairs[tuple(sorted((i,j)))]['priorityTier'],-float(S[i,j]),rows[j]['unitId']))[:5]
   retrieval_before+=sum(pairs[tuple(sorted((i,j)))]['types']==['retrieval_only'] for j in raw);retrieval_after+=sum(pairs[tuple(sorted((i,j)))]['types']==['retrieval_only'] for j in ranked)
   new_counts.append(len(set(raw)&set(ranked)))
   nr.append({'unitId':rows[i]['unitId'],'rawTop5':[rows[j]['unitId'] for j in raw],'typedTop5':[{'unitId':rows[j]['unitId'],'cosine':float(S[i,j]),'scope':pairs[tuple(sorted((i,j)))]} for j in ranked],'allRawNeighborsRemainAvailable':True})
  neighbors[encoder]=nr;metric[encoder]={'rawTop5NoExtractedScopeFraction':retrieval_before/(n*5),'typedTop5NoExtractedScopeFraction':retrieval_after/(n*5),'meanTop5Overlap':float(np.mean(new_counts)),'interpretation':'Selection diagnostics only. No semantic accuracy or generalization claim; missing factors are not evidence of unrelated physics.'}
 bridge=json.loads((a.inputs/'method-bridge-controls.json').read_text());ledger=json.loads((a.inputs/'current-relation-ledger.json').read_text());control=json.loads((a.inputs/'controls.json').read_text());relations=[];checks=[]
 for b in bridge['records']:
  r=b['sourceRelation'];assert r['status']=='accepted_relation' and not r['promotionWithheld'];edge=source_relation(r);relations.append(edge)
  checks.append({'id':b['id'],'systems':b['systems'],'scopedMethodEdgeRetained':True,'sourceDirection':edge['source'],'targetDirection':edge['target'],'bothEndpointsInspectable':True,'reverseBrowsingDoesNotReverseAssertion':True,'sameQuestionIdentityInferred':False,'basis':'Prior admitted source-scoped method relation, development control.'})
 predictions=[]
 for c in control['records']:
  wanted=set(c['sourceObjectIds']);matches=[r for r in ledger['records'] if set(r['nodeIds'])==wanted];admitted=[r for r in matches if r['admittedScientificEdge']]
  output={'id':c['id'],'sourceObjectIds':c['sourceObjectIds'],'prompt':c['prompt'],'genericExactEndpointLookup':True,'questionIdentity':'Not established by a source-method comparison; keep scoped question identity separate.','activeRelations':[source_relation(r) for r in admitted],'nonpositiveAssessments':[{'taskId':r['taskId'],'status':r['status'],'promotionWithheld':r['promotionWithheld'],'readerNote':r.get('readerNote')} for r in matches if not r['admittedScientificEdge']],'unmatched':not matches,'reservedExpectedLabelsRead':False}
  predictions.append(output)
 examples=[]
 for pa,pb in [('astro-ph/0703099','2311.05318'),('2205.13931','2311.05318'),('0803.0859','1901.08603'),('2105.08045','1904.10298')]:
  for i,u in enumerate(rows):
   if u['paperId']!=pa:continue
   for j,v in enumerate(rows):
    if v['paperId']!=pb:continue
    examples.append({'source':u['unitId'],'target':v['unitId'],'paperIds':[pa,pb],'typedProposal':pairs[tuple(sorted((i,j)))],'cosine':{e:float(S[i,j]) for e,S in graphs.items()},'rawTop5Ranks':{e:int(np.where(np.argsort(S[i])[::-1]==j)[0][0])+1 for e,S in graphs.items()},'developmentCase':True})
 dump(a.out/'factor-graph.json',{'questionNodes':[{'id':u['unitId'],'text':u['text'],'paperId':u['paperId']} for u in rows],'factorNodes':list(factor_nodes.values()),'factorEdges':factor_edges,'questionProposalEdges':question_edges,'reviewedSourceMethodEdges':relations,'edgeMeaning':'Source-span factors organize navigation; geometric edges and reviewed source-method edges retain distinct semantics. No canonical merges.'})
 dump(a.out/'neighbors.json',neighbors);dump(a.out/'method-control-checks.json',checks);dump(a.out/'post-rule-predictions.json',predictions);dump(a.out/'development-cases.json',examples)
 report={'unitCount':n,'factorNodeCount':len(factor_nodes),'factorEdges':len(factor_edges),'proposalPairTypes':dict(types),'roleCoverage':{role:sum(any(f['role']==role for f in row['factors']) for row in factors) for role in ['system','framework','target','regime','assumption_mentioned']},'nearestNeighborDiagnostics':metric,'methodControlsRetained':len(checks),'postRuleControls':len(predictions),'scientificAccuracyMeasured':False,'evaluationLimits':['Known mixed regions are development examples.','Post-rule controls reuse existing admitted receipts; this is an endpoint/type/scope audit, not blind-source generalization.','A shared scope factor does not imply question equivalence.','All raw geometric neighbors and exact source-method routes remain accessible.','No whole-paper assumption is attached as a question premise.']}
 dump(a.out/'diagnostics.json',report);dump(a.out/'input-manifest.json',{'scriptSha256':sha(__file__),'inputFiles':{p.name:sha(p) for p in a.inputs.glob('*.json')},'frozenBeforePostRuleControls':freeze,'geometryInputs':sourcefiles,'encodingRerun':False});print(json.dumps(report,indent=2),flush=True)

if __name__=='__main__':main()
