#!/bin/bash
#SBATCH --job-name=q025-real-qa21
#SBATCH --account=randall_lab
#SBATCH --partition=test
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=00:12:00
#SBATCH --output=/n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/integration/qa21/slurm-%j.out
#SBATCH --error=/n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/integration/qa21/slurm-%j.err
set -euo pipefail
umask 077
run_dir=/n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/integration/qa21
prior_dir=/n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/integration/qa20
project_dir="$run_dir/project"
node_bin=/n/home09/obarrera/.conda/envs/ising_bootstrap/bin/node
python_bin=/n/netscratch/randall_lab/Everyone/obarrera/physics-atlas-encoders/20261104-v1/env/bin/python
export PYTHONPATH=/n/netscratch/randall_lab/Everyone/obarrera/physics-atlas-graph-design/20261105-v1/ui-deps
export PLAYWRIGHT_BROWSERS_PATH=/n/netscratch/randall_lab/Everyone/obarrera/physics-atlas-graph-design/20261105-v1/browsers
export PYTHONUNBUFFERED=1 PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4
export NODE_OPTIONS=--max-old-space-size=12288
test ! -e "$project_dir"
"$python_bin" - "$run_dir" "$prior_dir" <<'PYINNER'
import hashlib,json,tarfile,sys,os
from pathlib import Path
run,prior=map(Path,sys.argv[1:]);m=json.loads((run/'input-manifest.json').read_text());project=run/'project';project.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(run/'repository.tar.gz')==m['archiveSha256']
assert sha(prior/'input-manifest.json')==m['priorQa20InputManifestSha256']
with tarfile.open(run/'repository.tar.gz')as tar:
 for row in m['files']:
  body=tar.extractfile(row['path']).read();assert len(body)==row['bytes']and hashlib.sha256(body).hexdigest()==row['sha256']
  target=project/row['path'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(body)
# Overlay exact successful built tree and its runtime. Unlink before linking; never mutate prior files.
for source in (prior/'project').rglob('*'):
 target=project/source.relative_to(prior/'project')
 if source.is_dir():target.mkdir(parents=True,exist_ok=True)
 elif source.is_file():
  target.parent.mkdir(parents=True,exist_ok=True)
  if target.exists():target.unlink()
  os.link(source,target)
old=json.loads((prior.parent/'qa19/content-manifest.json').read_text());assert sha(prior.parent/'qa19/content-manifest.json')==m['priorQa19ContentManifestSha256']
for row in old['files']:
 body=(project/row['path']).read_bytes();assert len(body)==row['bytes']and hashlib.sha256(body).hexdigest()==row['sha256'],row['path']
for row in m['closure']['generatedMarkdown']:assert sha(project/row['path'])==row['sha256'],row['path']
for name in m['closure']['allRepositoryTargets']+m['closure']['literalRootReads']:assert (project/name).exists(),name
assert sha(project/'scripts/site-check.mjs')==m['closure']['checkerSha256']
print('Complete pinned Git repository plus exact QA20 built tree; closure verified before checker')
PYINNER
cd "$project_dir"
"$node_bin" scripts/site-check.mjs > "$run_dir/site-check.log" 2>&1
"$python_bin" - "$run_dir" <<'PY'
import hashlib,json,sys
from pathlib import Path
files=[p for p in Path('dist').rglob('*')if p.is_file()];sizes=[p.stat().st_size for p in files]
r={'files':len(files),'bytes':sum(sizes),'largestFileBytes':max(sizes),'under20000Files':len(files)<20000,'under25MiBPerFile':max(sizes)<=25*1024*1024,'partialCandidateOnly':True,'buildReusedFromJob':'61546342'}
(Path(sys.argv[1])/'build-size.json').write_text(json.dumps(r,indent=2)+'\n');assert r['under20000Files']and r['under25MiBPerFile']
PY
"$python_bin" research/q025/integration/qa19/browser.py --project "$project_dir" --output "$run_dir/artifacts" --node "$node_bin" > "$run_dir/browser.log" 2>&1
