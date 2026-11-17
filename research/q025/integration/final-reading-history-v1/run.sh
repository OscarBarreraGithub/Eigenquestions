#!/bin/bash
set -euo pipefail
run=/n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/integration/final-reading-history-v1
project=/tmp/q025-final-61597944-bsXncp/supplement
node=/n/home09/obarrera/.conda/envs/ising_bootstrap/bin/node
python=/n/netscratch/randall_lab/Everyone/obarrera/physics-atlas-encoders/20261104-v1/env/bin/python
export PATH=/n/home09/obarrera/.conda/envs/ising_bootstrap/bin:$PATH
export PYTHONPATH=/n/netscratch/randall_lab/Everyone/obarrera/physics-atlas-graph-design/20261105-v1/ui-deps
export PLAYWRIGHT_BROWSERS_PATH=/n/netscratch/randall_lab/Everyone/obarrera/physics-atlas-graph-design/20261105-v1/browsers
trap 'echo exitCode=$? > "$run/exit.txt"' EXIT
rm "$project/lib/protocol/approved-display-editorial.mjs"
cp "$run/approved-display-editorial.mjs" "$project/lib/protocol/approved-display-editorial.mjs"
cd "$project"
"$node" scripts/build-site.mjs > "$run/build.log" 2>&1
"$python" "$run/check-page.py" --project "$project" --node "$node" --output "$run" > "$run/check.log" 2>&1
