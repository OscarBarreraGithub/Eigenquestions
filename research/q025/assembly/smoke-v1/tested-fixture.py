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
with tempfile.TemporaryDirectory() as d:
    p=Path(d)/'complete.json';dump(p,r['diagnostics']);assert len(sha(p))==64;assert json.loads(p.read_text())['expectedPaperMass']==3
print(json.dumps({'syntheticOnly':True,'allNumericalInvariantsPass':True,'diagnostics':r['diagnostics']},indent=2))
