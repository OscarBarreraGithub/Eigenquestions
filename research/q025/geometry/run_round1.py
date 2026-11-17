#!/usr/bin/env python3
"""Q-025 bounded geometry comparison. Execute numerical work in Slurm.

Every output region is a candidate organization, never canonical equivalence.
Independent scientific connections remain typed, scoped records.
"""
import argparse, hashlib, json, os, platform, time, traceback
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
import scipy
from scipy import sparse
from scipy.sparse.csgraph import connected_components, shortest_path
from sklearn.metrics import adjusted_rand_score
import igraph as ig
import leidenalg as la


def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()

def dump(path, data):
    Path(path).write_text(json.dumps(data,indent=2,ensure_ascii=False,allow_nan=False)+'\n')

def digest(values):
    return hashlib.sha256('\n'.join(values).encode()).hexdigest()

def compact_units(path):
    result=[]
    for line in open(path):
        u=json.loads(line)
        result.append({k:u.get(k) for k in ['unit_id','paper_id','view','text','text_sha256','mass','facet_ids','node_ids','source_record_ids','embedding_rows']})
    return result

def normalize(W):
    degree=np.asarray(W.sum(1)).ravel()
    return (sparse.diags(1/np.sqrt(np.maximum(degree,1e-30)))@W@sparse.diags(1/np.sqrt(np.maximum(degree,1e-30)))).tocsr()

def dropout(W,seed=1307):
    U=sparse.triu(W,1).tocoo();rng=np.random.default_rng(seed)
    keep=rng.random(U.nnz)>=.1
    V=sparse.csr_matrix((U.data[keep],(U.row[keep],U.col[keep])),shape=W.shape)
    return (V+V.T).tocsr()

def hard_matrix(labels):
    ids=sorted(set(labels));lookup={v:i for i,v in enumerate(ids)}
    return sparse.csr_matrix((np.ones(len(labels)),(np.arange(len(labels)),[lookup[x] for x in labels])),shape=(len(labels),len(ids))),ids

def diffuse(W,H,alpha):
    degree=np.asarray(W.sum(1)).ravel()
    P=sparse.diags(1/np.maximum(degree,1e-30))@W
    base=H.toarray();X=base.copy()
    for iteration in range(160):
        Y=(1-alpha)*base+alpha*(P@X)
        residual=float(np.abs(Y-X).max());X=Y
        if residual<1e-9:break
    X[X<.2*X.max(1)[:,None]]=0
    X/=np.maximum(X.sum(1)[:,None],1e-30)
    return sparse.csr_matrix(X),{'alpha':alpha,'iterations':iteration+1,'max_residual':residual,'retention':'all memberships >= 0.2 of largest; row normalized'}

def split_leiden(W,seed,resolution):
    U=sparse.triu(W,1).tocoo()
    g=ig.Graph(n=W.shape[0],edges=list(zip(U.row.tolist(),U.col.tolist())),directed=False)
    partition=la.find_partition(g,la.RBConfigurationVertexPartition,weights=U.data.tolist(),resolution_parameter=resolution,seed=seed,n_iterations=6)
    labels=np.asarray(partition.membership)
    return labels

def hierarchy(W,units,seed,minmass=12,maxdepth=6):
    mass=np.asarray([u['mass'] for u in units]);nodes=[];leaflabels=np.zeros(len(units),dtype=int);leaves=[]
    def visit(rows,parent,depth):
        identity='region:'+digest(sorted(units[i]['unit_id'] for i in rows))[:20]
        node={'id':identity,'parentId':parent,'depth':depth,'children':[],'rows':rows.tolist(),'mass':float(mass[rows].sum())}
        nodes.append(node)
        reason='size_or_depth'
        if depth<maxdepth and len(rows)>=60 and mass[rows].sum()>=80:
            sub=W[rows][:,rows];labels=split_leiden(sub,seed+depth,.65 if depth==0 else .8)
            groups=[rows[labels==label] for label in sorted(set(labels))]
            sizes=[mass[x].sum() for x in groups]
            if 2<=len(groups)<=15 and min(sizes)>=minmass and min(map(len,groups))>=12:
                # Seed repeatability is measured, not used as a semantic gate.
                second=split_leiden(sub,seed+depth+100,.65 if depth==0 else .8)
                node['seedARI']=float(adjusted_rand_score(labels,second))
                for group in groups:node['children'].append(visit(group,identity,depth+1))
                node['stopReason']=None
                return identity
            reason='split_gate';node['rejectedSplit']={'childCount':len(groups),'masses':list(map(float,sizes)),'units':list(map(len,groups))}
        node['stopReason']=reason;leaflabels[rows]=len(leaves);leaves.append(identity)
        return identity
    root=visit(np.arange(len(units)),None,0)
    H=sparse.csr_matrix((np.ones(len(units)),(np.arange(len(units)),leaflabels)),shape=(len(units),len(leaves)))
    return H,leaves,nodes,root

