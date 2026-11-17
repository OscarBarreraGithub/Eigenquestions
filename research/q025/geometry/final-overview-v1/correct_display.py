"""One authorized broad-display correction; exact canonical H/F/C untouched."""
import argparse,json
from pathlib import Path
import numpy as np
from scipy.spatial.distance import pdist,squareform
from scipy import sparse
import overview as core
p=argparse.ArgumentParser();p.add_argument('--previous',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
previous=json.loads((a.previous/'overview.json').read_text());flows=np.load(a.previous/'complete-coarse-flow.npz');A=flows['broadOverlapFlow'];nodes=previous['nodes'];ids=[n['destinationId']for n in nodes];assert A.shape==(215,215)
# Normalize the overlapping-feature flow as a display Markov operator. It is
# not a conserved source allocation and does not replace the canonical C.
degree=A.sum(axis=1);S=A/np.sqrt(degree[:,None]*degree[None,:]);e,U=np.linalg.eigh((np.eye(len(A))+S)*.5);order=np.argsort(e)[::-1];e=e[order];U=U[:,order];Y=U[:,1:]/np.sqrt(degree[:,None])*e[None,1:]**4;X=Y[:,:2].copy();X-=X.mean(axis=0)
for j in range(2):
 if X[np.argmax(abs(X[:,j])),j]<0:X[:,j]*=-1
X/=max(float(np.max(np.linalg.norm(X,axis=1))),1e-30)
for n,x in zip(nodes,X):n['x']=float(x[0]);n['y']=float(x[1]);n['coordinateBasis']='two_diffusion_modes_of_degree_normalized_broad_overlap_flow'
metrics=core.distance_diagnostics(squareform(pdist(Y)),X);diagnostics=previous['diagnostics'];diagnostics['failedFineCentroidProjection']=diagnostics.pop('displayedBroadPointFidelity');diagnostics['displayedBroadPointFidelity']=metrics;diagnostics['displayOperator']={'kind':'degree_normalized_overlapping_region_feature_flow','formula':'A=B^T F B; P=D_A^-1 A; lazy=(I+P)/2; t=4','isCanonicalConservedC':False,'regionOverlapCreatesRepeatedFeatureSupport':True,'rowNormalizationMeaning':'Transition probabilities between overlapping displayed scope features only; not source membership, confidence or additional source mass.','leadingLazyEigenvalues':e[:8].tolist(),'twoModeSpectralEnergyFraction':float(np.sum(e[1:3]**8)/np.sum(e[1:]**8)),'sourceSupportCoverageUnchanged':True}
previous.update(layoutId='accepted-broad-overlap-diffusion-v2',nodes=nodes,diagnostics=diagnostics)
previous['provenance'].update(displayOperator=diagnostics['displayOperator'],correctionScriptSha256=core.sha(__file__),failedOverviewSha256=core.sha(a.previous/'overview.json'))
previous['limitations'][0]='Broad coordinates use a degree-normalized diffusion operator on overlapping admitted region feature flow B^T F B. This display operator does not replace the complete conserved canonical H/F/C.'
previous['limitations'].append('Broad flow and its displayed neighborhood exclude regions without admitted member/support sources. Every scientific scope remains available through exact text routes; no whole-corpus broad containment is claimed.')
core.dump(a.out/'overview.json',previous);core.dump(a.out/'diagnostics.json',diagnostics);core.dump(a.out/'manifest.json',{'schemaVersion':'q025-final-broad-display-correction/1','status':'complete','canonicalGeometryInputSha256':previous['membershipSha256'],'unchangedCompleteFlowSha256':core.sha(a.previous/'complete-coarse-flow.npz'),'originalManifestSha256':core.sha(a.previous/'manifest.json'),'files':{q.name:{'sha256':core.sha(q),'bytes':q.stat().st_size}for q in sorted(a.out.iterdir())if q.is_file()}});print(json.dumps({'failed':diagnostics['failedFineCentroidProjection'],'corrected':metrics,'operator':diagnostics['displayOperator']},indent=2),flush=True)
