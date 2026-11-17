#!/usr/bin/env python3
"""Actual approved-H geometry plus explicitly massless positive-target supports."""
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import overview as core

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--support',type=Path,required=True);p.add_argument('--reference-root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    data=json.loads(a.input.read_text());support=json.loads(a.support.read_text());a.out.mkdir(parents=True,exist_ok=True)
    assert support['geometryInputSha256']==core.sha(a.input)
    W,files,selection=core.load_reference(a.reference_root,data['units'],True)
    result=core.compute(data,W)
    lookup={u['unitId']:i for i,u in enumerate(data['units'])};m=np.array([u['paperBalancedMass'] for u in data['units']]);mass_before=float(result['coarseFlow'].sum())
    accepted={d['id'] for d in data['destinations']};plotted={n['destinationId'] for n in result['nodes']};support_rows=[]
    for d in support['questions']:
        assert d['destinationId'] in accepted and d['destinationId'] not in plotted
        ids=sorted(set(d['unitIds']));rows=[lookup[u] for u in ids if u in lookup]
        status='all_support_sources_allocated' if len(rows)==len(ids) else 'partially_allocated_support' if rows else 'unallocated_support'
        record={'destinationId':d['destinationId'],'status':status,'supportSourceCount':len(ids),'representedSupportSourceCount':len(rows),'supportUnitIdsSha256':hashlib.sha256('\n'.join(ids).encode()).hexdigest(),'roles':['addresses','instantiates','specializes'],'methodComparisonBoundaryExcluded':True,'addedAllocationMass':0}
        if rows:
            point=np.average(result['unitCoordinates'][rows],axis=0,weights=m[rows]);record['diagnosticCentroid']={'x':float(point[0]),'y':float(point[1])}
        if status=='all_support_sources_allocated':
            result['nodes'].append({'destinationId':d['destinationId'],**record['diagnosticCentroid'],'mass':0.,'directAllocationMass':0.,'scopeKind':'question','depth':0,'sourceUnitCount':len(rows),'supportOnly':True,'coordinateBasis':'admitted_positive_target_support_centroid','supportCoverage':record,'coordinateMeaning':'Source-balanced centroid of exact admitted addresses/instantiates/specializes supports. This is an orientation coordinate, not membership, organizational allocation, equivalence or method applicability. The scope adds no mass to H or C.'})
            record['plotted']=True
        else:record['plotted']=False
        support_rows.append(record)
    assert float(result['coarseFlow'].sum())==mass_before
    result['diagnostics']['referenceSelection']=selection
    result['diagnostics']['supportPositions']={'policy':'Plot only complete support sets in this partial candidate; partial centroids remain diagnostics.','questions':support_rows,'massAddedToHOrC':0,'positiveRoleOnly':True,'supportOnlyNodeCount':sum(r['plotted'] for r in support_rows),'partialSupportCentroidCount':sum(r['status']=='partially_allocated_support' for r in support_rows),'noRepresentedSupportCount':sum(r['status']=='unallocated_support' for r in support_rows)}
    overview={'layoutId':'approved-home-candidate-with-positive-support-v1','kind':'diffusion_chart','membershipSha256':core.sha(a.input),'supportInputSha256':core.sha(a.support),'sourceCandidateId':data['originalCandidate']['candidateId'],'nodes':result['nodes'],'edges':result['edges'],'diagnostics':result['diagnostics'],'provenance':{'operator':'Pinned multiview affinity; Metropolis source-balanced flow F; explicit approved H; C=H^T F H; lazy diffusion coordinates','retrievalLayers':{'minilmQuestion':.5,'qwenQuestion':.3,'samePaperMethodContext':.2},'referenceInputs':files,'scriptSha256':core.sha(__file__),'coreScriptSha256':core.sha(core.__file__),'sourceSupportSeparateFromAllocation':True},'limitations':['Partial5,765-source candidate, not a complete atlas or pre-holdout freeze.','Source mass is renormalized within the explicitly admitted cohort; these are cohort diagnostics, not full-corpus totals.','Positive-target support coordinates carry zero H/C mass and do not supply scientific edges. Incomplete support sets are not plotted.','Native source science and destination navigation are separate from retrieval affinity; reviewed method edges are not injected in this baseline.','Coordinates are lossy summaries, not physical distances. Public global navigation/reconciliation remains incomplete.']}
    core.dump(a.out/'overview.json',overview);core.dump(a.out/'diagnostics.json',result['diagnostics']);core.dump(a.out/'atom-ids.json',result['atomIds']);np.savez_compressed(a.out/'coarse-flow.npz',flow=result['coarseFlow']);core.dump(a.out/'manifest.json',{'schemaVersion':'q025-approved-cohort-geometry/1','inputSha256':core.sha(a.input),'supportInputSha256':core.sha(a.support),'files':{x.name:{'sha256':core.sha(x),'bytes':x.stat().st_size} for x in sorted(a.out.iterdir()) if x.is_file()}})
    print(json.dumps({'status':'complete','nodes':len(result['nodes']),'atoms':len(result['atomIds']),'supportNodes':sum(r['plotted'] for r in support_rows),'mass':mass_before,'components':result['diagnostics']['components']},indent=2),flush=True)

if __name__=='__main__':main()