def coarse_edges(W,H):
    C=(H.T@W@H).toarray();np.fill_diagonal(C,0)
    strength=np.sqrt(np.maximum(C.sum(1),1e-30));N=C/strength[:,None]/strength[None,:]
    keep=np.zeros_like(C,dtype=bool)
    for i,row in enumerate(N):
        positive=np.flatnonzero(row>0);top=positive[np.argsort(row[positive])[-6:]];keep[i,top]=True
    keep|=keep.T
    return C,N,keep

def diagnostics(W,H,units,nodes,relations):
    mass=np.asarray([u['mass'] for u in units]);primary=np.asarray(H.argmax(1)).ravel();sizes=np.bincount(primary,minlength=H.shape[1]);regions_mass=np.asarray(H.T@mass).ravel()
    C,N,keep=coarse_edges(W,H)
    total=float(W.sum());internal=float((H.T@W@H).diagonal().sum())
    rowsums=np.asarray(H.sum(1)).ravel();degree=np.asarray(W.sum(1)).ravel()
    # Conductance of hard primary homes; overlaps assessed separately.
    conductance=[]
    for j in range(H.shape[1]):
        mask=primary==j;volume=float(degree[mask].sum());cut=float(W[mask][:,~mask].sum())
        conductance.append(cut/max(min(volume,total-volume),1e-30))
    paperrows=defaultdict(list)
    for i,u in enumerate(units):paperrows[u['paper_id']].append(i)
    relationchecks=[]
    for r in relations:
        left=paperrows.get(r['leftPaperId'],[]);right=paperrows.get(r['rightPaperId'],[])
        a=set(primary[left]);b=set(primary[right]);cross=[(i,j) for i in a for j in b if i!=j]
        relationchecks.append({'relationId':r['id'],'represented':bool(left and right),'samePrimaryRegion':bool(a&b),'crossRegionPairs':len(cross),'geometricTop6RetainsAny':any(keep[i,j] for i,j in cross),'typedScientificEdgeRetained':True})
    text=[u['text'].lower() for u in units]
    groups={'kk':[i for i,t in enumerate(text) if 'kaluza' in t or 'kk tower' in t or 'extra dimension' in t], 'dark_matter':[i for i,t in enumerate(text) if 'dark matter' in t], 'cosmology':[i for i,t in enumerate(text) if 'cosmolog' in t]}
    bridge={}
    for k,rows in groups.items():
        bridge[k]={'units':len(rows),'primaryRegions':sorted(set(map(int,primary[rows])))}
    D=shortest_path(sparse.csr_matrix(keep.astype(float)),directed=False,unweighted=True)
    for a,b in [('kk','dark_matter'),('dark_matter','cosmology')]:
        aa=bridge[a]['primaryRegions'];bb=bridge[b]['primaryRegions'];d=D[np.ix_(aa,bb)]
        bridge[a+'__'+b]={'minCoarseHops':float(d.min()) if d.size and np.isfinite(d.min()) else None,'samePrimaryRegions':len(set(aa)&set(bb))}
    depths=[n['depth'] for n in nodes if not n.get('children')]
    return {'unitCount':len(units),'representedPapers':len(paperrows),'coverageFraction':float(np.mean(rowsums>0)),'rowWeightMaxError':float(abs(rowsums-1).max()),'regionCount':H.shape[1],'primaryUnitsMinMedianMax':[int(sizes.min()),float(np.median(sizes)),int(sizes.max())],'massMinMedianMax':[float(regions_mass.min()),float(np.median(regions_mass)),float(regions_mass.max())],'overlapUnitCount':int(np.sum(np.diff(H.indptr)>1)),'meanMembershipCount':float(H.nnz/H.shape[0]),'primaryConductanceMedian':float(np.median(conductance)),'internalFraction':internal/total,'coarseOffDiagonalMassTop6Retained':float(C[keep].sum()/max(C.sum(),1e-30)),'leafDepthMinMedianMax':[min(depths),float(np.median(depths)),max(depths)] if depths else None,'largestTerminalNodes':[{'id':n['id'],'mass':n['mass'],'units':len(n['rows']),'depth':n['depth'],'stopReason':n.get('stopReason'),'rejectedSplit':n.get('rejectedSplit')} for n in sorted((n for n in nodes if not n.get('children')),key=lambda n:n['mass'],reverse=True)[:8]],'relationChecks':relationchecks,'lexicalBridgeDiagnostics':bridge,'scientificValidation':False,'limits':['Lexical bridge masks are diagnostics, not scientific labels.','Coverage and repeatability are not semantic correctness.','All imported scientific links remain explicit regardless of coarse affinity pruning.']}

