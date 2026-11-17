import copy, json, unittest
from pathlib import Path
from compile_homes import exclusion, F

class Homes(unittest.TestCase):
 def setUp(self):
  self.r = {'candidateId':'dest','scopeStatus':'independently_supported','scopeDefinitionFlags':[],'admissionJustificationFlags':[]}
  self.a = {'i':0,'d':'member','identity':'s','q':[{'id':'p0','role':'addresses'}],'reason':'direct_target','note':'The source investigates the stated scoped target.'}
 def test_broader_home_does_not_require_statement_equivalence(self):
  self.assertIsNone(exclusion(self.a,self.a,'p0',{'dest'},self.r))
 def test_inherited_kk_context_is_not_a_home(self):
  b=copy.deepcopy(self.a);b['note']='Production is inherited context for the evolution calculation.'
  self.assertEqual(exclusion(self.a,b,'p0',{'dest'},self.r),'context_compound_or_unclear_target')
 def test_compound_and_changed_target_fail_closed(self):
  b=copy.deepcopy(self.a);b['q'].append({'id':'p1','role':'specializes'})
  self.assertEqual(exclusion(self.a,b,'p0',{'dest'},self.r),'multiple_or_changed_positive_targets')
  b=copy.deepcopy(self.a);b['reason']='changed_regime'
  self.assertEqual(exclusion(self.a,b,'p0',{'dest'},self.r),'changed_scope_or_regime')
 def test_method_annotation_alone_does_not_create_or_erase_positive_home(self):
  b=copy.deepcopy(self.a);b['q'].append({'id':'p1','role':'method'})
  self.assertIsNone(exclusion(self.a,b,'p0',{'dest'},self.r))
  b['q']=[{'id':'p0','role':'method'}]
  self.assertEqual(exclusion(self.a,b,'p0',{'dest'},self.r),'no_paired_addresses')
 def test_exact_real_fragment_preserves_separate_adjudication(self):
  x=json.loads((Path(__file__).parent/'home-admission-delta.json').read_text())
  self.assertEqual(len(x['placements']),1055);self.assertEqual(len({p['unitId'] for p in x['placements']}),1055)
  self.assertTrue(all(p['allocationWeight']==1 for p in x['placements']))
  self.assertTrue(all(d['challengerAgreement']=='not_reviewed_as_placement' and d['sourceEvidenceAgreement']=='independently_agreed' for d in x['decisions']))
  self.assertFalse(x['aliases']);self.assertFalse(x['relations']);self.assertFalse(x['scopeChanges'])

if __name__=='__main__':unittest.main()
