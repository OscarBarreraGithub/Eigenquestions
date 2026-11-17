#!/usr/bin/env python3
"""Numerical invariants on a synthetic overlap/rare-paper/isolated-source fixture."""
import json,tempfile
from pathlib import Path
import numpy as np
from scipy import sparse
from overview import source_balanced_flow,regional_allocation,compute,dump,sha

W=sparse.csr_matrix([[0,2,1,0],[2,0,1,0],[1,1,0,0],[0,0,0,0]],dtype=float)
m=np.array([.5,.5,1,1]);F,report=source_balanced_flow(W,m)
assert np.allclose(F.sum(axis=1).A.ravel(),m)
assert np.allclose(F.toarray(),F.T.toarray())
assert F[3,3]==1 and report['isolatedSourceCount']==1
data={'units':[{'unitId':str(i),'paperId':'p'+str(0 if i<2 else i),'paperBalancedMass':float(m[i])} for i in range(4)],'allocations':[{'unitId':'0','destinationId':'fine','weight':1,'placementStatus':'accepted'},{'unitId':'1','destinationId':'a','weight':.5,'placementStatus':'accepted'},{'unitId':'1','destinationId':'b','weight':.5,'placementStatus':'provisional'},{'unitId':'2','destinationId':'b','weight':1,'placementStatus':'accepted'},{'unitId':'3','destinationId':'root','weight':1,'placementStatus':'unresolved'}],'destinations':[{'id':'root','kind':'region','parentIds':[],'memberIds':['0','1','2','3']},{'id':'a','kind':'region','parentIds':['root'],'memberIds':['0','1']},{'id':'b','kind':'region','parentIds':['root'],'memberIds':['1','2']},{'id':'fine','kind':'question','parentIds':['a'],'memberIds':['0']}],'baseDestinationIds':[]}
H,ids,_,_=regional_allocation(data);assert np.allclose(H.sum(axis=1).A.ravel(),1)
assert set(ids)=={'a','b','root'}
r=compute(data,W);assert np.isclose(r['coarseFlow'].sum(),3)
assert {n['destinationId'] for n in r['nodes']}=={'a','b','root'}
assert all(np.isfinite(n['x']) and np.isfinite(n['y']) for n in r['nodes'])
assert next(n for n in r['nodes'] if n['destinationId']=='root')['spansDisconnectedComponents']
assert 'displayedRegionCentroids' in r['diagnostics']['components'][0]
# Five connected catchments with overlap: shown centroids must be evaluated
# separately from hidden atom coordinates, since the two generally differ.
W2=sparse.csr_matrix(np.array([[0,2,1,0,0,.2],[2,0,2,0,0,0],[1,2,0,1,0,0],[0,0,1,0,2,0],[0,0,0,2,0,1],[.2,0,0,0,1,0]],float))
d2={'units':[{'unitId':str(i),'paperId':'paper'+str(i),'paperBalancedMass':1.} for i in range(6)],'allocations':[{'unitId':str(i),'destinationId':home,'weight':weight,'placementStatus':'accepted'} for i,home,weight in [(0,'a',1),(1,'a',.5),(1,'b',.5),(2,'b',1),(3,'c',1),(4,'d',1),(5,'e',1)]],'destinations':[{'id':home,'kind':'region','parentIds':[],'memberIds':members} for home,members in [('a',['0','1']),('b',['1','2']),('c',['3']),('d',['4']),('e',['5'])]],'baseDestinationIds':[]}
r2=compute(d2,W2);c=r2['diagnostics']['components'][0]
assert abs(c['atomProjection']['distanceStress']-c['displayedRegionCentroids']['distanceStress'])>1e-8
with tempfile.TemporaryDirectory() as d:
    p=Path(d)/'complete.json';dump(p,r['diagnostics']);assert len(sha(p))==64;assert json.loads(p.read_text())['expectedPaperMass']==3
print(json.dumps({'syntheticOnly':True,'allNumericalInvariantsPass':True,'diagnostics':r['diagnostics'],'overlapDisplayedFidelity':r2['diagnostics']},indent=2))
