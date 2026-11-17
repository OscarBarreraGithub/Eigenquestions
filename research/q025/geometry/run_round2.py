#!/usr/bin/env python3
"""Target historical giant leaves with multiway spectral geometry; paired relation audit."""
import argparse, copy, json, time
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import eigsh
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from run_round1 import compact_units, normalize, dropout, digest, dump, sha, hierarchy, export_candidate


def level_labels(nodes,n,level,subset=None):
    labels=np.zeros(n,dtype=int)
    for j,node in enumerate(sorted(nodes,key=lambda x:x['depth'])):
        if node['depth']<=level:labels[node['rows']]=j
    return labels if subset is None else labels[subset]


def partition_agreement(nodes1,nodes2,n,subset=None):
    result={'levelARI':{str(k):float(adjusted_rand_score(level_labels(nodes1,n,k,subset),level_labels(nodes2,n,k,subset))) for k in range(1,9)}}
    a=level_labels(nodes1,n,100,subset);b=level_labels(nodes2,n,100,subset)
    counts=defaultdict(int);sa=defaultdict(int);sb=defaultdict(int)
    for x,y in zip(a,b):counts[(int(x),int(y))]+=1;sa[int(x)]+=1;sb[int(y)]+=1
    best=[];matched=0
    for x,total in sa.items():
        options=[(num/(total+sb[y]-num),num) for (xx,y),num in counts.items() if xx==x]
        j,core=max(options);best.append((j,total));matched+=core
    result.update(leafARI=float(adjusted_rand_score(a,b)),meanBestClusterJaccard=float(np.mean([x[0] for x in best])),unitWeightedBestClusterJaccard=float(sum(j*s for j,s in best)/len(a)),bestMatchCoreCoverage=matched/len(a))
    return result


def spectral_refine(W,units,base_nodes,target_rows,seed=20261117):
    nodes=copy.deepcopy(base_nodes);mass=np.array([u['mass'] for u in units]);targets={tuple(sorted(rows)) for rows in target_rows};records=[]
    def split(node,localdepth):
        rows=np.array(node['rows']);sub=W[rows][:,rows].tocsr();degrees=np.asarray(sub.sum(1)).ravel()
        if localdepth>=4 or len(rows)<60 or mass[rows].sum()<70:
            node['stopReason']='local_size_or_depth';return
        if np.any(degrees<=0):
            node['stopReason']='isolated_units_preserved';records.append({'nodeId':node['id'],'isolated':int(np.sum(degrees<=0))});return
        S=normalize(sub);kmax=min(13,len(rows)-2)
        v0=np.random.default_rng(seed).normal(size=len(rows))
        vals,vecs=eigsh(S,k=kmax,which='LA',tol=1e-7,maxiter=10000,v0=v0)
        order=np.argsort(vals)[::-1];vals=vals[order];vecs=vecs[:,order]
        choices=[(float(vals[k-1]-vals[k]),k) for k in range(2,min(12,kmax-1)+1)]
        gap,k=max(choices)
        X=vecs[:,:k];X/=np.maximum(np.linalg.norm(X,axis=1,keepdims=True),1e-30)
        labels=KMeans(n_clusters=k,n_init=20,random_state=seed).fit_predict(X)
        repeat=KMeans(n_clusters=k,n_init=20,random_state=seed+1).fit_predict(X)
        groups=[rows[labels==j] for j in range(k)];groups=[g for g in groups if len(g)]
        node['stopReason']=None;node['children']=[]
        record={'nodeId':node['id'],'units':len(rows),'mass':float(mass[rows].sum()),'chosenChildren':k,'eigenvalues':vals.tolist(),'eigengaps':[{'k':kk,'gap':gg} for gg,kk in sorted(choices,reverse=True)],'kmeansSeedARI':float(adjusted_rand_score(labels,repeat)),'childSizes':[len(g) for g in groups],'childMasses':[float(mass[g].sum()) for g in groups]};records.append(record)
        for g in groups:
            identity='spectral:'+digest(sorted(units[i]['unit_id'] for i in g))[:20]
            low=mass[g].sum()<12 or len(g)<12
            child={'id':identity,'parentId':node['id'],'children':[],'depth':node['depth']+1,'rows':g.tolist(),'mass':float(mass[g].sum()),'stopReason':'low_support_candidate_preserved' if low else None,'supportStatus':'limited' if low else 'candidate'}
            node['children'].append(identity);nodes.append(child)
            if not low:split(child,localdepth+1)
    for node in list(nodes):
        if tuple(sorted(node['rows'])) in targets:split(node,0)
    leaves=[n['id'] for n in nodes if not n['children']];labels=np.zeros(len(units),dtype=int)
    for j,node in enumerate(n for n in nodes if not n['children']):labels[node['rows']]=j
    H=sparse.csr_matrix((np.ones(len(units)),(np.arange(len(units)),labels)),shape=(len(units),len(leaves)))
    return H,leaves,nodes,records


