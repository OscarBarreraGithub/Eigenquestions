import json,sys,unittest
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;sys.path.insert(0,str(F/'findings-v1'));from audit_field_completeness import screen
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.c=json.loads((B/'supported-scope-role-component-v1.json').read_text());cls.reg=json.loads((F/'reconciliation-v1/authored-scope-registry-v3-20261117T121953Z.json').read_text());cls.records={r['candidateId']:r for r in cls.reg['records']};cls.decisions={d['id']:d for d in cls.c['decisions']}
 def test_every_admitted_scope_is_exact_and_no_definition_flag(self):
  for d in self.c['destinations']:
   r=self.records[d['id']];self.assertEqual(r['scopeStatus'],'independently_supported');self.assertFalse(screen({'cards':[{'id':r['localRef'],**r['definition']}]})[0])
   for k in ['title','question','summary','scope']:self.assertEqual(d[k],r['definition'][k])
   self.assertEqual(d['readingCoverage']['readingLimit'],r['definition']['readingLimit'])
 def test_common_reading_not_upgraded(self):
  for row in self.c['sourceContributions']:
   d=self.decisions[row['decisionId']];r=d['readingAgreement'];self.assertEqual(row['basis'],r['commonBasis']);self.assertNotEqual(r['proposalReviewId'],r['challengeReviewId']);self.assertTrue(any(e['kind']=='description'and e['unitId']==row['unitId']for e in row['evidenceRefs']))
   if row['basis']=='source_excerpt_checked':self.assertEqual(r['proposalBasis'],'excerpt');self.assertEqual(r['challengeBasis'],'excerpt');self.assertGreater(r['commonPrimaryWindowCount'],0)
 def test_no_roles_promoted_to_homes_aliases_or_links(self):
  self.assertFalse(self.c['placements']);self.assertFalse(self.c['relations']);self.assertFalse(self.c['aliases']);self.assertTrue(all(x['type']in['scope_acceptance','source_contribution']for x in self.c['decisions']))
 def test_changed_premise_and_scope_limits_are_excluded(self):
  self.assertTrue(any(x['reason']=='explicit_changed_regime_or_scope_mismatch'for x in self.c['exclusions']['roles']));self.assertTrue(any(x['reason']=='limits_require_adjudication'for x in self.c['exclusions']['scopeRecords']))
 def test_home_audit_is_candidate_only(self):
  x=json.loads((B/'uncomplicated-home-policy-audit-v1.json').read_text());self.assertEqual(x['homesAdmitted'],0);self.assertEqual(len(x['representativeCandidates']),10);self.assertTrue(x['explicitKKCounterexamples'])
if __name__=='__main__':unittest.main()
