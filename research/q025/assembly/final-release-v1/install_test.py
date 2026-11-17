import gzip
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('final_install', Path(__file__).with_name('install.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.candidate = self.root / 'candidate'
        self.candidate.mkdir()
        self.external = self.root / 'context.json.gz'
        self.external.write_bytes(gzip.compress(b'{"public":"source context"}'))

    def tearDown(self):
        self.temp.cleanup()

    def write(self, name, value):
        body = json.dumps(value).encode()
        (self.candidate / name).write_bytes(body)
        return {'path': name, 'sha256': m.sha(body), 'bytes': len(body)}

    def fixture(self, duplicate=False, partial=False):
        catalog = self.write('catalog.json', {'kind': 'test'})
        ext = {'path': 'context.json.gz', 'bytes': self.external.stat().st_size, 'sha256': m.sha(self.external.read_bytes()), 'sourcePath': str(self.external)}
        plan = self.write('asset-plan.json', {'assets': [ext]})
        rows = [catalog, {k: ext[k] for k in ['path', 'bytes', 'sha256']}]
        if duplicate:
            rows.append(catalog)
        delivery = self.write('delivery-assets.json', {'files': rows, 'gate': {'passed': True}})
        manifest = self.write('manifest.json', {'atlasId': 'test-atlas', 'atlasVersion': 'v1', 'entryDestinationId': 'physics', 'scope': {'sourceAccountingComplete': True, 'reservedQuestionCount': 43 if partial else 0, 'description': 'Dated coverage'}, 'files': {'catalog': catalog, 'deliveryAssets': delivery}})
        handoff = self.write('handoff.json', {'manifestSha256': manifest['sha256'], 'assetPlan': plan})
        freeze = self.write('freeze.json', {'files': [manifest, handoff, plan, delivery]})
        return self.candidate / 'freeze.json', freeze['sha256']

    def prepare(self, **kwargs):
        path, digest = self.fixture(**kwargs)
        return m.prepare(self.root, self.candidate, path, digest)

    def test_read_only_then_exact_install_preserves_old_index_and_ignores_scratch(self):
        (self.candidate / 'private-notes.json').write_text('{"not":"public"}')
        manifest, rows, destination, report = self.prepare()
        self.assertFalse(destination.exists())
        self.assertEqual(report['dataFiles'], 4)
        self.assertEqual(report['leakageScreen']['gzipFiles'], 1)
        index = self.root / 'data/atlas/index.json'
        index.parent.mkdir(parents=True)
        old = {'atlasId': 'old', 'atlasVersion': 'v0', 'entryDestinationId': 'old-root'}
        index.write_text(json.dumps({'schemaVersion': '1.0.0', 'atlases': [old]}))
        receipt = m.install(manifest, rows, destination, report['manifestSha256'], report['manifestSha256'], index)
        self.assertTrue(receipt['installed'])
        self.assertEqual({p.name for p in destination.iterdir()}, {'catalog.json', 'manifest.json', 'delivery-assets.json', 'context.json.gz'})
        self.assertEqual(json.loads(index.read_text())['atlases'][0], old)
        self.assertEqual(json.loads(index.read_text())['home']['destinationId'], 'physics')
        with self.assertRaisesRegex(ValueError, 'overwrite'):
            m.install(manifest, rows, destination, report['manifestSha256'], report['manifestSha256'], index)

    def test_changed_external_bytes_cannot_create_public_version(self):
        manifest, rows, destination, report = self.prepare()
        self.external.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'Changed declared bytes'):
            m.install(manifest, rows, destination, report['manifestSha256'], report['manifestSha256'], self.root / 'data/atlas/index.json')
        self.assertFalse(destination.exists())
        self.assertFalse((self.root / 'data/atlas/index.json').exists())

    def test_exact_operator_acceptance_required(self):
        manifest, rows, destination, report = self.prepare()
        with self.assertRaisesRegex(ValueError, 'acceptance'):
            m.install(manifest, rows, destination, '0' * 64, report['manifestSha256'], self.root / 'data/atlas/index.json')
        self.assertFalse(destination.exists())

    def test_duplicate_and_reserved_inputs_reject(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate delivery'):
            self.prepare(duplicate=True)
        with self.assertRaisesRegex(ValueError, 'partial accounting'):
            self.prepare(partial=True)

    def test_traversal_and_private_payload_reject_including_gzip(self):
        for path in ['../x.json', '/x.json', './x.json', 'x//y.json', 'x\\y.json']:
            with self.assertRaises(ValueError):
                m.safe_name(path)
        for name, body in [('plain.json', b'{"path":"/Users/example/private"}'), ('compressed.json.gz', gzip.compress(b'{"path":"/n/netscratch/private"}'))]:
            with self.assertRaisesRegex(ValueError, 'private_absolute_path'):
                m.leakage_check(body, name)

    def test_missing_external_and_changed_freeze_reject(self):
        path, digest = self.fixture()
        with self.assertRaisesRegex(ValueError, 'Changed final freeze'):
            m.prepare(self.root, self.candidate, path, '0' * 64)
        self.external.unlink()
        with self.assertRaisesRegex(ValueError, 'Missing or symlink'):
            m.prepare(self.root, self.candidate, path, digest)


if __name__ == '__main__':
    unittest.main()
