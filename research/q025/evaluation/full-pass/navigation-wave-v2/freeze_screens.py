"""Complete screen intake; six variant conflicts remain explicitly withheld."""
import collections,hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent;W=E.parents[2];L=F/'native-local/navigation-wave-v2';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pin(p):return {'path':str(p.relative_to(W)),'sha256':sha(p)}
paths=[]
for campaign in ['canonical-triage-v1','canonical-triage-wave-v2']:
 for d in sorted((F/'native-local'/campaign/'jobs').glob('*')):
  if(d/'receipt.json').exists()and json.loads((d/'receipt.json').read_text())['status']=='complete':paths.append(d)
paths+=sorted((F/'native-local/screen-recovery-v1/jobs').glob('*completion'))+sorted((F/'native-local/screen-recovery-v1/adopted').glob('*'))
records={};receipts=[];conflicts=[]
for d in paths:
 receipt=json.loads((d/'receipt.json').read_text());assert receipt['status']=='complete'and receipt['normalizedReplySha256']==sha(d/'reply.json');p=json.loads((d/'packet.actual.json').read_text());r=json.loads((d/'reply.json').read_text());n=json.loads((d/'normalization.json').read_text());withheld={x['selectedPath'][1]:x for x in n.get('withheldComponents',[])if x['selectedPath'][0]=='comparisonReviews'};side=p['machineSidecar'];nom={x['ref']:x for x in p['nominations']};scopes=side['scopeBindings'];receipts.append({'jobId':d.name,'reply':pin(d/'reply.json'),'receipt':pin(d/'receipt.json'),'packet':pin(d/'packet.actual.json'),'normalization':pin(d/'normalization.json')})
 for i,row in enumerate(r['comparisonReviews']):
  source=nom[row['ref']];ids=sorted([scopes[source['left']]['recordId'],scopes[source['right']]['recordId']]);key=hashlib.sha256('\n'.join(ids).encode()).hexdigest()[:24];entry=records.setdefault(key,{'comparisonId':key,'recordIds':ids,'screens':[],'workloadIds':set(),'scientificAdmission':False,'variantConflictWithheld':False});binding=side['comparisonBindings'][row['ref']];workload=binding.get('nominationIds',binding.get('workloadIds',binding.get('originalIds')));assert workload,'Missing original workload IDs';entry['workloadIds'].update(workload);entry['screens'].append({'jobId':d.name,'ref':row['ref'],'judgment':row,'nominationChannels':source.get('channels',[]),'variantConflictWithheld':i in withheld})
  if i in withheld:entry['variantConflictWithheld']=True;conflicts.append({'comparisonId':key,'jobId':d.name,'ref':row['ref'],**withheld[i]})
def lane(e):
 if e['variantConflictWithheld']:return 'explicit_variant_conflict_withheld'
 ids={x['judgment']['identityScreen']for x in e['screens']};conn={v for x in e['screens']for v in x['judgment']['scientificConnections']}
 if 'plausible_same_scope'in ids:return 'priority_existing_scope_reuse'
 if ids&{'specialization_candidate','common_target_candidate'}:return 'organization_and_shared_question_decision'
 if conn-{'none_identified','unresolved'}:return 'possible_typed_connection_decision'
 if ids=={'different_scoped_targets'}:return 'retained_definition_contrast_screen_only'
 return 'unresolved_context_needed'
for e in records.values():e['workloadIds']=sorted(e['workloadIds']);e['lane']=lane(e)
assert len(receipts)==121 and len(conflicts)==6
L.mkdir(parents=True,exist_ok=True);out=L/'combined-screen-intake.json';data={'schemaVersion':'q025-complete-screen-intake/2','inputReceipts':receipts,'comparisons':list(records.values()),'withheldVariantConflicts':conflicts,'allScientificAdmissions':False,'sourceReadingMeaning':'Definition/description screening with scope-level review notes; full paired unit reasons and consequential primary premises are supplied only in later decision packets.','priorRichPilotNominationsDeferred':18};out.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n');report={'schemaVersion':'q025-complete-screen-report/2','completedLogicalCalls':121,'original117Statuses':{'complete':114,'failed_preserved':3},'recoveryCalls':2,'deterministicAdoptions':1,'pilotCalls':4,'uniqueComparisons':len(records),'uniqueWorkloadIds':len({x for e in records.values()for x in e['workloadIds']}),'lanes':dict(collections.Counter(e['lane']for e in records.values())),'withheldVariantConflicts':conflicts,'intake':pin(out),'allAutomaticAdmissions':0};(B/'screen-intake-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
