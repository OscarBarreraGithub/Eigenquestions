"""Explicit compact Git inventory; bulk recovery remains separately checksummed."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent


def descriptor(p):
    return {'path': str(p.relative_to(ROOT)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size}


selected = set()
for name in ['accepted.mjs', 'assemble.mjs', 'fine-identities.mjs', 'lazy-package.mjs', 'accounting.mjs', 'accounting.test.mjs']:
    selected.add(ROOT / 'research/q025/assembly' / name)
for name in ['compile_mapped_homes.mjs', 'compile_mapped_homes.test.mjs', 'compile_changed_homes.mjs', 'compile_changed_homes.test.mjs']:
    selected.add(ROOT / 'research/q025/assembly/placement-incremental-v1' / name)
for p in HERE.iterdir():
    if p.is_file() and p.suffix in ['.mjs', '.py', '.md', '.json'] and p.name != 'checkpoint.json':
        selected.add(p)
selected.add(HERE / 'assembly-tests.log')
for name in ['aggregate-admission.json', 'source-accounting-admission.json', 'collection-frontier-admission.json', 'fine-home-access-admission.json', 'organizational-access-policy.json', 'binding.json']:
    selected.add(HERE / 'packet' / name)
for folder in ['final-frontier-v1', 'cut03-scope-review-v1']:
    for p in (ROOT / 'research/q025/assembly' / folder).iterdir():
        if p.is_file() and p.suffix in ['.py', '.json'] and p.name != 'console.json' and '.local.' not in p.name:
            selected.add(p)
bulk = []
for folder in ['cut-04', 'cut-05', 'new-scope-cut-02', 'new-scope-cut-03', 'new-scope-cut-04', 'new-scope-cut-05', 'explicit-cut-03', 'explicit-cut-04']:
    directory = ROOT / 'research/q025/assembly/placement-incremental-v1' / folder
    for p in directory.rglob('*.json'):
        if p.name not in ['settings.json', 'report.json', 'component.json', 'admission.json']:
            continue
        if p.stat().st_size <= 500_000:
            selected.add(p)
        else:
            bulk.append(descriptor(p))
geometry = ROOT / 'research/q025/geometry/final-overview-v1'
for name in ['compute.py', 'correct_display.py', 'build_schematic.mjs', 'run.sbatch', 'correction.sbatch', 'input-pins.json', 'job-receipt.json', 'correction-job-receipt.json', 'schematic-overview.json', 'sacct.txt', 'results/manifest.json', 'results/diagnostics.json', 'corrected-display/manifest.json', 'corrected-display/diagnostics.json']:
    selected.add(geometry / name)
files = [descriptor(p) for p in sorted(selected)]
out = {'schemaVersion': 'q025-final-preholdout-checkpoint/1', 'status': 'frozen', 'files': files, 'count': len(files), 'totalBytes': sum(r['bytes'] for r in files), 'bulkComponentPinsNotForGit': bulk, 'archiveReceipt': descriptor(HERE / 'archive-receipt.json'), 'scope': 'Assembly-owned code, exact compact scientific receipts, review/frontier evidence, final acceptance freeze, and numerical negative results. No native runtime output, primary page text, bulk package or source-context pack is included.', 'externalInterfacePins': json.loads((HERE / 'freeze-handoff.json').read_text())['interfacePins'], 'nextAction': 'Root verifies and stages only listed files plus this checkpoint. Product performs isolated acceptance; the evaluator uses frozen scopes for already planned blinded routing. No further implementation or scientific edits before that acceptance.'}
(HERE / 'checkpoint.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'count': len(files), 'bytes': out['totalBytes'], 'checkpoint': descriptor(HERE / 'checkpoint.json')}, indent=2))
