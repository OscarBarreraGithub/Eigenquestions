#!/usr/bin/env python3
import json,collections,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;WORK=HERE.parents[2];UP=Path('/Users/emmy/Developer/physics-atlas-swampland');G=UP/'components/atlas_graph/output/20261104-foundation-v3'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 units=[u for f in (WORK/'data/navigation').glob('units-*.json') for u in json.loads(f.read_text())];qs=[u for u in units if u['lens']=='physical_question'];node_to_units=collections.defaultdict(set)
 for u in units:
  for n in u['evidence']['sourceNodeIds']:node_to_units[n].add(u['id'])
 qids={u['id'] for u in qs};edge_types=collections.Counter();statuses=collections.Counter();direct=collections.defaultdict(set);contexts=collections.defaultdict(set);examples={};types_by_status=collections.defaultdict(collections.Counter)
 for line in (G/'edges.jsonl').open():
  e=json.loads(line);t=e['type'];status=e['semantic_status'];edge_types[t]+=1;statuses[status]+=1;types_by_status[status][t]+=1
  if t not in examples:examples[t]={k:e[k] for k in ['source','target','type','semantic_status','evidence_ids']}
  endpoints=node_to_units.get(e['source'],set())|node_to_units.get(e['target'],set())
  if t not in ['contains','literal_identifier_mention']:
   for uid in endpoints:direct[uid].add(t)
  if t in ['has_assumption','has_convention','has_control_regime','has_limitation','has_derivation']:
   for uid in node_to_units.get(e['source'],set()):contexts[uid].add(t)
 counts={t:sum(t in ts for uid,ts in contexts.items() if uid in qids) for t in ['has_assumption','has_convention','has_control_regime','has_limitation','has_derivation']}
 manifest=json.loads((G/'MANIFEST.json').read_text())
 out=dict(schemaVersion='q025-rich-source-context-audit/1',foundationManifestSha256=sha(G/'MANIFEST.json'),nodeCounts=manifest['counts'],edgeTypes=dict(edge_types),edgeSemanticStatuses=dict(statuses),edgeTypesBySemanticStatus={k:dict(v) for k,v in types_by_status.items()},questionUnitCount=len(qs),questionUnitsWithNoncontainmentIncidentRelation=sum(uid in direct for uid in qids),questionUnitsWithDirectAttachedContextByType=counts,joinKeys={'unit_to_source_nodes':'navigation.units[].evidence.sourceNodeIds[] -> nodes.id','unit_to_facets':'navigation.units[].evidence.facetIds[] -> retrieval-facets.id','facet_to_node':'retrieval-facets.node_id -> nodes.id','facet_vector':'navigation originalEmbeddingRows correspond only after embedding row manifest identity validation; do not assume JSONL ordinal is vector row','edge_to_nodes':'edges.source / edges.target -> nodes.id','node_to_evidence':'nodes.evidence_ids[] -> evidence.id; retain evidence_scope','edge_to_evidence':'edges.evidence_ids[] -> evidence.id','node_to_original_record':'nodes.provenance.record_id -> source-records.id; retain bundle hash, source_unit_id and JSON pointer','record_to_file':'source-records.path + record hash under upstream root','paper_context':'nodes.paper_node_id and paper_id; same paper is context, not automatic premise compatibility'},safeAttachmentLayers=[{'kind':'direct_record_relation','meaning':'Exact scoped local relation; preserve semantic_status, direction and evidence.'},{'kind':'shared_extraction_window_context','meaning':'Sibling record/window material; useful supporting context, not a demonstrated logical premise of every question.'},{'kind':'same_paper_context','meaning':'Additional paper material; never attach every paper assumption to every question as if proven applicable.'}],examples=examples,limits=['This scan reconstructs identities and counts, not scientific validation.','A source-local assertion, extraction inference, and local nomination are distinct; do not collapse them.','97 admitted cross-paper scientific relations are in the separate current receipt ledger.','A direct attachment can inherit source evidence rather than independently anchor a child claim.'])
 (HERE/'rich-context-joins.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ['edgeSemanticStatuses','questionUnitCount','questionUnitsWithNoncontainmentIncidentRelation','questionUnitsWithDirectAttachedContextByType']},indent=2))
if __name__=='__main__':main()
