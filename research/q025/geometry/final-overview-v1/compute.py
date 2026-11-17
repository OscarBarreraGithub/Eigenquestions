"""Final broad orientation from complete F and explicit accepted H; no new search."""
import argparse,json,hashlib,time
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy import sparse
from scipy.spatial.distance import pdist,squareform
from scipy.sparse.csgraph import connected_components
import overview as core

def project(Y):
 z=Y-Y.mean(axis=0);U,s,V=np.linalg.svd(z,full_matrices=False);X=np.zeros((len(Y),2));X[:,:min(2,len(s))]=U[:,:2]*s[:2]
 for j in range(2):
  if X[np.argmax(abs(X[:,j])),j]<0:X[:,j]*=-1
 return X/max(float(np.max(np.linalg.norm(X,axis=1))),1e-30)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--support',type=Path,required=True);ap.add_argument('--reference-root',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True);data=json.loads(a.input.read_text());support=json.loads(a.support.read_text());assert support['geometryInputSha256']==core.sha(a.input)
 units=data['sourceMassInventory'];lookup={u['unitId']:i for i,u in enumerate(units)};mass=np.array([u['paperBalancedMass']for u in units]);assert len(units)==8473
 W,reference,selection=core.load_reference(a.reference_root,units,False);F,flow=core.source_balanced_flow(W,mass)
 ids=sorted(set(r['destinationId']for r in data['allocations']));cols={id:i for i,id in enumerate(ids)};H=sparse.csr_matrix(([r['weight']for r in data['allocations']],([lookup[r['unitId']]for r in data['allocations']],[cols[r['destinationId']]for r in data['allocations']])),shape=(len(units),len(ids)))
 sums=np.asarray(H.sum(axis=1)).ravel();resolved=np.array([u['allocationStatus']=='resolved'for u in units]);assert np.max(abs(sums[resolved]-1))<1e-12 and not np.any(sums[~resolved]);C=np.asarray((H.T@F@H).todense());degree=C.sum(axis=1);assert np.all(degree>0);nc,labels=connected_components(sparse.csr_matrix(C),directed=False);assert nc==1,'Multiple geometric components require explicit separate plotting, not false common distances.'
 # Complete C is preserved. The spectral operator is normalized only on C's
 # represented flow; lost flow to zero-H sources is separately quantified.
 eigen,V=np.linalg.eigh((np.eye(len(C))+C/np.sqrt(degree[:,None]*degree[None,:]))*.5);order=np.argsort(eigen)[::-1];eigen=eigen[order];V=V[:,order];Y=(V[:,1:]/np.sqrt(degree[:,None]))*eigen[None,1:]**4;sourceY=np.asarray(H@Y)
 dest={d['id']:d for d in data['destinations']};children=defaultdict(set)
 for d in dest.values():
  for p in d['parentIds']:children[p].add(d['id'])
 cache={}
 def descendants(d):
  if d not in cache:
   value={d}
   for child in children[d]:value|=descendants(child)
   cache[d]=value
  return cache[d]
 broad=[];Z=[];Bcols=[];covered=set();unplotted=[]
 for d in sorted(dest.values(),key=lambda d:d['id']):
  if d['kind']!='region':continue
  atomcols=[cols[x]for x in descendants(d['id']) if x in cols];membership=np.asarray(H[:,atomcols].sum(axis=1)).ravel() if atomcols else np.zeros(len(units));membership=np.minimum(membership,1)
  positive=support['positiveSupport'].get(d['id'],[]);pix=[lookup[u]for u in positive if u in lookup and resolved[lookup[u]]];weights=membership.copy();basis='admitted_direct_and_narrower_descendant_allocation'
  if not weights.any() and pix:weights[pix]=1;basis='positive_target_support_centroid_zero_H_mass'
  if not weights.any():unplotted.append(d['id']);continue
  active=np.where(weights>0)[0];covered.update(active.tolist());weighted=mass*weights;Z.append(np.average(sourceY,axis=0,weights=weighted));Bcols.append(weights);broad.append({'destinationId':d['id'],'mass':float((mass*membership).sum()),'depth':support['depths'].get(d['id'],0),'scopeKind':'region','coordinateBasis':basis,'sourceCount':len(active),'coordinateSupportMass':float(weighted.sum()),'positiveSupportCoverage':{'represented':len(pix),'total':len(positive)},'membershipOverlapPermitted':True})
 Z=np.array(Z);X=project(Z);D=squareform(pdist(Z));metrics=core.distance_diagnostics(D,X);B=sparse.csc_matrix(np.array(Bcols).T);BC=np.asarray((B.T@F@B).todense());bd=BC.sum(axis=1);score=BC/np.sqrt(bd[:,None]*bd[None,:]);np.fill_diagonal(score,0);pairs=set()
 for i in range(len(broad)):
  for j in np.argsort(score[i])[-6:]:
   if score[i,j]>0:pairs.add(tuple(sorted((i,int(j)))))
 edges=[{'source':broad[i]['destinationId'],'target':broad[j]['destinationId'],'kind':'geometric_affinity','weight':float(BC[i,j]),'normalizedWeight':float(score[i,j])}for i,j in sorted(pairs)]
 for n,x in zip(broad,X):n.update(x=float(x[0]),y=float(x[1]))
 assert len(broad)<1500;assert set(support['entryDestinationIds'])<=set(n['destinationId']for n in broad),'Approved entrance lacks actual geometric support'
 off=BC.copy();np.fill_diagonal(off,0);retained=sum(2*BC[i,j]for i,j in pairs);assigned_mass=mass[resolved].sum();Ctotal=C.sum();cross=float(assigned_mass-Ctotal);unassigned=~resolved;uu=float(F[unassigned][:,unassigned].sum());assert abs(mass[unassigned].sum()-(cross+uu))<1e-8
 diagnostics={'coverage':{'allSourceQuestionCount':len(units),'allocatedSourceCount':int(resolved.sum()),'zeroHSourceCount':int(unassigned.sum()),'directScientificBaseCount':len(ids),'plottedBroadRegions':len(broad),'unplottedRegionIds':unplotted,'broadCoordinateSupportUniqueSources':len(covered),'broadCoordinateSupportMassUnion':float(mass[list(covered)].sum()),'allDirectBasesInfluenceFullCoarseOperator':True,'methodsAreContextAffinityOnly':True},'mass':{**data['coverage']['sourceMass'],'fullFMass':float(F.sum()),'CRepresentedFlow':float(Ctotal),'assignedToZeroHFlowOneDirection':cross,'zeroHToZeroHFlow':uu,'totalFlowOutsideC':float(F.sum()-Ctotal),'coarseMassNotRenormalized':True},'flow':flow,'displayedBroadPointFidelity':metrics,'broadAffinityDisplay':{'displayedEdges':len(edges),'positiveUndirectedPairs':int(np.sum(off>0)//2),'retainedOffDiagonalOverlapFlowFraction':float(retained/off.sum()),'overlapFlowIsNotAProbabilityOrAdditionalHMass':True},'operator':{'lazyDiffusionTime':4,'completeEigenDimensions':len(ids)-1,'sourceGraphComponents':int(connected_components(W,directed=False)[0]),'coarseComponents':nc},'referenceSelection':selection,'limitations':['Broad coordinates are source-mass-weighted centroids in the full accepted coarse diffusion space; plotting then retains its two leading broad centroid axes.','Broad regions can overlap; their support masses do not sum to corpus mass. Direct residual H and full descendant-scope display are different quantities.','Fine scopes remain navigable through exact text and typed routes. This plot makes no claim of globally faithful fine-question distances.','All source mass and flow to unresolved/reserved sources remain counted outside C. Source descriptions of reserved papers were not read.','Scientific route validity is independent of geometric proximity. Reviewed source relations did not change the selected retrieval operator.']}
 membership=core.sha(a.input);overview={'layoutId':'accepted-broad-parent-support-diffusion-v1','kind':'diffusion_chart','entryDestinationId':support['entryDestinationId'],'membershipSha256':membership,'nodes':broad,'edges':edges,'coverage':'Accepted broad scientific regions, with admitted narrower-descendant source allocations or explicitly labeled zero-H positive-target support; fine scopes remain in text/navigation.','diagnostics':diagnostics,'provenance':{'operator':'Complete source-balanced Metropolis F; explicit H; C=H^T F H; source-balanced broad membership/support centroids in lazy diffusion space.','retrievalLayers':{'minilmQuestion':.5,'qwenQuestion':.3,'samePaperMethodContext':.2},'reviewedGraphContribution':'Typed source and destination routes are separately navigable; held-out coupling did not improve and was not added to W.','membershipSha256':membership,'referenceInputs':reference,'supportSha256':core.sha(a.support),'scriptSha256':core.sha(__file__),'coreSha256':core.sha(core.__file__)},'limitations':diagnostics['limitations']}
 core.dump(a.out/'overview.json',overview);core.dump(a.out/'diagnostics.json',diagnostics);core.dump(a.out/'atom-ids.json',ids);np.savez_compressed(a.out/'complete-coarse-flow.npz',C=C,broadOverlapFlow=BC);sparse.save_npz(a.out/'accepted-H.npz',H);sparse.save_npz(a.out/'complete-F.npz',F);core.dump(a.out/'manifest.json',{'schemaVersion':'q025-final-broad-geometry/1','status':'complete','inputSha256':membership,'supportSha256':core.sha(a.support),'files':{p.name:{'sha256':core.sha(p),'bytes':p.stat().st_size}for p in sorted(a.out.iterdir())if p.is_file()}});print(json.dumps(diagnostics,indent=2),flush=True)
if __name__=='__main__':main()
