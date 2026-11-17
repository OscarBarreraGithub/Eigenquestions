"""Earlier nominations do not disappear when lexical IDF changes."""
import json,hashlib,copy
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent;Q=E.parent;W=Q.parent.parent;L=F/'native-local/canonical-wave-v1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();index=json.loads((B/'compacted-index.json').read_text());receiptpath=Q/'assembly/reconciliation-refresh-v3.json';prior=json.loads(receiptpath.read_text())['priorNominationsStillPending'];families=index['families'];packets=[json.loads((E/f['sourcePacketPath']).read_text())for f in families];queued={n['id']for p in packets for n in p['nominations']};added=[];newpackets=[]
# Load only merge's definitions/metadata, not its executable packing loop.
ns={'__file__':str(B/'compact_batches.py')};exec((B/'compact_batches.py').read_text().split('packets=[json.loads')[0],ns);merge=ns['merge']
def subset(packet,rid):
 out=copy.deepcopy(packet);out['scopes']=[s for s in out['scopes']if s['recordId']==rid];wanted=set(out['scopes'][0]['evidenceRefs'])|{c['unitRef']for c in out['scopes'][0]['sourceContributions']};out['units']=[u for u in out['units']if u['ref']in wanted];out['evidence']=[e for e in out['evidence']if e['ref']in wanted];out['refRegistry']={r:m for r,m in out['refRegistry'].items()if r in wanted};out['nominations']=[];return out
for pair in prior:
 if pair['id']in queued:continue
 found=False
 for p in packets:
  mapping={s['recordId']:s['ref']for s in p['scopes']}
  if set(pair['recordIds'])<=set(mapping) and len(p['nominations'])<40:
   p['nominations'].append({'id':pair['id'],'left':mapping[pair['recordIds'][0]],'right':mapping[pair['recordIds'][1]],'channels':pair['nominationChannels'],'status':'retained_prior_nomination_not_equivalence'});p['coverage']['nominatedPairs']=len(p['nominations']);found=True;break
 if not found:
  source=[next(p for p in packets if any(s['recordId']==rid for s in p['scopes']))for rid in pair['recordIds']];p=merge([subset(s,rid)for s,rid in zip(source,pair['recordIds'])]);mapping={s['recordId']:s['ref']for s in p['scopes']};p['nominations']=[{'id':pair['id'],'left':mapping[pair['recordIds'][0]],'right':mapping[pair['recordIds'][1]],'channels':pair['nominationChannels'],'status':'retained_prior_nomination_not_equivalence'}];p['coverage']['nominatedPairs']=1;assert len(json.dumps(p,ensure_ascii=False,separators=(',',':')))<=280000;newpackets.append(p)
 queued.add(pair['id']);added.append(pair['id'])
# Pack small residual prior-pair cases together without inventing a common family.
for p in newpackets:
 fitted=False
 for i,current in enumerate(packets):
  if len(current['scopes'])+len(p['scopes'])>20 or len(current['nominations'])+len(p['nominations'])>40:continue
  trial=merge([current,p]);
  if len(json.dumps(trial,ensure_ascii=False,separators=(',',':')))<=280000:packets[i]=trial;fitted=True;break
 if not fitted:packets.append(p)
rows=[]
for i,p in enumerate(packets):
 key=f'global-canonical-{i+1:04}';p['familyId']=key;path=L/'sources-final'/f'{key}.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(p,ensure_ascii=False,separators=(',',':'))+'\n');rows.append({'familyId':key,'sourcePacketPath':str(path.relative_to(E)),'sourcePacketSha256':sha(path),'characters':len(path.read_text()),'recordIds':[s['recordId']for s in p['scopes']],'pairIds':[n['id']for n in p['nominations']],'counts':p['coverage']})
assert len(added)==42;assert {r for f in rows for r in f['recordIds']}=={r for f in index['families']for r in f['recordIds']};out={**index,'families':rows,'priorPendingReceipt':{'path':str(receiptpath.relative_to(W)),'sha256':sha(receiptpath)},'retainedPriorPairIds':added,'coverage':{**index['coverage'],'queuedNominations':index['coverage']['queuedNominations']+42,'cumulativeNominations':index['coverage']['globalNominations']+42,'batches':len(rows),'proposedCalls':2*len(rows),'availablePrimaryWindows':sum(x['counts']['availablePrimaryWindows']for x in rows),'providedPrimaryWindows':sum(x['counts']['primaryWindows']for x in rows)}};(B/'final-source-index.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out['coverage']))
