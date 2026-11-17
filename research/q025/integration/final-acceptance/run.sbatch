#!/bin/bash
#SBATCH --job-name=q025-final-acceptance
#SBATCH --account=randall_lab
#SBATCH --partition=test
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=00:45:00
set -euo pipefail
umask 077
: "${Q025_RUN_DIR:?Set the exact frozen private run directory}"
run_dir="$Q025_RUN_DIR"
node_bin=/n/home09/obarrera/.conda/envs/ising_bootstrap/bin/node
python_bin=/n/netscratch/randall_lab/Everyone/obarrera/physics-atlas-encoders/20261104-v1/env/bin/python
export PYTHONPATH=/n/netscratch/randall_lab/Everyone/obarrera/physics-atlas-graph-design/20261105-v1/ui-deps
export PLAYWRIGHT_BROWSERS_PATH=/n/netscratch/randall_lab/Everyone/obarrera/physics-atlas-graph-design/20261105-v1/browsers
export PYTHONUNBUFFERED=1 PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 NODE_OPTIONS=--max-old-space-size=12288
node_root="${SLURM_TMPDIR:-/tmp}"
local_run=$(mktemp -d "$node_root/q025-final-${SLURM_JOB_ID}-XXXXXX")
project_dir="$local_run/project"
# Compact receipts remain readable while the application and build stay node-local.
trap 'status=$?; printf "exitCode=%s\njobId=%s\n" "$status" "$SLURM_JOB_ID" > "$run_dir/job-exit.txt"; rm -rf "$local_run"; exit "$status"' EXIT
"$python_bin" "$run_dir/stage.py" --input "$run_dir/final-input.json" --project "$project_dir" --receipt "$run_dir/ingress.json"
cd "$project_dir"
"$node_bin" scripts/build-site.mjs > "$run_dir/build.log" 2>&1
"$node_bin" scripts/site-check.mjs > "$run_dir/site-check.log" 2>&1
"$python_bin" - "$run_dir" <<'PY'
import json,sys
from pathlib import Path
run=Path(sys.argv[1]);config=json.loads((run/'final-input.json').read_text());sizes=[(str(p),p.stat().st_size)for p in Path('dist').rglob('*')if p.is_file()];largest=max(sizes,key=lambda x:x[1]);receipt={'files':len(sizes),'bytes':sum(s for _,s in sizes),'largestFile':largest[0],'largestFileBytes':largest[1],'fileLimit':20000,'perFileLimit':25*1024*1024,'manifestSha256':config['manifestSha256']};(run/'build-size.json').write_text(json.dumps(receipt,indent=2)+'\n');assert len(sizes)<20000 and largest[1]<=25*1024*1024
PY
# This exact command list is hash-bound in final-input.json; no oracle is handed to the fresh agent.
"$python_bin" - "$run_dir" "$project_dir" "$node_bin" "$python_bin" <<'PY'
import json,subprocess,sys
from pathlib import Path
run,project=map(Path,sys.argv[1:3]);node,python=sys.argv[3:];config=json.loads((run/'final-input.json').read_text())
allowed={'research/q025/integration/final-acceptance/browser.py','research/q025/integration/agent-browser-observer.py','research/q025/integration/public-bridge-acceptance.py'}
outcomes=[]
for phase in config['phases']:
 assert phase['script'] in allowed
 args=[python,str(project/phase['script']),'--project',str(project),'--node',node,'--output',str(run/phase['output'])]
 assert not Path(phase['output']).is_absolute() and '..' not in Path(phase['output']).parts
 for arg in phase.get('args',[]):args.append(arg.replace('{ATLAS}',str(project/config['atlasDirectory'])).replace('{PROJECT}',str(project)))
 with (run/(phase['output']+'.log')).open('w')as log:
  result=subprocess.run(args,cwd=project,stdout=log,stderr=subprocess.STDOUT)
 outcomes.append({'script':phase['script'],'output':phase['output'],'exitCode':result.returncode,'separatePolicyOutcome':bool(phase.get('recordExpectedPolicyFailure',False))});(run/'phase-results.json').write_text(json.dumps(outcomes,indent=2)+'\n')
 if result.returncode and not phase.get('recordExpectedPolicyFailure',False):raise SystemExit(result.returncode)
PY
