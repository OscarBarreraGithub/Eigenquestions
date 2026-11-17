import copy,sys,unittest
from pathlib import Path
from production_contract import evaluate
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'recovery'))
from test_compact import fixture
class ProductionTests(unittest.TestCase):
 def factor(self):return {'id':'pf0','kind':'assumption','label':'Conditional setup','status':'scope_candidate','qualification':'A specified regime only.','refs':['d0']}
 def test_identical_definition_reuses_prior(self):
  p,r=fixture();f=self.factor();p['priorFactors']=[f];r['factors']=[copy.deepcopy(f)];r['units'][0]['f']=['pf0'];d=evaluate(p,r);self.assertEqual(d['normalizedReview']['factors'],[]);self.assertEqual(d['normalizedReview']['units'][0]['f'],['pf0']);self.assertEqual(d['factorTransformations'][0]['kind'],'identical_prior_definition_reuse')
 def test_changed_definition_is_new_and_all_row_refs_renamed(self):
  p,r=fixture();f=self.factor();p['priorFactors']=[f];r['factors']=[dict(f,qualification='A distinct stated regime.')]
  for a in r['units']:a['f']=['pf0']
  d=evaluate(p,r);self.assertEqual(d['factorRenameMap'],{'pf0':'f_revision_pf0'});self.assertTrue(all(a['f']==['f_revision_pf0'] for a in d['normalizedReview']['units']));self.assertEqual(p['priorFactors'][0]['qualification'],'A specified regime only.');self.assertEqual(d['factorTransformations'][0]['scientificStatus'],'new_candidate_not_prior_agreement')
 def test_cross_unit_description_retained_as_context(self):
  p,r=fixture();r['units'][0]['refs'].append('d1');d=evaluate(p,r);self.assertEqual(d['normalizedReview']['units'][0]['refs'],['e0']);self.assertEqual(d['crossUnitDescriptionContext'][0]['reference'],'d1');self.assertFalse(d['crossUnitDescriptionContext'][0]['scientificImplicationInferred'])
 def test_context_cannot_certify_own_primary_reading(self):
  p,r=fixture();r['units'][0]['refs']=['d1']
  with self.assertRaises(AssertionError):evaluate(p,r)
 def test_missing_rows_still_fail(self):
  p,r=fixture();r['units']=[]
  with self.assertRaises(AssertionError):evaluate(p,r)
 def test_invented_ref_still_fails(self):
  p,r=fixture();r['units'][0]['refs']=['invented']
  with self.assertRaises(AssertionError):evaluate(p,r)
 def test_duplicate_factor_definition_still_fails(self):
  p,r=fixture();f=self.factor();p['priorFactors']=[f];r['factors']=[f,f]
  # Duplicate definitions are ambiguous even if they happen to share bytes.
  with self.assertRaises(AssertionError):evaluate(p,r)
if __name__=='__main__':unittest.main()
