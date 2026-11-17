"""Verify the final application envelope once on ingress into a node-local QA tree."""
import argparse, hashlib, json, shutil, tarfile
from pathlib import Path

def safe_path(name):
 p=Path(name)
 if p.is_absolute() or '..' in p.parts or not p.parts or '\\' in name:raise ValueError('Unsafe delivery path')
 return p

def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as stream:
  for part in iter(lambda:stream.read(1024*1024),b''):h.update(part)
 return h.hexdigest()

def stage(config_path,project):
 config_path=Path(config_path).resolve();config=json.loads(config_path.read_text());project=Path(project)
 if project.exists():raise ValueError('Refuse to reuse or overwrite an application tree')
 project.mkdir(parents=True)
 verified={}
 for archive in config['archives']:
  source=config_path.parent/safe_path(archive['path'])
  assert digest(source)==archive['sha256'],'Archive checksum mismatch'
  expected={r['path']:r for r in archive['files']};assert len(expected)==len(archive['files'])
  seen=set()
  with tarfile.open(source,'r:*') as tar:
   for member in tar:
    relative=safe_path(member.name)
    if member.isdir():continue
    if not member.isfile() or member.name not in expected or member.name in seen:raise ValueError('Unlisted, duplicate or non-regular archive entry')
    row=expected[member.name];body=tar.extractfile(member).read()
    assert len(body)==row['bytes'] and hashlib.sha256(body).hexdigest()==row['sha256'],member.name
    target=project/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(body)
    verified[member.name]=row;seen.add(member.name)
  assert seen==set(expected),'Missing archive entries'
 atlas=project/safe_path(config['atlasDirectory'])
 for row in config.get('externalAssets',[]):
  relative=safe_path(row['path']);target=atlas/relative
  if target.exists():raise ValueError('External asset collides with application envelope')
  source=Path(row['sourcePath']);target.parent.mkdir(parents=True,exist_ok=True)
  h=hashlib.sha256();size=0
  with source.open('rb')as incoming,target.open('wb')as outgoing:
   for chunk in iter(lambda:incoming.read(1024*1024),b''):
    h.update(chunk);size+=len(chunk);outgoing.write(chunk)
  assert size==row['bytes'] and h.hexdigest()==row['sha256'],row['path']
  verified[str(target.relative_to(project))]={'path':str(target.relative_to(project)),'bytes':size,'sha256':h.hexdigest()}
 assert digest(atlas/'manifest.json')==config['manifestSha256'],'Wrong scientific package'
 manifest=json.loads((atlas/'manifest.json').read_text());scope=manifest['scope']
 assert scope.get('partialRehearsal') is not True and scope.get('partialCandidate') is not True,'Partial package is not final acceptance'
 assert scope.get('sourceAccountingComplete')is True and scope.get('reservedQuestionCount')==0,'Final QA requires complete source accounting and no reserved cases'
 assert config['releaseAccountingReceipt']['sha256'] and config['releaseAccountingReceipt']['path'],'Final accounting receipt required'
 accounting=config['releaseAccountingReceipt'];assert digest(project/safe_path(accounting['path']))==accounting['sha256'],'Wrong accounting receipt'
 index=json.loads((project/'data/atlas/index.json').read_text())
 assert index['home']=={'atlasId':manifest['atlasId'],'atlasVersion':manifest['atlasVersion'],'destinationId':manifest['entryDestinationId']},'Default home must be explicit'
 for filename in ['package.json','package-lock.json','wrangler.toml','scripts/build-site.mjs','scripts/site-check.mjs','bin/navigate.mjs','bin/mcp-navigator.mjs','skills/physics-navigator/SKILL.md','research/q025/integration/agent-browser-observer.py']:
  assert (project/filename).is_file(),f'Missing application closure: {filename}'
 return {'kind':'final-qa-ingress','manifestSha256':config['manifestSha256'],'project':str(project),'verifiedFileCount':len(verified),'verifiedBytes':sum(r['bytes']for r in verified.values()),'sourceArchiveSha256':[a['sha256']for a in config['archives']],'externalAssetsVerifiedWhileCopied':len(config.get('externalAssets',[])),'policy':'Complete frozen source accounting; unresolved zero-semantic-mass facets remain allowed with explicit reasons. Scientific containment and access reachability are separate.'}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--project',required=True);p.add_argument('--receipt',required=True);a=p.parse_args();r=stage(a.input,a.project);Path(a.receipt).write_text(json.dumps(r,indent=2)+'\n')
