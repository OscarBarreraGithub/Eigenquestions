import copy,unittest
from contract import evaluate
class ContractTests(unittest.TestCase):
 def setUp(self):
  self.p={'familyId':'t','rows':[{'id':'z0','unitRef':'u0','questionRef':'pq0','role':'addresses'}],'units':[{'ref':'u0','paperId':'paper'}],'scopes':[{'ref':'pq0'}],'pairedUnitContext':[],'refRegistry':{'u0':{'kind':'description'},'e0':{'kind':'primary','paperId':'paper'},'e1':{'kind':'primary','paperId':'other'}}}
  self.r={'version':'q025-source-role-confirmation/1','familyId':'t','stage':'confirmation','summary':'bounded','rows':[{'id':'z0','verdict':'supported_as_written','basis':'description_checked','revisedRole':'unchanged','additionalQualifications':[],'reason':'Exact target contribution with original limits retained.','refs':['u0','pq0']}],'limitations':['No home or identity admission.'],'unresolved':[]}
 def test_exact_role_confirmation(self):self.assertEqual(evaluate(self.p,self.r)['validation']['exactRowCount'],1)
 def test_missing_row_rejected(self):self.r['rows']=[];self.assertRaises(AssertionError,evaluate,self.p,self.r)
 def test_foreign_primary_cannot_upgrade_basis(self):self.r['rows'][0].update(basis='source_excerpt_checked',refs=['u0','pq0','e1']);self.assertRaises(AssertionError,evaluate,self.p,self.r)
 def test_invented_reference_rejected(self):self.r['rows'][0]['refs'].append('e404');self.assertRaises(AssertionError,evaluate,self.p,self.r)
 def test_new_limit_is_not_exact_agreement(self):self.r['rows'][0]['additionalQualifications']=['Only one component'];self.assertRaises(AssertionError,evaluate,self.p,self.r)
 def test_role_revision_cannot_be_hidden(self):self.r['rows'][0]['revisedRole']='comparison';self.assertRaises(AssertionError,evaluate,self.p,self.r)
if __name__=='__main__':unittest.main()
