"""Read-only failure forensics; exact prefixes private, only structure/counts public."""
import ast,hashlib,importlib.util,json,re
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;W=B.parents[4]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
parser_path=F/'canonical-recovery-v2/extract_prefix.py'
function=next(n for n in ast.parse(parser_path.read_text()).body if isinstance(n,ast.FunctionDef)and n.name=='parse_attempt')
namespace={'json':json,'hashlib':hashlib}
exec(compile(ast.Module(body=[function],type_ignores=[]),'<isolated pure prefix parser>','exec'),namespace)
parse=namespace['parse_attempt'];reports=[]
spec=importlib.util.spec_from_file_location('frozen_placement_contract',F/'placement-continuation-v1/contract.py');contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract)
for family in ['0002','0007']:
 job='placement-continuation-'+family+'-proposal';d=F/'native-local/placement-continuation-v1/jobs'/job
 receipt=json.loads((d/'receipt.json').read_text());packet=json.loads((d/'packet.actual.json').read_text());raw=d/'reply.stream.raw.txt';text=raw.read_text();assert receipt['status']=='failed'
 prefix=parse(text,0);complete=prefix['completeFields'];rows=complete.get('placements',prefix['completeArrayPrefixes'].get('placements',[]))
 row_checks=[]
 for row in rows:
  contract.structure(row,contract.placement);u=next(x for x in packet['units']if x['ref']==row['unitRef']);expected={(c['reviewRef'],stage)for c in u['priorContexts']for stage in ['proposal','challenge']};actual=[(a['reviewRef'],a['stage'])for a in row['priorAssessments']];assert len(actual)==len(set(actual))and set(actual)==expected
  row_checks.append(row['unitRef'])
 partial_scope=None
 if 'newScopes'in prefix['completeArrayPrefixes']:
  match=re.search(r'"newScopes"\s*:\s*\[\s*(\{)',text)
  if match:
   partial_scope=parse(text,match.start(1))
 private=F/'native-local/placement-continuation-triage-v1'/job;private.mkdir(parents=True,exist_ok=True)
 derived={'originalStreamSha256':sha(raw),'topLevelPrefix':prefix,'partialFirstScope':partial_scope,'adopted':False,'nativeLaunches':0}
 output=private/'extracted-prefix.json';assert not output.exists()or json.loads(output.read_text())==derived,'preserve earlier extraction';output.write_text(json.dumps(derived,ensure_ascii=False,separators=(',',':'))+'\n')
 scopes=(partial_scope or{}).get('completeFields',{});status={k:sum(row['status']==k for row in rows)for k in ['existing_homes','new_scope_proposed','unresolved']}
 report={'jobId':job,'error':receipt['error'],'originalPins':[{'path':str((d/name).relative_to(W)),'sha256':sha(d/name)}for name in ['receipt.json','request.json','packet.actual.json','reply.stream.raw.txt']],'streamCharacters':len(text),'streamBytes':raw.stat().st_size,'streamTruncated':receipt['streamTruncated'],'trailingWhitespaceCharacters':len(text)-len(text.rstrip()),'tabs':text.count('\t'),'singleVersionObjectStart':len(re.findall(r'\{\s*"version"\s*:',text))==1,'fullJsonParses':False,'completeFields':{k:len(v)if isinstance(v,(list,dict))else type(v).__name__ for k,v in complete.items()},'completeArrayPrefixes':{k:len(v)for k,v in prefix['completeArrayPrefixes'].items()},'expectedSourceRows':len(packet['units']),'completePlacementRows':len(rows),'completePlacementRefs':row_checks,'placementRowSchemaAndAllPriorAnnotationsValid':True,'placementStatuses':status,'selectedNewScopeRefs':sorted({h['scopeRef']for row in rows for h in row['homes']if h['scopeRef'].startswith('n')}),'partialFirstNewScopeCompleteFields':list(scopes),'partialFirstNewScopeId':scopes.get('id'),'missingFirstNewScopeFields':sorted(set(contract.proposed['properties'])-set(scopes))if partial_scope else None,'missingTopLevelFields':sorted(set(contract.SCHEMA['properties'])-set(complete)),'privateExtraction':{'path':str(output.relative_to(W)),'sha256':sha(output)},'completeScientificValidation':False,'adoption':False,'newNativeCalls':0}
 try:json.loads(text);report['fullJsonParses']=True
 except json.JSONDecodeError as e:report['parseFailure']={'message':e.msg,'characterOffset':e.pos}
 reports.append(report)
result={'schemaVersion':'q025-placement-whitespace-forensics/1','cases':reports,'parser':{'path':str(parser_path.relative_to(W)),'sha256':sha(parser_path),'execution':'Only parse_attempt function AST executed; original module top-level never imported.'},'interpretation':'Outside-string whitespace loop within a single response stream. Complete source-placement rows retained; missing substantive/required fields are not inferred. No retry, adoption or scientific admission.','originalFilesChanged':False,'nativeLaunches':0}
(B/'report.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps([{'jobId':r['jobId'],'completeRows':r['completePlacementRows'],'expectedRows':r['expectedSourceRows'],'completeFields':r['completeFields'],'partialScopeFields':r['partialFirstNewScopeCompleteFields'],'missingScopeFields':r['missingFirstNewScopeFields'],'trailingWhitespace':r['trailingWhitespaceCharacters']}for r in reports]))
