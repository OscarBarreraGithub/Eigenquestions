import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;W=F.parents[3];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def pin(p):return {'path':str(p.relative_to(W)),'sha256':sha(p)}
def read(p):return json.loads(p.read_text())
items=[]
for d in sorted((F/'native-local/screen-recovery-v1/jobs').iterdir()):
 p=read(d/'packet.actual.json');r=read(d/'reply.json');n=read(d/'normalization.json');sc={s['ref']:s for s in p['scopes']};variants={x['variantRef']:x for x in p['preservedScreen']['attemptVariants']}
 for a in n['attemptVariantReviews']:
  if a['judgment']!='material_conflict':continue
  v=variants[a['variantRef']];selected=r
  for k in v['selectedPath']:selected=selected[k]
  needed={x for x in a['refs']+selected['refs']+v['alternateValue']['refs']if x in sc};scopes=[{k:v for k,v in sc[x].items()if k in ['ref','kind','definition','methods','priorReadingAssessment','scopeStatus','primaryRereadInThisPacket','pairedUnitNotesProvided']}for x in sorted(needed)];bindings={x:{k:v for k,v in p['machineSidecar']['scopeBindings'][x].items()if k in ['recordId','candidateId','admittedDestinationId','definitionSha256','scopeContentSha256']}for x in sorted(needed)}
  items.append({'variantRef':a['variantRef'],'selectedScreen':selected,'alternateScreen':v['alternateValue'],'explicitConflictAssessment':a,'exactFullScopes':scopes,'scopeBindings':bindings,'pins':{'packet':pin(d/'packet.actual.json'),'reply':pin(d/'reply.json'),'normalization':pin(d/'normalization.json'),'receipt':pin(d/'receipt.json')},'identityScreenUnchanged':selected['identityScreen']==v['alternateValue']['identityScreen'],'sourceReadingLimit':'Full existing scope definitions and inherited scope assessments only. No new primary or complete per-unit attribution reading is claimed.','currentStatus':'withheld_connection_conflict_not_a_scientific_relation_admission'})
assert len(items)==6 and all(x['identityScreenUnchanged']for x in items);out=F/'native-local/screen-conflict-intake-v1';out.mkdir(exist_ok=True);op=out/'six-conflicts.json';op.write_text(json.dumps({'schemaVersion':'q025-six-screen-conflict-intake/1','items':items,'noAutomaticResolution':True,'finding':'All six retained conflicts leave the original identity-screen category unchanged. Five change possible-connection sets; one adds an unsupported family-wide relaxation prerequisite. None is an actual admitted route or equality.'},ensure_ascii=False,indent=2)+'\n');report={'intake':pin(op),'bytes':op.stat().st_size,'caseCount':6,'identityScreenUnchangedInAllSix':True,'identityCategories':[x['selectedScreen']['identityScreen']for x in items],'scientificConnectionResolution':'pending_coordinator_or_bounded_existing-definition_decision','noNewModelCalls':True};(B/'index.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
