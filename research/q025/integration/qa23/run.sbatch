#!/bin/bash
#SBATCH --job-name=q025-real-qa23
#SBATCH --account=randall_lab
#SBATCH --partition=test
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=00:20:00
#SBATCH --output=/n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/integration/qa23/slurm-%j.out
#SBATCH --error=/n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/integration/qa23/slurm-%j.err
set -euo pipefail
umask 077
run_dir=/n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/integration/qa23
project_dir="$run_dir/project"
node_bin=/n/home09/obarrera/.conda/envs/ising_bootstrap/bin/node
python_bin=/n/netscratch/randall_lab/Everyone/obarrera/physics-atlas-encoders/20261104-v1/env/bin/python
export PYTHONPATH=/n/netscratch/randall_lab/Everyone/obarrera/physics-atlas-graph-design/20261105-v1/ui-deps
export PLAYWRIGHT_BROWSERS_PATH=/n/netscratch/randall_lab/Everyone/obarrera/physics-atlas-graph-design/20261105-v1/browsers
export PYTHONUNBUFFERED=1 PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4
export NODE_OPTIONS=--max-old-space-size=12288
prior_dir=/n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/integration/qa22
test ! -e "$project_dir"
cp -al "$prior_dir/project" "$project_dir"
"$python_bin" - "$run_dir" <<'PYINNER'
import hashlib,json,tarfile,sys,shutil
from pathlib import Path
run=Path(sys.argv[1]);project=run/'project';m=json.loads((run/'content-manifest.json').read_text());assert hashlib.sha256((run/'overlay.tar.gz').read_bytes()).hexdigest()==m['overlayArchiveSha256']
shutil.rmtree(project/'data/atlas') # Isolated hardlinks only; original package remains immutable.
with tarfile.open(run/'overlay.tar.gz')as tar:
 for member in tar:
  assert member.isfile()and not member.name.startswith('/')and'..'not in Path(member.name).parts
  target=project/member.name;target.parent.mkdir(parents=True,exist_ok=True)
  if target.exists():target.unlink() # Never overwrite a file hardlinked to the retained QA22 tree.
  target.write_bytes(tar.extractfile(member).read())
index=json.loads((project/'data/atlas/index.json').read_text());home=index['home'];manifest=json.loads((project/m['atlasDirectory']/'manifest.json').read_text());assert home=={'atlasId':manifest['atlasId'],'atlasVersion':manifest['atlasVersion'],'destinationId':manifest['entryDestinationId']}
assert (project/'wrangler.toml').is_file()
print('Complete prior repository retained; exact new runtime/data overlay and home binding checked')
PYINNER
cd "$project_dir"
"$python_bin" - "$run_dir/content-manifest.json" <<'PY'
import hashlib,json,shutil,sys
from pathlib import Path
m=json.loads(Path(sys.argv[1]).read_text())
for item in m['files']:
 body=Path(item['path']).read_bytes()
 assert len(body)==item['bytes'] and hashlib.sha256(body).hexdigest()==item['sha256'],item['path']
for item in m['externalAssets']:
 source=Path(item['sourcePath']);body=source.read_bytes()
 assert len(body)==item['bytes'] and hashlib.sha256(body).hexdigest()==item['sha256'],item['path']
 target=Path(m['atlasDirectory'])/item['path'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
print('Verified exact local inputs',len(m['files']),'and external context assets',len(m['externalAssets']))
PY
"$node_bin" scripts/build-site.mjs > "$run_dir/build.log" 2>&1
"$node_bin" scripts/site-check.mjs > "$run_dir/site-check.log" 2>&1
"$python_bin" - "$run_dir" <<'PY'
import json,sys
from pathlib import Path
files=[p for p in Path('dist').rglob('*')if p.is_file()];sizes=[p.stat().st_size for p in files]
r={'files':len(files),'bytes':sum(sizes),'largestFileBytes':max(sizes),'under20000Files':len(files)<20000,'under25MiBPerFile':max(sizes)<=25*1024*1024,'partialCandidateOnly':True}
(Path(sys.argv[1])/'build-size.json').write_text(json.dumps(r,indent=2)+'\n');assert r['under20000Files'] and r['under25MiBPerFile']
PY
"$python_bin" research/q025/integration/qa23/browser.py --project "$project_dir" --output "$run_dir/artifacts" --node "$node_bin" > "$run_dir/browser.log" 2>&1
