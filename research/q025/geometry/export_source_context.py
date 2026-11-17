#!/usr/bin/env python3
"""Create bounded lazy browser source-context shards from extracted objects only.

No PDFs, page images, evidence.jsonl page materializations or raw source packets.
"""
import argparse, gzip, hashlib, json
from collections import Counter, defaultdict
from pathlib import Path

def readlines(path):
 with gzip.open(path,'rt') as f:
  for line in f:yield json.loads(line)

def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()

def write(path,data):
 path.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')

def evidence(ids):return ['source-graph:'+x for x in (ids or [])]

def main():
 p=argparse.ArgumentParser();p.add_argument('--round3',type=Path,required=True);p.add_argument('--ledger',type=Path,required=True);p.add_argument('--full-nodes',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 units=[json.loads(line) for line in (a.round3/'source-rows.jsonl').open()];unitmap={u['unit_id']:u for u in units};ledger=json.loads(a.ledger.read_text())
 nodes={x['id']:x for x in readlines(a.round3/'source-objects.jsonl.gz')}
 required=set(n for r in ledger['records'] for n in r['nodeIds']);missing=required-set(nodes)
 if missing:
  for x in readlines(a.full_nodes):
   if x['id'] in missing:nodes[x['id']]=x
 assert not (required-set(nodes)),sorted(required-set(nodes))
 shards={};index={};nodecache={};edgecache={};attached_units=set();counts=Counter();nonpositive=set();positive=set();paper_units=defaultdict(list)
 def shard_for(paper):
  key=hashlib.sha256(paper.encode()).hexdigest()[:2]
  if key not in shards:shards[key]={'objects':{},'relations':{},'attachments':[],'assessments':{},'papers':set(),'units':set()}
  shards[key]['papers'].add(paper);return key,shards[key]
 def obj(nid):
  if nid not in nodecache:
   x=nodes[nid];nodecache[nid]={'id':nid,'kind':x['type'],'paperId':x['paper_id'],'text':x.get('text') or x.get('label') or '', 'evidenceRefs':evidence(x.get('evidence_ids')),'evidenceScope':x.get('evidence_scope'),'provenance':{'sourceGraphNodeId':nid,'sourceSha256':x.get('source_sha256'),'layer':x.get('layer'),'record':x.get('provenance',{}),'certainty':x.get('certainty'),'originalEvidenceIds':x.get('evidence_ids',[])}}
  return nodecache[nid]
 for e in readlines(a.round3/'source-local-edges.jsonl.gz'):
  edgecache[e['id']]={'id':e['id'],'source':e['source'],'target':e['target'],'type':e['type'],'directed':True,'semanticStatus':e['semantic_status'],'evidenceRefs':evidence(e.get('evidence_ids')),'provenance':{'record':e.get('provenance',{}),'attributes':e.get('attributes',{}),'originalEvidenceIds':e.get('evidence_ids',[])}}
 for attachment in readlines(a.round3/'unit-science-attachments.jsonl.gz'):
  uid=attachment['unitId'];u=unitmap[uid];key,shard=shard_for(u['paper_id']);shard['units'].add(uid);paper_units[u['paper_id']].append(uid);attached_units.add(uid)
  direct_edges=set(attachment['directEdgeIds'])
  for path in attachment['propertyEdgePaths']:direct_edges.update(path)
  direct_objects=set(attachment['sourceNodeIds'])
  for eid in direct_edges:
   e=edgecache[eid];shard['relations'][eid]=e;direct_objects.update([e['source'],e['target']])
  for nid in direct_objects:shard['objects'][nid]=obj(nid)
  shard['attachments'].append({'unitId':uid,'scope':'direct_record_relation','objectIds':sorted(direct_objects),'relationIds':sorted(direct_edges),'anchorObjectIds':attachment['sourceNodeIds'],'propertyEdgePaths':attachment['propertyEdgePaths'],'statement':'Exact source anchors and incident local object relations. Property paths qualify their named parent object; they do not silently apply to every question in the paper.'})
  byrecord=defaultdict(list)
  for nid in attachment['sameExtractionContextNodeIds']:
   x=nodes[nid];pr=x.get('provenance',{});byrecord[(pr.get('record_id'),pr.get('source_unit_id'))].append(nid);shard['objects'][nid]=obj(nid)
  for (rid,window),ids in byrecord.items():
   is_window=bool(window and window.startswith('w') and window[1:].isdigit())
   scope='shared_extraction_window_context' if is_window else 'same_paper_context'
   shard['attachments'].append({'unitId':uid,'scope':scope,'objectIds':sorted(ids),'relationIds':[],'recordId':rid,'sourceUnitId':window,'statement':'Source extraction context only. Co-occurrence does not establish this question\u2019s assumptions, support, derivation or contradiction.'});counts[scope]+=1
  counts['direct_record_relation']+=1
 # Independently reviewed edges keep exact source-object endpoints, never Q destinations.
 for r in ledger['records']:
  papers=set(e['paper_id'] for e in r['endpoints']);admitted=r['admittedScientificEdge'];rid='scientific:'+r['taskId']
  for paper in papers:
   if paper not in paper_units:continue
   key,shard=shard_for(paper)
   for nid in r['nodeIds']:shard['objects'][nid]=obj(nid)
   if admitted:
    assert r['status']=='accepted_relation' and not r['promotionWithheld'];source,target=r['nodeIds'];direction=r['direction']
    if direction=='right_to_left':source,target=target,source
    rel={'id':rid,'source':source,'target':target,'type':r['relationCategory'],'semanticStatus':'reviewed_scoped','directed':direction in ['left_to_right','right_to_left'],'direction':direction,'statement':r.get('exactAssertion'),'premises':r.get('applicability'),'conventions':r.get('conventionDictionary'),'readerNote':r.get('readerNote'),'evidenceRefs':sorted(set(evidence(nodes[nid].get('evidence_ids'))[j] for nid in r['nodeIds'] for j in range(len(evidence(nodes[nid].get('evidence_ids')))))),'provenance':{'taskId':r['taskId'],'contextRevision':r['contextRevision'],'receiptPath':r['receiptPath'],'receiptSha256':r['receiptSha256'],'originalEndpointOrder':r['nodeIds'],'originalDirection':direction,'endpointScope':'exact_reviewed_source_objects_not_question_destinations'}}
    shard['relations'][rid]=rel;positive.add(rid)
    for uid in paper_units[paper]:shard['attachments'].append({'unitId':uid,'scope':'same_paper_context','objectIds':r['nodeIds'],'relationIds':[rid],'statement':'A reviewed relation involving named source objects in this paper. It is not automatically a relation between this question and every question of the other paper.'})
   else:
    assessment={'id':'assessment:'+r['taskId'],'nodeIds':r['nodeIds'],'status':r['status'],'promotionWithheld':r['promotionWithheld'],'readerNote':r.get('readerNote'),'statement':r.get('exactAssertion'),'applicability':r.get('applicability'),'provenance':{'taskId':r['taskId'],'contextRevision':r['contextRevision'],'receiptPath':r['receiptPath'],'receiptSha256':r['receiptSha256']},'activeScientificEdge':False}
    shard['assessments'][assessment['id']]=assessment;nonpositive.add(assessment['id'])
 assert attached_units==set(unitmap);assert len(positive)==97
 files={};max_objects=0;max_relations=0
 for key,shard in sorted(shards.items()):
  object_ids=set(shard['objects']);assert all(e['source'] in object_ids and e['target'] in object_ids for e in shard['relations'].values())
  assert all(set(at['objectIds'])<=object_ids and set(at['relationIds'])<=set(shard['relations']) for at in shard['attachments'])
  payload={'sourceObjects':list(shard['objects'].values()),'sourceRelations':list(shard['relations'].values()),'sourceAttachments':shard['attachments'],'sourceAssessments':list(shard['assessments'].values()),'coverage':{'description':'Extracted source summaries, claims and conditions with exact provenance. No PDF, raw page, page image or complete source packet. Context associations are distinct from question-specific relations.','paperCount':len(shard['papers']),'unitCount':len(shard['units']),'objectCount':len(shard['objects']),'localRelationsRetainOriginalSemanticStatus':True}}
  path=a.out/f'context-{key}.json';write(path,payload);descriptor={'path':path.name,'sha256':sha(path)};files[path.name]=dict(descriptor,bytes=path.stat().st_size,unitCount=len(shard['units']),objectCount=len(shard['objects']),relationCount=len(shard['relations']))
  for uid in shard['units']:index[uid]=descriptor
  max_objects=max(max_objects,len(shard['objects']));max_relations=max(max_relations,len(shard['relations']))
 coverage={'description':'Source context is available for all8473 question units. Only2408 have noncontainment source-local edges; all other rich objects are scoped context, not asserted premises. Reviewed cross-paper relations attach to exact source objects, not question destinations.','unitCount':len(index),'directSourceRelationUnitCount':2408,'sourceObjectCount':len(nodecache),'reviewedScopedRelations':len(positive),'nonpositiveSourceAssessments':len(nonpositive),'pdfOrRawEvidenceIncluded':False}
 indexpath=a.out/'source-context-index.json';write(indexpath,{'schemaVersion':'1.0.0','kind':'eigenquestions-source-context-index','coverage':coverage,'units':index})
 report={'schemaVersion':'q025-source-context-export/1','sourceContextIndex':{'path':indexpath.name,'sha256':sha(indexpath),'bytes':indexpath.stat().st_size},'coverage':coverage,'attachmentCounts':dict(counts),'shardCount':len(files),'totalShardBytes':sum(x['bytes'] for x in files.values()),'maxShardBytes':max(x['bytes'] for x in files.values()),'maxShardObjects':max_objects,'maxShardRelations':max_relations,'files':files,'invariants':{'allUnitsIndexed':True,'allAttachmentIdsResolve':True,'allRelationEndpointsResolveInShard':True,'nonpositiveAssessmentsAreNotEdges':True},'provenance':{'scriptSha256':sha(Path(__file__)),'round3InputManifestSha256':sha(a.round3/'input-manifest.json'),'ledgerSha256':sha(a.ledger),'sourceObjectFileSha256':sha(a.round3/'source-objects.jsonl.gz'),'sourceAttachmentFileSha256':sha(a.round3/'unit-science-attachments.jsonl.gz')}}
 write(a.out/'manifest.json',report);print(json.dumps({k:v for k,v in report.items() if k!='files'},indent=2),flush=True)

if __name__=='__main__':main()
