"""One fixed-H layout comparison and bounded reviewed-method retrieval coupling."""
import argparse,hashlib,json,math,time
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy import sparse
from scipy.sparse.csgraph import connected_components
from scipy.spatial.distance import pdist,squareform
import overview as core
def h(path):return core.sha(path)
def orient(X):
    X=X-X.mean(axis=0);_,_,V=np.linalg.svd(X,full_matrices=False);X=X@V.T
    for j in range(min(2,X.shape[1])):
        if X[np.argmax(abs(X[:,j])),j]<0:X[:,j]*=-1
    return X/max(float(np.max(np.linalg.norm(X,axis=1))),1e-30)
def project(Y):
    z=Y-Y.mean(axis=0);U,s,V=np.linalg.svd(z,full_matrices=False);X=np.zeros((len(Y),2));X[:,:min(2,len(s))]=U[:,:2]*s[:2];return orient(X)
def full_latent(C):
    d=C.sum(axis=1);S=C/np.sqrt(d[:,None]*d[None,:]);e,U=np.linalg.eigh((np.eye(len(C))+S)*.5);ix=np.argsort(e)[::-1];e=e[ix];U=U[:,ix]
    return U[:,1:]/np.sqrt(d[:,None])*e[None,1:]**4
def percentile(xs):
    return {'min':float(min(xs)),'median':float(np.median(xs)),'p90':float(np.quantile(xs,.9)),'max':float(max(xs))} if xs else None
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--support',type=Path,required=True);ap.add_argument('--routes',type=Path,required=True);ap.add_argument('--reference-root',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    data=json.loads(a.input.read_text());support=json.loads(a.support.read_text());methodmap=json.loads(a.routes.read_text());assert support['geometryInputSha256']==h(a.input)
    W,files,selection=core.load_reference(a.reference_root,data['units'],True);H,ids,lookup,dest=core.regional_allocation(data);mass=np.array([u['paperBalancedMass']for u in data['units']]);F,flow=core.source_balanced_flow(W,mass);C=np.asarray((H.T@F@H).todense());assert connected_components(sparse.csr_matrix(C),directed=False)[0]==1, "Disconnected C requires separate-component charts";Y=full_latent(C);D=squareform(pdist(Y));baseline=project(Y[:,:2]);before=core.distance_diagnostics(D,baseline)
    fits=[core.fit_stress(D,seed)for seed in range(3)];chosen=min(range(3),key=lambda i:fits[i][1]);fitted=orient(fits[chosen][0]);after=core.distance_diagnostics(D,fitted)
    # The broad chart contains actual direct scientific-family allocations only.
    broad=[i for i,d in enumerate(ids) if dest[d]['kind']=='region'];broadY=Y[broad];broadX=project(broadY);broad_metrics=core.distance_diagnostics(squareform(pdist(broadY)),broadX)
    all_vectors={d:Y[i]for i,d in enumerate(ids)};unitY=np.asarray(H@Y);support_counts={}
    for did,uids in support['positiveSupport'].items():
        if did in all_vectors:continue
        ix=[lookup[u]for u in uids if u in lookup];support_counts[did]={'represented':len(ix),'total':len(uids)}
        if ix and len(ix)==len(uids):all_vectors[did]=np.average(unitY[ix],axis=0,weights=mass[ix])
    adjacency=defaultdict(set)
    for r in support['organizationalRoutes']:adjacency[r['source']].add(r['target'])
    local=[];local_points=[]
    for d in [ids[i]for i in broad]:
        requested=[d]+sorted(adjacency[d]);members=[x for x in requested if x in all_vectors]
        if len(members)<2:continue
        target=np.array([all_vectors[x]for x in members]);X=project(target);metrics=core.distance_diagnostics(squareform(pdist(target)),X)
        local.append({'entryDestinationId':d,'requested':len(requested),'represented':len(members),'unplottedIds':[x for x in requested if x not in all_vectors],**metrics})
        local_points.append({'entryDestinationId':d,'nodes':[{'destinationId':id,'x':float(x[0]),'y':float(x[1]),'basis':'direct_home'if id in ids else'complete_positive_support_zero_mass'}for id,x in zip(members,X)]})
    # Sparse display edges preserve the complete numerical C separately.
    degree=C.sum(axis=1);off=C.copy();np.fill_diagonal(off,0);score=off/np.sqrt(degree[:,None]*degree[None,:]);pairs=set()
    for i in range(len(ids)):
        for j in np.argsort(score[i])[-8:]:
            if score[i,j]>0:pairs.add(tuple(sorted((i,int(j)))))
    retained=sum(2*C[i,j]for i,j in pairs);sparse_edges=[{'source':ids[i],'target':ids[j],'kind':'geometric_affinity','weight':float(C[i,j]),'normalizedWeight':float(score[i,j])}for i,j in sorted(pairs)]
    # Reviewed uses_method source-object endpoints map exactly to browser methods.
    # The subsequent Q association is explicitly same-paper retrieval context.
    methods=[json.loads(x)for x in (a.reference_root/'geometry-minilm-method/units.jsonl').read_text().splitlines()];mi={m['unit_id']:i for i,m in enumerate(methods)};by_paper=defaultdict(list)
    for j,m in enumerate(methods):by_paper[m['paper_id']].append(j)
    rr=[];cc=[];vv=[]
    for i,u in enumerate(data['units']):
        js=by_paper[u['paperId']];den=sum(methods[j]['mass']for j in js)
        for j in js:rr.append(i);cc.append(j);vv.append(methods[j]['mass']/den)
    B=sparse.csr_matrix((vv,(rr,cc)),shape=(len(data['units']),len(methods)))
    used=[];held=[];rrow=[];rcol=[];rval=[]
    for id,r in methodmap['routes'].items():
        if r['type']!='uses_method' or not r['bothEndpointsRepresented']:continue
        assert r['status']=='accepted_relation' and not r['promotionWithheld']
        for uid in r['sourceMethodUnitIds']+r['targetMethodUnitIds']:assert uid in mi and methods[mi[uid]]['text_sha256']==methodmap['units'][uid]['textSha256']
        (held if int(hashlib.sha256(id.encode()).hexdigest()[:8],16)%3==0 else used).append(id)
        if id in held:continue
        weight=1/(len(r['sourceMethodUnitIds'])*len(r['targetMethodUnitIds']))
        for u in r['sourceMethodUnitIds']:
            for v in r['targetMethodUnitIds']:rrow.extend([mi[u],mi[v]]);rcol.extend([mi[v],mi[u]]);rval.extend([weight,weight])
    R=sparse.csr_matrix((rval,(rrow,rcol)),shape=(len(methods),len(methods)));K=(B@R@B.T).tocsr();K.setdiag(0);K.eliminate_zeros();w=W.copy();w.setdiag(0);wd=np.asarray(w.sum(axis=1)).ravel();kd=np.asarray(K.sum(axis=1)).ravel();rate=np.divide(wd,kd,out=np.zeros_like(wd),where=kd>0);coo=K.tocoo();addition=sparse.csr_matrix((.1*coo.data*np.minimum(rate[coo.row],rate[coo.col]),(coo.row,coo.col)),shape=W.shape);aug=W+addition
    row_fraction=np.divide(np.asarray(addition.sum(axis=1)).ravel(),wd,out=np.zeros_like(wd),where=wd>0);assert row_fraction.max()<=.10000001
    AF,_=core.source_balanced_flow(aug,mass);AC=np.asarray((H.T@AF@H).todense());by_question_paper=defaultdict(list)
    for i,u in enumerate(data['units']):by_question_paper[u['paperId']].append(i)
    def ranks(graph,id):
        r=methodmap['routes'][id];sources={methodmap['units'][u]['paperId']for u in r['sourceMethodUnitIds']};targets={methodmap['units'][u]['paperId']for u in r['targetMethodUnitIds']};out=[]
        for sp in sources:
            for tp in targets:
                for i in by_question_paper[sp]:
                    row=graph.getrow(i).toarray().ravel();row[i]=-np.inf
                    for j in by_question_paper[tp]:
                        if i==j:continue
                        out.append({'source':data['units'][i]['unitId'],'target':data['units'][j]['unitId'],'rank':int(np.sum(row>row[j])+1),'weight':float(row[j])})
        return out
    evaluations=[]
    for id in used+held:
        q0,q1=ranks(W,id),ranks(aug,id);assert len(q0)==len(q1)
        evaluations.append({'relationId':id,'partition':'development_injected'if id in used else'withheld_not_injected','representedQuestionPairs':len(q0),'baseline':q0,'coupled':q1})
    controls=[];rng=np.random.default_rng(25025)
    for i in rng.choice(len(data['units']),size=min(200,len(data['units'])),replace=False):
        old=set(W.getrow(i).indices[np.argsort(W.getrow(i).data)[-10:]]);new=set(aug.getrow(i).indices[np.argsort(aug.getrow(i).data)[-10:]]);controls.append(len(old&new)/max(len(old),1))
    coupling={'policy':'Fixedeta0.1symmetric incident-budget addition from independently reviewed uses_method only; exact method endpoints followed by explicitly contextual same-paper Q projection. No implication or Q applicability.','developmentRelations':used,'withheldRelations':held,'unmappedControl':'scientific:production-020 remains absent from R if endpoints unmapped','affectedQuestionVertices':int(np.sum(row_fraction>0)),'addedIncidentFraction':percentile(row_fraction[row_fraction>0].tolist()),'coarseFlowRelativeL1Change':float(np.sum(abs(AC-C))/C.sum()),'randomQuestionTop10Retention':float(np.mean(controls)),'relationEvaluations':evaluations,'interpretation':'Injected-route rank gains are constraint fit, not generalization. Withheld pairs and unrelated row retention govern whether any exploratory coupling gain is defensible.'}
    broad_sources=set(u for i in broad for u in dest[ids[i]]['memberIds']);summary={'status':'complete','membershipSha256':h(a.input),'sourceCount':len(data['units']),'atomCount':len(ids),'paperMassPolicy':data['coverage']['paperMassPolicy'],'globalTwoModes':before,'globalMetricFit':after,'chosenGlobalInitialization':chosen,'globalIterations':fits[chosen][2],'broadOverview':{'nodes':len(broad),'directSourceCoverage':len(broad_sources),'fractionOfCohort':len(broad_sources)/len(data['units']),**broad_metrics,'limitation':'Direct broad residual-family membership only; this is not a complete all-source parent closure.'},'localDetail':{'charts':len(local),'representedNodeCounts':percentile([r['represented']for r in local]),'stress':percentile([r['distanceStress']for r in local]),'neighborRecall':percentile([r['topFiveNeighborRecall']for r in local if r['topFiveNeighborRecall']is not None]),'limitations':'Each local chart has its own axes. Only actual direct homes or fully represented positive-support centroids are plotted; the latter add no H mass.'},'sparseDisplay':{'edges':len(pairs),'fullOffDiagonalPairs':int(np.sum(off>0)//2),'retainedOffDiagonalFlowFraction':float(retained/max(off.sum(),1e-30)),'fullFlowRetainedNumerically':True},'methodCoupling':coupling,'referenceSelection':selection,'referenceFiles':files,'runtimeSeconds':time.time()-START}
    core.dump(a.out/'summary.json',summary);core.dump(a.out/'local-chart-diagnostics.json',local);core.dump(a.out/'local-charts.json',local_points);core.dump(a.out/'broad-chart.json',{'nodes':[{'destinationId':ids[i],'x':float(x[0]),'y':float(x[1])}for i,x in zip(broad,broadX)],'coverage':summary['broadOverview']});core.dump(a.out/'global-metric-chart.json',{'nodes':[{'destinationId':id,'x':float(x[0]),'y':float(x[1])}for id,x in zip(ids,fitted)],'edges':sparse_edges,'diagnostics':summary['globalMetricFit']});np.savez_compressed(a.out/'complete-flows.npz',baseline=C,coupled=AC);core.dump(a.out/'atom-ids.json',ids)
    core.dump(a.out/'manifest.json',{'schemaVersion':'q025-one-bounded-comparison/1','inputs':{'geometry':h(a.input),'support':h(a.support),'reviewedMethodRoutes':h(a.routes),'script':h(__file__),'core':h(core.__file__)},'files':{p.name:{'sha256':h(p),'bytes':p.stat().st_size}for p in sorted(a.out.iterdir())if p.is_file()}})
    print(json.dumps({k:summary[k]for k in ['status','sourceCount','atomCount','globalTwoModes','globalMetricFit','broadOverview','localDetail','sparseDisplay','runtimeSeconds']},indent=2),flush=True)
START=time.time()
if __name__=='__main__':main()
