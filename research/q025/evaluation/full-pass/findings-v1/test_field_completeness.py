import unittest
from audit_field_completeness import screen
class AuditTests(unittest.TestCase):
 def test_under_cap_review_notes_are_screened_separately(self):
  r={'cardReviews':[{'id':f'p{i}','note':('A'*150)+' and ','refs':[]} for i in range(5)]}
  flags,_=screen(r);self.assertEqual(len(flags),5)
  self.assertTrue(all(x['schemaMaxLength']==420 and not x['atSchemaCap'] and x['impact']=='admission_justification' for x in flags))
 def test_cap_is_only_screening_flag(self):
  flags,_=screen({'factors':[{'id':'f0','kind':'regime','qualification':'A'*239+'.','refs':[]}]})
  self.assertEqual(flags[0]['reasons'],['exact_schema_max_length'])
 def test_unlimited_scope_strings_traversed(self):
  flags,n=screen({'region':{'scope':{'assumptions':['complete assumption.']},'summary':'B'*80+' but'}})
  self.assertEqual(n,2);self.assertIn('terminal_function_word',flags[0]['reasons'])
if __name__=='__main__':unittest.main()
