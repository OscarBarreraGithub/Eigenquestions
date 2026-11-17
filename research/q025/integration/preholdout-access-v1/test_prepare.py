import importlib.util,tempfile,unittest,hashlib,os
from pathlib import Path
spec=importlib.util.spec_from_file_location('preholdout_prepare',Path(__file__).with_name('prepare.py'));module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class PrepareTests(unittest.TestCase):
 def test_exact_preholdout_phase_and_counts(self):
  scope={'deliveryState':'partial_pre_holdout_candidate','accountingReason':'pre_holdout_freeze','sourceInventoryAccounted':True,'sourceAccountingComplete':False,'allocatedQuestionCount':8399,'unresolvedQuestionCount':31,'reservedQuestionCount':43}
  module.preholdout_scope(scope)
  for change in [{'sourceAccountingComplete':True},{'reservedQuestionCount':0},{'allocatedQuestionCount':8400},{'deliveryState':'accepted_for_installation'}]:
   with self.subTest(change=change),self.assertRaises(AssertionError):module.preholdout_scope(scope|change)
 def test_verified_hardlink_is_never_written_or_chmodded(self):
  with tempfile.TemporaryDirectory()as tmp:
   root=Path(tmp);source=root/'source';source.write_bytes(b'Frozen scientific bytes');before=source.stat();target=root/'staged'/'copy';row={'path':'copy','bytes':source.stat().st_size,'sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
   receipt=module.link_verified(source,target,row);self.assertEqual(target.stat().st_ino,before.st_ino);self.assertEqual(source.read_bytes(),b'Frozen scientific bytes');self.assertEqual(source.stat().st_mode,before.st_mode);self.assertEqual(receipt['sha256'],row['sha256'])
   with self.assertRaises(AssertionError):module.link_verified(source,root/'wrong',row|{'sha256':'0'*64})
   with self.assertRaises(FileExistsError):module.link_verified(source,target,row)
 def test_paths_reject_escape(self):
  for name in ['../x','/tmp/x','x/../../y','x\\y']:
   with self.subTest(name=name),self.assertRaises(ValueError):module.safe(name)
if __name__=='__main__':unittest.main()
