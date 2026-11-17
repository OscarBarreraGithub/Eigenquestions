"""Proposed coordinator class; independent full reassertion is kept explicit."""
import collections,hashlib,json,re
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent;W=E.parents[2];f=F/'native-local/parent-route-admissions-v1/route-audit.json';rows=json.loads(f.read_text())['rows'];classrows=[];held=[]
for r in rows:
 if r['class']not in['exact_statement_and_reference_metadata_reasserted','same_statement_evidence_changed_or_referenced_differently','independent_reworded_statement_requires_condition_comparison']:continue
 flags=[];reasontexts=[r['currentReason']]+[x['priorReason']for x in r['comparisons']]
 for s in reasontexts:
  if re.search(r'\b(?:and|or|but|the|a|an|of|to|with|under|than|that|where|which|from|must|also|as|for|into|by|without)\s*$',s,re.I)or s.endswith((' ','-','–','—')):flags.append('possible_incomplete_clause')
  if re.search(r'provenance.only|provenance assessment|not a public|not public|review.batch provenance',s,re.I):flags.append('explicit_provenance_or_nonpublic_language')
 if r['nativeType']not in['narrows','related','comparison']:flags.append('direction_or_application_semantics_needs_explicit_decision')
 # The full prior reassertion must have its own stated rationale and reference.
 if not r['currentRefs']or not any(x['priorRefs']and x['priorReason'].strip()for x in r['comparisons']):flags.append('missing_independent_reason_or_evidence')
 if flags:held.append({'id':r['id'],'nativeType':r['nativeType'],'flags':sorted(set(flags))});continue
 classrows.append(r)
counts=collections.Counter(r['nativeType']for r in classrows);edges={};adj=collections.defaultdict(set)
for r in classrows:
 k=(r['sourceId'],r['targetId'],r['nativeType']);edges.setdefault(k,[]).append(r['id'])
 if r['nativeType']=='narrows':adj[r['sourceId']].add(r['targetId'])
active=set();done=set();cycle=[]
def visit(v,path):
 if v in active:cycle.append(path[path.index(v):]+[v]);return
 if v in done:return
 active.add(v)
 for w in sorted(adj[v]):visit(w,path+[v])
 active.remove(v);done.add(v)
for v in list(adj):visit(v,[])
# Deterministic diverse reading examples, including exact and independently
# rephrased routes. Selection is not a scientific classification.
chosen=[]
for prefix,num in [('parent-00602c',14),('parent-00602c',22),('parent-00ca19',4),('parent-10605',9),('parent-278f3',6),('parent-278f3',24),('parent-2ad7',45),('parent-5705',29),('parent-d52c',22),('successor2-parent-c877',17)]:
 match=next((r for r in classrows if r['id'].startswith(prefix)and r['id'].endswith(':link:'+str(num))),None)
 if match:chosen.append(match['id'])
report={'schemaVersion':'q025-parent-route-class-proposal/1','input':{'path':str(f.relative_to(W)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()},'candidateIndependentReassertions':len(classrows),'uniqueDirectedTypedEdges':len(edges),'candidateCounts':dict(counts),'heldAfterPairedAdmittedEndpointFilter':len(held),'holdReasons':dict(collections.Counter(x for r in held for x in r['flags'])),'narrowerCyclesDetected':cycle,'representativeCandidateIds':chosen,'policyStatus':'awaiting_root_coordinator_class_authorization','scientificReadingBasis':'The independent parent challenge separately authors a complete final scoped link with its own rationale and citations under its original instructions. Both endpoint definitions are independently admitted. This is not a retroactive supported_as_written field or agreement inferred from endpoint presence. Both complete statements and evidence lineages remain attached.','proposedTypeMap':{'narrows':'narrower','related':'related_question','comparison':'comparison'},'strictExclusions':['649source/provenance endpoints','356unadmitted endpoint scopes','56new/changed endpoint-type rows among admitted scopes','method/application/premise_check/broadens require separate direction/applicability decision','Possible unfinished or explicitly provenance-only statements remain held','Cycles cannot become accepted containment'],'readingLimit':'No new primary reading or scientific-result verification. Source-local conditions are inherited from exact endpoint scopes and both full route statements. Conservative use of canonical target title supplies an already-reviewed outgoing label, not an invented action phrase.'};(B/'class-proposal.json').write_text(json.dumps(report,indent=2)+'\n');out=F/'native-local/parent-route-admissions-v1/class-candidates.json';out.write_text(json.dumps({'report':report,'candidateRows':classrows,'held':held},ensure_ascii=False,separators=(',',':'))+'\n');print(json.dumps(report))
