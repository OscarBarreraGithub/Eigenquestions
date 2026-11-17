"""Package manually authored judgments; mechanical checks do not establish scientific support."""
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5]
HERE=Path(__file__).resolve().parent
INPUT=Path('research/q025/evaluation/full-pass/native-local/placement-cut04-review-v1/product-70-scopes.json')
EXPECTED='eccddd693841192e844fb1d79370224913073110271189cbdfe99aa1e22c618b'
sha=lambda b:hashlib.sha256(b).hexdigest()
raw=(ROOT/INPUT).read_bytes(); assert sha(raw)==EXPECTED
packet=json.loads(raw); notes=json.loads((HERE/'decisions-in-progress.json').read_text())
rows={r['index']:r for r in packet['rows']}; assert sorted(r['index'] for r in notes['rows'])==packet['assignedIndices']
assert len({r['index'] for r in notes['rows']})==70
inventory=packet['rows'][0]['globalExistingScopeLookup']['inventory']
aggregate=json.loads((ROOT/inventory['path']).read_text())
definitions={x['id']:x for x in aggregate['destinations']}
for row in packet['rows']:
 for c in row['globalExistingScopeLookup']['candidates']:definitions[c['id']]=c['definition']
classification_path='research/q025/geometry/physics-entrance/results/destinations.json'
classifications=json.loads((ROOT/classification_path).read_text())
definitions.update({x['id']:x for x in classifications})
checked={}
def check_refs(x):
 if isinstance(x,dict):
  if isinstance(x.get('path'),str) and isinstance(x.get('sha256'),str) and len(x['sha256'])==64:
   path=x['path']
   if path not in checked:
    data=(ROOT/path).read_bytes(); assert sha(data)==x['sha256'],path
    if 'bytes' in x:assert len(data)==x['bytes'],path
    checked[path]={'path':path,'sha256':sha(data),'bytes':len(data)}
  for v in x.values():check_refs(v)
 elif isinstance(x,list):
  for v in x:check_refs(v)
check_refs(packet)
checked[str(INPUT)]={'path':str(INPUT),'sha256':EXPECTED,'bytes':len(raw)}
cb=(ROOT/classification_path).read_bytes();checked[classification_path]={'path':classification_path,'sha256':sha(cb),'bytes':len(cb)}
final=[]
for note in notes['rows']:
 r=rows[note['index']]; definition=r['definition']; assert sha(json.dumps(definition,ensure_ascii=False,separators=(',',':')).encode())==r['definitionSha256']
 candidates=r['globalExistingScopeLookup']['candidates']
 entry_id=note.get('entryDestinationId') or candidates[note['entryCandidate']]['id']; assert entry_id in definitions
 endpoint=definitions[entry_id]
 contrasts=list(note.get('contrastsRead',[]))
 for field in ['entryCandidate']:
  if field in note:contrasts.append(candidates[note[field]]['id'])
 for j in note.get('additionalContrasts',[]):contrasts.append(candidates[j]['id'])
 contrasts.append(entry_id);contrasts=list(dict.fromkeys(contrasts))
 cross=note.get('crossCutContrastsRead',[])
 if note['index']==53:cross=sorted(set(cross+[91]))
 entry={'direction':'entry_neighbor_to_reviewed_scope','type':note['type'],'rationale':note['entryRationale'],'wholeEndpointDefinitionsRead':True,'endpointTitle':endpoint['title'],'endpointDefinitionSha256':sha(json.dumps(endpoint,ensure_ascii=False,separators=(',',':')).encode())}
 if entry_id.startswith('pending-placement-scope:'):
  _,family,stage,ref=entry_id.split(':');entry['pendingScope']={'familyId':family,'stage':stage,'localRef':ref};entry['admissionRequiredBeforeLink']=True
 else:entry['destinationId']=entry_id
 if note.get('metadataOnly'):
  assert endpoint['metadataOnly'] is True
  entry.update(metadataOnly=True,scientificContainment=False,transfersHMass=False,policy='Root-approved metadata-only collection navigation; no scientific implication.')
 final.append({'index':r['index'],'familyId':r['familyId'],'stage':r['stage'],'localRef':r['localRef'],'definitionSha256':r['definitionSha256'],'status':'eligible_unchanged_class','reason':note['reason'],'closestContrastIds':contrasts,'additionalCurrentCutContrastIndices':cross,'entry':entry,'sourceUnitIds':[s['unitId'] for s in r['sources']],'paperIds':sorted(set(s['paperId'] for s in r['sources'])),'completeSourceDescriptionsRead':True,'bothOriginalAnnotationsRead':True,'bothCurrentPlacementJudgmentsRead':True,'independentDefinitionAssessmentRead':True,'definitionUnchanged':True,'readingCoverageRetained':definition['readingCoverage'],'limits':['Description-and-paired-review scope assessment only; no new primary text was read and no calculation or physical conclusion was verified.','This review finds no established same-scoped-question duplicate among the inspected full candidates and current-cut contrasts; it does not certify global uniqueness.','Historical truncation, unresolved prior attribution and source-era qualifications remain in the exact frozen records.','Entry is qualified navigation only; it does not imply scientific equivalence, method applicability, source-role promotion or allocation mass.']})
result={'schemaVersion':'1.0.0','kind':'delegated-unchanged-scope-review','status':'complete_for_coordinator_intake','reviewer':'atlas_product_integration','input':checked[str(INPUT)],'assignment':packet['assignedIndices'],'basis':'Root-authorized delegated full-scope review of unchanged independently retained definitions. Eligibility applies to the approved admission class; evaluator/geometry compile the combined component. It is not a claim that root personally read these seventy scopes.','rows':final,'summary':{'assigned':70,'reviewed':70,'eligibleUnchangedClass':70,'possibleDuplicate':0,'needsAdjudication':0,'scientificEntrySuggestions':68,'metadataOnlyEntrySuggestions':2,'newPrimaryReads':0,'scopeDefinitionsEdited':0,'sourceUnits':len({u for r in final for u in r['sourceUnitIds']})},'entryLimits':'Outgoing entry-neighbor to new scope; related/comparison links preserve both endpoint scopes. Pending entries require actual admitted endpoint resolution. Metadata portals use an existing vocabulary node and create no scientific narrower edge or H mass. All final links remain subject to the common compiler/policy gate.','verification':{'inputPins':sorted(checked.values(),key=lambda x:x['path']),'definitionHashEncoding':'SHA-256 of supplied definition JSON in original insertion order, UTF-8, compact separators, ensure_ascii=False','mechanicalChecksDoNotReplaceScientificReview':True}}
(HERE/'review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'rows':len(final),'pins':len(checked),'summary':result['summary'],'reviewSha256':sha((HERE/'review.json').read_bytes())}))
