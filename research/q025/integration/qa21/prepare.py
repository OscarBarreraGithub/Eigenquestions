"""Complete immutable Git source plus exact prior built tree; no browser or native call."""
from pathlib import Path
import subprocess,tarfile,json,hashlib,re
B=Path(__file__).resolve().parent;W=B.parents[3];G='f3f99c50438768cc88bf9b3c6f8d23eb191a43e7';A=Path('/tmp/q025-qa21-repository.tar.gz')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
subprocess.run(['git','archive','--format=tar.gz','--output='+str(A),G],cwd=W,check=True)
files=[];texts={}
with tarfile.open(A)as t:
 for m in t:
  if m.isdir():continue
  assert m.isfile()and not m.name.startswith('/')and'..'not in Path(m.name).parts,m.name
  assert not any(x in Path(m.name).parts for x in ['.git','node_modules','native-local','.env']),m.name
  body=t.extractfile(m).read();files.append({'path':m.name,'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest()})
  if m.name.startswith('docs/')and m.name.endswith('.md')or m.name=='scripts/site-check.mjs':texts[m.name]=body.decode()
old=json.loads((B.parent/'qa19/content-manifest.json').read_text());patch=json.loads((B.parent/'qa20/input-manifest.json').read_text());available={x['path']for x in files}|{x['path']for x in old['files']}|{x['path']for x in patch['files']}
def exists(p):return p in available or any(x.startswith(p.rstrip('/')+'/')for x in available)
repo_targets=set()
for name,body in texts.items():
 if name.endswith('.md'):
  repo_targets.update(re.findall(r'https://github\.com/OscarBarreraGithub/Eigenquestions/(?:blob|tree)/main/([^\s)#]+)',body))
# The checker reads generated dist assets, repository Markdown targets, and this explicit root config.
checker=texts['scripts/site-check.mjs'];literal=set(re.findall(r"readFile\(path\.join\(root,\s*'([^']+)'",checker));assert literal=={'wrangler.toml'},literal
observation=json.loads((B/'closure-observation.json').read_text());repo_targets.update(observation['repositoryTargets'])
missing=sorted(p for p in repo_targets|literal if not exists(p));assert not missing,missing
m={'schemaVersion':'q025-complete-repository-qa/1','gitCommit':G,'archiveSha256':sha(A),'archiveBytes':A.stat().st_size,'files':files,'priorQa19ContentManifestSha256':sha(B.parent/'qa19/content-manifest.json'),'priorQa20InputManifestSha256':sha(B.parent/'qa20/input-manifest.json'),'overlayPolicy':'Exact prior QA20 project tree overlays the complete pinned Git archive; original hardlinked files are never overwritten in place.','runtimeAndDataChanged':False,'privateFilesIncluded':False,'closure':{'checkerSha256':next(x['sha256']for x in files if x['path']=='scripts/site-check.mjs'),'allRepositoryTargets':sorted(repo_targets),'generatedMarkdown':observation['generatedMarkdown'],'observedPriorMissing':observation['sourceTreeMissing'],'literalRootReads':sorted(literal),'missing':missing,'generatedDist':'Exact successful QA19 build preserved in QA20; actual checker still runs before browser.'}}
(B/'input-manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps({'archive':str(A),'archiveSha256':sha(A),'bytes':A.stat().st_size,'trackedFiles':len(files),'closureTargets':len(repo_targets|literal),'missing':missing}))
