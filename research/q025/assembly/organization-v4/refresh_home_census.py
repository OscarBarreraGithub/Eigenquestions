"""Apply the frozen home-evidence audit to the final leaf-complete cut.

The admission policy is unchanged. This wrapper writes only this new staging
directory and never modifies the v4 census or running screening inputs.
"""
import hashlib
import json
import sys
from pathlib import Path

B = Path(__file__).resolve().parent
ROOT = B.parents[3]
original = ROOT / 'research/q025/geometry/canonical-review-design/audit_home_lanes_v4.py'
sys.path.insert(0, str(original.parent))
source = original.read_text()
source = source.replace('authored-scope-registry-v4-20261117T131639Z.json', 'authored-scope-registry-v5-20261117T135430Z.json')
source = source.replace('8fec0de5da3901625e4fea16240d4a487878b7b6c803c29a3e3893dc89c1fe7e', '0e0d5443114cbcba6078a70241c809b5fb713097b22d9d1846b63f6172da69d5')
source = source.replace('home-lanes-v4', 'home-lanes-v5')
exec(compile(source, str(original), 'exec'), {'__file__': str(Path(__file__)), '__name__': '__main__'})
out = B / 'home-lanes-v5-report.json'
report = json.loads(out.read_text())
report['frozenAuditImplementation'] = {'path': str(original.relative_to(ROOT)), 'sha256': hashlib.sha256(original.read_bytes()).hexdigest()}
report['refreshWrapperSha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
