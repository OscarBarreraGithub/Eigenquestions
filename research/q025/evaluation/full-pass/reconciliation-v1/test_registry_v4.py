import copy, hashlib, json, unittest
from pathlib import Path
from refresh_registry_v4 import E, B, resolve_home, same_science, proposal_dependency

class RegistryV4(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.path=B/'authored-scope-registry-v4-20261117T131639Z.json'
  cls.registry=json.loads(cls.path.read_text())
 def test_exact_cut_unique_lineage_and_successors(self):
  x=self.registry;self.assertEqual(hashlib.sha256(self.path.read_bytes()).hexdigest(),'8fec0de5da3901625e4fea16240d4a487878b7b6c803c29a3e3893dc89c1fe7e')
  keys=[v['canonicalReviewKey'] for v in x['selectedReviewLineages']]
  self.assertEqual(len(keys),len(set(keys)));self.assertEqual(x['counts']['completedLeafPairs'],185)
  for family in ['54e3','55a2311c12b246ddbd15','90980b7a8339256bfea7','ce36cae0274019373c8a','ce2']:
   matches=[v for v in x['selectedReviewLineages'] if v['kind']=='leaf' and v['familyId'].startswith(family)]
   self.assertEqual(len(matches),1);self.assertGreater(matches[0]['lineagePriority'],10)
 def test_all_actual_proposal_dependency_hashes(self):
  for r in self.registry['reviews']:
   if 'proposalDependency' not in r:continue
   self.assertEqual(proposal_dependency(E/r['artifactDirectory']),r['proposalDependency'])
 def test_original_id_normalization_checks_exact_definition(self):
  c={'id':'p0','originalId':'q0','title':'Title','question':'Question','summary':'Summary','scope':{},'readingLimit':'Bounded','methods':[]}
  self.assertEqual(resolve_home('q0',{},[c])['normalizedRef'],'p0')
  self.assertEqual(resolve_home('p0',{},[c,copy.deepcopy(c)])['status'],'exact_card_reference')
  d=copy.deepcopy(c);d['scope']={'regimes':['changed']}
  self.assertFalse(same_science(c,d));self.assertEqual(resolve_home('p0',{},[c,d])['status'],'unresolved_or_ambiguous_reference')
 def test_original_notes_and_reservations_preserved(self):
  sealed={r['paperId'] for r in json.loads((E/'final-holdout-reservation.local.json').read_text())['records']}
  for a in self.registry['unitAssessments']:
   self.assertNotIn(a['paperId'],sealed);self.assertEqual(a['note'],a['challengeAttribution']['note'])
   self.assertIn('note',a['proposalAttribution']);self.assertIn('reason',a['proposalAttribution'])
   if a['homeAgreement']['sameExplicitScientificCard']:self.assertTrue(a['homeAgreement']['proposalDefinitionMatchesPinnedOriginal'])
   self.assertFalse(a['homeAgreement']['placementAdmission'])
 def test_admitted_kk_ids_not_reauthored_and_parent_reuse_not_new(self):
  admitted=[r for r in self.registry['records'] if r.get('admittedDestinationId')]
  self.assertEqual(len(admitted),8);self.assertTrue(all(r['candidateId']==r['admittedDestinationId'] for r in admitted))
  self.assertTrue(all(not r['createsNewRecord'] for r in self.registry['parentReusedScopeReferences']))

if __name__=='__main__':unittest.main()
