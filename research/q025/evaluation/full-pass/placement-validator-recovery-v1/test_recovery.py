import unittest,copy,json
from pathlib import Path
import contract
B=Path(__file__).resolve().parent;F=B.parent;O=F/'native-local/placement-successors-v1/jobs/successor-placement-continuation-0041-proposal';P=json.loads((O/'packet.actual.json').read_text());R=json.loads((O/'reply.raw.txt').read_text())
class Recovery(unittest.TestCase):
 def test_exact_content_parity(self):
  self.assertEqual(contract.evaluate(P,R)['normalizedReview'],R);self.assertEqual(contract.base.evaluate(P,R)['normalizedReview'],R)
 def test_missing_source_still_rejected(self):
  r=copy.deepcopy(R);r['placements'].pop()
  with self.assertRaises(AssertionError):contract.evaluate(P,r)
 def test_unknown_scope_still_rejected(self):
  r=copy.deepcopy(R);r['placements'][0]['homes'][0]['scopeRef']='unknown_scope'
  with self.assertRaises(AssertionError):contract.evaluate(P,r)
 def test_failed_original_preserved_and_derived_receipt_explicit(self):
  old=json.loads((O/'receipt.json').read_text());new=json.loads((F/'native-local/placement-validator-recovery-v1/adopted/0041-proposal/receipt.json').read_text());self.assertEqual(old['status'],'failed');self.assertIn('ETIMEDOUT',old['error']);self.assertEqual(new['originalNativeStatus'],'failed');self.assertFalse(new['nativeReviewRepeated']);self.assertFalse(new['scientificContentChanged'])
