import copy,unittest
from contract import evaluate
class Tests(unittest.TestCase):
 def setUp(self):
  self.p={'familyId':'f','scopes':[{'ref':'c0','priorReadingAssessment':{'decision':'supported_as_written'},'scopeStatus':'independently_supported'},{'ref':'c1','priorReadingAssessment':None,'scopeStatus':'new_challenger_proposal'}],'units':[{'ref':'u0'}],'nominations':[{'ref':'n0','left':'c0','right':'c1'}]};self.r={'version':'q025-canonical-triage/1','familyId':'f','stage':'triage','summary':'Distinct targets can share a method.','scopeReviews':[{'ref':c,'status':'retain_as_scoped','basis':'scope_definition','reason':'Explicit stated target.','refs':[c]}for c in ['c0','c1']],'comparisonReviews':[{'ref':'n0','identityScreen':'different_scoped_targets','scientificConnections':['shared_method','comparison'],'basis':'scope_definition','priority':'rich_relation_review','definingDifferences':['Different physical target.'],'reason':'Do not infer lack of methodological connection.','refs':['c0','c1']}],'limitations':['No primary text read.'],'unresolved':[]}
 def test_identity_contrast_keeps_method_possible(self):
  x=evaluate(self.p,self.r);self.assertFalse(x['scientificAdmission']);self.assertEqual(x['validation']['primaryWindowsRead'],0)
 def test_missing_pair_rejected(self):
  self.r['comparisonReviews']=[]
  with self.assertRaisesRegex(AssertionError,'comparison'):evaluate(self.p,self.r)
 def test_absent_primary_reference_rejected(self):
  self.r['comparisonReviews'][0]['refs']=['e99']
  with self.assertRaisesRegex(AssertionError,'evidence'):evaluate(self.p,self.r)
 def test_description_basis_requires_source(self):
  self.r['comparisonReviews'][0]['basis']='description_checked'
  with self.assertRaisesRegex(AssertionError,'Description'):evaluate(self.p,self.r)
 def test_none_does_not_erase_connection(self):
  self.r['comparisonReviews'][0]['scientificConnections']=['none_identified','shared_method']
  with self.assertRaisesRegex(AssertionError,'connection'):evaluate(self.p,self.r)
if __name__=='__main__':unittest.main()
