#!/usr/bin/env python3
"""Add Q/M unit lookup buckets; reuse all original compressed paper bytes."""
import argparse, gzip, hashlib, json
from collections import Counter, defaultdict
from pathlib import Path
from context_override import POLICY, resolve_override

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''): h.update(b)
    return h.hexdigest()
def write(p,x):
    Path(p).write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
def desc(p): return {'path':p.name,'sha256':sha(p),'bytes':p.stat().st_size}

def main():
    p=argparse.ArgumentParser();p.add_argument('--pack',type=Path,required=True);p.add_argument('--units',type=Path,required=True);p.add_argument('--ledger',type=Path,required=True);p.add_argument('--full-edges',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    units=json.loads(a.units.read_text());old=json.loads((a.pack/'manifest.json').read_text());oldindex=json.loads((a.pack/'source-context-index.json').read_text());by_paper=defaultdict(list)
    for u in units:by_paper[u['paperId']].append(u)
    assert len(units)==26410 and len({u['id'] for u in units})==len(units)
    methods=[u for u in units if u['lens']=='method'];node_units=defaultdict(list)
    for u in methods:
        for n in u['sourceNodeIds']:node_units[n].append(u['id'])
    full_incident=defaultdict(set); full_edge_metadata={}; all_edge_census=Counter()
    with gzip.open(a.full_edges,'rt') as f:
        for line in f:
            e=json.loads(line);all_edge_census[(e['type'],e['semantic_status'])]+=1
            if e['type'] in ['contains','literal_identifier_mention'] or e['semantic_status']=='unvalidated_mention':continue
            for endpoint in [e['source'],e['target']]:
                for uid in node_units.get(endpoint,[]):full_incident[uid].add(e['id']);full_edge_metadata[e['id']]={'type':e['type'],'semanticStatus':e['semantic_status']}
    buckets=defaultdict(lambda:{'units':{},'shards':{}});counts=Counter();fixtures={};method_audit=[];exported_scientific={};missing=[];paper_summaries={};all_exported_nodes=set();all_unit_ids=set();missing_edge_ids=set();exported_edge_ids=set()
    for name,fd in sorted(old['files'].items()):
        paper=fd['paperId'];path=a.pack/name;assert sha(path)==fd['sha256'];raw=gzip.decompress(path.read_bytes());assert len(raw)==fd['uncompressedBytes'];payload=json.loads(raw);objects={o['id']:o for o in payload['sourceObjects']};all_exported_nodes.update(objects)
        sd={k:fd[k] for k in ['path','sha256','encoding','uncompressedBytes']};pc=Counter()
        for u in by_paper[paper]:
            uid=u['id'];all_unit_ids.add(uid);prefix=uid.split(':',1)[1][:2];entry={'shardId':paper,'lens':u['lens']}
            if u['lens']=='method':
                entry['attachmentOverride']={'policy':POLICY,'anchorObjectIds':u['sourceNodeIds'],'sourceRecordIds':u['sourceRecordIds']}
                resolved=resolve_override(uid,entry,payload);c=resolved['coverage'];missing.extend({'unitId':uid,'objectId':n} for n in resolved['missingAnchorIds']);direct=next((x for x in resolved['sourceAttachments'] if x['scope']=='direct_record_relation'),{'relationIds':[]});exported=set(direct['relationIds']);local_exported={r for r in exported if not r.startswith('scientific:')};full=full_incident.get(uid,set());assert local_exported<=full,(uid,local_exported-full)
                for r in payload['sourceRelations']:
                    if r['id'] in exported and r['semanticStatus']=='reviewed_scoped':exported_scientific[r['id']]=r
                missing_edge_ids.update(full-local_exported);exported_edge_ids.update(local_exported)
                stats={'unitId':uid,'paperId':paper,'anchorObjectIds':u['sourceNodeIds'],'missingAnchorIds':resolved['missingAnchorIds'],'exportedLocalIncidentRelationCount':len(local_exported),'fullLocalIncidentRelationCount':len(full),'unexportedLocalIncidentRelationCount':len(full-local_exported),'directReviewedRelationCount':c['directReviewedRelationCount']};method_audit.append(stats)
                for k,value in [('methodUnits',True),('methodUnitsWithMissingAnchors',bool(resolved['missingAnchorIds'])),('methodUnitsWithExportedLocalRelations',bool(local_exported)),('methodUnitsWithFullLocalRelations',bool(full)),('methodUnitsWithUnexportedLocalRelations',bool(full-local_exported)),('methodUnitsWithReviewedRelations',bool(c['directReviewedRelationCount'])),('methodUnitsWithWindowContext',bool(c['windowRecordCount']))]:counts[k]+=int(value);pc[k]+=int(value)
                # Small fixtures preserve real IDs/record provenance, with a deliberately
                # synthetic missing-anchor case. They are not complete source packets.
                for kind,condition in [('direct_reviewed',c['directReviewedRelationCount']>0),('shared_window',c['windowRecordCount']>0),('whole_paper',c['windowRecordCount']==0)]:
                    if not condition or kind in fixtures:continue
                    anchors=set(u['sourceNodeIds']);rel=next((r for r in payload['sourceRelations'] if r['id'] in exported and r['semanticStatus']=='reviewed_scoped'),None);ids=set(anchors)
                    if rel:ids.update([rel['source'],rel['target']])
                    for at in resolved['sourceAttachments']:
                        if at['scope']!='direct_record_relation':ids.update(at['objectIds'][:2])
                    small={'sourceObjects':[objects[n] for n in sorted(ids) if n in objects],'sourceRelations':[rel] if rel else [],'sourceAssessments':[]}
                    fixtures[kind]={'unitId':uid,'descriptor':entry,'payload':small,'expected':resolve_override(uid,entry,small),'fixtureScope':'Representative real source IDs and provenance; deliberately reduced payload.'}
            else:
                assert oldindex['units'][uid]['sha256']==sd['sha256'];counts['questionUnits']+=1;pc['questionUnits']+=1
            buckets[prefix]['units'][uid]=entry;buckets[prefix]['shards'][paper]=sd
        paper_summaries[paper]=dict(pc)
    assert all_unit_ids=={u['id'] for u in units}
    fixture=fixtures['whole_paper'];md=json.loads(json.dumps(fixture['descriptor']));md['attachmentOverride']['anchorObjectIds']=['obj:fixture:missing:anchor'];fixtures['missing_anchor']={'unitId':fixture['unitId'],'descriptor':md,'payload':fixture['payload'],'expected':resolve_override(fixture['unitId'],md,fixture['payload']),'fixtureScope':'Synthetic missing-anchor ID with real paper context and record fallback; absence must remain explicit.'}
    ledger=json.loads(a.ledger.read_text());routes=[]
    for r in ledger['records']:
        if not r['admittedScientificEdge']:continue
        endpoints=[node_units.get(n,[]) for n in r['nodeIds']]
        if not any(endpoints):continue
        edge=exported_scientific['scientific:'+r['taskId']]
        routes.append({'sourceRelationId':edge['id'],'sourceObjectId':edge['source'],'targetObjectId':edge['target'],'sourceMethodUnitIds':node_units.get(edge['source'],[]),'targetMethodUnitIds':node_units.get(edge['target'],[]),'type':edge['type'],'directed':edge['directed'],'receiptSha256':r['receiptSha256'],'bothEndpointsRepresented':all(endpoints),'questionEquivalenceInferred':False})
    assert len(routes)==51 and sum(r['bothEndpointsRepresented'] for r in routes)==50
    unit_shards={}
    for prefix,b in sorted(buckets.items()):
        f=a.out/('unit-index-'+prefix+'.json');write(f,dict(schemaVersion='1.0.0',kind='eigenquestions-source-context-unit-index',**b));unit_shards[prefix]=desc(f)
    omitted=Counter((full_edge_metadata[r]['type'],full_edge_metadata[r]['semanticStatus']) for r in missing_edge_ids)
    coverage={'description':'Lazy source context for all 26,410 question and method entries. Exact method anchors and exported incident edges are distinct from window/paper context. Existing payloads are reused; some source-local method edges are not in this export. Missing exported relations never establish scientific absence.','unitCount':len(units),**dict(counts),'uniqueExportedMethodLocalEdges':len(exported_edge_ids),'uniqueUnexportedMethodLocalEdges':len(missing_edge_ids),'unexportedMethodLocalEdgeCensus':[{'type':t,'semanticStatus':s,'count':n} for (t,s),n in sorted(omitted.items())],'reviewedRelationsTouchingMethodEntries':len(routes),'reviewedRelationsWithBothMethodEndpoints':sum(r['bothEndpointsRepresented'] for r in routes),'sourcePayloadUnchanged':True,'pdfOrRawPageTextIncluded':False}
    index={'schemaVersion':'1.0.0','kind':'eigenquestions-source-context-index','policyVersion':'q025-qm-context-index-v2','coverage':coverage,'unitIndex':{'kind':'unit-hash-prefix','prefixLength':2,'prefixSource':'hexadecimal suffix after unit:','shards':unit_shards},'attachmentOverridePolicies':{POLICY:'Exact incident edges only for direct scope; numbered wN extraction windows require exact paper/record/source-unit identity. Whole-paper records remain paper context.'}}
    ip=a.out/'source-context-index-v2.json';write(ip,index)
    write(a.out/'fixtures.json',{'schemaVersion':'q025-method-attachment-fixtures/1','policy':POLICY,'cases':fixtures})
    write(a.out/'method-relation-routes.json',routes)
    write(a.out/'method-coverage-audit.json',{'coverage':coverage,'fullSourceEdgeCensus':[{'type':t,'semanticStatus':s,'count':n} for (t,s),n in sorted(all_edge_census.items())],'missingAnchors':missing,'methods':method_audit,'papers':paper_summaries})
    report={'schemaVersion':'q025-source-context-index-export/2','sourceContextIndex':desc(ip),'coverage':coverage,'bucketCount':len(unit_shards),'totalIndexBucketBytes':sum(x['bytes'] for x in unit_shards.values()),'maxIndexBucketBytes':max(x['bytes'] for x in unit_shards.values()),'reusedPayloadCount':len(old['files']),'reusedPayloadBytes':old['totalShardBytes'],'reusedPayloadManifestSha256':sha(a.pack/'manifest.json'),'invariants':{'all26410UnitsIndexed':True,'originalQuestionDescriptorsPreservedByReference':True,'everyPayloadHashVerified':True,'all51MethodReviewedRoutesPresent':True,'zeroQuestionEquivalenceInferences':True},'provenance':{'scriptSha256':sha(__file__),'resolverSha256':sha(Path(__file__).with_name('context_override.py')),'unitsMetadataSha256':sha(a.units),'ledgerSha256':sha(a.ledger),'fullSourceEdgesSha256':sha(a.full_edges)},'files':{p.name:desc(p) for p in sorted(a.out.glob('*.json'))}}
    write(a.out/'manifest.json',report);print(json.dumps({k:v for k,v in report.items() if k!='files'},indent=2),flush=True)

if __name__=='__main__':main()
