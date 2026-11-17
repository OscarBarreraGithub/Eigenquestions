import copy,json,unittest
from pathlib import Path
from derive import derive,separate_context,old
B=Path(__file__).resolve().parent;F=B.parent
class Tests(unittest.TestCase):
 def test_actual_both_outputs_validate_without_science_edits(self):
  for family,count in [('mediation-scope',1),('control-statistics',5)]:
   p,r,d=derive(F/'native-local/canonical-recovery-v2/jobs'/f'canonical-recovery-{family}-proposal');self.assertTrue(d['validation']['valid']);self.assertEqual(sum(len(x['contextualDecisionIds']) for x in d['contextualDispositionReferences']),count);self.assertFalse(d['scientificContentChanged']);self.assertEqual(d['discardedReferences'],0)
   original={x['ref']:x for x in d['originalScopeDispositions']}
   for row in r['scopeDispositions']:
    self.assertEqual({k:v for k,v in row.items() if k!='decisionIds'},{k:v for k,v in original[row['ref']].items() if k!='decisionIds'})
 def test_unknown_context_is_rejected(self):
  with self.assertRaisesRegex(AssertionError,'Unknown'):separate_context({'decisions':[],'scopeDispositions':[{'ref':'c0','decisionIds':['invented']}]})
 def test_no_endpoint_inference(self):
  r={'decisions':[{'id':'pd0','members':['pq0','pq1'],'target':''}],'scopeDispositions':[{'ref':'c0','decisionIds':['pd0'],'resolution':'common_target'}]};x,ctx=separate_context(r);self.assertEqual(x['scopeDispositions'][0]['decisionIds'],[]);self.assertEqual(x['decisions'],r['decisions']);self.assertEqual(ctx[0]['contextualDecisionIds'],['pd0'])
 def test_budget_single_source(self):
  text=(B/'INSTRUCTIONS.md').read_text();self.assertEqual(text.count('{{MAX_OUTPUT_CHARACTERS}}'),1);self.assertNotIn('120000',text);self.assertNotIn('60000',text)
if __name__=='__main__':unittest.main()
