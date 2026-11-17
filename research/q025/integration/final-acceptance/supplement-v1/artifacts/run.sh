#!/bin/bash
set -euo pipefail
umask 077
run=/n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/integration/final-supplement-v1
source_project=/tmp/q025-final-61597944-bsXncp/project
project=/tmp/q025-final-61597944-bsXncp/supplement
node=/n/home09/obarrera/.conda/envs/ising_bootstrap/bin/node
python=/n/netscratch/randall_lab/Everyone/obarrera/physics-atlas-encoders/20261104-v1/env/bin/python
export PYTHONPATH=/n/netscratch/randall_lab/Everyone/obarrera/physics-atlas-graph-design/20261105-v1/ui-deps
export PLAYWRIGHT_BROWSERS_PATH=/n/netscratch/randall_lab/Everyone/obarrera/physics-atlas-graph-design/20261105-v1/browsers
export PYTHONUNBUFFERED=1 PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NODE_OPTIONS=--max-old-space-size=4096
trap 'code=$?; printf "exitCode=%s\n" "$code" > "$run/exit.txt"; exit "$code"' EXIT
test ! -e "$project"
cp -al "$source_project" "$project"
"$python" - "$run" "$project" <<'PY'
from pathlib import Path
import sys,json,hashlib,tarfile
run,project=map(Path,sys.argv[1:]);c=json.loads((run/'input.json').read_text());assert hashlib.sha256((run/'overlay.tar.gz').read_bytes()).hexdigest()==c['overlaySha256'];expected={r['path']:r for r in c['files']};seen=set()
with tarfile.open(run/'overlay.tar.gz')as tar:
 for m in tar:
  assert m.isfile()and m.name in expected and '..'not in Path(m.name).parts and not Path(m.name).is_absolute();r=expected[m.name];b=tar.extractfile(m).read();assert len(b)==r['bytes']and hashlib.sha256(b).hexdigest()==r['sha256'];target=project/m.name;target.parent.mkdir(parents=True,exist_ok=True)
  if target.exists():target.unlink()
  target.write_bytes(b);seen.add(m.name)
assert seen==set(expected)
PY
cd "$project"
"$node" scripts/build-site.mjs > "$run/build.log" 2>&1
"$node" scripts/site-check.mjs > "$run/site-check.log" 2>&1
atlas="$project/data/atlas/q025-approved-organization-candidate/2026-11-17-post-test-accounted-v1"
"$python" research/q025/integration/final-acceptance/browser.py --project "$project" --output "$run/core" --node "$node" --cases "$project/research/q025/integration/final-acceptance/cases.json" > "$run/core.log" 2>&1
"$python" research/q025/integration/final-acceptance/supplemental.py --project "$project" --atlas "$atlas" --output "$run/supplement" --node "$node" > "$run/supplement.log" 2>&1
