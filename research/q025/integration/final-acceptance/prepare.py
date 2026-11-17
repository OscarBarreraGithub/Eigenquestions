"""Seal the existing final handoff into the complete-repository QA envelope; no install."""
import argparse, hashlib, io, json, shutil, subprocess, tarfile, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
sha=lambda data:hashlib.sha256(data).hexdigest()
def descriptor(path,name=None):
 body=Path(path).read_bytes();return {'path':name or Path(path).name,'sha256':sha(body),'bytes':len(body)}
def member_inventory(path):
 with tarfile.open(path)as tar:return [{'path':m.name,'bytes':m.size,'sha256':sha(tar.extractfile(m).read())}for m in tar if m.isfile()]
def main():
 p=argparse.ArgumentParser()
 for key in ['candidate','cases','accounting','output','commit','manifest-sha']:p.add_argument('--'+key,required=True)
 p.add_argument('--with-observer',action='store_true');a=p.parse_args();candidate=Path(a.candidate).resolve();out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=False)
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==a.commit
 subprocess.run(['git','diff','--quiet','HEAD','--','bin','lib','web','scripts','schemas','skills','docs','package.json','package-lock.json','wrangler.toml'],cwd=ROOT,check=True)
 manifest_body=(candidate/'manifest.json').read_bytes();assert sha(manifest_body)==a.manifest_sha;manifest=json.loads(manifest_body)
 assert not manifest['scope'].get('partialRehearsal') and not manifest['scope'].get('partialCandidate'),'Partial package cannot be final QA'
 cases=json.loads(Path(a.cases).read_text());assert cases['finalAccounting'] is True and cases['manifestSha256']==a.manifest_sha
 assert (cases['atlasId'],cases['atlasVersion'],cases['entryDestinationId'])==(manifest['atlasId'],manifest['atlasVersion'],manifest['entryDestinationId'])
 base=out/'repository.tar.gz';subprocess.run(['git','archive','--format=tar.gz','--output',str(base),a.commit],cwd=ROOT,check=True)
 relative=Path('data/atlas')/manifest['atlasId']/manifest['atlasVersion'];overlay={}
 def add(src,dest,expected=None):
  body=Path(src).read_bytes();row={'path':str(dest),'bytes':len(body),'sha256':sha(body)}
  if expected:assert row['bytes']==expected['bytes'] and row['sha256']==expected['sha256'],str(src)
  if str(dest)in overlay:assert overlay[str(dest)]==body,'Conflicting overlay path'
  overlay[str(dest)]=body
 delivery_desc=manifest['files']['deliveryAssets'];delivery_body=(candidate/delivery_desc['path']).read_bytes();assert sha(delivery_body)==delivery_desc['sha256'];delivery=json.loads(delivery_body)
 plan_body=(candidate/'asset-plan.json').read_bytes();plan=json.loads(plan_body);external={r['path']:r for r in plan['assets']};assert len(external)==len(plan['assets'])
 for row in delivery['files']:
  if row['path'] not in external:add(candidate/row['path'],relative/row['path'],row)
 add(candidate/'manifest.json',relative/'manifest.json');add(candidate/delivery_desc['path'],relative/delivery_desc['path'])
 remote=[];marker='/source-context-v3-compact/pack/'
 for row in plan['assets']:
  if marker in row['sourcePath']:
   remote.append({k:row[k]for k in ['path','sha256','bytes']}|{'sourcePath':'/n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/geometry/source-context-v3-compact/pack/'+row['sourcePath'].split(marker,1)[1]})
  else:add(row['sourcePath'],relative/row['path'],row)
 index={'schemaVersion':'1.0.0','home':{k:manifest[k]for k in ['atlasId','atlasVersion']}|{'destinationId':manifest['entryDestinationId']},'atlases':[{k:manifest[k]for k in ['atlasId','atlasVersion','entryDestinationId']}|{'title':'Physics atlas','scope':manifest['scope']['description']}]};overlay['data/atlas/index.json']=(json.dumps(index,ensure_ascii=False)+'\n').encode()
 prefix=Path('research/q025/integration/final-acceptance');add(a.cases,prefix/'cases.json');add(a.accounting,prefix/'accounting.json')
 for name in ['stage.py','browser.py','run.sbatch','README.md']:add(ROOT/prefix/name,prefix/name)
 for name in ['agent-browser-observer.py','public-bridge-acceptance.py']:add(ROOT/'research/q025/integration'/name,Path('research/q025/integration')/name)
 archive=out/'overlay.tar.gz'
 with tarfile.open(archive,'w:gz',compresslevel=4)as tar:
  for name,body in sorted(overlay.items()):m=tarfile.TarInfo(name);m.size=len(body);m.mode=0o644;m.mtime=0;tar.addfile(m,io.BytesIO(body))
 phases=[{'script':str(prefix/'browser.py'),'output':'browser','args':['--cases','{PROJECT}/'+str(prefix/'cases.json')]}]
 if a.with_observer:phases.append({'script':'research/q025/integration/agent-browser-observer.py','output':'observer','args':['--atlas','{ATLAS}','--minutes','30']})
 config={'kind':'q025-final-frozen-qa-envelope','baseCommit':a.commit,'manifestSha256':a.manifest_sha,'atlasDirectory':str(relative),'sourceAssetPlanSha256':sha(plan_body),'releaseAccountingReceipt':descriptor(a.accounting,str(prefix/'accounting.json')),'archives':[descriptor(base)|{'files':member_inventory(base)},descriptor(archive)|{'files':member_inventory(archive)}],'externalAssets':remote,'phases':phases,'freshAgentReceivesNoCasesOrOracle':True,'releaseDecisionExternal':'Root gates this frozen handoff and launches the job; preparation does not deploy or admit science.'}
 (out/'final-input.json').write_text(json.dumps(config,indent=2)+'\n')
 for name in ['stage.py','run.sbatch']:shutil.copyfile(ROOT/prefix/name,out/name)
 print(json.dumps({'output':str(out),'inputSha256':sha((out/'final-input.json').read_bytes()),'archiveBytes':base.stat().st_size+archive.stat().st_size,'remoteContextAssets':len(remote),'observerIncluded':a.with_observer}))
if __name__=='__main__':main()
