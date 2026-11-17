#!/usr/bin/env python3
"""Read-only whole-wave input audit and bounded-output stress measurement."""
import copy,hashlib,json,sys
from pathlib import Path
B=Path(__file__).resolve().parent;E=B.parent;W=E.parents[2];L=B/'native-local'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
from test_contract import fixture
from validate_contract import validate
m=json.loads((B/'wave-manifest.json').read_text());p=json.loads((L/'pilot.json').read_text());assert sha(L/'pilot.json')==m['pilotSha256'];assert len(p['jobs'])==24
reserved={x['paperId'] for x in json.loads((E/'final-holdout-reservation.local.json').read_text())['records']}
exposure=json.loads((L/'source-exposure.local.json').read_text());assert not(set(exposure['freshPapers'])&set(exposure['previousAndWaveDescriptionPapers']));assert len(exposure['freshPapers'])==48
units={u['id']:u for f in sorted((W/'data/navigation').glob('units-*.json')) for u in json.loads(f.read_text())};seen=[]
for j in p['jobs']:
 d=L/'jobs'/j['jobId'];r=json.loads((d/'request.json').read_text());pk=json.loads((d/'packet.json').read_text());assert sha(d/'request.json')==j['requestSha256'];assert sha(d/'packet.json')==r['packetSha256'];assert sha(d/'prompt-base.txt')==r['promptBaseSha256'];assert sha(L/'review-schema.json')==r['schemaSha256'];assert r['maxOutputCharacters']==180000
 assert [u['unitIndex'] for u in pk['units']]==list(range(len(pk['units'])))
 assert not ({u['paperId'] for u in pk['units']}|{o.get('paperId') for o in pk['sourceObjects']}|{e['paper_id'] for e in pk['evidence']})&reserved
 for u in pk['units']:
  original=units[u['unitId']];assert u['description']==original['text'] and u['paperId']==original['paperId'] and u['sourceNodeIds']==original['evidence']['sourceNodeIds']
  assert set(u['sourceEvidenceIds'])<={e['id'] for e in pk['evidence']}
 if pk['stage']=='fresh':assert all(u['paperId'] in exposure['freshPapers'] for u in pk['units'])
 seen.append({'jobId':j['jobId'],'descriptions':len(pk['units']),'promptCharacters':len((d/'prompt-base.txt').read_text()),'sourceExcerptUnits':sum(bool(u['sourceEvidenceIds']) for u in pk['units'])})
# Stress fixture exercises maximal family count, eight cards, 20 factors and nontrivial notes.
sp,so=fixture();n=max(x['descriptions'] for x in seen);a=so['unitAssessments'][0]
so['unitAssessments']=[dict(a,unitIndex=i,note='Explicit description supports this target; detailed source assumptions remain unverified.') for i in range(n)]
so['questionCards']=[dict(copy.deepcopy(so['questionCards'][0]),localId=f'q{k}') for k in range(8)]
so['factorDictionary']=[dict(copy.deepcopy(so['factorDictionary'][0]),id=f'f{k}',supportingUnitIndices=list(range(n))) for k in range(20)]
compact=len(json.dumps(so,separators=(',',':')));indented=len(json.dumps(so,indent=2));assert compact<180000 and indented<180000
max_prompt=max(x['promptCharacters'] for x in seen);schema_chars=len(json.dumps(json.loads((L/'review-schema.json').read_text()),separators=(',',':')))
out={'schemaVersion':'q025-wave-prelaunch-audit/1','status':'passed_read_only_no_native_launch','jobs':len(seen),'reservedPapersConsumed':0,'freshPreviouslyExposedPapers':0,'freshDistinctPapers':48,'allDescriptionsMatchFrozenSource':True,'allRequestPacketPromptSchemaHashesMatch':True,'largestDescriptionCount':n,'maxBasePromptCharacters':max_prompt,'compactSchemaCharacters':schema_chars,'stressOutput':{'units':n,'questionCards':8,'factorDictionaryEntries':20,'compactCharacters':compact,'indentedCharacters':indented,'hardLimitCharacters':180000,'interpretation':'Constructed plausible-load stress case, not a mathematical upper bound over arbitrary prose. Runtime preserves raw outputs and fails explicitly if the limit is exceeded.'},'conservativeInitialCombinedTokens':(max_prompt+schema_chars+180000+2)//3+16000,'contextPolicy':'Default272k tokens,95% effective258400. Guard220k for chars/3 estimate including actual compact dependency, schema, max response and16k reasoning/protocol headroom. This is a sizing estimate, not exact tokenization. Oversize jobs fail before model start and require explicit splitting; no truncation/retry.','jobsMeasured':seen}
(B/'prelaunch-audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='jobsMeasured'},indent=2))
