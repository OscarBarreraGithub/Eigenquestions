#!/usr/bin/env python3
"""Build the frozen public corpus without an encoder or third-party packages.
Usage: python3 scripts/data/build-corpus.py /path/to/physics-atlas-swampland
Source archives remain untouched. All output provenance is root-relative.
"""
import array, ast, collections, hashlib, io, json, math, pathlib, re, struct, sys, zipfile
ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = pathlib.Path(sys.argv[1])
OUT = ROOT / 'data/navigation'
ORG = SOURCE / 'organization/20261104-v2'
MAP = SOURCE / 'graph-design/20261105-v1/publication-v1/map-data.json'
OUT.mkdir(parents=True, exist_ok=True)

def sha(data): return hashlib.sha256(data).hexdigest()
def read_npy(raw):
    f=io.BytesIO(raw); assert f.read(6)==b'\x93NUMPY'; version=f.read(2)
    size=struct.unpack('<H' if version[0]==1 else '<I', f.read(2 if version[0]==1 else 4))[0]
    head=ast.literal_eval(f.read(size).decode()); assert not head['fortran_order']
    kinds={'<f4':'f','<f8':'d','<i4':'i','<i8':'q','<u4':'I','|u1':'B'}
    if head['descr'] not in kinds:return head,None,f.read()
    a=array.array(kinds[head['descr']]); a.frombytes(f.read())
    if sys.byteorder!='little':a.byteswap()
    return head,a,None

def dump(name,data):
    raw=json.dumps(data,ensure_ascii=False,separators=(',',':')).encode()
    (OUT/name).write_bytes(raw);return {'path':name,'sha256':sha(raw),'bytes':len(raw)}
def source_pin(path):
    raw=path.read_bytes();return {'path':str(path.relative_to(SOURCE)),'sha256':sha(raw),'bytes':len(raw)}

data=json.loads(MAP.read_bytes()); papers=[]
for p in data['papers']:
    a=p.get('arxiv_id'); date=None
    if a and re.match(r'^\d{4}\.\d+',a): date=f"{p['year']}-{a[2:4]}"
    elif a and re.search(r'/(\d{2})(\d{2})\d{3}',a):date=f"{p['year']}-{re.search(r'/(\d{2})(\d{2})\d{3}',a)[2]}"
    papers.append({'id':p['id'],'title':p['title'],'year':int(p['year']) if p['year'] else None,'date':date or p['year'],'datePrecision':'month' if date else 'year','url':p['url'],'arxivId':a,'authors':p.get('authors',[]),'sourceSha256':p.get('pdf_sha256'),'sourceNotice':p.get('source_notice_text'),'scientificStatus':p.get('scientific_status')})
paper_ids={p['id'] for p in papers};files={'papers':dump('papers.json',papers),'units':[],'vectors':[],'graph':[]};pins=[source_pin(MAP)];units=[];vectors=array.array('f');adjacency=[];layers={};checks={};embedding_fingerprint=None;scopes={}
for layer in ['physical_question','method']:
    base=ORG/layer; offset=len(units);layer_units=[]
    expected=json.loads((base/'INPUTS.json').read_text())['files']
    for filename in ['units.jsonl','vectors.npy','neighbors.json','affinity.npz','input-provenance.json']:
        pin=source_pin(base/filename);assert pin['sha256']==expected[filename]['sha256'],f'Hash mismatch {filename}';pins.append(pin)
    provenance=json.loads((base/'input-provenance.json').read_text())
    fingerprint=provenance['embedding_input_fingerprint']
    if embedding_fingerprint is None:embedding_fingerprint=fingerprint
    assert fingerprint==embedding_fingerprint, 'Incompatible encoder fingerprints'
    for line in (base/'units.jsonl').open():
        u=json.loads(line);assert u['paper_id'] in paper_ids
        assert sha(u['text'].encode())==u['text_sha256']
        records=u.get('source_records',[]);nodes=u.get('source_nodes',[])
        scope=records[0].get('reading_scope') if records else None
        scope_id=sha(json.dumps(scope,sort_keys=True,separators=(',',':')).encode());scopes[scope_id]=scope
        layer_units.append({'id':u['unit_id'],'paperId':u['paper_id'],'lens':layer,'text':u['text'],'mass':u['mass'],'vectorRow':offset+len(layer_units),'evidence':{'kind':'source_scoped_extraction','facetIds':u['facet_ids'],'sourceRecordIds':u['source_record_ids'],'sourceNodeIds':u['node_ids'],'textSha256':u['text_sha256'],'originalEmbeddingRows':u['embedding_rows'],'anchors':sorted(set(e for n in nodes for e in n.get('evidence_ids',[]))),'sourceSha256':records[0].get('source_sha256') if records else None,'reviewStatus':records[0].get('review',{}).get('status') if records else None,'readingScopeId':scope_id,'claimStatus':'retrieval_nomination_only; not independent scientific certification'}})
    neighbors=json.loads((base/'neighbors.json').read_text());assert neighbors['unit_ids']==[u['id'] for u in layer_units], 'Row binding mismatch'
    head,vec,_=read_npy((base/'vectors.npy').read_bytes()); assert head['shape']==(len(layer_units),384)
    norms=[math.sqrt(sum(x*x for x in vec[i*384:(i+1)*384])) for i in range(len(layer_units))]
    assert max(abs(n-1) for n in norms)<1e-4 and all(math.isfinite(x) for x in vec)
    with zipfile.ZipFile(base/'affinity.npz') as z:
        _,indices,_=read_npy(z.read('indices.npy'));_,indptr,_=read_npy(z.read('indptr.npy'));_,weights,_=read_npy(z.read('data.npy'))
    kept=0
    for i,u in enumerate(layer_units):
        # Preserve source affinity weights and strongest 16 distinct-paper edges.
        row=sorted(((indices[j],weights[j]) for j in range(indptr[i],indptr[i+1]) if indices[j]!=i and layer_units[indices[j]]['paperId']!=u['paperId']),key=lambda z:(-z[1],z[0]))
        unique=[];seen=set()
        for j,w in row:
            p=layer_units[j]['paperId']
            if p not in seen:unique.append([offset+j,round(w,9)]);seen.add(p)
            if len(unique)==16:break
        kept+=len(unique);adjacency.append(unique)
    checks[layer]={'rows':len(layer_units),'maxNormError':max(abs(n-1) for n in norms),'rowBinding':'exact neighbors.json unit_ids == units.jsonl line order','graphEdgesRetained':kept,'graphEdgesOriginal':len(weights),'sourceFacetCount':provenance['source_facet_count'],'papers':provenance['paper_count']}
    layers[layer]={'start':offset,'count':len(layer_units)};units.extend(layer_units);vectors.extend(vec)
