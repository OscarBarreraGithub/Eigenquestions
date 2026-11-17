#!/usr/bin/env python3
"""Existing full scientific graph attachments and additional facet signal experiment."""
import argparse, gzip, json, time
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from scipy import sparse
from sklearn.neighbors import NearestNeighbors
from run_round1 import compact_units, normalize, digest, dump, sha, split_leiden, export_candidate, hard_matrix
from run_round2 import partition_agreement

EXPECTED={'paper-facet-index.jsonl.gz':'c6a1a84cb77352a3d7d8bf4c59f272c05ca280bba62f8a0b43bcd2fc09b0d889','paper-facet-vectors.npy':'7dc730bd7cd761ec5aa3bcd83e6f89e7ff58af3ce391791c97c68f584115b9b9','nodes.jsonl.gz':'398ea5ea662c30c635302aef3b58e94eea11eda6efa5223533bacc992f23fc11','edges.jsonl.gz':'cabee8f05de78edac20203cc95eea38945c20b7eb2d0eb537bcfdfda9500cde8'}


def hierarchy_preserve(W,units,seed):
 mass=np.array([u['mass'] for u in units]);nodes=[];leaves=[];labels=np.zeros(len(units),int)
 def visit(rows,parent,depth):
  identity='region:'+digest(sorted(units[i]['unit_id'] for i in rows))[:20]
  node={'id':identity,'parentId':parent,'depth':depth,'children':[],'rows':rows.tolist(),'mass':float(mass[rows].sum())};nodes.append(node)
  if depth<6 and len(rows)>=60 and mass[rows].sum()>=80:
   sub=W[rows][:,rows];ll=split_leiden(sub,seed+depth,.65 if depth==0 else .8);groups=[rows[ll==j] for j in sorted(set(ll))]
   if 2<=len(groups)<=30:
    node['stopReason']=None
    for g in groups:node['children'].append(visit(g,identity,depth+1))
    return identity
  node['stopReason']='low_support_candidate_preserved' if mass[rows].sum()<12 or len(rows)<12 else 'local_size_or_unsplit'
  labels[rows]=len(leaves);leaves.append(identity);return identity
 visit(np.arange(len(units)),None,0)
 H=sparse.csr_matrix((np.ones(len(units)),(np.arange(len(units)),labels)),shape=(len(units),len(leaves)))
 return H,leaves,nodes


