"""Reusable, source-pinned packet compiler. No native calls or scientific admission."""
import collections,hashlib,json,re
from pathlib import Path
import numpy as np
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,separators=(',',':'))+'\n')
class Corpus:
 def __init__(self,work,upstream):
  self.work=Path(work);self.up=Path(upstream);self.graph=self.up/'components/atlas_graph/output/20261104-foundation-v3'
  self.units={u['id']:u for p in sorted((self.work/'data/navigation').glob('units-*.json')) for u in json.loads(p.read_text())}
  self.rows=[r for r in map(json.loads,(self.work/'research/q025/geometry/round1/source-rows.jsonl').read_text().splitlines()) if r['view']=='physical_question'];self.rowindex={r['unit_id']:i for i,r in enumerate(self.rows)}
  V=np.concatenate([np.fromfile(p,dtype='<f4').reshape(-1,384) for p in sorted((self.work/'data/navigation').glob('vectors-*.f32'))]);self.V=V[[r['browserVectorRow'] for r in self.rows]]
  self.held={r['paperId'] for r in json.loads((self.work/'research/q025/evaluation/final-holdout-reservation.local.json').read_text())['records']};self.selected=set();self.readings={};self.nodes={};self.edges=[];self.evidence={}
 def eligible(self,ids):return [u for u in ids if self.units[u]['paperId'] not in self.held]
 def select(self,region,children=None):
  member=set(region['memberIds']);visible=self.eligible(region['memberIds']);idx=[self.rowindex[u] for u in visible];center=np.mean(self.V[idx],axis=0);center/=max(np.linalg.norm(center),1e-12);scores=self.V@center;inside=sorted(idx,key=lambda i:-float(scores[i]));outside=sorted((i for i,r in enumerate(self.rows) if r['unit_id'] not in member and r['paper_id'] not in self.held),key=lambda i:-float(scores[i]));picks=[];papers=set()
  def choose(indices,n,role):
   added=0
   for i in indices:
    u=self.units[self.rows[i]['unit_id']]
    if u['paperId'] in papers or u['paperId'] in self.held or not u['evidence']['anchors']:continue
    papers.add(u['paperId']);picks.append((u['id'],role));self.selected.add(u['id']);added+=1
    if added==n:break
   return added
  if children:
   for child in children:
    candidates=[self.rowindex[u] for u in self.eligible(child['representativeUnitIds']+child['memberIds'])];choose(candidates,1,'child_scope_contrast')
   boundary=sorted(idx,key=lambda i:float(scores[i]));choose(boundary,1,'parent_boundary_contrast')
  else:
   reps=[self.rowindex[u] for u in self.eligible(region['representativeUnitIds'])];choose(reps+inside,4,'central_source')
   boundary=sorted(idx,key=lambda i:abs(float(scores[i])-float(np.quantile(scores[idx],.20))));choose(boundary,3,'boundary_source');choose(outside,3,'outside_source_probe')
  assert picks and not ({self.units[u]['paperId'] for u,_ in picks}&self.held)
  return {'visibleMemberIds':visible,'picks':picks,'reservedUnreviewedCount':len(member)-len(visible)}
 def load_science(self):
  # Verify complete graph bytes once; the immutable manifest alone is not a content check.
  manifest=json.loads((self.graph/'MANIFEST.json').read_text());self.graphpins={'foundationManifestSha256':sha(self.graph/'MANIFEST.json')}
  selectednodes={n for u in self.selected for n in self.units[u]['evidence']['sourceNodeIds']};wantednodes=set(selectednodes);adj=collections.defaultdict(list)
  for line in (self.graph/'edges.jsonl').open():
   e=json.loads(line)
   if e['type'] in ['contains','literal_identifier_mention','mentions']:continue
   if e['source'] in selectednodes or e['target'] in selectednodes:
    self.edges.append(e);wantednodes.update([e['source'],e['target']])
    for n in [e['source'],e['target']]:
     if n in selectednodes:adj[n].append(e)
  for line in (self.graph/'nodes.jsonl').open():
   n=json.loads(line)
   if n['id'] in wantednodes:self.nodes[n['id']]=n
  assert wantednodes<=self.nodes.keys()
  # Pertinent exact parent links are bounded per exemplar; omission counts remain explicit.
  rank={'has_control_regime':0,'has_assumption':1,'has_limitation':2,'has_derivation':3,'uses_method':4,'addresses':5,'derived_from':6,'has_convention':7,'supports':8,'challenges':9,'constrains':10,'specializes':11,'instantiates':12}
  self.unit_edges={};candidate_evidence=set()
  for uid in self.selected:
   u=self.units[uid];es={e['id']:e for n in u['evidence']['sourceNodeIds'] for e in adj[n]};ordered=sorted(es.values(),key=lambda e:(rank.get(e['type'],30),e['id']));self.unit_edges[uid]={'selected':ordered[:12],'omittedCount':max(0,len(ordered)-12),'totalExactIncidentCount':len(ordered)}
   candidate_evidence.update(u['evidence']['anchors'])
   for e in ordered[:12]:
    for n in [e['source'],e['target']]:candidate_evidence.update(self.nodes[n].get('evidence_ids',[]))
  rx=re.compile(r'"id"\s*:\s*"(ev:[^"]+)"')
  for line in (self.graph/'evidence.jsonl').open():
   m=rx.search(line[:700])
   if m and m.group(1) in candidate_evidence:self.evidence[m.group(1)]=json.loads(line)
  for name in ['nodes.jsonl','edges.jsonl','evidence.jsonl']:
   digest=sha(self.graph/name);assert digest==manifest['files'][name]['sha256'];self.graphpins[name]=digest
  # One facet anchor plus source-linked methodological/result/condition context where available.
  # All are reading candidates, not independently verified science or inherited universal premises.
  type_priority={'method':0,'derivation':1,'claim':2,'control_regime':3,'limitation':4,'assumption':5,'convention':6}
  for uid in self.selected:
   u=self.units[uid];first=list(u['evidence']['anchors']);neighbors={n for e in self.unit_edges[uid]['selected'] for n in [e['source'],e['target']]}
   extra=[eid for n in sorted(neighbors,key=lambda n:(type_priority.get(self.nodes[n]['type'],20),n)) for eid in self.nodes[n].get('evidence_ids',[])];seq=first[:1]+extra+first[1:];chosen=[];pages=set()
   def eligible(eid):
    e=self.evidence.get(eid);return e and e['paper_id']==u['paperId'] and e['source_sha256']==u['evidence']['sourceSha256']
   for eid in seq:
    if not eligible(eid) or eid in chosen:continue
    page=self.evidence[eid]['original_evidence']['page']
    if chosen and page in pages:continue
    chosen.append(eid);pages.add(page)
    if len(chosen)==3:break
   for eid in seq:
    if len(chosen)==3:break
    if eligible(eid) and eid not in chosen:chosen.append(eid)
   assert chosen;self.readings[uid]=chosen
  wanted={e for es in self.readings.values() for e in es};self.evidence={k:v for k,v in self.evidence.items() if k in wanted};pagecache={}
  for e in self.evidence.values():
   path=self.up/'papers'/e['paper_key']/'reading-order.json'
   if path not in pagecache:pagecache[path]=(json.loads(path.read_text()),sha(path))
   source,pin=pagecache[path];assert source['source_sha256']==e['source_sha256'];page=e['original_evidence']['page'];text=source['pages'][page-1];quote=e['original_evidence'].get('quote','');position=text.find(quote);start=max(0,position-1100) if position>=0 else 0;end=min(len(text),max(start+3000,position+len(quote)+1100));context=text[start:end]
   e['original_evidence']={k:v for k,v in e['original_evidence'].items() if k!='quote'};e['primaryTextField']='sourceContext.text';e['sourceContext']={'path':str(path.relative_to(self.up)),'fileSha256':pin,'pdfPage':page,'start':start,'end':end,'text':context,'textSha256':hashlib.sha256(context.encode()).hexdigest(),'quoteExactInPage':position>=0,'scope':'Bounded archived primary text; no equation-image or full-paper certification.'}
 def packet(self,key,kind,region,selection):
  ids=selection['visibleMemberIds'] if kind=='leaf' else [];ids=list(ids)+[u for u,_ in selection['picks'] if u not in ids];index={u:i for i,u in enumerate(ids)};selected=dict(selection['picks']);ev=set();nodeindices=collections.defaultdict(list);packetunits=[];contextcoverage=[]
  for uid in ids:
   u=self.units[uid];anchors=self.readings[uid] if uid in selected else [];ev.update(anchors)
   for n in u['evidence']['sourceNodeIds']:nodeindices[n].append(index[uid])
   packetunits.append({'unitIndex':index[uid],'unitId':uid,'paperId':u['paperId'],'description':u['text'],'sourceNodeIds':u['evidence']['sourceNodeIds'],'sourceNodeKinds':[self.nodes[n]['type'] if n in self.nodes else n.split(':')[-2] for n in u['evidence']['sourceNodeIds']],'sourceRecordIds':u['evidence']['sourceRecordIds'],'sourceSha256':u['evidence']['sourceSha256'],'browserVectorRow':u['vectorRow'],'sourceEvidenceIds':anchors,'selectionRole':selected.get(uid,'candidate_member_description'),'readingScope':'Description; supplied primary excerpts only when sourceEvidenceIds is nonempty.'})
   if uid in selected:contextcoverage.append({'unitIndex':index[uid],'exactIncidentCount':self.unit_edges[uid]['totalExactIncidentCount'],'suppliedRelationCount':len(self.unit_edges[uid]['selected']),'omittedExactIncidentCount':self.unit_edges[uid]['omittedCount']})
  es={e['id']:e for uid in selected for e in self.unit_edges[uid]['selected']};pn={n for uid in selected for n in self.units[uid]['evidence']['sourceNodeIds']};rels=[]
  for e in es.values():
   pn.update([e['source'],e['target']]);rels.append({'id':e['id'],'source':e['source'],'target':e['target'],'type':e['type'],'semanticStatus':e['semantic_status'],'directUnitIndices':sorted(set(nodeindices[e['source']]+nodeindices[e['target']])),'evidenceIds':e['evidence_ids'],'statement':'Exact source-object link; retain parent scope and extraction status.','provenance':{k:e['provenance'].get(k) for k in ['record_id','json_pointer']}})
  objects=[{'id':n,'kind':self.nodes[n]['type'],'paperId':self.nodes[n].get('paper_id'),'text':self.nodes[n].get('text',''),'evidenceIds':self.nodes[n].get('evidence_ids',[]),'evidenceScope':self.nodes[n].get('evidence_scope'),'provenance':{k:self.nodes[n].get('provenance',{}).get(k) for k in ['record_id','json_pointer']}} for n in sorted(pn)]
  assert not({u['paperId'] for u in packetunits}|{o['paperId'] for o in objects}|{self.evidence[e]['paper_id'] for e in ev})&self.held
  return {'schemaVersion':'q025-full-description-source-packet/3','familyId':key,'kind':kind,'stage':'proposal','candidateRegionId':region['id'],'candidateMembershipStatus':'Immutable numerical provenance, not an accepted scientific grouping','units':packetunits,'evidence':[self.evidence[e] for e in sorted(ev)],'sourceObjects':objects,'sourceRelations':rels,'graphContextCoverage':contextcoverage,'graphContextScope':'At most12 pertinent exact incident relations per source exemplar. Counts disclose omissions. Relations to a source setting/method/claim are not automatically premises of its physical-question retrieval facet. Graph text is extracted context, not independent primary verification.','existingQuestionRefs':[],'priorQuestionRefs':[],'reservedUnreviewedCount':selection['reservedUnreviewedCount'],'candidateMembershipPinnedExternally':True,'graphPins':self.graphpins,'primaryReadingLimit':'One facet anchor and additional exact source-parent methodological/result/condition anchors where available; bounded original pages only, no images or full-paper verification.'}
