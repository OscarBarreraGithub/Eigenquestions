"""Deterministic private evidence bundle; no execution/account configuration."""
import gzip,hashlib,json,tarfile
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;W=F.parents[3]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def pin(p):return {'path':str(p.relative_to(W)),'sha256':sha(p),'bytes':p.stat().st_size}
def read(p):return json.loads(p.read_text())
paths=set()
for rel in ['parent-route-admissions-v1/route-audit.json','parent-route-admissions-v1/class-candidates.json','parent-route-admissions-v1/coordinator-intake.json','parent-route-admissions-v1/direction-intake.json','parent-route-admissions-v1/admitted-component.json','parent-route-admissions-v2/class-candidates.json','parent-route-admissions-v2/admitted-component.json']:
 paths.add(F/'native-local'/rel)
for rel in ['parent-route-admissions-v1/admitted-component.json','parent-route-admissions-v2/admitted-component.json']:
 for r in read(F/'native-local'/rel)['reviewRegistry']:
  d=(W/r['path']).parent
  for name in ['reply.json','reply.raw.txt','receipt.json','normalization.json','packet.actual.json','packet.json','request.json','dispatch-request.json']:
   p=d/name
   if p.exists():paths.add(p)
# All paths come from an explicit scientific artifact allow-list. Never package
# native account/execution files, queue state, live logs or environment data.
rows=[pin(p)for p in sorted(paths)];manifest={'schemaVersion':'q025-private-parent-evidence-bundle/1','fileCount':len(rows),'uncompressedBytes':sum(x['bytes']for x in rows),'files':rows,'alreadyArchivedScopeInputs':['admissions-v5/supported-scope-role-component-v5.json'],'meaning':'Exact latest successful parent review payloads, replies, normalization/receipt lineage and admitted route/intake artifacts. Private bounded primary passages remain private. This is not a new reading or permanent-storage claim.','excluded':['Account/helper/execution configuration','Credentials/environment','Queue state/live logs','Full primary-paper archive and existing scope corpus (separately preserved)']};(B/'bundle-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');out=F/'native-local/parent-evidence-archive-v1';out.mkdir(exist_ok=True);tar=out/'parent-evidence-v1.tar.gz'
with tar.open('wb')as raw:
 with gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0)as gz:
  with tarfile.open(fileobj=gz,mode='w|')as tf:
   for p in sorted(paths):
    info=tarfile.TarInfo(str(p.relative_to(W)));info.size=p.stat().st_size;info.mode=0o600;info.mtime=0;info.uid=info.gid=0;info.uname=info.gname=''
    with p.open('rb')as h:tf.addfile(info,h)
verified=0
with tarfile.open(tar,'r:gz')as tf:
 for member,row in zip(tf,rows):
  assert member.name==row['path'];h=tf.extractfile(member);assert h and hashlib.sha256(h.read()).hexdigest()==row['sha256'];verified+=1
assert verified==len(rows)
report={'schemaVersion':'q025-parent-evidence-archive-inputs/1','bundle':pin(tar),'manifest':pin(B/'bundle-manifest.json'),'verifiedMemberCount':verified,'sourceBytes':manifest['uncompressedBytes'],'privateOnly':True,'remoteCopy':'pending_authorized_archiver','localOriginalBytesUnchanged':True};(B/'archive-inputs.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