def export_candidate(out,cid,W,H,leafids,nodes,units,V,relations,extra):
    d=out/cid;d.mkdir(parents=True,exist_ok=True)
    ids={x:cid+':'+x for x in [n['id'] for n in nodes]};leaflookup={v:j for j,v in enumerate(leafids)}
    parent={n['id']:n.get('parentId') for n in nodes};desc=defaultdict(list)
    for leaf,j in leaflookup.items():
        current=leaf
        while current is not None:desc[current].append(j);current=parent.get(current)
    regions=[];primary=np.asarray(H.argmax(1)).ravel()
    with open(d/'memberships.jsonl','w') as f:
        for i,u in enumerate(units):
            for j,w in zip(H.indices[H.indptr[i]:H.indptr[i+1]],H.data[H.indptr[i]:H.indptr[i+1]]):
                f.write(json.dumps({'unitId':u['unit_id'],'sourceRow':i,'browserVectorRow':i,'regionId':ids[leafids[j]],'weight':float(w),'primary':bool(primary[i]==j)})+'\n')
    for n in nodes:
        columns=desc.get(n['id'],[]);weights=np.asarray(H[:,columns].sum(1)).ravel();rows=np.flatnonzero(weights>0)
        center=np.asarray(weights@V);center/=max(np.linalg.norm(center),1e-30)
        score=V[rows]@center;representatives=rows[np.argsort(score)[-8:][::-1]]
        regions.append({'id':ids[n['id']],'kind':'region','candidateId':cid,'title':None,'scope':{'status':'numerical_candidate_needs_source_review'},'parentIds':[ids[n['parentId']]] if n.get('parentId') else [],'childIds':[ids[x] for x in n.get('children',[])],'depth':n['depth'],'memberIds':[units[i]['unit_id'] for i in rows],'memberCount':len(rows),'mass':float(sum(units[i]['mass']*weights[i] for i in rows)),'representativeUnitIds':[units[i]['unit_id'] for i in representatives],'evidenceIds':sorted(set(z for i in representatives for z in units[i]['source_record_ids'])),'provenance':{'construction':cid,'definitionStatus':'numerical_candidate','seedARI':n.get('seedARI'),'stopReason':n.get('stopReason')}})
    dump(d/'regions.json',regions)
    C,N,keep=coarse_edges(W,H)
    with open(d/'edges.jsonl','w') as f:
        for i,j in zip(*np.nonzero(np.triu(C,1))):
            f.write(json.dumps({'id':f'{cid}:affinity:{i}:{j}','source':ids[leafids[i]],'target':ids[leafids[j]],'kind':'geometric_affinity','directed':False,'weight':float(C[i,j]),'normalizedWeight':float(N[i,j]),'displayTop6':bool(keep[i,j]),'scientificEvidence':False})+'\n')
        for r in relations:f.write(json.dumps(dict(r,kind='reviewed_scientific_relation'))+'\n')
    report=diagnostics(W,H,units,nodes,relations);report.update(extra);dump(d/'diagnostics.json',report)
    sparse.save_npz(d/'memberships.npz',H);dump(d/'column-ids.json',[ids[x] for x in leafids]);return report

