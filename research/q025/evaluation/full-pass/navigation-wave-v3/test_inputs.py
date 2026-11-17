import hashlib,json,unittest
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent;W=E.parents[2]
class Inputs(unittest.TestCase):
 def test_exact_eighty_three_with_no_covered_or_conflict_repeats(self):
  census=json.loads((F/'navigation-wave-v2/canonical-completion-census.json').read_text());expected={v for g in census['remainingPriorityGroups']for v in g['comparisonIds']};seen=[];idx=json.loads((B/'source-index.json').read_text())
  for family in idx['families']:
   p=W/family['packet']['path'];self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),family['packet']['sha256']);x=json.loads(p.read_text());seen+=x['screenComparisonIds'];self.assertEqual(len(x['nominations']),len(x['screenComparisonIds']));self.assertTrue(all(not n['screenVariantConflictWithheld']for n in x['nominations']));self.assertTrue(x['units'])
  self.assertEqual(len(seen),83);self.assertEqual(len(set(seen)),83);self.assertEqual(set(seen),expected)
 def test_all_exact_descriptions_and_disclosed_reading(self):
  eligible=set(json.loads((F/'reconciliation-v1/eligible-preholdout-unit-ids-v1.json').read_text())['unitIds']);idx=json.loads((B/'source-index.json').read_text())
  for fam in idx['families']:
   x=json.loads((W/fam['packet']['path']).read_text());self.assertFalse(x['evidence']);self.assertFalse(x['coverage']['completeSourceAssignmentReview']);self.assertEqual(x['coverage']['actualPrimaryWindows'],0)
   for u in x['units']:self.assertIn(u['unitId'],eligible);self.assertEqual(hashlib.sha256(u['description'].encode()).hexdigest(),x['refRegistry'][u['ref']]['textSha256'])
 def test_generated_scope_contract_is_pinned(self):
  c=json.loads((F/'native-local/navigation-wave-v3/campaign.json').read_text());paths={x['path']for x in c['publicPins']};self.assertIn('full-pass/navigation-contract-v3/contract.py',paths);self.assertIn('full-pass/navigation-wave-v2/contract.py',paths)
if __name__=='__main__':unittest.main()
