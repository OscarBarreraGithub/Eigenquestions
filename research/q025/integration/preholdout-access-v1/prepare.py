"""Private pre-holdout read access. Does not install a release or alter source assets."""
import argparse, hashlib, io, json, os, subprocess, tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
def digest(path):
 h=hashlib.sha256()
 with Path(path).open('rb')as stream:
  for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def safe(name):
 p=Path(name)
 if p.is_absolute()or'..'in p.parts or not p.parts or'\\'in name:raise ValueError('Unsafe staged path')
 return p
def preholdout_scope(scope):
 assert scope.get('deliveryState')=='partial_pre_holdout_candidate' and scope.get('accountingReason')=='pre_holdout_freeze','Wrong test phase'
 assert scope.get('sourceInventoryAccounted')is True and scope.get('sourceAccountingComplete')is False,'Pre-holdout accounting must stay explicit'
 assert (scope.get('allocatedQuestionCount'),scope.get('unresolvedQuestionCount'),scope.get('reservedQuestionCount'))==(8399,31,43),'Unexpected frozen pre-holdout accounting'
def link_verified(source,target,row):
 source=Path(source);target=Path(target)
 assert source.is_file()and not source.is_symlink(),'Only existing regular immutable files may be linked'
 assert source.stat().st_size==row['bytes']and digest(source)==row['sha256'],f'Asset mismatch: {row["path"]}'
 target.parent.mkdir(parents=True,exist_ok=True)
 # Deliberately no chmod/write: permissions or contents would change the original inode.
 os.link(source,target)
 assert os.stat(source).st_ino==os.stat(target).st_ino
 return {'path':str(target),'bytes':row['bytes'],'sha256':row['sha256'],'sourcePath':str(source),'mode':'verified-read-only-use-hardlink'}
def main():
 p=argparse.ArgumentParser()
 for key in ['candidate','manifest-sha','commit','output']:p.add_argument('--'+key,required=True)
 a=p.parse_args();candidate=Path(a.candidate).resolve();out=Path(a.output).resolve()
 assert digest(candidate/'manifest.json')==a.manifest_sha,'Manifest mismatch'
 manifest=json.loads((candidate/'manifest.json').read_text());preholdout_scope(manifest['scope'])
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==a.commit,'Use the root-frozen runtime commit'
 subprocess.run(['git','diff','--quiet','HEAD','--','bin','lib','schemas','skills','docs','package.json','package-lock.json'],cwd=ROOT,check=True)
 out.mkdir(parents=True,exist_ok=False);project=out/'application';project.mkdir()
 # Complete CLI/module/skill closure, from exact committed blobs. No native accounts or jobs.
 paths=['bin','lib','schemas','skills','docs','package.json','package-lock.json']
 archive=subprocess.check_output(['git','archive','--format=tar',a.commit,*paths],cwd=ROOT)
 code=[]
 with tarfile.open(fileobj=io.BytesIO(archive))as tar:
  for member in tar:
   target=project/safe(member.name)
   if member.isdir():target.mkdir(parents=True,exist_ok=True);continue
   if not member.isfile():raise ValueError('Non-regular application archive entry')
   body=tar.extractfile(member).read();target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(body)
   code.append({'path':member.name,'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest()})
 atlas=project/'atlas';atlas.mkdir();delivery_desc=manifest['files']['deliveryAssets'];delivery_path=candidate/safe(delivery_desc['path'])
 assert digest(delivery_path)==delivery_desc['sha256'];delivery=json.loads(delivery_path.read_text());plan_path=candidate/'asset-plan.json';plan=json.loads(plan_path.read_text());external={r['path']:r for r in plan['assets']};rows={r['path']:r for r in delivery['files']}
 assert len(rows)==len(delivery['files'])and len(external)==len(plan['assets'])and set(external)<=set(rows),'Inventory mismatch'
 linked=[]
 for name,row in rows.items():
  relative=safe(name);source=candidate/relative
  if name in external:
   descriptor=external[name];assert all(descriptor[k]==row[k]for k in ['bytes','sha256']);source=Path(descriptor['sourcePath'])
  linked.append(link_verified(source,atlas/relative,row))
 for source in [candidate/'manifest.json',delivery_path,plan_path]:
  if source.name not in rows:linked.append(link_verified(source,atlas/source.name,{'path':source.name,'bytes':source.stat().st_size,'sha256':digest(source)}))
 corpus=ROOT/'data/navigation';source_manifest=json.loads((corpus/'manifest.json').read_text())
 assert(source_manifest['corpusId'],source_manifest['contentHash'])==(manifest['corpusId'],manifest['corpusContentHash'])
 descriptors=[{'path':'manifest.json','bytes':(corpus/'manifest.json').stat().st_size,'sha256':digest(corpus/'manifest.json')},source_manifest['files']['papers'],*source_manifest['files']['units']]
 for row in descriptors:linked.append(link_verified(corpus/safe(row['path']),project/'data/navigation'/safe(row['path']),row))
 wrapper=Path(__file__).with_name('read.mjs');(out/'read.mjs').write_bytes(wrapper.read_bytes())
 config={'kind':'q025-preholdout-readonly-access','application':str(project),'atlas':str(atlas),'manifestSha256':a.manifest_sha,'runtimeCommit':a.commit,'scope':manifest['scope'],'staticEntry':str(atlas/'manifest.json'),'skill':str(project/'skills/physics-navigator/SKILL.md'),'assetPlanSha256':digest(plan_path),'publicationStatus':'not installed; pre-holdout only','sourceUse':'Hard-linked immutable data: never write, chmod, or run mutation fixtures in this tree. Native exploration is unavailable; only source metadata is staged.','linkedFiles':linked,'applicationFiles':code,'wrapperSha256':digest(out/'read.mjs')}
 (out/'access.json').write_text(json.dumps(config,indent=2)+'\n')
 print(json.dumps({'access':str(out/'access.json'),'staticEntry':config['staticEntry'],'manifestSha256':a.manifest_sha,'linkedFiles':len(linked),'copiedSourceBytes':0,'runtimeCommit':a.commit}))
if __name__=='__main__':main()
