#!/bin/bash
#SBATCH --job-name=q025-real-qa20
#SBATCH --account=randall_lab
#SBATCH --partition=test
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=00:12:00
#SBATCH --output=/n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/integration/qa20/slurm-%j.out
#SBATCH --error=/n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/integration/qa20/slurm-%j.err
set -euo pipefail
umask 077
run_dir=/n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/integration/qa20
prior_dir=/n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/integration/qa19
project_dir="$run_dir/project"
node_bin=/n/home09/obarrera/.conda/envs/ising_bootstrap/bin/node
python_bin=/n/netscratch/randall_lab/Everyone/obarrera/physics-atlas-encoders/20261104-v1/env/bin/python
export PYTHONPATH=/n/netscratch/randall_lab/Everyone/obarrera/physics-atlas-graph-design/20261105-v1/ui-deps
export PLAYWRIGHT_BROWSERS_PATH=/n/netscratch/randall_lab/Everyone/obarrera/physics-atlas-graph-design/20261105-v1/browsers
export PYTHONUNBUFFERED=1 PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4
export NODE_OPTIONS=--max-old-space-size=12288
test ! -e "$project_dir"
cp -al "$prior_dir/project" "$project_dir"
"$python_bin" - "$run_dir" "$prior_dir" <<'PY'
import hashlib,json,tarfile,sys
from pathlib import Path
run,prior=map(Path,sys.argv[1:]);m=json.loads((run/'input-manifest.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(prior/'content-manifest.json')==m['priorContentManifestSha256']
assert sha(run/'patch.tar.gz')==m['patchSha256']
with tarfile.open(run/'patch.tar.gz')as tar:
 for row in m['files']:
  body=tar.extractfile(row['path']).read();assert len(body)==row['bytes']and hashlib.sha256(body).hexdigest()==row['sha256']
  target=run/'project'/row['path'];target.parent.mkdir(parents=True,exist_ok=True)
  if target.exists():target.unlink() # Never modify an input hardlinked to preserved QA19.
  target.write_bytes(body)
old=json.loads((prior/'content-manifest.json').read_text())
for row in old['files']:
 body=(run/'project'/row['path']).read_bytes();assert len(body)==row['bytes']and hashlib.sha256(body).hexdigest()==row['sha256'],row['path']
print('Exact QA19 runtime/data retained; added only',len(m['files']),'public repository targets')
PY
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
