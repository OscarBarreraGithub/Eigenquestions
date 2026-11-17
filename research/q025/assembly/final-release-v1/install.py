"""Install only this frozen release's declared public bytes. Default: read-only audit."""
import argparse
import gzip
import hashlib
import json
import os
import re
import shutil
import tempfile
from collections import Counter
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
CANDIDATE = ROOT / 'research/q025/assembly/outputs/final-release-v1'
FREEZE_SHA256 = '141336abde9ec9e096beb6bda67f5f04f5ac21f72d7429a242d0920872881a91'
MANIFEST_SHA256 = '15b2dc99f216462e7d0deaec9f16b4de416cf0a291c76bcda6b973cd3b4ff3cb'
MAX_BYTES = 25 * 1024 * 1024
MAX_DECODED_BYTES = 64 * 1024 * 1024
PATTERNS = {
    'private_absolute_path': re.compile(r'/Users/|/home/|/n/netscratch/|/private/var/|/tmp/|file://|[A-Za-z]:\\\\(?:Users|home)\\\\'),
    'credential_like': re.compile(r'(?i)(?:\b(?:ghp|gho|ghu|ghs|github_pat)_[A-Za-z0-9_]{20,}|\bsk-[A-Za-z0-9_-]{24,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bBearer [A-Za-z0-9_.-]{20,})'),
}


def sha(body):
    return hashlib.sha256(body).hexdigest()


def safe_name(name):
    if not isinstance(name, str) or not name or '\\' in name:
        raise ValueError('Invalid public path')
    p = PurePosixPath(name)
    if p.is_absolute() or '..' in p.parts or str(p) != name or name == '.':
        raise ValueError('Unsafe or noncanonical public path')
    return name


def checked(path, descriptor):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError(f'Missing or symlink source: {path.name}')
    body = path.read_bytes()
    if len(body) != descriptor['bytes'] or sha(body) != descriptor['sha256']:
        raise ValueError(f'Changed declared bytes: {path.name}')
    return body


def leakage_check(body, name):
    if name.endswith('.gz'):
        import io
        with gzip.GzipFile(fileobj=io.BytesIO(body)) as stream:
            decoded = stream.read(MAX_DECODED_BYTES + 1)
        if len(decoded) > MAX_DECODED_BYTES:
            raise ValueError('Decoded public JSON exceeds audit bound')
    else:
        decoded = body
    text = decoded.decode('utf-8')
    # Report only category/path/offset; never print a possible credential itself.
    for kind, pattern in PATTERNS.items():
        if kind == 'private_absolute_path' and not any(token in text for token in ['/Users/', '/home/', '/n/netscratch/', '/private/var/', '/tmp/', 'file://', ':\\\\']):
            continue
        if kind == 'credential_like' and not any(token in text.lower() for token in ['ghp_', 'gho_', 'ghu_', 'ghs_', 'github_pat_', 'sk-', '-----begin ', 'bearer ']):
            continue
        hit = pattern.search(text)
        if hit:
            raise ValueError(f'Public leakage screen: {kind} in {name} at {hit.start()}')
    return len(decoded)


def prepare(root=ROOT, candidate=CANDIDATE, freeze_path=HERE / 'freeze-handoff.json', freeze_sha=FREEZE_SHA256):
    root, candidate = Path(root).resolve(), Path(candidate).resolve()
    freeze_body = Path(freeze_path).read_bytes()
    if sha(freeze_body) != freeze_sha:
        raise ValueError('Changed final freeze')
    freeze = json.loads(freeze_body)
    pins = {Path(r['path']).name: r for r in freeze['files']}
    for name in ['manifest.json', 'handoff.json', 'asset-plan.json', 'delivery-assets.json']:
        checked(candidate / name, pins[name])
    manifest = json.loads((candidate / 'manifest.json').read_bytes())
    handoff = json.loads((candidate / 'handoff.json').read_bytes())
    if handoff['manifestSha256'] != pins['manifest.json']['sha256']:
        raise ValueError('Handoff manifest mismatch')
    scope = manifest['scope']
    if scope.get('sourceAccountingComplete') is not True or scope.get('reservedQuestionCount') != 0 or scope.get('partialRehearsal') or scope.get('partialCandidate'):
        raise ValueError('Incomplete or partial accounting cannot install')
    for key in ['atlasId', 'atlasVersion']:
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:-]{0,199}', manifest[key]):
            raise ValueError('Unsafe atlas directory')
    plan = json.loads((candidate / 'asset-plan.json').read_bytes())
    if sha((candidate / 'asset-plan.json').read_bytes()) != handoff['assetPlan']['sha256']:
        raise ValueError('Asset plan mismatch')
    external = {}
    for r in plan['assets']:
        name = safe_name(r['path'])
        if name in external:
            raise ValueError('Duplicate external path')
        external[name] = r
    delivery = json.loads((candidate / 'delivery-assets.json').read_bytes())
    descriptors = {}
    for r in delivery['files']:
        name = safe_name(r['path'])
        if name in descriptors:
            raise ValueError('Duplicate delivery path')
        descriptors[name] = dict(r)
    for r in list(manifest['files'].values()) + [dict(pins['manifest.json'], path='manifest.json')]:
        name = safe_name(r['path'])
        if name in descriptors:
            old = descriptors[name]
            if old['sha256'] != r['sha256'] or ('bytes' in r and old['bytes'] != r['bytes']):
                raise ValueError('Conflicting delivery descriptor')
        else:
            descriptors[name] = dict(r)
    if not set(external) <= set(descriptors):
        raise ValueError('Undeclared external assets')
    rows, categories = [], Counter()
    total = decoded = 0
    for name, r in sorted(descriptors.items()):
        if not isinstance(r.get('bytes'), int) or not 0 <= r['bytes'] <= MAX_BYTES or not re.fullmatch('[a-f0-9]{64}', r['sha256']):
            raise ValueError('Invalid size/hash descriptor')
        if name in external:
            e = external[name]
            if any(e[k] != r[k] for k in ['bytes', 'sha256']):
                raise ValueError('External descriptor mismatch')
            source = Path(e['sourcePath'])
            category = 'source_context' if '/source-context-v3-compact/pack/' in str(source) else 'supplemental_external'
        else:
            source = candidate / name
            category = 'package'
        body = checked(source, r)
        decoded += leakage_check(body, name)
        rows.append({'path': name, 'sha256': r['sha256'], 'bytes': r['bytes'], 'source': source})
        total += len(body)
        categories[category + '_files'] += 1
        categories[category + '_bytes'] += len(body)
    if len(rows) > 20000:
        raise ValueError('Data alone exceeds static asset bound')
    relative = Path('data/atlas') / manifest['atlasId'] / manifest['atlasVersion']
    report = {
        'kind': 'q025-final-declared-install-audit', 'mode': 'read_only',
        'freezeSha256': freeze_sha, 'manifestSha256': pins['manifest.json']['sha256'],
        'installDirectory': str(relative), 'dataFiles': len(rows), 'indexFiles': 1,
        'dataBytes': total, 'largestFile': max(({k: r[k] for k in ['path', 'bytes']} for r in rows), key=lambda r: r['bytes']),
        'categories': dict(categories), 'decodedBytesScreened': decoded,
        'leakageScreen': {'files': len(rows), 'gzipFiles': sum(r['path'].endswith('.gz') for r in rows), 'findings': 0, 'categories': list(PATTERNS), 'limit': 'Pattern-based path/credential screen, not a general secret detector or scientific text audit.'},
        'projectedBuildGate': delivery['gate'], 'installed': False,
        'excluded': ['asset-plan.json', 'handoff.json', 'assembly-report.json', 'accepted-geometry-input.json', 'native review inputs', 'primary archives', 'recovery tar'],
    }
    return manifest, rows, root / relative, report