def typed_constraints(relations,units,H,cid):
    rows=defaultdict(list);nodes=defaultdict(list)
    for i,u in enumerate(units):
        rows[u['paper_id']].append(i)
        for node in u['node_ids']:nodes[node].append(i)
    policy={'same_result_under_dictionary':'Check stated dictionary and source claim identity; do not merge question destinations automatically.','specializes':'Check directed regime/assumption restriction; keep as scoped scientific edge, not automatic topic containment.','analogy_only':'Keep analogy as navigation with explicit disanalogy and no inferred implication/equivalence.','uses_method':'Expose a method-transfer route; retain different physical targets.','apparent_tension':'Keep contrasting assumptions/source evidence visible; do not attract or repel solely by tension label.','supports_under_assumptions':'Keep premise-scoped directed support and verify premises before promoting a navigation explanation.'}
    out=[]
    for r in relations:
        exact=[nodes.get(e['id'],[]) for e in r['endpoints']];paper=[rows.get(e['paper_id'],[]) for e in r['endpoints']]
        out.append({'id':r['id'],'candidateId':cid,'category':r['relationCategory'],'direction':r['direction'],'reviewConstraint':policy[r['relationCategory']],'nodeIds':r['nodeIds'],'exactQuestionEndpointRows':exact,'paperContextQuestionRows':paper,'endpointMappingStatus':'exact_question_nodes' if all(exact) else 'source_claim_to_question_mapping_not_established','receiptSha256':r['receiptSha256'],'scientificEdgePreserved':True,'questionEquivalenceInferred':False})
    return out


