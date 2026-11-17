import hashlib, importlib.util, io, json, tarfile, tempfile, unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('final_stage',Path(__file__).with_name('stage.py'));stage_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(stage_module)
sha=lambda data:hashlib.sha256(data).hexdigest()
class IngressTests(unittest.TestCase):
 def envelope(self,root,partial=False,wrong_home=False,incomplete=False,reserved=0):
  files={p:b'test' for p in ['package.json','package-lock.json','wrangler.toml','scripts/build-site.mjs','scripts/site-check.mjs','bin/navigate.mjs','bin/mcp-navigator.mjs','skills/physics-navigator/SKILL.md','research/q025/integration/agent-browser-observer.py']}
  manifest={'atlasId':'test','atlasVersion':'v1','entryDestinationId':'physics','scope':{'partialRehearsal':partial,'unallocatedQuestionCount':43,'sourceAccountingComplete':not incomplete,'reservedQuestionCount':reserved}};body=json.dumps(manifest).encode();files['data/atlas/test/v1/manifest.json']=body
  files['data/atlas/index.json']=json.dumps({'home':{'atlasId':'test','atlasVersion':'v1','destinationId':'wrong'if wrong_home else'physics'}}).encode();files['accounting.json']=b'{"unresolvedFacets":43,"allSourcesAccounted":true}'
  archive=root/'application.tar.gz'
  with tarfile.open(archive,'w:gz')as tar:
   for name,data in files.items():info=tarfile.TarInfo(name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
  config={'archives':[{'path':archive.name,'sha256':sha(archive.read_bytes()),'files':[{'path':k,'sha256':sha(v),'bytes':len(v)}for k,v in files.items()]}],'atlasDirectory':'data/atlas/test/v1','manifestSha256':sha(body),'releaseAccountingReceipt':{'path':'accounting.json','sha256':sha(files['accounting.json'])}}
  path=root/'final-input.json';path.write_text(json.dumps(config));return path
 def test_accounted_unresolved_facets_do_not_force_scientific_home(self):
  with tempfile.TemporaryDirectory()as tmp:
   root=Path(tmp);receipt=stage_module.stage(self.envelope(root),root/'project');self.assertEqual(receipt['verifiedFileCount'],12)
 def test_partial_and_wrong_explicit_home_fail(self):
  for options in [{'partial':True},{'wrong_home':True},{'incomplete':True},{'reserved':43}]:
   with self.subTest(options=options),tempfile.TemporaryDirectory()as tmp:
    root=Path(tmp)
    with self.assertRaises(AssertionError):stage_module.stage(self.envelope(root,**options),root/'project')
 def test_archive_hash_and_unsafe_paths_fail(self):
  with tempfile.TemporaryDirectory()as tmp:
   root=Path(tmp);config=self.envelope(root);(root/'application.tar.gz').write_bytes(b'changed')
   with self.assertRaisesRegex(AssertionError,'Archive checksum'):stage_module.stage(config,root/'project')
  for name in ['../outside','/outside','a/../../outside','a\\outside']:
   with self.subTest(name=name),self.assertRaises(ValueError):stage_module.safe_path(name)
if __name__=='__main__':unittest.main()
