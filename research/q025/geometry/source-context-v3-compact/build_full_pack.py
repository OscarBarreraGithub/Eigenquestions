#!/usr/bin/env python3
"""Paper-sharded full recorded source graph, with explicitly typed incidence."""
import argparse, gzip, hashlib, json, re
from collections import Counter, defaultdict
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'source-index-v2'))
from context_override import POLICY, resolve_override

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def encode(x):return (json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n').encode()
def write(p,x):Path(p).write_bytes(encode(x))
def desc(p):return {'path':p.name,'sha256':sha(p),'bytes':p.stat().st_size}
def lines(path):
    with gzip.open(path,'rt') as f:
        for line in f:yield json.loads(line)
def refs(ids):return ['source-graph:'+x for x in ids or []]

def main():
    p=argparse.ArgumentParser();p.add_argument('--downloads',type=Path,required=True);p.add_argument('--units',type=Path,required=True);p.add_argument('--ledger',type=Path,required=True);p.add_argument('--old-pack',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    graph_hashes={n:sha(a.downloads/n) for n in ['nodes.jsonl.gz','edges.jsonl.gz','evidence.jsonl.gz']}
    old=json.loads((a.old_pack/'manifest.json').read_text());units=json.loads(a.units.read_text());ledger=json.loads(a.ledger.read_text());paper_units=defaultdict(list);node_units=defaultdict(list)
    for u in units:
        paper_units[u['paperId']].append(u)
        for n in u['sourceNodeIds']:node_units[n].append(u)
    papers=set(paper_units);nodes={};paper_nodes=defaultdict(set);all_node_types=Counter()
    for n in lines(a.downloads/'nodes.jsonl.gz'):
        all_node_types[n['type']]+=1
        o={'id':n['id'],'kind':n['type'],'paperId':n['paper_id'],'text':n.get('text') or n.get('label') or '', 'evidenceRefs':refs(n.get('evidence_ids')),'evidenceScope':n.get('evidence_scope'),'provenance':{'sourceGraphNodeId':n['id'],'sourceSha256':n.get('source_sha256'),'layer':n.get('layer'),'record':n.get('provenance',{}),'certainty':n.get('certainty'),'originalEvidenceIds':n.get('evidence_ids',[])}}
        if n['type']=='paper':
            # Catalog paper.text is the original abstract, not an extracted object.
            # Keep exact identity and lightweight catalog provenance, never repeat
            # abstracts or the large internal per-paper review bookkeeping.
            attributes=n.get('attributes',{});certainty=n.get('certainty',{});science=certainty.get('science_status',{})
            o['text']=n.get('label') or attributes.get('title') or n['paper_id']
            o['catalogMetadata']={'title':o['text'],'year':attributes.get('year'),'version':attributes.get('version'),'landingUrl':attributes.get('landing_url'),'authors':attributes.get('authors',[])}
            o['sourceCoverage']=n.get('coverage')
            o['provenance']['certainty']={k:certainty.get(k) for k in ['catalog_authorship','full_mathematical_certification']}
            o['provenance']['catalogReviewMetadata']={k:science.get(k) for k in ['breadth_available','focused_reconstruction_available','effective_source_fidelity_accepted','mathematical_reproduction_complete']}
            o['provenance']['projection']='Paper catalog identity/title/source coverage; original abstract and verbose review bookkeeping omitted. Exact native node remains pinned by sourceGraphNodeId and source graph file hash.'
        nodes[n['id']]=o;paper_nodes[n['paper_id']].add(n['id'])
    edges={};paper_edges=defaultdict(set);edge_census=Counter();native_edge_count=0
    for e in lines(a.downloads/'edges.jsonl.gz'):
        assert e['source'] in nodes and e['target'] in nodes
        edge_census[(e['type'],e['semantic_status'])]+=1;native_edge_count+=1
        r={'id':e['id'],'source':e['source'],'target':e['target'],'type':e['type'],'directed':True,'semanticStatus':e['semantic_status'],'evidenceRefs':refs(e.get('evidence_ids')),'provenance':{'record':e.get('provenance',{}),'attributes':e.get('attributes',{}),'originalEvidenceIds':e.get('evidence_ids',[])}}
        edges[e['id']]=r
        for paper in {nodes[e['source']]['paperId'],nodes[e['target']]['paperId']}:
            if paper in papers:paper_edges[paper].add(e['id'])
    assessments={};paper_assessments=defaultdict(set);routes=[]
    for r in ledger['records']:
        left,right=r['nodeIds'];assert left in nodes and right in nodes
        involved={nodes[left]['paperId'],nodes[right]['paperId']}
        if r['admittedScientificEdge']:
            assert r['status']=='accepted_relation' and not r['promotionWithheld']
            source,target=(right,left) if r['direction']=='right_to_left' else (left,right);rid='scientific:'+r['taskId']
            edge={'id':rid,'source':source,'target':target,'type':r['relationCategory'],'semanticStatus':'reviewed_scoped','directed':r['direction'] in ['left_to_right','right_to_left'],'direction':r['direction'],'statement':r.get('exactAssertion'),'premises':r.get('applicability'),'conventions':r.get('conventionDictionary'),'readerNote':r.get('readerNote'),'evidenceRefs':sorted(set(nodes[left]['evidenceRefs']+nodes[right]['evidenceRefs'])),'provenance':{'taskId':r['taskId'],'contextRevision':r['contextRevision'],'receiptPath':r['receiptPath'],'receiptSha256':r['receiptSha256'],'originalEndpointOrder':r['nodeIds'],'originalDirection':r['direction'],'endpointScope':'exact_reviewed_source_objects_not_question_destinations'}}
            edges[rid]=edge
            for paper in involved & papers:paper_edges[paper].add(rid)
            source_methods=[u['id'] for u in node_units.get(source,[]) if u['lens']=='method'];target_methods=[u['id'] for u in node_units.get(target,[]) if u['lens']=='method']
            if source_methods or target_methods:routes.append({'sourceRelationId':rid,'sourceObjectId':source,'targetObjectId':target,'sourceMethodUnitIds':source_methods,'targetMethodUnitIds':target_methods,'type':edge['type'],'directed':edge['directed'],'receiptSha256':r['receiptSha256'],'bothEndpointsRepresented':bool(source_methods and target_methods),'questionEquivalenceInferred':False})
        else:
            aid='assessment:'+r['taskId'];assessments[aid]={'id':aid,'nodeIds':r['nodeIds'],'status':r['status'],'promotionWithheld':r['promotionWithheld'],'readerNote':r.get('readerNote'),'statement':r.get('exactAssertion'),'applicability':r.get('applicability'),'provenance':{'taskId':r['taskId'],'contextRevision':r['contextRevision'],'receiptPath':r['receiptPath'],'receiptSha256':r['receiptSha256']},'activeScientificEdge':False}
            for paper in involved & papers:paper_assessments[paper].add(aid)
    evidence={}
    for e in lines(a.downloads/'evidence.jsonl.gz'):
        original=e.get('original_evidence',{});pr=e.get('provenance',{});page=original.get('page');evidence['source-graph:'+e['id']]={'id':'source-graph:'+e['id'],'paperId':e['paper_id'],'page':page,'sourceSha256':e['source_sha256'],'recordId':pr.get('record_id'),'sourceUnitId':pr.get('source_unit_id'),'originalEvidenceId':original.get('evidence_id'),'sourceStart':original.get('source_start'),'sourceEnd':original.get('source_end'),'textView':original.get('text_view'),'evidenceScope':e.get('evidence_scope'),'pdfUrl':'https://arxiv.org/pdf/'+e['paper_id']+('#page='+str(page) if isinstance(page,int) else ''),'linkScope':'The PDF link locates the cited paper; sourceSha256 pins the frozen PDF used by extraction.'}
    buckets=defaultdict(lambda:{'units':{},'shards':{}});files={};summaries={};coverage_counts=Counter();included_nodes=set();included_edges=set();included_assessments=set();missing_anchors=[];max_raw=0;max_objects=0;max_relations=0
    print('loaded',json.dumps({'nodes':len(nodes),'nativeEdges':native_edge_count,'evidence':len(evidence),'papers':len(papers)}),flush=True)
    for paper in sorted(papers):
        ids=set(paper_nodes[paper]);rids=paper_edges[paper];aids=paper_assessments[paper]
        for rid in rids:ids.update((edges[rid]['source'],edges[rid]['target']))
        for aid in aids:ids.update(assessments[aid]['nodeIds'])
        eids={eid for o in [nodes[n] for n in ids]+[edges[r] for r in rids] for eid in o['evidenceRefs']};assert eids<=evidence.keys(),(paper,eids-evidence.keys())
        payload={'sourceObjects':[nodes[n] for n in sorted(ids)],'sourceRelations':[edges[r] for r in sorted(rids)],'sourceAttachments':[],'sourceAssessments':[assessments[k] for k in sorted(aids)],'sourceEvidence':[evidence[k] for k in sorted(eids)],'coverage':{'description':'All recorded source nodes and incident edges for this paper, including structural containment and unvalidated mentions with their original status. Only reviewed_scoped edges carry the separate native cross-paper review. Unit incidence is resolved from exact index anchors; context co-occurrence does not establish applicability.','paperId':paper,'unitCount':len(paper_units[paper]),'objectCount':len(ids),'relationCount':len(rids),'pdfOrRawPageTextIncluded':False,'objectTextMeaning':'Source-scoped extracted summaries, claims and conditions; not independent certification.','scopePolicy':POLICY}}
        raw=encode(payload);assert len(raw)<16*1024*1024,(paper,len(raw));compressed=gzip.compress(raw,compresslevel=9,mtime=0);name='context-'+hashlib.sha256(paper.encode()).hexdigest()[:24]+'.json.gz';path=a.out/name;path.write_bytes(compressed);assert gzip.decompress(compressed)==raw;sd={'path':name,'sha256':sha(path),'encoding':'gzip','uncompressedBytes':len(raw)};files[name]=dict(sd,bytes=len(compressed),paperId=paper,objectCount=len(ids),relationCount=len(rids),unitCount=len(paper_units[paper]));pc=Counter()
        for u in paper_units[paper]:
            uid=u['id'];entry={'shardId':paper,'lens':u['lens'],'attachmentOverride':{'policy':POLICY,'anchorObjectIds':u['sourceNodeIds'],'sourceRecordIds':u['sourceRecordIds']}}
            res=resolve_override(uid,entry,payload);missing_anchors.extend({'unitId':uid,'objectId':n} for n in res['missingAnchorIds']);direct=next((x for x in res['sourceAttachments'] if x['scope']=='direct_record_relation'),{'relationIds':[]});incident=[edges[r] for r in direct['relationIds']];scientific_local=[r for r in incident if r['type']!='contains' and r['semanticStatus'] not in ['unvalidated_mention','reviewed_scoped']];prefix=uid.split(':',1)[1][:2]
            anchor_evidence=sorted(set(e for n in u['sourceNodeIds'] if n in nodes for e in nodes[n]['evidenceRefs']));source_shas=sorted(set(nodes[n]['provenance']['sourceSha256'] for n in u['sourceNodeIds'] if n in nodes and nodes[n]['provenance'].get('sourceSha256')));entry['sourceLocator']={'paperId':paper,'sourceSha256':source_shas[0] if len(source_shas)==1 else None,'pages':sorted(set(evidence[e]['page'] for e in anchor_evidence if isinstance(evidence[e]['page'],int))),'evidenceRefs':anchor_evidence}
            for k,v in [('unitCount',1),(u['lens']+'Count',1),(u['lens']+'WithNoncontainmentNonmentionLocalRelations',bool(scientific_local)),(u['lens']+'WithReviewedRelations',res['coverage']['directReviewedRelationCount']>0)]:coverage_counts[k]+=int(v);pc[k]+=int(v)
            buckets[prefix]['units'][uid]=entry;buckets[prefix]['shards'][paper]=sd
        counts=Counter(nodes[n]['kind'] for n in ids);rc=Counter(edges[r]['semanticStatus'] for r in rids);pages=sorted(set(evidence[e]['page'] for e in eids if evidence[e]['paperId']==paper and isinstance(evidence[e]['page'],int)))
        summaries[paper]={'unitCounts':dict(pc),'objectKindCounts':dict(counts),'relationStatusCounts':dict(rc),'nonpositiveAssessmentCount':len(aids),'sourcePages':pages,'pdfUrl':'https://arxiv.org/pdf/'+paper,'fullContext':sd};included_nodes.update(ids);included_edges.update(rids);included_assessments.update(aids);max_raw=max(max_raw,len(raw));max_objects=max(max_objects,len(ids));max_relations=max(max_relations,len(rids))
    assert not missing_anchors,missing_anchors
    assert len(routes)==51 and sum(r['bothEndpointsRepresented'] for r in routes)==50
    assert len(included_assessments)==31
    omitted_nodes=set(nodes)-included_nodes;omitted_edges=set(edges)-included_edges
    coverage={'description':'All recorded nodes and edges incident to the 6,477 papers represented by 26,410 question/method entries. Structural containment and unvalidated mention edges remain explicitly typed; they are not independent scientific assertions. Exact object relations, numbered extraction-window context and whole-paper context stay separate. Nonpositive and withheld reviews remain inactive assessments.','paperCount':len(papers),**dict(coverage_counts),'sourceObjectCount':len(included_nodes),'sourceRelationCount':len(included_edges),'reviewedScopedRelations':97,'nonpositiveSourceAssessments':len(included_assessments),'methodReviewedRelationsAnyEndpoint':51,'methodReviewedRelationsBothEndpoints':50,'missingAnchorCount':0,'globalSourceNodeCount':len(nodes),'globalSourceNativeEdgeCount':native_edge_count,'outOfBrowserPaperNodeCount':len(omitted_nodes),'outOfBrowserPaperEdgeCount':len(omitted_edges),'pdfOrRawPageTextIncluded':False,'paperAbstractsIncluded':False,'paperNodesAreCatalogProjections':True}
    index_shards={}
    for prefix,b in sorted(buckets.items()):
        path=a.out/('unit-index-'+prefix+'.json');write(path,dict(schemaVersion='1.0.0',kind='eigenquestions-source-context-unit-index',**b));index_shards[prefix]=desc(path)
    ip=a.out/'source-context-index-v3.1.json';write(ip,{'schemaVersion':'1.0.0','kind':'eigenquestions-source-context-index','policyVersion':'q025-full-recorded-source-context-v3.1','coverage':coverage,'unitIndex':{'kind':'unit-hash-prefix','prefixLength':2,'prefixSource':'hexadecimal suffix after unit:','shards':index_shards},'attachmentOverridePolicies':{POLICY:'Exact incident edges only for direct scope; numbered wN windows require exact paper/record/source-unit identity. All statuses and directions preserved. Whole-paper records remain paper context.'}})
    sp=a.out/'source-context-summary-v3.1.json';write(sp,{'schemaVersion':'1.0.0','kind':'eigenquestions-source-context-summary','coverage':coverage,'papers':summaries})
    write(a.out/'method-relation-routes.json',routes)
    report={'schemaVersion':'q025-full-recorded-source-context-export/3.1','sourceContextIndex':desc(ip),'sourceContextSummary':desc(sp),'coverage':coverage,'sourceEdgeCensus':[{'type':t,'semanticStatus':s,'count':n} for (t,s),n in sorted(edge_census.items())],'sourceNodeTypeCensus':dict(all_node_types),'shardCount':len(files),'totalShardBytes':sum(x['bytes'] for x in files.values()),'maxShardBytes':max(x['bytes'] for x in files.values()),'totalUncompressedShardBytes':sum(x['uncompressedBytes'] for x in files.values()),'maxUncompressedShardBytes':max_raw,'maxShardObjects':max_objects,'maxShardRelations':max_relations,'bucketCount':len(index_shards),'totalIndexBucketBytes':sum(x['bytes'] for x in index_shards.values()),'maxIndexBucketBytes':max(x['bytes'] for x in index_shards.values()),'invariants':{'all26410UnitAnchorsResolve':True,'allSourceRelationEndpointsResolve':True,'allEvidenceRefsResolve':True,'allGzipRoundTripsPass':True,'all97ReviewedEdgesRetained':sum(r.startswith('scientific:') for r in included_edges)==97,'all31NonpositiveAssessmentsRetained':True,'allFiveMandatoryWithheldReaderNotesRetained':sum(bool(assessments[x]['promotionWithheld'] and assessments[x]['readerNote']) for x in included_assessments)==5,'eachDecompressedFileUnder16MiB':True,'noRawQuoteOrPdfPayloadExported':True,'noOriginalPaperAbstractsExported':all(nodes[n]['kind']!='paper' or nodes[n]['text']==nodes[n]['catalogMetadata']['title'] for n in included_nodes)},'provenance':{'scriptSha256':sha(__file__),'resolverSha256':sha(Path(__file__).resolve().parent.parent/'source-index-v2/context_override.py'),'unitsMetadataSha256':sha(a.units),'ledgerSha256':sha(a.ledger),'sourceGraphFiles':graph_hashes,'supersededCompactPackManifestSha256':sha(a.old_pack/'manifest.json')},'files':files,'unitIndexFiles':index_shards,'outOfBrowserPaperNodeExclusions':[{'id':n,'reason':'Source graph unavailable-paper stub has no browser question/method entries or incident edges; a PDF is not inferred to exist.'} for n in sorted(omitted_nodes)],'outOfBrowserPaperNodes':sorted(omitted_nodes),'outOfBrowserPaperEdges':sorted(omitted_edges)}
    assert all(report['invariants'].values()),report['invariants']
    write(a.out/'manifest.json',report);print(json.dumps({k:v for k,v in report.items() if k not in ['files','unitIndexFiles','outOfBrowserPaperNodes','outOfBrowserPaperEdges']},indent=2),flush=True)

if __name__=='__main__':main()
