#!/usr/bin/env python3
"""Lossless paper-scoped gzip context plus quote-free source-page locators."""
import argparse, gzip, hashlib, json
from collections import Counter, defaultdict
from pathlib import Path

def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()

def encode(x):return (json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n').encode()

def main():
 p=argparse.ArgumentParser();p.add_argument('--pack',type=Path,required=True);p.add_argument('--units',type=Path,required=True);p.add_argument('--evidence',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 units={u['unit_id']:u for u in map(json.loads,a.units.open())};oldmanifest=json.loads((a.pack/'manifest.json').read_text());oldindex=json.loads((a.pack/'source-context-index.json').read_text());evidence={}
 expected='bfeb1779d7134cdc5b3c27aa7385ea47fd69b94cd11e0a59f00279c4779ca8bc';assert sha(a.evidence)==expected
 with gzip.open(a.evidence,'rt') as f:
  for line in f:
   e=json.loads(line);original=e.get('original_evidence',{});pr=e.get('provenance',{});eid='source-graph:'+e['id'];page=original.get('page')
   locator={'id':eid,'paperId':e['paper_id'],'page':page,'sourceSha256':e['source_sha256'],'recordId':pr.get('record_id'),'sourceUnitId':pr.get('source_unit_id'),'originalEvidenceId':original.get('evidence_id'),'sourceStart':original.get('source_start'),'sourceEnd':original.get('source_end'),'textView':original.get('text_view'),'evidenceScope':e.get('evidence_scope'),'pdfUrl':'https://arxiv.org/pdf/'+e['paper_id']+('#page='+str(page) if isinstance(page,int) else ''),'linkScope':'The PDF link locates the cited paper; sourceSha256 pins the frozen PDF used by extraction.'}
   evidence[eid]=locator
 evidence_keys=set(evidence)
 files={};index={};summaries={};allrelations=set();allassessments=set();objects=set();max_uncompressed=0;max_objects=0;max_relations=0
 for name,descriptor in sorted(oldmanifest['files'].items()):
  path=a.pack/name;assert sha(path)==descriptor['sha256'];d=json.loads(path.read_text());node={x['id']:x for x in d['sourceObjects']};relation={x['id']:x for x in d['sourceRelations']};by_paper=defaultdict(list)
  for at in d['sourceAttachments']:by_paper[units[at['unitId']]['paper_id']].append(at)
  for paper,attachments in by_paper.items():
   unitids=sorted(set(x['unitId'] for x in attachments));nodeids=set(n for x in attachments for n in x['objectIds']);relids=set(n for x in attachments for n in x['relationIds']);assessments=[x for x in d.get('sourceAssessments',[]) if any(node[n]['paperId']==paper for n in x['nodeIds'])]
   for x in assessments:nodeids.update(x['nodeIds']);allassessments.add(x['id'])
   for rid in relids:nodeids.update([relation[rid]['source'],relation[rid]['target']]);allrelations.add(rid)
   selected_nodes=[node[n] for n in sorted(nodeids)];selected_relations=[relation[n] for n in sorted(relids)];objects.update(nodeids)
   evidenceids=set(x for n in selected_nodes+selected_relations for x in n.get('evidenceRefs',[]));assert evidenceids<=evidence_keys,(paper,list(evidenceids-evidence_keys)[:5])
   direct=sum(any(x['scope']=='direct_record_relation' and x['relationIds'] for x in attachments if x['unitId']==uid) for uid in unitids)
   counts=Counter(n['kind'] for n in selected_nodes);coverage={'description':'Complete extracted source context for these question units, loaded only on request. Direct relations and same-extraction/paper context are separately typed. Page locators contain no quoted source text.','paperId':paper,'unitCount':len(unitids),'objectCount':len(selected_nodes),'directSourceRelationUnitCount':direct,'objectKindCounts':dict(counts),'pdfOrRawPageTextIncluded':False,'nodeTextMeaning':'Source-scoped extracted summaries, claims and conditions; not independent certification.'}
   payload={'sourceObjects':selected_nodes,'sourceRelations':selected_relations,'sourceAttachments':attachments,'sourceAssessments':assessments,'sourceEvidence':[evidence[x] for x in sorted(evidenceids)],'coverage':coverage}
   raw=encode(payload);compressed=gzip.compress(raw,compresslevel=9,mtime=0);name='context-'+hashlib.sha256(paper.encode()).hexdigest()[:24]+'.json.gz';out=a.out/name;out.write_bytes(compressed);item={'path':name,'sha256':sha(out),'encoding':'gzip','uncompressedBytes':len(raw)}
   files[name]=dict(item,bytes=len(compressed),paperId=paper,unitCount=len(unitids),objectCount=len(selected_nodes),relationCount=len(selected_relations));assert gzip.decompress(compressed)==raw
   assert len(raw)<16*1024*1024,(paper,len(raw))
   for uid in unitids:assert uid not in index;index[uid]=item
   summaries[paper]={'unitCount':len(unitids),'directSourceRelationUnitCount':direct,'objectKindCounts':dict(counts),'reviewedScopedRelationCount':sum(r['semanticStatus']=='reviewed_scoped' for r in selected_relations),'nonpositiveAssessmentCount':len(assessments),'fullContext':item}
   max_uncompressed=max(max_uncompressed,len(raw));max_objects=max(max_objects,len(selected_nodes));max_relations=max(max_relations,len(selected_relations))
 assert set(index)==set(units)==set(oldindex['units']);assert objects=={n['id'] for name in oldmanifest['files'] for n in json.loads((a.pack/name).read_text())['sourceObjects']}
 coverage=dict(oldmanifest['coverage'],description='Lazy paper-scoped source context for all8473 question units. Exactly2408 have incident noncontainment source-local relations; context elsewhere is not asserted applicability. Source summaries and quote-free page locators only.',format='gzip-compressed complete extracted context, plain agent summary/index')
 indexpath=a.out/'source-context-index.json';indexpath.write_bytes(encode({'schemaVersion':'1.0.0','kind':'eigenquestions-source-context-index','coverage':coverage,'units':index}))
 summarypath=a.out/'source-context-summary.json';summarypath.write_bytes(encode({'schemaVersion':'1.0.0','kind':'eigenquestions-source-context-summary','coverage':coverage,'papers':summaries}))
 manifest={'schemaVersion':'q025-compact-source-context-export/1','sourceContextIndex':{'path':indexpath.name,'sha256':sha(indexpath),'bytes':indexpath.stat().st_size},'sourceContextSummary':{'path':summarypath.name,'sha256':sha(summarypath),'bytes':summarypath.stat().st_size},'coverage':coverage,'shardCount':len(files),'totalShardBytes':sum(x['bytes'] for x in files.values()),'maxShardBytes':max(x['bytes'] for x in files.values()),'totalUncompressedShardBytes':sum(x['uncompressedBytes'] for x in files.values()),'maxUncompressedShardBytes':max_uncompressed,'maxShardObjects':max_objects,'maxShardRelations':max_relations,'uniqueSourceRelationCount':len(allrelations),'uniqueSourceObjectCount':len(objects),'uniqueNonpositiveAssessmentCount':len(allassessments),'files':files,'invariants':{'everyQuestionUnitIndexed':True,'allObjectsPreservedFromFullExport':True,'eachGzipRoundTrips':True,'maximumDecompressedBytesUnder16MiB':True,'allEvidenceRefsResolveToQuoteFreeLocators':True},'provenance':{'scriptSha256':sha(Path(__file__)),'fullPackManifestSha256':sha(a.pack/'manifest.json'),'sourceEvidenceArchiveSha256':expected}}
 (a.out/'manifest.json').write_bytes(encode(manifest));print(json.dumps({k:v for k,v in manifest.items() if k!='files'},indent=2),flush=True)

if __name__=='__main__':main()
