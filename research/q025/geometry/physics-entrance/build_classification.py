#!/usr/bin/env python3
"""Low-resolution classification chart from pinned APS vocabulary memberships."""
import argparse,gzip,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial.distance import pdist,squareform

P='https://physh.org/rdf/2018/01/01/core#';S='http://www.w3.org/2004/02/skos/core#'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def vals(x,k):return [v['@id'] for v in x.get(k,[]) if '@id' in v]
def texts(x,k):return [v['@value'] for v in x.get(k,[]) if '@value' in v]
def label(x):return texts(x,P+'prefLabel')[0]
def cid(x):return 'classification:'+x.rsplit('/',1)[-1]
def deprecated(x):return any(v.get('@value') is True for v in x.get(P+'deprecated',[]))

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--manifest',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    data=json.loads(gzip.decompress(a.input.read_bytes()));D={x['@id']:x for x in data};provenance=json.loads(a.manifest.read_text());assert provenance['compressedSha256']==sha(a.input)
    disciplines=sorted([x['@id'] for x in data if P+'Discipline' in x['@type'] and not deprecated(x) and vals(x,P+'hasConcept')],key=lambda k:label(D[k]));assert len(disciplines)==17
    research='https://doi.org/10.29172/bdb1ef91-b776-4e36-8f8f-3e93666bac1e'
    roots={d:sorted([c for c in vals(D[d],P+'hasConcept') if research in vals(D[c],P+'inFacet') and not deprecated(D[c])]) for d in disciplines};areas=sorted(set(c for cs in roots.values() for c in cs));assert len(areas)==194
    children=defaultdict(set);broader=set();related=set()
    for x in data:
        for parent in vals(x,S+'broader'):children[parent].add(x['@id']);broader.add((parent,x['@id']))
        for child in vals(x,S+'narrower'):children[x['@id']].add(child);broader.add((x['@id'],child))
        for other in vals(x,S+'related'):related.add(tuple(sorted((x['@id'],other))))
    def descendants(root):
        seen=set();stack=[root]
        while stack:
            node=stack.pop()
            if node in seen:continue
            assert node in D,node
            seen.add(node);stack.extend(children[node]-seen)
        return {n for n in seen if not deprecated(D[n]) and P+'Facet' not in D[n]['@type']}
    member={c:descendants(c) for c in areas}
    for d in disciplines:member[d]=set().union(*(member[c] for c in roots[d]))
    ids=disciplines+areas;universe=sorted(set().union(*(member[c] for c in ids)));row={k:i for i,k in enumerate(universe)};H=np.zeros((len(universe),len(ids)))
    for j,k in enumerate(ids):H[[row[n] for n in member[k]],j]=1
    norms=np.linalg.norm(H,axis=0);F=H/np.maximum(norms,1e-30);W=F.T@F;np.fill_diagonal(W,0)
    components,assignment=connected_components(csr_matrix(W>0),directed=False);coords=np.zeros((len(ids),2));diagnostics=[];packing=[]
    groups=sorted([np.where(assignment==g)[0] for g in range(components)],key=lambda v:(-len(v),ids[int(v[0])]))
    columns=math.ceil(math.sqrt(components))
    for number,idx in enumerate(groups):
        local=W[np.ix_(idx,idx)];degree=local.sum(axis=1);n=len(idx)
        if n>1:
            A=local/np.sqrt(np.maximum(degree[:,None]*degree[None,:],1e-30));e,U=np.linalg.eigh((np.eye(n)+A)/2);order=np.argsort(e)[::-1];e=e[order];U=U[:,order];psi=U/np.sqrt(np.maximum(degree[:,None],1e-30));full=psi[:,1:]*e[None,1:]
            xy=np.zeros((n,2));xy[:,:min(2,n-1)]=full[:,:min(2,n-1)]
            for dim in range(2):
                pivot=int(np.argmax(np.abs(xy[:,dim])))
                if xy[pivot,dim]<0:xy[:,dim]*=-1
            target=pdist(full);projected=pdist(xy);scale=float(np.dot(target,projected)/max(np.dot(projected,projected),1e-30));stress=float(np.linalg.norm(target-scale*projected)/max(np.linalg.norm(target),1e-30));k=min(5,n-1);df=squareform(target);dx=squareform(projected);np.fill_diagonal(df,np.inf);np.fill_diagonal(dx,np.inf);recall=float(np.mean([len(set(np.argsort(df[i])[:k])&set(np.argsort(dx[i])[:k]))/k for i in range(n)]));retained=float(np.sum(e[1:3]**2)/max(np.sum(e[1:]**2),1e-30))
            xy-=xy.mean(axis=0);radius=max(np.max(np.linalg.norm(xy,axis=1)),1e-30);xy/=radius
            diagnostic={'component':number,'nodeCount':n,'leadingLazyEigenvalues':e[:6].tolist(),'twoDimensionalDistanceStressAfterUniformFit':stress,'topFiveDiffusionNeighborRecall':recall,'twoModeSpectralEnergyFraction':retained}
        else:xy=np.zeros((1,2));diagnostic={'component':number,'nodeCount':1,'twoDimensionalDistanceStressAfterUniformFit':None,'topFiveDiffusionNeighborRecall':None}
        offset=np.array([3.0*(number%columns),3.0*(number//columns)]);coords[idx]=xy+offset;diagnostics.append(diagnostic);packing.append({'component':number,'offset':offset.tolist(),'nodeIds':[cid(ids[int(i)]) for i in idx],'interComponentDistancesMeaningful':False})
    edges=[{'source':cid(d),'target':cid(c),'kind':'classification','predicate':P+'hasConcept','directed':True} for d in disciplines for c in roots[d]]
    destinations=[{'id':'classification:physics','kind':'region','title':'Physics','metadataOnly':True,'scope':{'description':'A broad classification entrance. Detailed source-backed paper coverage is a separate chart reached through an explicit portal.'},'classificationChildIds':[cid(d) for d in disciplines],'memberIds':[]}]
    for i,k in enumerate(ids):
        is_d=k in disciplines;parents=['classification:physics'] if is_d else [cid(d) for d in disciplines if k in roots[d]]
        destinations.append({'id':cid(k),'kind':'region','title':label(D[k]),'metadataOnly':True,'classificationKind':'discipline' if is_d else 'research_area','sourceUri':k,'scope':{'description':'Classification vocabulary; no empirical paper coverage, scientific implication or question identity is established by this placement.','includes':texts(D[k],S+'scopeNote')},'classificationParentIds':parents,'classificationChildIds':[cid(c) for c in roots[k]] if is_d else [],'classificationConceptCount':len(member[k]),'memberIds':[],'provenance':{'source':'APS classification vocabulary','sourceTag':provenance['tag'],'sourceCommit':provenance['commit'],'sourceSha256':provenance['compressedSha256'],'sourceUri':k}})
    landmarks=[k for k in ids if label(D[k]) in ['Particles & Fields','Gravitation, Cosmology & Astrophysics','Strings & branes']]
    orientation={'layoutId':'physics-classification-v2.8.0-shared-descendants-v1','kind':'classification_graph','entryDestinationId':'classification:physics','frontierDestinationIds':[cid(d) for d in disciplines],'nodes':[{'destinationId':cid(k),'x':float(coords[i,0]),'y':float(coords[i,1]),'depth':0 if k in disciplines else 1,'mass':len(member[k]),'component':next(j for j,g in enumerate(groups) if i in g)} for i,k in enumerate(ids)],'edges':edges,'portals':[],'provenance':{'sourceTaxonomy':provenance,'scriptSha256':sha(__file__),'operator':'lazy random walk on cosine of binary descendant-concept memberships; diagonal removed before laziness','membershipConstruction':'Research Areas concepts directly assigned to each active discipline; SKOS narrower/broader descendant closure; no embeddings or paper counts.','diffusionTime':1,'modes':2,'coordinateTransform':'Eigenvector signs fixed by largest absolute entry; each disconnected component centered and uniformly scaled, then packed on a deterministic grid.'},'diagnostics':{'inputEntityCount':len(data),'activeDisciplineCount':len(disciplines),'directResearchAreaCount':len(areas),'descendantConceptUniverseCount':len(universe),'classificationEdgeCount':len(edges),'derivedPositiveAffinityPairs':int(np.count_nonzero(W>0)//2),'connectedComponents':components,'components':diagnostics,'packing':packing},'limitations':['Vocabulary/classification overview, not empirical all-physics paper geometry.','Broad/narrow and shared-concept relations do not imply scientific dependence, truth or question equivalence.','Two dimensions distort the recorded membership geometry; diagnostics report within-component loss.','Between disconnected components, grid spacing is display packing only.','Coordinates cannot be compared with the separate Swampland source-geometry chart.','Discipline concept counts reflect taxonomy granularity, not research volume or importance.']}
    taxonomy=[]
    for x in data:
        taxonomy.append({'id':x['@id'],'label':label(x),'types':x['@type'],'deprecated':deprecated(x),'broader':vals(x,S+'broader'),'narrower':vals(x,S+'narrower'),'related':vals(x,S+'related'),'inDiscipline':vals(x,P+'inDiscipline'),'inFacet':vals(x,P+'inFacet'),'scopeNotes':texts(x,S+'scopeNote'),'alternateLabels':texts(x,S+'altLabel')})
    write(a.out/'orientation.json',orientation);write(a.out/'destinations.json',destinations);write(a.out/'taxonomy.json',taxonomy);write(a.out/'portal-nominations.json',[{'destinationId':cid(k),'title':label(D[k]),'target':'destination','entryBinding':'arxiv-hep-th-curator-landmark-or-accepted-detail-root','basis':'Curator collection navigation, not an APS taxonomy equivalence or scientific implication.','requiresAssemblyBinding':True} for k in landmarks]);write(a.out/'memberships.json',{cid(k):sorted(member[k]) for k in ids})
    write(a.out/'manifest.json',{'schemaVersion':'q025-physics-classification-overview/1','scope':'Low-resolution vocabulary/classification chart; separate from paper geometry.','source':provenance,'diagnostics':orientation['diagnostics'],'files':{p.name:{'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(a.out.glob('*.json'))}})
    print(json.dumps(orientation['diagnostics'],indent=2),flush=True)

if __name__=='__main__':main()
