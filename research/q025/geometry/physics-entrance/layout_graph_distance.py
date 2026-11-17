#!/usr/bin/env python3
"""Compare a classification-graph stress layout with the retained diffusion failure."""
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import shortest_path,connected_components
from scipy.spatial.distance import pdist,squareform

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def fit_stress(D,seed):
    n=len(D);rng=np.random.default_rng(seed)
    if seed==0:
        J=np.eye(n)-np.ones((n,n))/n;B=-.5*J@(D*D)@J;e,U=np.linalg.eigh(B);ix=np.argsort(e)[::-1][:2];X=U[:,ix]*np.sqrt(np.maximum(e[ix],0))
    else:X=rng.normal(size=(n,2))*np.mean(D)/2
    previous=np.inf
    for iteration in range(1500):
        distance=squareform(pdist(X));ratio=np.divide(D,distance,out=np.zeros_like(D),where=distance>1e-12);B=-ratio;B[np.diag_indices(n)]=ratio.sum(axis=1);new=B@X/n;new-=new.mean(axis=0);stress=float(np.sum((squareform(pdist(new))-D)**2)/2)
        X=new
        if np.isfinite(previous) and (previous-stress)/max(previous,1e-30)<1e-10:break
        previous=stress
    return X,stress,iteration+1
def diagnostics(D,X):
    target=squareform(D,checks=False);projected=pdist(X);scale=float(target@projected/max(projected@projected,1e-30));stress=float(np.linalg.norm(target-scale*projected)/np.linalg.norm(target));dx=squareform(projected);df=D.copy();np.fill_diagonal(dx,np.inf);np.fill_diagonal(df,np.inf);k=min(5,len(D)-1);recall=float(np.mean([len(set(np.argsort(df[i])[:k])&set(np.argsort(dx[i])[:k]))/k for i in range(len(D))]));return {'graphDistanceStressAfterUniformFit':stress,'graphTopFiveNeighborRecall':recall,'neighborTieCaveat':'Equal-distance ties use fixed source order; this graph metric is a display construction, not physics distance.'}
def main():
    p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    o=json.loads((a.baseline/'orientation.json').read_text());members=json.loads((a.baseline/'memberships.json').read_text());ids=[n['destinationId'] for n in o['nodes']];universe=sorted(set(c for x in members.values() for c in x));rows={c:i for i,c in enumerate(universe)};H=np.zeros((len(universe),len(ids)))
    for j,k in enumerate(ids):H[[rows[c] for c in members[k]],j]=1
    H/=np.maximum(np.linalg.norm(H,axis=0),1e-30);W=H.T@H;np.fill_diagonal(W,0);nc,assignment=connected_components(csr_matrix(W>0),directed=False);groups=sorted([np.where(assignment==g)[0] for g in range(nc)],key=lambda v:(-len(v),ids[int(v[0])]))
    coords=np.zeros((len(ids),2));report=[];columns=math.ceil(math.sqrt(nc));packing=[]
    for number,idx in enumerate(groups):
        local=W[np.ix_(idx,idx)];length=np.divide(1,np.sqrt(local),out=np.zeros_like(local),where=local>0);D=shortest_path(csr_matrix(length),directed=False);assert np.all(np.isfinite(D));old=np.array([[o['nodes'][int(i)]['x'],o['nodes'][int(i)]['y']] for i in idx]);candidates=[fit_stress(D,seed) for seed in range(5)];best=min(range(len(candidates)),key=lambda k:candidates[k][1]);X,stress,iterations=candidates[best]
        # Canonical orientation uses PCA of the fitted chart; it is a rigid motion.
        _,_,V=np.linalg.svd(X,full_matrices=False);X=X@V.T
        for dim in range(2):
            if X[np.argmax(np.abs(X[:,dim])),dim]<0:X[:,dim]*=-1
        measures={'component':number,'nodeCount':len(idx),'baselineDiffusionAgainstGraphDistance':diagnostics(D,old),'graphStressLayout':diagnostics(D,X),'chosenInitialization':best,'iterations':iterations,'fiveInitializationStress':[float(v[1]) for v in candidates]};report.append(measures)
        X-=X.mean(axis=0);X/=max(np.max(np.linalg.norm(X,axis=1)),1e-30);offset=np.array([3*(number%columns),3*(number//columns)]);coords[idx]=X+offset;packing.append({'component':number,'offset':offset.tolist(),'nodeIds':[ids[int(i)] for i in idx],'interComponentDistancesMeaningful':False})
    for i,n in enumerate(o['nodes']):n['x']=float(coords[i,0]);n['y']=float(coords[i,1])
    o['layoutId']='physics-classification-v2.8.0-shared-descendants-graph-stress-v2';o['provenance'].update(operator='Metric stress minimization of shortest-path distances on the shared-descendant concept graph',edgeLength='1 / sqrt(cosine(binary descendant membership)); this monotone display construction has no empirical physics units.',optimization='SMACOF, classical initialization plus four fixed random starts, at most1500 iterations; selected minimum stress.',scriptSha256=sha(__file__),baselineOrientationSha256=sha(a.baseline/'orientation.json'),coordinateTransform='Rigid PCA orientation/sign fixing; uniform per-component scaling and deterministic disconnected-component packing.');o['provenance'].pop('diffusionTime',None);o['provenance'].pop('modes',None);o['diagnostics']['components']=report;o['diagnostics']['packing']=packing;o['limitations'].append('Graph-distance layout is a browsing aid; edge-length mapping and 2D fit can change visible proximity without changing classification memberships.')
    write(a.out/'orientation.json',o);write(a.out/'comparison.json',{'selected':'graph_distance_stress','sameNodesAndMembershipsAsBaseline':True,'components':report,'selectionRationale':'The first two diffusion modes collapsed most fields; graph-distance stress layout is evaluated against the same declared graph-distance target for both candidates. Source membership and exact classification links remain unchanged.'});write(a.out/'manifest.json',{'schemaVersion':'q025-classification-layout-comparison/1','sourceBaselineManifestSha256':sha(a.baseline/'manifest.json'),'scriptSha256':sha(__file__),'files':{p.name:{'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(a.out.glob('*.json'))}});print(json.dumps(report,indent=2),flush=True)

if __name__=='__main__':main()
