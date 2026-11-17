import copy,importlib.util,unittest
from pathlib import Path
s=importlib.util.spec_from_file_location('prep',Path(__file__).with_name('prepare.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class ExactClass(unittest.TestCase):
 def setUp(self):self.rows=m.read(m.INPUT)['newScopes']
 def test_actual_complete_class(self):
  self.assertEqual(len(self.rows),27);self.assertEqual(sum(len(n['sources'])for n in self.rows),34)
  for n in self.rows:self.assertTrue(m.check_scope(n))
 def test_changed_definition_or_coverage_is_not_exact_class(self):
  for change in ['replace','target','weight','missing','union']:
   n=copy.deepcopy(self.rows[0]);r=n['sources'][0]
   if change=='replace':n['independentAssessment']['verdict']='revise'
   if change=='target':r['challengeJudgment']['targetCoverage'][0]['explanation']='Changed target'
   if change=='weight':r['challengeJudgment']['homes'][0]['weight']=.5
   if change=='missing':r['challengeJudgment']['missingPremises']=['Unidentified system']
   if change=='union':r['challengeJudgment']['coverageMode']='compound_union'
   with self.assertRaises(AssertionError):m.check_scope(n)
 def test_original_whole_source_cannot_change(self):
  n=copy.deepcopy(self.rows[0]);n['sources'][0]['description']+=' silently changed'
  with self.assertRaises(AssertionError):m.check_scope(n)
 def test_distinct_independent_scope_review_required(self):
  n=copy.deepcopy(self.rows[0]);n['stage']='challenge'
  with self.assertRaises(AssertionError):m.check_scope(n)
if __name__=='__main__':unittest.main()