def main():
    p=argparse.ArgumentParser();p.add_argument('--input-root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--relations',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    started=time.time();progress=[]
    def mark(stage,**data):
        progress.append({'stage':stage,'elapsed':time.time()-started,**data});dump(a.out/'progress.json',progress);print(stage,json.dumps(data),flush=True)
    paths={f'{e}:{lens}':a.input_root/f'geometry-{e}-{lens}' for e in ['minilm','qwen-4b-raw'] for lens in ['physical_question','method']}
    inputs={};allunits={};graphs={}
    for key,path in paths.items():
        us=compact_units(path/'units.jsonl');allunits[key]=us;graphs[key]=sparse.load_npz(path/'affinity.npz').tocsr()
        inputs[key]={'files':{name:{'sha256':sha(path/name),'bytes':(path/name).stat().st_size} for name in ['units.jsonl','vectors.npy','affinity.npz','partition.json']},'unitCount':len(us),'unitIdOrderSha256':digest([u['unit_id'] for u in us]),'graphShape':list(graphs[key].shape),'graphNNZ':graphs[key].nnz}
    units=allunits['minilm:physical_question'];W=graphs['minilm:physical_question'];V=np.load(paths['minilm:physical_question']/'vectors.npy')
    assert V.shape[0]==len(units)==W.shape[0]
    qids=[u['unit_id'] for u in units]
    for lens in ['physical_question','method']:
        ref=allunits['minilm:'+lens];other=allunits['qwen-4b-raw:'+lens];lookup={u['unit_id']:i for i,u in enumerate(other)};order=[lookup[u['unit_id']] for u in ref]
        assert all(ref[i]['text_sha256']==other[j]['text_sha256'] for i,j in enumerate(order))
        graphs['qwen-4b-raw:'+lens]=graphs['qwen-4b-raw:'+lens][order][:,order]
    relationdata=json.loads(a.relations.read_text()) if a.relations else []
    if isinstance(relationdata,list):relations=relationdata
    else:
        relations=[]
        for r in relationdata.get('records',[]):
            if not r.get('admittedScientificEdge'):continue
            assert r['status']=='accepted_relation' and not r['promotionWithheld']
            assert len(r['endpoints'])==2
            relations.append(dict(r,id='scientific:'+r['taskId'],leftPaperId=r['endpoints'][0]['paper_id'],rightPaperId=r['endpoints'][1]['paper_id']))
    dump(a.out/'input-manifest.json',{'schemaVersion':'q025-geometry-inputs/1','inputs':inputs,'relationFileSha256':sha(a.relations) if a.relations else None,'relationCount':len(relations),'software':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'igraph':ig.__version__},'scriptSha256':sha(__file__)})
    with open(a.out/'source-rows.jsonl','w') as f:
        for i,u in enumerate(units):f.write(json.dumps(dict(u,sourceRow=i,browserVectorRow=i))+'\n')
    mark('inputs_verified',units=len(units),relations=len(relations))
    partition=json.loads((paths['minilm:physical_question']/'partition.json').read_text());assert [u['unit_id'] for u in partition['units']]==qids
    A,leaves=hard_matrix(partition['leaf_membership']);nodes=[];rowlookup={v:i for i,v in enumerate(qids)}
    for n in partition['nodes']:
        rows=n.get('rows')
        if rows is None:rows=[rowlookup[x] for x in n.get('unit_ids',[])]
        nodes.append({'id':n['id'],'parentId':n.get('parent_id'),'depth':n['depth'],'children':n['children'],'rows':rows,'mass':n.get('mass',0),'stopReason':n.get('stop_reason',n.get('diagnostics',{}).get('stop_reason'))})
    # Original node ids have stable parent pointers; derive parent if format omits it.
    for n in nodes:
        for c in n['children']:next(x for x in nodes if x['id']==c)['parentId']=n['id']
    summaries={};summaries['inherited_ncut']=export_candidate(a.out,'inherited_ncut',W,A,leaves,nodes,units,V,relations,{'family':'inherited normalized cut','inheritedStability':partition.get('config')});mark('baseline_done')
    WD=dropout(W);diffusion_stability={}
    for alpha in [.35,.65,.85]:
        B,meta=diffuse(W,A,alpha);BD,_=diffuse(WD,A,alpha)
        meta['dropoutPrimaryARI']=float(adjusted_rand_score(np.asarray(B.argmax(1)).ravel(),np.asarray(BD.argmax(1)).ravel()))
        meta['dropoutMeanRowL1']=float(np.asarray(abs(B-BD).sum(1)).mean())
        cid='diffusion_'+str(alpha).replace('.','');summaries[cid]=export_candidate(a.out,cid,W,B,leaves,nodes,units,V,relations,{'family':'restart diffusion overlap','parameters':meta});mark(cid,**meta)
    # Cross-view relation is co-paper method context, explicitly not implication.
    mus=allunits['minilm:method'];bypaper=defaultdict(list)
    for j,u in enumerate(mus):bypaper[u['paper_id']].append(j)
    br=[];bc=[];bv=[]
    for i,u in enumerate(units):
        js=bypaper[u['paper_id']];denom=sum(mus[j]['mass'] for j in js)
        for j in js:br.append(i);bc.append(j);bv.append(mus[j]['mass']/denom)
    B=sparse.csr_matrix((bv,(br,bc)),shape=(len(units),len(mus)))
    method=(B@normalize(graphs['minilm:method'])@B.T).tocsr();method.setdiag(0);method.eliminate_zeros()
    Q=(.5*normalize(W)+.3*normalize(graphs['qwen-4b-raw:physical_question'])+.2*normalize(method)).tocsr()
    mark('multiview_graph',nnz=Q.nnz,methodNNZ=method.nnz)
    C,cl,cn,cr=hierarchy(Q,units,20261117)
    C2,_,_,_=hierarchy(Q,units,20261118)
    CD,_,_,_=hierarchy(dropout(Q),units,20261117)
    meta={'family':'encoder and method multiview hierarchy','layerWeights':{'minilmQuestion':.5,'qwenQuestion':.3,'samePaperMethodProjection':.2},'seedLeafARI':float(adjusted_rand_score(np.asarray(C.argmax(1)).ravel(),np.asarray(C2.argmax(1)).ravel())),'dropoutLeafARI':float(adjusted_rand_score(np.asarray(C.argmax(1)).ravel(),np.asarray(CD.argmax(1)).ravel())),'scientificRelationsAffectPartition':False}
    summaries['multiview']=export_candidate(a.out,'multiview',W,C,cl,cn,units,V,relations,meta);mark('multiview_done',**meta)
    # A deliberate sparse-relation injection ablation quantifies the danger of treating
    # all accepted relation categories as attractive affinities. Never selected silently.
    pr=defaultdict(list)
    for i,u in enumerate(units):pr[u['paper_id']].append(i)
    rr=[];rc=[];rv=[]
    for r in relations:
        aa=pr[r['leftPaperId']];bb=pr[r['rightPaperId']]
        if not aa or not bb:continue
        for i in aa:
            for j in bb:
                if i!=j:rr.extend([i,j]);rc.extend([j,i]);rv.extend([1/(len(aa)*len(bb))]*2)
    R=sparse.csr_matrix((rv,(rr,rc)),shape=W.shape)
    if R.nnz:
        QR=Q+.03*normalize(R)
        HR,rl,rn,root=hierarchy(QR,units,20261117)
        extra={'family':'relation-injection ablation only','scientificRelationsAffectPartition':True,'warning':'Artificial symmetrized attraction; preserves original edge separately but is not a scientific inference.','relationWeight':.03,'baseLeafARI':float(adjusted_rand_score(np.asarray(C.argmax(1)).ravel(),np.asarray(HR.argmax(1)).ravel())),'relationTouchedUnits':int(np.sum(np.asarray(R.sum(1)).ravel()>0))}
        summaries['multiview_relation_ablation']=export_candidate(a.out,'multiview_relation_ablation',W,HR,rl,rn,units,V,relations,extra);mark('relation_ablation_done',**extra)
    dump(a.out/'comparison.json',summaries);mark('complete',elapsed=time.time()-started)


if __name__=='__main__':
    try:main()
    except Exception:
        traceback.print_exc();raise