assert len(set(u['id'] for u in units))==len(units)
for start in range(0,len(units),2048):
    count=min(2048,len(units)-start);suffix=f'{start//2048:03d}'
    f=dump(f'units-{suffix}.json',units[start:start+count]);f.update(start=start,count=count);files['units'].append(f)
    raw=vectors[start*384:(start+count)*384].tobytes();name=f'vectors-{suffix}.f32';(OUT/name).write_bytes(raw)
    files['vectors'].append({'path':name,'sha256':sha(raw),'bytes':len(raw),'start':start,'count':count})
    f=dump(f'graph-{suffix}.json',adjacency[start:start+count]);f.update(start=start,count=count);files['graph'].append(f)
files['scopes']=dump('scopes.json',scopes)
manifest={'schemaVersion':'1.0.0','corpusId':'swampland-navigation-20261105-minilm-v1','title':'Swampland source-linked question and method corpus','snapshotDate':'2026-11-05','scope':{'paperCount':len(papers),'vectorCoveredPaperCount':len(set(u['paperId'] for u in units)),'unitCount':len(units),'earliestPublicationDate':min(p['date'] for p in papers),'latestPublicationDate':max(p['date'] for p in papers),'earliestYear':min(p['year'] for p in papers if p['year']),'latestYear':max(p['year'] for p in papers if p['year']),'recentMeaning':'Recent within this frozen corpus, not a live literature search. Month precision from arXiv identifier when available; otherwise year.','limitations':['Swampland-centered collection; not all physics or all relevant literature.','Unit text is a source-scoped extraction, not a quotation or independently certified result.','Affinities are retrieval similarities, not physical implications.','No query encoder runs in v1; matching source facets provide real embedding anchors.']},'encoder':{'id':embedding_fingerprint['model_id'],'revision':embedding_fingerprint['revision'],'dimensions':384,'dtype':'float32','byteOrder':'little','normalization':'source token-window normalized mean, unit vectors L2 normalized in original organization build','fingerprint':embedding_fingerprint},'layers':layers,'files':files,'inputs':pins,'checks':checks,'graph':{'type':'retrieval_affinity','source':'paper-balanced self-tuning kernel from the original organization graph','selection':'strongest 16 distinct-other-paper neighbors per unit; source weights retained; directed truncation','crossLens':'same-paper incidence at runtime; not an implication','noScientificRelationsPromoted':True}}
manifest['contentHash']=sha(json.dumps(files,sort_keys=True,separators=(',',':')).encode())
dump('manifest.json',manifest)
print(json.dumps({'corpusId':manifest['corpusId'],'papers':len(papers),'units':len(units),'bytes':sum(p.stat().st_size for p in OUT.iterdir() if p.is_file()),'checks':checks},indent=2))