def main():
    p=argparse.ArgumentParser();p.add_argument('--input-root',type=Path,required=True);p.add_argument('--round1',type=Path,required=True);p.add_argument('--relations',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    start=time.time();progress=[]
    def mark(stage,**details):progress.append(dict(stage=stage,elapsed=time.time()-start,**details));dump(a.out/'progress.json',progress);print(stage,json.dumps(details),flush=True)
    root=a.input_root;units=compact_units(root/'geometry-minilm-physical_question/units.jsonl');n=len(units);lookup={u['unit_id']:i for i,u in enumerate(units)}
    W=sparse.load_npz(root/'geometry-minilm-physical_question/affinity.npz').tocsr();V=np.load(root/'geometry-minilm-physical_question/vectors.npy')
    qwen=compact_units(root/'geometry-qwen-4b-raw-physical_question/units.jsonl');qi={u['unit_id']:i for i,u in enumerate(qwen)};order=[qi[u['unit_id']] for u in units];Wq=sparse.load_npz(root/'geometry-qwen-4b-raw-physical_question/affinity.npz').tocsr()[order][:,order]
    assert all(u['text_sha256']==qwen[j]['text_sha256'] for u,j in zip(units,order))
    part=json.loads((root/'geometry-minilm-physical_question/partition.json').read_text());nodes=[{'id':x['id'],'parentId':x.get('parent_id'),'depth':x['depth'],'children':x['children'],'rows':[lookup[u] for u in x['unit_ids']],'mass':x['mass'],'stopReason':x.get('diagnostics',{}).get('stop_reason')} for x in part['nodes']]
    targets=[x['rows'] for x in nodes if not x['children'] and len(x['rows'])>900];giant=max(targets,key=len)
    ledger=json.loads(a.relations.read_text());relations=[dict(r,id='scientific:'+r['taskId'],leftPaperId=r['endpoints'][0]['paper_id'],rightPaperId=r['endpoints'][1]['paper_id']) for r in ledger['records'] if r['admittedScientificEdge']]
    assert all(r['status']=='accepted_relation' and not r['promotionWithheld'] for r in relations)
    source=a.round1/'source-rows.jsonl';(a.out/'source-rows.jsonl').write_bytes(source.read_bytes())
    dump(a.out/'input-manifest.json',{'round1InputManifestSha256':sha(a.round1/'input-manifest.json'),'sourceRowsSha256':sha(source),'scriptSha256':sha(__file__),'helperSha256':sha(Path(__file__).with_name('run_round1.py')),'relationLedgerSha256':sha(a.relations),'targetRegionSizes':[len(x) for x in targets],'sourceIdOrderSha256':digest([u['unit_id'] for u in units])})
    mark('inputs_ready',targetSizes=[len(x) for x in targets])
    Sm=normalize(W);Sq=normalize(Wq);mutual=Sm.multiply(Sq);mutual.data=np.sqrt(mutual.data);consensus=.5*Sm+.5*Sq+mutual
    constructions={'local_spectral_minilm':W,'local_spectral_qwen':Wq,'local_spectral_consensus':consensus};results={};saved={}
    for cid,G in constructions.items():
        H,leaves,nn,records=spectral_refine(G,units,nodes,targets)
        HD,ld,nd,rd=spectral_refine(dropout(G),units,nodes,targets)
        meta={'family':'targeted multiway spectral refinement','targetOriginalLeafSizes':[len(x) for x in targets],'dropoutAgreementGlobal':partition_agreement(nn,nd,n),'dropoutAgreementGiant':partition_agreement(nn,nd,n,giant),'splitPolicy':'Eigengap chooses 2–12 children. Keep low-support children explicit/source-visible rather than reject all siblings. No scientific acceptance inferred.','spectralSplits':records}
        results[cid]=export_candidate(a.out,cid,W,H,leaves,nn,units,V,relations,meta);saved[cid]=(H,leaves,nn)
        dump(a.out/cid/'typed-relation-review-constraints.json',typed_constraints(relations,units,H,cid))
        # Boundary halos are separate suggestions; they do not alter hard containment.
        P=sparse.diags(1/np.maximum(np.asarray(W.sum(1)).ravel(),1e-30))@W;F=(P@H).tocsr();primary=np.asarray(H.argmax(1)).ravel();halos=[]
        for i in range(n):
            for j,weight in zip(F.indices[F.indptr[i]:F.indptr[i+1]],F.data[F.indptr[i]:F.indptr[i+1]]):
                if j!=primary[i] and weight>=.2:halos.append({'unitId':units[i]['unit_id'],'regionId':cid+':'+leaves[j],'kind':'boundary_neighbor_share','weight':float(weight),'membership':False,'scientificRelation':False})
        dump(a.out/cid/'boundary-halos.json',halos);mark(cid,leaves=len(leaves),haloCount=len(halos),giantDropoutARI=meta['dropoutAgreementGiant']['leafARI'])
    comparisons={}
    for x,y in [('local_spectral_minilm','local_spectral_qwen'),('local_spectral_consensus','local_spectral_minilm'),('local_spectral_consensus','local_spectral_qwen')]:comparisons[x+'__'+y]={'global':partition_agreement(saved[x][2],saved[y][2],n),'giant':partition_agreement(saved[x][2],saved[y][2],n,giant)}
    dump(a.out/'spectral-cross-encoder-comparison.json',comparisons)
    # Paired repeated-seed causal audit of relation attraction against baseline variability.
    mus=compact_units(root/'geometry-minilm-method/units.jsonl');Wm=sparse.load_npz(root/'geometry-minilm-method/affinity.npz');bypaper=defaultdict(list)
    for j,u in enumerate(mus):bypaper[u['paper_id']].append(j)
    br=[];bc=[];bv=[];pr=defaultdict(list)
    for i,u in enumerate(units):
        pr[u['paper_id']].append(i);js=bypaper[u['paper_id']];denom=sum(mus[j]['mass'] for j in js)
        for j in js:br.append(i);bc.append(j);bv.append(mus[j]['mass']/denom)
    B=sparse.csr_matrix((bv,(br,bc)),shape=(n,len(mus)));M=(B@normalize(Wm)@B.T).tocsr();M.setdiag(0);M.eliminate_zeros();Q=.5*Sm+.3*Sq+.2*normalize(M)
    def relation_graph(selected):
        rr=[];rc=[];rv=[]
        for r in selected:
            aa=pr[r['leftPaperId']];bb=pr[r['rightPaperId']]
            for i in aa:
                for j in bb:
                    if i!=j:rr.extend([i,j]);rc.extend([j,i]);rv.extend([1/(len(aa)*len(bb))]*2)
        return sparse.csr_matrix((rv,(rr,rc)),shape=(n,n))
    R=relation_graph(relations);strong=[r for r in relations if r['relationCategory'] in ['same_result_under_dictionary','specializes']];Rstrong=relation_graph(strong)
    paired={};histories={};seeds=[20261117,20261118]
    for seed in seeds:
        histories[seed]={}
        for name,G in [('base',Q),('all_types_attraction',Q+.03*normalize(R)),('result_specialization_attraction',Q+.03*normalize(Rstrong))]:
            H,ll,nn,rr=hierarchy(G,units,seed);histories[seed][name]=nn
            dump(a.out/f'paired-{seed}-{name}-tree.json',nn);mark('paired_tree',seed=seed,variant=name,leaves=H.shape[1])
        paired[str(seed)]={name:partition_agreement(histories[seed]['base'],histories[seed][name],n) for name in ['all_types_attraction','result_specialization_attraction']}
    background={name:partition_agreement(histories[seeds[0]][name],histories[seeds[1]][name],n) for name in histories[seeds[0]]}
    dump(a.out/'paired-relation-audit.json',{'paired':paired,'seedBackground':background,'relationCounts':{'all':len(relations),'resultAndSpecialization':len(strong)},'causalLimit':'Two paired seeds characterize this bounded implementation; no population inference. Paper-projected attraction does not prove a relation between every question in endpoint papers.','typeAwareAlternative':'typed-relation-review-constraints.json preserves scoped endpoint-specific obligations, with explicit abstention where claim-to-question mapping is not established; no forced question merges.'})
    dump(a.out/'comparison.json',results);mark('complete',wallSeconds=time.time()-start)

if __name__=='__main__':main()
