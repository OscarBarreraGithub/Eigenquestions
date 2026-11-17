"""Compact, reproducible coverage receipt for the expanded admitted-scope registry."""
import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent;ROOT=B.parents[2]
def read(p,expected=None):
    path=ROOT/p;raw=path.read_bytes();h=hashlib.sha256(raw).hexdigest()
    if expected:assert h==expected
    return json.loads(raw),{'path':str(p),'sha256':h,'bytes':len(raw)}
registry,rpin=read('research/q025/evaluation/full-pass/reconciliation-v1/authored-scope-registry-v3-20261117T121953Z.json','c9c419d7ded388f1355e31b1bef413ab09ca12de0e7cd60be996f687655fcf8a')
current,cpin=read('research/q025/assembly/outputs/scope-candidates-v3/candidates.json','7dbe13c22c7d464abd7fa37d72fe8c3d969e1417de8770ff384fbf5eed6eb35c')
oldpairs={};previous=[]
for version in [1,2]:
    value,pin=read(f'research/q025/assembly/outputs/scope-candidates-v{version}/candidates.json');previous.append(pin);oldpairs.update({p['id']:p for p in value['pairs']})
currentids={p['id'] for p in current['pairs']};prioronly=[p for id,p in oldpairs.items() if id not in currentids]
records={r['recordId']:r for r in registry['records']};admitted=[]
for r in records.values():
    if not r.get('admittedDestinationId'):continue
    pairs=[p for p in current['pairs'] if r['recordId'] in p['recordIds']]
    admitted.append({'recordId':r['recordId'],'admittedDestinationId':r['admittedDestinationId'],'candidateId':r['candidateId'],'scopeContentSha256':r['scopeContentSha256'],'candidates':[{'pairId':p['id'],'otherRecords':[{'recordId':id,'title':records[id]['definition']['title']} for id in p['recordIds'] if id!=r['recordId']],'channels':p['nominationChannels'],'sharedUnitIds':p['sharedUnitIds']} for p in pairs],'status':'explicitly_pending_comparison' if pairs else 'unmatched_review_required_not_certified_unique'})
manual,mpin=read('research/q025/assembly/reconciliation-refresh-v2.json','975362d59128b5e6ed4d376ce3a8c692bf0c915683da7d209c05552b01916ff1')
manual_checks=[]
for group in manual['neighborhoods']:
    for old in group['records']:
        now=records[old['recordId']];assert now['definition']==old['definition'];manual_checks.append({'recordId':old['recordId'],'definitionUnchanged':True,'candidateId':now['candidateId']})
report={'schemaVersion':'q025-reconciliation-refresh/3','status':'nomination_and_coverage_plan_not_admission','registry':rpin,'currentCandidates':cpin,'previousCandidatePins':previous,'counts':{'scopes':len(records),'questions':sum(r['kind']=='question' for r in records.values()),'currentPairs':len(currentids),'scopesWithCurrentCandidates':len(records)-len(current['unmatched']),'unmatchedScopes':len(current['unmatched']),'priorPairsNotRenominated':len(prioronly),'cumulativePairs':len(currentids)+len(prioronly),'admittedScopesPreserved':len(admitted),'admittedScopeCrossReviewPairs':sum(len(a['candidates']) for a in admitted),'admittedScopeSharedSourcePairs':sum(bool(p['sharedUnitIds']) for a in admitted for p in a['candidates'])},'admittedScopeCoverage':admitted,'priorNominationsStillPending':prioronly,'sourceGroundedNeighborhoodReceipt':mpin,'sourceGroundedDefinitionsStillExact':manual_checks,'scientificReadingCautions':['The five present KK-to-wave nominations are weak vocabulary/target nominations with no exact shared source. Flat-dimension freeze-in versus Higgs stability and linear KK cosmology versus vacuum decay are explicit likely contrast cases, not proposed equivalences.','No match for thermal production, threshold dynamics or UHECR presently certifies uniqueness. Their exact stable IDs remain in the same registry and unmatched review queue.','Gauss–Bonnet inflation versus late-time phantom dynamics remains a compound-source/method-bridge review target; the nine previously inspected definitions remain exact in this snapshot.','Original review-bin regions and parent c/x references are not new canonical scientific identities. Reused parent question IDs must converge to the same accepted target.'],'completionGates':['Every final authored/admitted scope requires an explicit canonical disposition, including unmatched records; bounded pair review alone is insufficient.','Retain all nominated-but-unreviewed pairs across registry versions; changes in lexical IDF do not clear a pending identity comparison.','Keep known distinction, changed-premise and specialization constraints when checking any complete canonical group; common-target parents are not equivalence unions.','After canonical decisions, admit each source home separately with scope/premise compatibility and normalized compound weights; contributions do not supply mass automatically.','Final geometry uses admitted scientific homes and exact global question-per-paper counts; original numerical bins survive as provenance only.'],'noNewScienceAdmission':True,'noSealedHoldoutAccess':True}
out=B/'reconciliation-refresh-v3.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'path':str(out.relative_to(ROOT)),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'counts':report['counts']},indent=2))
