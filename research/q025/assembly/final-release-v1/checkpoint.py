"""Compact final-amendment checkpoint; bulk package/data stay in recovery storage."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent


def pin(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'bytes': path.stat().st_size}


files = {ROOT / 'research/q025/assembly/fine-identities.mjs', ROOT / 'research/q025/assembly/accounting.test.mjs'}
for path in HERE.iterdir():
    if path.is_file() and path.suffix in ['.mjs', '.py', '.md', '.json'] and path.name != 'checkpoint.json' and '.local.' not in path.name:
        files.add(path)
files.update([HERE / 'tests.log', HERE / 'assembly-input.log'])
for name in ['placement-admission.json', 'source-accounting-admission.json', 'aggregate-admission.json', 'binding.json']:
    files.add(HERE / 'packet' / name)
geometry = ROOT / 'research/q025/geometry/final-release-v1'
for name in ['update_flow.py', 'update_schematic.mjs', 'run.sbatch', 'job-receipt.json', 'schematic-overview.json', 'results/manifest.json', 'results/diagnostics.json', 'results/entry-support.json']:
    files.add(geometry / name)
pins = [pin(path) for path in sorted(files)]
result = {'schemaVersion': 'q025-final-dated-amendment-checkpoint/1', 'status': 'frozen', 'files': pins, 'count': len(pins), 'totalBytes': sum(r['bytes'] for r in pins), 'releaseFreeze': pin(HERE / 'freeze-handoff.json'), 'rootAdjudication': pin(ROOT / 'research/q025/evaluation/final-holdout/root-43-source-adjudication.json'), 'recoveryArchive': pin(HERE / 'archive-receipt.json'), 'externalInterfacePins': json.loads((HERE / 'freeze-handoff.json').read_text())['interfacePins'], 'excluded': 'Bulk aggregate/catalog/lazy package, raw primary/native artifacts, source-context pack, numeric matrices and recovery archive are excluded from Git. Exact recovery and dependency pins are retained.', 'remaining': 'Root owns final browser/agent acceptance, actual delivery file count, installation and deployment. Scientific source accounting and final numerical update are complete.'}
(HERE / 'checkpoint.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'count': len(pins), 'bytes': result['totalBytes'], 'checkpoint': pin(HERE / 'checkpoint.json')}, indent=2))
