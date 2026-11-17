#!/bin/bash
#SBATCH --job-name=q025-prepared-qa09
#SBATCH --account=randall_lab
#SBATCH --partition=test
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:12:00
#SBATCH --output=/n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/integration/qa09/slurm-%j.out
#SBATCH --error=/n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/integration/qa09/slurm-%j.err
set -euo pipefail
umask 077
run_dir=/n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/integration/qa09
project_dir="$run_dir/project"
node_bin=/n/home09/obarrera/.conda/envs/ising_bootstrap/bin/node
python_bin=/n/netscratch/randall_lab/Everyone/obarrera/physics-atlas-encoders/20261104-v1/env/bin/python
export PYTHONPATH=/n/netscratch/randall_lab/Everyone/obarrera/physics-atlas-graph-design/20261105-v1/ui-deps
export PLAYWRIGHT_BROWSERS_PATH=/n/netscratch/randall_lab/Everyone/obarrera/physics-atlas-graph-design/20261105-v1/browsers
export PYTHONUNBUFFERED=1 PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
mkdir -p "$project_dir"
tar -xzf "$run_dir/project.tar.gz" -C "$project_dir"
cd "$project_dir"
"$python_bin" - "$run_dir/content-manifest.json" <<'PY'
import hashlib,json,sys
from pathlib import Path
manifest=json.loads(Path(sys.argv[1]).read_text())
for item in manifest['files']:
    body=Path(item['path']).read_bytes()
    if len(body)!=item['bytes'] or hashlib.sha256(body).hexdigest()!=item['sha256']:
        raise SystemExit('Input checksum mismatch: '+item['path'])
print('Verified',len(manifest['files']),'exact input files')
PY
"$node_bin" --version
"$python_bin" - <<'STAGE'
import json,shutil
from pathlib import Path
source=Path('research/q025/assembly/outputs/full-scale-delivery-fixture');manifest=json.loads((source/'manifest.json').read_text());target=Path('data/atlas')/manifest['atlasId']/manifest['atlasVersion'];shutil.copytree(source,target,dirs_exist_ok=True)
Path('data/atlas/index.json').write_text(json.dumps({'schemaVersion':'1.0.0','atlases':[{'atlasId':manifest['atlasId'],'atlasVersion':manifest['atlasVersion'],'entryDestinationId':manifest['entryDestinationId'],'title':'Full-scale delivery diagnostic','scope':manifest['scope']['description']}]}))
STAGE
"$node_bin" scripts/build-site.mjs
"$python_bin" tests/integration/q025_prepared_acceptance.py --project "$project_dir" --output "$run_dir/artifacts" --node "$node_bin" --draft-atlas "$project_dir/research/q025/assembly/preview-methods-package" --scale-atlas "$project_dir/research/q025/assembly/outputs/full-scale-delivery-fixture" --source-context-pack /n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/geometry/source-context-v3-compact/pack --source-context-manifest-sha c86bc90966007c28ce40523348e51e4ace4d20d62354f79928133d371f77c6f5 > "$run_dir/browser.log" 2>&1
