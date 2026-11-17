import copy,json,unittest
from pathlib import Path
from build_intake_overlay import apply_scope_resolution,REG
B=Path(__file__).resolve().parent
class Overlay(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.r=json.loads(REG.read_text());cls.o=json.loads((B/'intake-overlay.json').read_text());cls.a=json.loads((B/'explicit-adjudications.json').read_text())
 def test_only_exact_approved_fields_change(self):
  records={r['recordId']:r for r in self.r['records']}
  for resolution in self.o['scopeAssessmentResolutions']:
   old=records[resolution['recordId']];new=apply_scope_resolution(old,resolution)
   self.assertEqual(old['definition'],new['definition']);self.assertEqual(old['scopeStatus'],new['scopeStatus']);self.assertEqual(new['originalAdmissionAssessment'],old['assessment']);self.assertFalse(new['admissionJustificationFlags'])
   broken=copy.deepcopy(old);broken['assessment']['note']+=' changed'
   with self.assertRaises(AssertionError):apply_scope_resolution(broken,resolution)
 def test_premise_amendment_never_becomes_annotation_only(self):
  premise=[r for r in self.a['rows'] if r['scopeImpact']=='premise_change'];self.assertEqual(len(premise),1);self.assertTrue(premise[0]['dependencyRevalidationRequired'])
  f=[r for r in self.o['factorQualificationResolutions'] if r['scopeImpact']=='premise_change'];self.assertEqual(len(f),1);self.assertTrue(f[0]['dependencyRevalidationRequired'])
 def test_complete_case_accounting_and_abstention(self):
  self.assertEqual(len(self.o['scopeAssessmentResolutions']),30);self.assertEqual(len(self.o['factorQualificationResolutions']),27);self.assertFalse(self.o['unmatchedAdmittedCases']);self.assertEqual(len(self.a['pending']),1)
  self.assertIn(':f28:',self.a['pending'][0]['caseId'])
 def test_dependency_inventory_has_no_affected_existing_home(self):
  a=json.loads((B/'premise-dependency-audit.json').read_text());self.assertEqual(len(a['dependentUnitAssessments']),1);self.assertEqual(len(a['dependentScopeContributions']),1);self.assertFalse(a['affectedExisting1055Homes'])
if __name__=='__main__':unittest.main()