def install(manifest, rows, destination, approved_sha, actual_sha, index_path):
    if approved_sha != actual_sha:
        raise ValueError('Explicit acceptance of the exact manifest is required')
    destination, index_path = Path(destination), Path(index_path)
    if destination.exists() or destination.is_symlink():
        raise ValueError('Refuse to overwrite an immutable atlas version')
    before = index_path.read_bytes() if index_path.exists() else None
    index = json.loads(before) if before else {'schemaVersion': '1.0.0', 'atlases': []}
    if index.get('schemaVersion') != '1.0.0' or not isinstance(index.get('atlases'), list):
        raise ValueError('Invalid existing discovery index')
    if any(e['atlasId'] == manifest['atlasId'] and e['atlasVersion'] == manifest['atlasVersion'] for e in index['atlases']):
        raise ValueError('Version already appears in discovery index')
    entry = {k: manifest[k] for k in ['atlasId', 'atlasVersion', 'entryDestinationId']}
    entry.update(title='Physics atlas', scope=manifest['scope']['description'])
    index['atlases'].append(entry)
    index['home'] = {k: manifest[k] for k in ['atlasId', 'atlasVersion']}
    index['home']['destinationId'] = manifest['entryDestinationId']
    index_body = (json.dumps(index, ensure_ascii=False, indent=2) + '\n').encode()
    destination.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.q025-install-', dir=destination.parent))
    moved = False
    try:
        for row in rows:
            body = checked(row['source'], row)  # Detect changes since read-only audit.
            target = stage / safe_name(row['path'])
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(body)
            checked(target, row)
        if (index_path.read_bytes() if index_path.exists() else None) != before:
            raise ValueError('Discovery index changed during staging')
        if destination.exists():
            raise ValueError('Immutable version appeared during staging')
        stage.rename(destination)
        moved = True
        # Select the version only after every public file has been copied and verified.
        index_path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_index = tempfile.mkstemp(prefix='.q025-index-', dir=index_path.parent)
        try:
            with os.fdopen(fd, 'wb') as stream:
                stream.write(index_body)
            os.replace(temp_index, index_path)
        finally:
            if Path(temp_index).exists():
                Path(temp_index).unlink()
    finally:
        if not moved:
            shutil.rmtree(stage)
    return {'indexSha256': sha(index_body), 'indexBytes': len(index_body), 'installed': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--install', action='store_true', help='Only after root accepts the final browser/agent result.')
    parser.add_argument('--approved-manifest-sha256', help='Explicit operator release acceptance; does not alter the frozen manifest.')
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    if args.install and args.approved_manifest_sha256 != MANIFEST_SHA256:
        parser.error('--install requires --approved-manifest-sha256 with this exact final manifest')
    manifest, rows, destination, report = prepare()
    if args.install:
        report.update(install(manifest, rows, destination, args.approved_manifest_sha256, report['manifestSha256'], ROOT / 'data/atlas/index.json'))
        report['mode'] = 'installed_after_explicit_operator_acceptance'
    body = json.dumps(report, indent=2) + '\n'
    if args.report:
        args.report.write_text(body)
    print(body, end='')


if __name__ == '__main__':
    main()
