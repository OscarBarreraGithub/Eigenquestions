#!/usr/bin/env python3
"""Geometry downstream of explicit organization; never infer scopes or acceptance."""
import argparse,hashlib,json,math
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy import sparse
from scipy.sparse.csgraph import connected_components
from scipy.spatial.distance import pdist,squareform

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def dump(path,value):Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def normalize(W):
    d=np.asarray(W.sum(axis=1)).ravel();s=1/np.sqrt(np.maximum(d,1e-30));return (sparse.diags(s)@W@sparse.diags(s)).tocsr()

def source_balanced_flow(W,mass):
    """Metropolis reversible flow, preserving every source mass including isolates."""
    W=((W+W.T)*.5).tocsr();W.setdiag(0);W.eliminate_zeros()
    if np.any(W.data<0) or np.any(~np.isfinite(W.data)):raise ValueError('Invalid source affinity')
    degree=np.asarray(W.sum(axis=1)).ravel();rate=np.divide(mass,degree,out=np.zeros_like(mass),where=degree>0);coo=W.tocoo();F=sparse.csr_matrix((coo.data*np.minimum(rate[coo.row],rate[coo.col]),(coo.row,coo.col)),shape=W.shape)
    residual=mass-np.asarray(F.sum(axis=1)).ravel();assert residual.min()>-1e-10
    F.setdiag(np.maximum(residual,0));F.eliminate_zeros()
    assert np.max(np.abs(np.asarray(F.sum(axis=1)).ravel()-mass))<1e-10
    assert not (F-F.T).nnz or np.max(np.abs((F-F.T).data))<1e-12
    return F,{'isolatedSourceCount':int(np.sum(degree==0)),'selfFlowFraction':float(F.diagonal().sum()/mass.sum()),'sourceMassMaxError':float(np.max(np.abs(np.asarray(F.sum(axis=1)).ravel()-mass)))}

def regional_allocation(data):
    units=data['units'];lookup={u['unitId']:i for i,u in enumerate(units)};dest={d['id']:d for d in data['destinations']}
    allowed=set(data.get('baseDestinationIds') or [d['id'] for d in dest.values() if d['kind']=='region'])
    assert all(d in dest and dest[d]['kind']=='region' for d in allowed)
    ancestors_cache={}
    def ancestors(id):
        if id in ancestors_cache:return ancestors_cache[id]
        seen=set();todo=list(dest[id]['parentIds'])
        while todo:
            p=todo.pop()
            if p in seen:continue
            if p==id:raise ValueError('Cyclic accepted region graph')
            seen.add(p);todo.extend(dest[p]['parentIds'])
        ancestors_cache[id]=seen;return seen
    assignments=[];active=set()
    for a in data['allocations']:
        assert a['unitId'] in lookup and a['destinationId'] in dest
        candidates=({a['destinationId']}|ancestors(a['destinationId']))&allowed
        nearest={r for r in candidates if not any(r in ancestors(other) for other in candidates if other!=r)}
        if not nearest:raise ValueError('No admitted regional catchment for '+a['unitId'])
        for r in nearest:assignments.append((lookup[a['unitId']],r,a['weight']/len(nearest)));active.add(r)
    atom_ids=sorted(active);columns={r:j for j,r in enumerate(atom_ids)};H=sparse.csr_matrix(([w for i,r,w in assignments],([i for i,r,w in assignments],[columns[r] for i,r,w in assignments])),shape=(len(units),len(atom_ids)))
    assert np.max(np.abs(np.asarray(H.sum(axis=1)).ravel()-1))<1e-10
    # Atoms are direct regional catchments; a broad unresolved source may have
    # an ancestor atom without creating a new semantic residual destination.
    return H,atom_ids,lookup,dest

def fit_stress(D,seed):
    n=len(D);rng=np.random.default_rng(seed)
    if seed==0:
        J=np.eye(n)-np.ones((n,n))/n;e,U=np.linalg.eigh(-.5*J@(D*D)@J);ix=np.argsort(e)[::-1][:2];X=U[:,ix]*np.sqrt(np.maximum(e[ix],0))
    else:X=rng.normal(size=(n,2))*max(np.mean(D),1e-6)/2
    previous=np.inf
    for it in range(1200):
        d=squareform(pdist(X));ratio=np.divide(D,d,out=np.zeros_like(D),where=d>1e-12);B=-ratio;B[np.diag_indices(n)]=ratio.sum(axis=1);X=B@X/n;X-=X.mean(axis=0);cost=float(np.sum((squareform(pdist(X))-D)**2)/2)
        if np.isfinite(previous) and (previous-cost)/max(previous,1e-30)<1e-10:break
        previous=cost
    return X,cost,it+1
