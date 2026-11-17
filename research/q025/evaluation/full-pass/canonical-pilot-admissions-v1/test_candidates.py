import json,unittest
from pathlib import Path
B=Path(__file__).resolve().parent
class CandidateLedger(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.x=json.loads((B/'agreement-candidates.json').read_text())
 def test_all_questions_and_decisions_accounted_without_promoting_revisions(self):
  x=self.x;self.assertEqual(x['counts']['supportedPriorQuestionDefinitions'],27);self.assertEqual(x['counts']['supportedPriorDecisions'],63)
  self.assertEqual({r['priorDecision']['id'] for f in x['families'] for r in f['revisedDecisions']},{'pd6','pd15'})
  self.assertTrue(all(q['priorAssessment']['verdict']=='supported_as_written' for f in x['families'] for q in f['unchangedQuestionCandidates']))
 def test_new_stats_questions_and_roles_separate(self):
  s=next(f for f in self.x['families'] if f['family']=='statistics');self.assertEqual(len(s['newChallengerQuestions']),3)
  self.assertTrue(all(q['id'].startswith('cq') for q in s['newChallengerQuestions']))
  self.assertTrue(all(c['questionRef'].startswith('cq') for c in s['newOrChangedChallengerContributions']))
 def test_carried_roles_are_not_claimed_repeated_judgments(self):
  self.assertEqual(self.x['counts']['carriedPriorSourceRoles'],124);self.assertEqual(self.x['counts']['independentlyRepeatedSourceRoleRows'],0)
  self.assertTrue(all(not c['independentlyRepeatedRoleRow'] for f in self.x['families'] for c in f['carriedPriorContributions']))
 def test_complete_constraint_and_disposition_inventory_retained(self):
  for f in self.x['families']:
   self.assertEqual(len(f['originalScopeDispositions']),len(f['sourceScopeBindings']));self.assertEqual(len(f['challengeScopeDispositions']),len(f['sourceScopeBindings']));self.assertTrue(f['priorPairConstraints']);self.assertTrue(f['challengePairConstraints'])
  self.assertEqual(self.x['counts']['identitiesAdmitted'],0);self.assertEqual(self.x['counts']['homesAdmitted'],0)
if __name__=='__main__':unittest.main()
