"""Exact isolated QA overlay; no local public-data installation."""
import hashlib,json,os,tarfile,tempfile,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];B=ROOT/'research/q025/integration/qa19'
C=ROOT/'research/q025/assembly/outputs/organization-candidate-6030-connected-v4'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((C/'manifest.json').read_text());plan=json.loads((C/'asset-plan.json').read_text());rel=Path('data/atlas')/m['atlasId']/m['atlasVersion']
stage=Path(tempfile.mkdtemp(prefix='q025-qa19-package-'));files={}
def add(src,dest):
 target=stage/dest;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,target);files[str(dest)]={'path':str(dest),'bytes':target.stat().st_size,'sha256':sha(target)}
for directory in ['web','lib','bin','scripts','schemas','skills','docs']:
 for p in (ROOT/directory).rglob('*'):
  if p.is_file() and '__pycache__'not in p.parts:add(p,p.relative_to(ROOT))
for name in ['package.json','package-lock.json']:add(ROOT/name,Path(name))
for p in B.iterdir():
 if p.is_file() and p.suffix in ['.py','.mjs'] or p.name=='cases.json':add(p,p.relative_to(ROOT))
# Package only the declared delivery records plus manifest/asset inventory.
delivery=json.loads((C/m['files']['deliveryAssets']['path']).read_text())
external_paths={row['path']for row in plan['assets']}
for row in delivery['files']:
 if row['path']in external_paths:continue
 p=C/row['path'];assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256'];add(p,rel/row['path'])
for name in ['manifest.json',m['files']['deliveryAssets']['path']]:add(C/name,rel/name)
remote=[]
for row in plan['assets']:
 src=Path(row['sourcePath']);assert src.stat().st_size==row['bytes'] and sha(src)==row['sha256']
 marker='/source-context-v3-compact/pack/'
 if marker in str(src):remote.append({**{k:row[k]for k in ['path','sha256','bytes']},'sourcePath':'/n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/geometry/source-context-v3-compact/pack/'+str(src).split(marker)[1]})
 else:add(src,rel/row['path'])
index={'schemaVersion':'1.0.0','atlases':[{'atlasId':m['atlasId'],'atlasVersion':m['atlasVersion'],'entryDestinationId':m['entryDestinationId'],'title':'Physics atlas — partial research candidate','scope':m['scope']['description']}]}
(stage/'data/atlas/index.json').write_text(json.dumps(index)+'\n');p=stage/'data/atlas/index.json';files['data/atlas/index.json']={'path':'data/atlas/index.json','bytes':p.stat().st_size,'sha256':sha(p)}
# Frozen corpus bytes come from the already retained QA14 base, never copied from credentials/private review state.
for directory in ['data/navigation','data/overview']:
 for p in (ROOT/directory).rglob('*'):
  if p.is_file():files[str(p.relative_to(ROOT))]={'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)}
archive=Path('/tmp/q025-qa19-overlay.tar.gz')
with tarfile.open(archive,'w:gz',compresslevel=4)as tar:
 for p in sorted(stage.rglob('*')):
  if p.is_file():tar.add(p,arcname=str(p.relative_to(stage)),recursive=False)
receipt={'kind':'q025-qa19-content-manifest','scope':'Actual admitted 6030-source partial candidate; isolated build/browser/MCP, no site installation or scientific completion.','baseArchiveSha256':'f7ef7e78dadc5a5d5dc0fbddec732a5e72bd4e3d02f5eb3a03feb42171b2f2c5','overlayArchiveSha256':sha(archive),'overlayArchiveBytes':archive.stat().st_size,'baseCommit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'files':list(files.values()),'externalAssets':remote,'atlasDirectory':str(rel),'candidateManifestSha256':sha(C/'manifest.json'),'sourceAssetPlanSha256':sha(C/'asset-plan.json')}
(B/'content-manifest.json').write_text(json.dumps(receipt,indent=2)+'\n');shutil.rmtree(stage)
print(json.dumps({'archive':str(archive),'bytes':archive.stat().st_size,'overlayAndFrozenFiles':len(files),'externalPinnedAssets':len(remote),'sha256':sha(archive)}))