def context_graph(units,indices,vectors,role):
 selected=[x for x in indices if x['facet']==role];paperrow={x['paper_id']:i for i,x in enumerate(selected)}
 X=np.array(vectors[[x['row'] for x in selected]],copy=True);X/=np.maximum(np.linalg.norm(X,axis=1,keepdims=True),1e-30)
 dist,nn=NearestNeighbors(n_neighbors=25,metric='cosine',algorithm='brute',n_jobs=4).fit(X).kneighbors(X)
 rr=[];cc=[];vv=[];sigma=np.sqrt(np.maximum(2*dist[:,-1],1e-12))
 for i in range(len(X)):
  for j,d in zip(nn[i],dist[i]):
   if i==j or 1-d<.2:continue
   rr.append(i);cc.append(j);vv.append(float(np.exp(-2*max(d,0)/(sigma[i]*sigma[j]))))
 P=sparse.csr_matrix((vv,(rr,cc)),shape=(len(X),len(X)));P=P.maximum(P.T)
 ur=[];uc=[];uv=[];attachments=[]
 for i,u in enumerate(units):
  j=paperrow.get(u['paper_id'])
  if j is not None:
   ur.append(i);uc.append(j);uv.append(u['mass']);src=selected[j]
   attachments.append({'unitId':u['unit_id'],'contextFacet':role,'paperFacetVectorRow':src['row'],'inputFacetIds':src['input_facet_ids'],'attachmentScope':'same_paper_facet_aggregate_only','logicalApplicabilityToQuestionEstablished':False})
 B=sparse.csr_matrix((uv,(ur,uc)),shape=(len(units),len(selected)));W=(B@P@B.T).tocsr()
 return W,attachments,{'facet':role,'paperCount':len(selected),'questionUnitsWithContext':len(ur),'paperGraphEdges':P.nnz//2,'questionGraphEdges':W.nnz//2,'sourceFacetCount':sum(x['input_facet_count'] for x in selected)}


def science_attachments(downloads,units,out):
 anchors=set(x for u in units for x in u['node_ids']);records=set(x for u in units for x in u['source_record_ids']);node_info={};byrecord=defaultdict(list);types=Counter()
 with gzip.open(downloads/'nodes.jsonl.gz','rt') as f:
  for line in f:
   x=json.loads(line);types[x['type']]+=1;rid=x.get('provenance',{}).get('record_id')
   if rid in records or x['id'] in anchors:
    node_info[x['id']]={k:x.get(k) for k in ['id','type','paper_id','text','label','evidence_ids','evidence_scope','provenance','source_sha256','layer','certainty']}
    if rid:byrecord[rid].append(x['id'])
 edges=[];byendpoint=defaultdict(list);statuses=Counter();edge_types=Counter()
 with gzip.open(downloads/'edges.jsonl.gz','rt') as f:
  for line in f:
   e=json.loads(line);statuses[e['semantic_status']]+=1;edge_types[e['type']]+=1
   if e['type'] in ['contains','literal_identifier_mention'] or e['semantic_status']=='unvalidated_mention':continue
   if e['source'] in node_info and e['target'] in node_info:
    j=len(edges);edges.append(e);byendpoint[e['source']].append(j);byendpoint[e['target']].append(j)
 property_types={'has_assumption','has_convention','has_control_regime','has_limitation','has_derivation','has_symmetry'}
 used_edges=set();used_nodes=set();counts=Counter();attachments=[]
 for u in units:
  direct=set(j for node in u['node_ids'] for j in byendpoint.get(node,[]));path_edges=set(direct)
  first_neighbors=set(z for j in direct for z in [edges[j]['source'],edges[j]['target']]);paths=[]
  for j in direct:
   e=edges[j]
   for endpoint in [e['source'],e['target']]:
    for k in byendpoint.get(endpoint,[]):
     if edges[k]['type'] in property_types and edges[k]['source']==endpoint:
      paths.append([e['id'],edges[k]['id']]);path_edges.add(k)
  context=set(x for r in u['source_record_ids'] for x in byrecord.get(r,[]));context-=set(u['node_ids'])
  used_edges.update(path_edges);used_nodes.update(context);used_nodes.update(u['node_ids'])
  for j in path_edges:used_nodes.update([edges[j]['source'],edges[j]['target']])
  counts['units']+=1;counts['unitsWithDirectLocalEdges']+=bool(direct);counts['unitsWithPropertyPaths']+=bool(paths);counts['unitsWithSameRecordContext']+=bool(context)
  attachments.append({'unitId':u['unit_id'],'sourceNodeIds':u['node_ids'],'sourceRecordIds':u['source_record_ids'],'directEdgeIds':[edges[j]['id'] for j in sorted(direct)],'propertyEdgePaths':paths,'sameExtractionContextNodeIds':sorted(context),'contextScope':'Objects from the same source extraction record; co-occurrence alone does not establish applicability, derivation, support or contradiction.','propertyScope':'Property paths qualify their actual source object; they do not automatically qualify every question in the paper.'})
 with gzip.open(out/'unit-science-attachments.jsonl.gz','wt') as f:
  for x in attachments:f.write(json.dumps(x,ensure_ascii=False)+'\n')
 with gzip.open(out/'source-objects.jsonl.gz','wt') as f:
  for nid in sorted(used_nodes):
   if nid in node_info:f.write(json.dumps(node_info[nid],ensure_ascii=False)+'\n')
 with gzip.open(out/'source-local-edges.jsonl.gz','wt') as f:
  for j in sorted(used_edges):f.write(json.dumps(edges[j],ensure_ascii=False)+'\n')
 summary={'allSourceNodeTypes':dict(types),'allEdgeSemanticStatuses':dict(statuses),'allEdgeTypes':dict(edge_types),'attachmentCounts':dict(counts),'attachedSourceObjects':len(used_nodes),'attachedLocalEdges':len(used_edges),'sourceRecordsUsed':len(records),'statusBoundary':'Source-local assertions and extraction inferences retain their status. These are not independently reviewed cross-paper relations. Unvalidated mentions excluded from scientific attachments.'};dump(out/'scientific-object-inventory.json',summary);return summary


def main():
 p=argparse.ArgumentParser();p.add_argument('--input-root',type=Path,required=True);p.add_argument('--downloads',type=Path,required=True);p.add_argument('--round1',type=Path,required=True);p.add_argument('--relations',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 start=time.time();progress=[]
 def mark(stage,**data):progress.append(dict(stage=stage,elapsed=time.time()-start,**data));dump(a.out/'progress.json',progress);print(stage,json.dumps(data),flush=True)
 files={}
 for name,expected in EXPECTED.items():
  actual=sha(a.downloads/name);assert actual==expected,(name,actual,expected);files[name]={'sha256':actual,'bytes':(a.downloads/name).stat().st_size}
 root=a.input_root;units=compact_units(root/'geometry-minilm-physical_question/units.jsonl');n=len(units);lookup={u['unit_id']:i for i,u in enumerate(units)};W=sparse.load_npz(root/'geometry-minilm-physical_question/affinity.npz').tocsr();V=np.load(root/'geometry-minilm-physical_question/vectors.npy')
 qwen=compact_units(root/'geometry-qwen-4b-raw-physical_question/units.jsonl');qi={u['unit_id']:i for i,u in enumerate(qwen)};order=[qi[u['unit_id']] for u in units];Wq=sparse.load_npz(root/'geometry-qwen-4b-raw-physical_question/affinity.npz').tocsr()[order][:,order]
 assert all(u['text_sha256']==qwen[j]['text_sha256'] for u,j in zip(units,order))
 ledger=json.loads(a.relations.read_text());relations=[dict(r,id='scientific:'+r['taskId'],leftPaperId=r['endpoints'][0]['paper_id'],rightPaperId=r['endpoints'][1]['paper_id']) for r in ledger['records'] if r['admittedScientificEdge']]
 (a.out/'source-rows.jsonl').write_bytes((a.round1/'source-rows.jsonl').read_bytes())
 dump(a.out/'input-manifest.json',{'scriptSha256':sha(__file__),'helperSha256':sha(Path(__file__).with_name('run_round1.py')),'round1InputManifestSha256':sha(a.round1/'input-manifest.json'),'additionalFiles':files,'scope':'Existing full scientific object graph and paper-facet vectors; no reencoding.'})
 mark('inputs_verified')
 inventory=science_attachments(a.downloads,units,a.out);mark('scientific_attachments',**inventory['attachmentCounts'])
 # Reuse the full Qwen hierarchy without imposing MiniLM parent boundaries.
 part=json.loads((root/'geometry-qwen-4b-raw-physical_question/partition.json').read_text());qids=[u['unit_id'] for u in part['units']];oldlabels={uid:lab for uid,lab in zip(qids,part['leaf_membership'])};H,ll=hard_matrix([oldlabels[u['unit_id']] for u in units]);nn=[{'id':x['id'],'parentId':x.get('parent_id'),'depth':x['depth'],'children':x['children'],'rows':[lookup[u] for u in x['unit_ids']],'mass':x['mass'],'stopReason':x.get('diagnostics',{}).get('stop_reason')} for x in part['nodes']]
 summaries={};summaries['inherited_global_qwen']=export_candidate(a.out,'inherited_global_qwen',W,H,ll,nn,units,V,relations,{'family':'independent inherited global Qwen hierarchy'});mark('global_qwen',leaves=H.shape[1])
 # Diagnose why Qwen isolates occurred inside inherited MiniLM parent sets.
 old=json.loads((root/'geometry-minilm-physical_question/partition.json').read_text());isolation=[]
 for node in old['nodes']:
  if node['children'] or len(node['unit_ids'])<=900:continue
  rows=np.array([lookup[u] for u in node['unit_ids']]);degree=np.asarray(Wq[rows][:,rows].sum(1)).ravel();inside=set(rows)
  for i in rows[degree<=0]:
   js=Wq.indices[Wq.indptr[i]:Wq.indptr[i+1]];ws=Wq.data[Wq.indptr[i]:Wq.indptr[i+1]];top=np.argsort(ws)[-8:][::-1]
   isolation.append({'unitId':units[i]['unit_id'],'paperId':units[i]['paper_id'],'text':units[i]['text'],'oldParentId':node['id'],'globalQwenLeafId':oldlabels[units[i]['unit_id']],'externalNeighbors':[{'unitId':units[js[k]]['unit_id'],'paperId':units[js[k]]['paper_id'],'text':units[js[k]]['text'],'weight':float(ws[k]),'outsideInheritedParent':int(js[k]) not in inside} for k in top]})
 dump(a.out/'qwen-cross-boundary-isolates.json',isolation);mark('isolation_diagnosed',units=len(isolation))
 indices=[json.loads(line) for line in gzip.open(a.downloads/'paper-facet-index.jsonl.gz','rt')];vectors=np.load(a.downloads/'paper-facet-vectors.npy',mmap_mode='r');assert len(indices)==vectors.shape[0] and all(x['row']==i for i,x in enumerate(indices))
 graphs={};stats={};attachments=[]
 for role in ['result','applicability','mathematical_structure']:
  G,aa,ss=context_graph(units,indices,vectors,role);graphs[role]=normalize(G);stats[role]=ss;attachments.extend(aa);mark('facet_graph',**ss)
 with gzip.open(a.out/'unit-facet-contexts.jsonl.gz','wt') as f:
  for x in attachments:f.write(json.dumps(x)+'\n')
 dump(a.out/'additional-facet-coverage.json',stats)
 # Compare the same less-blocking hierarchy policy with and without added facets.
 mus=compact_units(root/'geometry-minilm-method/units.jsonl');Wm=sparse.load_npz(root/'geometry-minilm-method/affinity.npz');bp=defaultdict(list)
 for j,u in enumerate(mus):bp[u['paper_id']].append(j)
 rr=[];cc=[];vv=[]
 for i,u in enumerate(units):
  js=bp[u['paper_id']];denom=sum(mus[j]['mass'] for j in js)
  for j in js:rr.append(i);cc.append(j);vv.append(mus[j]['mass']/denom)
 B=sparse.csr_matrix((vv,(rr,cc)),shape=(n,len(mus)));M=(B@normalize(Wm)@B.T).tocsr();M.setdiag(0);M.eliminate_zeros()
 base=.5*normalize(W)+.3*normalize(Wq)+.2*normalize(M)
 richer=.7*base+.1*graphs['result']+.1*graphs['applicability']+.1*graphs['mathematical_structure']
 trees={}
 for cid,G in [('multiview_preserve_candidates',base),('extra_facet_context',richer)]:
  H,ll,nn=hierarchy_preserve(G,units,20261117);H2,l2,n2=hierarchy_preserve(G,units,20261118);trees[cid]=nn
  extra={'family':'global multiview with low-support candidates preserved','seedAgreement':partition_agreement(nn,n2,n),'extraFacetWeights':{'existingQuestionMethodMultiview':.7,'result':.1,'applicability':.1,'mathematical_structure':.1} if cid=='extra_facet_context' else None,'sourceContextScope':'Paper-facet co-context is retrieval geometry, not established question-specific logical applicability. Exact graph attachments are separate.'}
  summaries[cid]=export_candidate(a.out,cid,W,H,ll,nn,units,V,relations,extra);mark(cid,leaves=H.shape[1],seedLeafARI=extra['seedAgreement']['leafARI'])
 dump(a.out/'extra-facet-agreement.json',partition_agreement(trees['multiview_preserve_candidates'],trees['extra_facet_context'],n))
 dump(a.out/'comparison.json',summaries);mark('complete',elapsed=time.time()-start)

if __name__=='__main__':main()
