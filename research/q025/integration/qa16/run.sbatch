#!/bin/bash
#SBATCH --job-name=q025-source-qa16
#SBATCH --account=randall_lab
#SBATCH --partition=test
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:08:00
#SBATCH --output=/n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/integration/qa16/slurm-%j.out
#SBATCH --error=/n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/integration/qa16/slurm-%j.err
set -euo pipefail
umask 077
run_dir=/n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/integration/qa16
project_dir="$run_dir/project"
node_bin=/n/home09/obarrera/.conda/envs/ising_bootstrap/bin/node
python_bin=/n/netscratch/randall_lab/Everyone/obarrera/physics-atlas-encoders/20261104-v1/env/bin/python
export PYTHONPATH=/n/netscratch/randall_lab/Everyone/obarrera/physics-atlas-graph-design/20261105-v1/ui-deps
export PLAYWRIGHT_BROWSERS_PATH=/n/netscratch/randall_lab/Everyone/obarrera/physics-atlas-graph-design/20261105-v1/browsers
export PYTHONUNBUFFERED=1 PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
mkdir -p "$project_dir"
base_archive=/n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/integration/qa14/project.tar.gz
"$python_bin" - "$base_archive" <<'PYVERIFY'
import hashlib,sys
from pathlib import Path
assert hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest()=='f7ef7e78dadc5a5d5dc0fbddec732a5e72bd4e3d02f5eb3a03feb42171b2f2c5'
PYVERIFY
tar -xzf "$base_archive" -C "$project_dir"
prior_overlay=/n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/integration/qa15/overlay.tar.gz
"$python_bin" - "$prior_overlay" <<'PYPRIOR'
import hashlib,sys
from pathlib import Path
assert hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest()=='d152930b95e92a23b1b7ef21d5d25a290042befde6b139c6ac9c9257e8dc9d1e'
PYPRIOR
tar -xzf "$prior_overlay" -C "$project_dir"
tar -xzf "$run_dir/overlay.tar.gz" -C "$project_dir"
cd "$project_dir"
"$python_bin" - "$run_dir/content-manifest.json" <<'PY'
import hashlib,json,sys
from pathlib import Path
manifest=json.loads(Path(sys.argv[1]).read_text())
for item in manifest['files']:
    body=Path(item['path']).read_bytes()
    if len(body)!=item['bytes'] or hashlib.sha256(body).hexdigest()!=item['sha256']:raise SystemExit('Input checksum mismatch: '+item['path'])
print('Verified',len(manifest['files']),'exact input files')
PY
"$node_bin" --version
"$node_bin" research/q025/integration/source-endpoint-v1/create-browser-fixture.mjs data/atlas/q025-source-endpoint-qa/2026-11-17-protocol-v1
"$python_bin" - <<'PY'
import json
from pathlib import Path
Path('data/atlas/index.json').write_text(json.dumps({'schemaVersion':'1.0.0','atlases':[{'atlasId':'q025-source-endpoint-qa','atlasVersion':'2026-11-17-protocol-v1','entryDestinationId':'physics','title':'Source endpoint protocol QA','scope':'Protocol destination with exact reviewed source objects; not accepted atlas.'}]}))
PY
"$node_bin" scripts/build-site.mjs
"$python_bin" research/q025/integration/source-endpoint-browser-acceptance.py --project "$project_dir" --output "$run_dir/artifacts" --node "$node_bin" > "$run_dir/browser.log" 2>&1