def distance_diagnostics(D,X):
    target=squareform(D,checks=False);projected=pdist(X);den=float(np.linalg.norm(target))
    if den<1e-15:return {'distanceStress':0.,'topFiveNeighborRecall':None,'degenerateTarget':True}
    scale=float(target@projected/max(projected@projected,1e-30));error=float(np.linalg.norm(target-scale*projected)/den);n=len(D);k=min(n-1,5);actual=squareform(projected);reference=D.copy();np.fill_diagonal(actual,np.inf);np.fill_diagonal(reference,np.inf)
    return {'distanceStress':error,'topFiveNeighborRecall':float(np.mean([len(set(np.argsort(actual[i])[:k])&set(np.argsort(reference[i])[:k]))/k for i in range(n)])),'degenerateTarget':False}

def coarse_layout(C,atom_ids,time=4):
    off=C.copy();np.fill_diagonal(off,0);nc,labels=connected_components(sparse.csr_matrix(off>1e-15),directed=False);groups=sorted([np.where(labels==k)[0] for k in range(nc)],key=lambda v:(-len(v),atom_ids[int(v[0])]))
    coords=np.zeros((len(C),2));reports=[];components={};columns=math.ceil(math.sqrt(nc))
    for ci,ix in enumerate(groups):
        A=C[np.ix_(ix,ix)];n=len(ix);d=A.sum(axis=1)
        if n==1:X=np.zeros((1,2));report={'component':ci,'atomCount':1,'layout':'isolated','distanceStress':None}
        else:
            S=A/np.sqrt(d[:,None]*d[None,:]);e,U=np.linalg.eigh((np.eye(n)+S)/2);order=np.argsort(e)[::-1];e=e[order];U=U[:,order];full=(U[:,1:]/np.sqrt(d[:,None]))*(e[None,1:]**time);D=squareform(pdist(full));projected=np.zeros((n,2));projected[:,:min(n-1,2)]=full[:,:min(n-1,2)];before=distance_diagnostics(D,projected)
            fits=[fit_stress(D,seed) for seed in range(3)];best=min(range(len(fits)),key=lambda j:fits[j][1]);fitted,cost,iterations=fits[best];after=distance_diagnostics(D,fitted)
            use_fit=before['distanceStress']-after['distanceStress']>.05;X=fitted if use_fit else projected;_,_,V=np.linalg.svd(X,full_matrices=False);X=X@V.T
            report={'component':ci,'atomCount':n,'layout':'metric_fit_to_diffusion_distances' if use_fit else 'two_diffusion_modes','projection':before,'metricFit':after,'chosenInitialization':best,'iterations':iterations,'leadingLazyEigenvalues':e[:8].tolist(),'twoModeEnergyFraction':float(np.sum(e[1:3]**(2*time))/max(np.sum(e[1:]**(2*time)),1e-30))}
        for dim in range(2):
            if X[np.argmax(np.abs(X[:,dim])),dim]<0:X[:,dim]*=-1
        X-=X.mean(axis=0);radius=max(np.max(np.linalg.norm(X,axis=1)),1e-30);X/=radius;offset=np.array([3*(ci%columns),3*(ci//columns)]);coords[ix]=X+offset
        for j in ix:components[atom_ids[int(j)]]=ci
        report['displayPackingOffset']=offset.tolist();report['interComponentDistancesMeaningful']=False;reports.append(report)
    return coords,reports,components

def compute(data,W):
    H,atom_ids,lookup,dest=regional_allocation(data);m=np.array([u['paperBalancedMass'] for u in data['units']],float);assert np.all(m>0)
    per_paper=defaultdict(float)
    for u in data['units']:per_paper[u['paperId']]+=u['paperBalancedMass']
    assert max(abs(x-1) for x in per_paper.values())<1e-10
    F,flow_report=source_balanced_flow(W,m);C=np.asarray((H.T@F@H).todense());assert abs(C.sum()-m.sum())<1e-8
    coords,layout_report,components=coarse_layout(C,atom_ids);unit_coords=np.asarray(H@coords);nodes=[]
    def depth(id,seen=None):
        seen=set() if seen is None else seen
        if id in seen:raise ValueError('Cycle in destination ancestry')
        return 0 if not dest[id]['parentIds'] else 1+min(depth(p,seen|{id}) for p in dest[id]['parentIds'])
    for d in dest.values():
        if d['kind']!='region':continue
        rows=[lookup[u] for u in d['memberIds'] if u in lookup]
        if not rows:continue
        weights=m[rows];point=np.average(unit_coords[rows],axis=0,weights=weights)
        nodes.append({'destinationId':d['id'],'x':float(point[0]),'y':float(point[1]),'mass':float(weights.sum()),'depth':depth(d['id']),'sourceUnitCount':len(rows),'coordinateMeaning':'source-balanced centroid of accepted regional membership; direct-catchment atoms are computational only'})
    degree=C.sum(axis=1);edges=[]
    for i in range(len(atom_ids)):
        for j in range(i+1,len(atom_ids)):
            if C[i,j]>0:edges.append({'source':atom_ids[i],'target':atom_ids[j],'kind':'geometric_affinity','weight':float(C[i,j]),'normalizedWeight':float(C[i,j]/np.sqrt(degree[i]*degree[j]))})
    diagnostics={'coverage':{'questionUnits':len(data['units']),'papers':len(per_paper),'regionNodes':len(nodes),'directRegionalCatchments':len(atom_ids),'methodsExcludedFromGeometry':True,'provisionalAllocationCount':sum(a['placementStatus']!='accepted' for a in data['allocations'])},'flow':flow_report,'coarseFlowTotal':float(C.sum()),'expectedPaperMass':len(per_paper),'components':layout_report,'fineQuestionsPlotted':False}
    return {'nodes':nodes,'edges':edges,'diagnostics':diagnostics,'atomIds':atom_ids,'coarseFlow':C,'unitCoordinates':unit_coords}

def load_reference(root,accepted_units):
    files={}
    def load(kind):
        path=root/kind;units=[]
        for line in (path/'units.jsonl').open():
            u=json.loads(line);units.append({k:u.get(k) for k in ['unit_id','paper_id','mass','text_sha256']})
        W=sparse.load_npz(path/'affinity.npz');assert W.shape==(len(units),len(units))
        for name in ['units.jsonl','affinity.npz']:files[str(Path(kind)/name)]={'sha256':sha(path/name),'bytes':(path/name).stat().st_size}
        return units,W
    q,W=load('geometry-minilm-physical_question');qq,Wq=load('geometry-qwen-4b-raw-physical_question');methods,Wm=load('geometry-minilm-method');order={u['unit_id']:i for i,u in enumerate(q)};qorder={u['unit_id']:i for i,u in enumerate(qq)}
    assert len(order)==len(q)==len(accepted_units)
    for u in accepted_units:
        row=order[u['unitId']];assert q[row]['paper_id']==u['paperId'] and q[row]['text_sha256']==u['textSha256'] and row==u['sourceRow']
    permutation=[qorder[u['unit_id']] for u in q];Wq=Wq[permutation][:,permutation];method_papers=defaultdict(list)
    for j,u in enumerate(methods):method_papers[u['paper_id']].append(j)
    rr=[];cc=[];vv=[]
    for i,u in enumerate(q):
        js=method_papers[u['paper_id']];den=sum(methods[j]['mass'] for j in js)
        for j in js:rr.append(i);cc.append(j);vv.append(methods[j]['mass']/den)
    B=sparse.csr_matrix((vv,(rr,cc)),shape=(len(q),len(methods)));M=(B@normalize(Wm)@B.T).tocsr();M.setdiag(0);M.eliminate_zeros();G=.5*normalize(W)+.3*normalize(Wq)+.2*normalize(M)
    accepted_order=[order[u['unitId']] for u in accepted_units];return G[accepted_order][:,accepted_order],files

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--reference-root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();data=json.loads(a.input.read_text());assert data['schemaVersion']=='q025-accepted-geometry-input/1';a.out.mkdir(parents=True,exist_ok=True)
    W,files=load_reference(a.reference_root,data['units']);result=compute(data,W);reference_hash=hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode()).hexdigest();membership_hash=sha(a.input)
    overview={'layoutId':'accepted-regions-source-balanced-v1','kind':'diffusion_chart','sourceCandidateId':data['originalCandidate']['candidateId'],'referenceGraphSha256':reference_hash,'membershipSha256':membership_hash,'nodes':result['nodes'],'edges':result['edges'],'provenance':{'operator':'Metropolis source-balanced reversible flow; H^T F H; lazy diffusion distances','retrievalLayers':{'minilmQuestion':.5,'qwenQuestion':.3,'samePaperMethodContext':.2},'directCatchmentMeaning':'Nearest accepted regional ancestors of explicit organizational homes. Broad residual sources retain their actual family; no semantic residual region is invented.','diffusionTime':4,'layoutSelection':'Two-mode projection versus metric fit to the same full diffusion distances; fit used only for an absolute stress reduction above0.05.','coordinateTransform':'Rigid axis orientation; uniform per-component scale; explicit disconnected-component packing. Region positions are source-balanced membership centroids.','scriptSha256':sha(__file__),'referenceInputs':files},'diagnostics':result['diagnostics'],'limitations':['Geometry is downstream of reviewed organization and does not certify its science.','Membership weights are organizational allocations, not confidence or relevance.','Same-paper method geometry is retrieval context; reviewed scientific edges are separately navigable.','Two dimensions are lossy; inspect component distortion before interpreting proximity.','Disconnected-component display spacing has no metric meaning.','Fine scoped-question identity states are accessible through text/navigation and are not all plotted.']}
    dump(a.out/'overview.json',overview);dump(a.out/'diagnostics.json',result['diagnostics']);np.savez_compressed(a.out/'coarse-flow.npz',flow=result['coarseFlow']);dump(a.out/'atom-ids.json',result['atomIds']);dump(a.out/'manifest.json',{'schemaVersion':'q025-accepted-overview/1','acceptedMembershipInputSha256':membership_hash,'referenceGraphSha256':reference_hash,'files':{p.name:{'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(a.out.iterdir()) if p.is_file()}});print(json.dumps(result['diagnostics'],indent=2),flush=True)

if __name__=='__main__':main()
