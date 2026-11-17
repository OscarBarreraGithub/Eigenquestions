"""Run the frozen deterministic miner on the additive registry-v4 envelope.

No nomination rule changes. Keep the old frozen miner byte-for-byte intact.
"""
import hashlib
import json
import sys
from pathlib import Path

original = Path(__file__).with_name('mine_scope_candidates.py')
source = original.read_text()
old = "['q025-authored-scope-registry/1','q025-authored-scope-registry/3']"
new = "['q025-authored-scope-registry/1','q025-authored-scope-registry/3','q025-authored-scope-registry/4']"
assert source.count(old) == 1
exec(compile(source.replace(old, new), str(original), 'exec'),
     {'__name__': '__main__', '__file__': str(original)})
out = Path(sys.argv[sys.argv.index('--out') + 1]) / 'report.json'
report = json.loads(out.read_text())
report['registryCompatibilityWrapper'] = {
    'path': str(Path(__file__)),
    'sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'meaning': 'Accept additive registry schema v4; all frozen nomination rules unchanged.'}
out.write_text(json.dumps(report, indent=2) + '\n')
