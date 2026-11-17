import copy,unittest
from compact_contract import SCHEMA,validate

def blank(s):
 if 'const' in s:return s['const']
 if 'enum' in s:return s['enum'][0]
 return {k:blank(v) for k,v in s['properties'].items()} if s['type']=='object' else [] if s['type']=='array' else 0 if s['type']=='integer' else ''
def fixture():
 p={'familyId':'test','stage':'challenge','units':[{'i':0,'primaryRefs':['e0']},{'i':1,'primaryRefs':[]}],'refRegistry':{'d0':{'kind':'description','unitIndex':0},'d1':{'kind':'description','unitIndex':1},'e0':{'kind':'primary'},'u0':{'kind':'source_unit'},'u1':{'kind':'source_unit'}},'priorCards':[{'id':'p0'}],'existingCards':[],'priorFactors':[],'priorGroups':[]}
 r=blank(SCHEMA);r.update(familyId='test',stage='challenge',verdict='usable_with_limits',summary='Synthetic fixture.')
 row=SCHEMA['properties']['units']['items'];a=blank(row);a.update(i=0,b='excerpt',d='member',q=[{'id':'p0','role':'addresses'}],refs=['e0'],a='same',reason='central',identity='s',title='A scoped source question')
 b=copy.deepcopy(a);b.update(i=1,b='description',refs=[],title='A distinct scoped source question');r['units']=[a,b]
 r['cardReviews']=[{'id':'p0','decision':'supported_as_written','scopeChange':'same','replacement':'','note':'Same explicit scope.','refs':['e0']}]
 r['links']=[{'source':'r','target':'p0','type':'narrows','reason':'Useful scoped question.','refs':['e0']}]
 return p,r
class Tests(unittest.TestCase):
 def reject(self,mut):
  p,r=fixture();mut(p,r)
  with self.assertRaises(AssertionError):validate(p,r)
 def test_valid_reuse_without_copying_prior_card(self):p,r=fixture();self.assertEqual(validate(p,r)['newOverviewCards'],0)
 def test_zero_rows_cannot_certify_coverage(self):self.reject(lambda p,r:r.update(units=[]))
 def test_duplicate_rows(self):self.reject(lambda p,r:r['units'].append(copy.deepcopy(r['units'][0])))
 def test_source_facet_not_overview_identity(self):self.reject(lambda p,r:r['units'][0].update(q=[{'id':'u0','role':'addresses'}]))
 def test_source_context_link_is_allowed(self):
  p,r=fixture();r['links'].append({'source':'p0','target':'u1','type':'source_context','reason':'Distinct source question awaits canonicalization.','refs':['d1']});self.assertTrue(validate(p,r)['valid'])
 def test_unresolved_identity_explicit(self):self.reject(lambda p,r:r['units'][0].update(identity='?',note=''))
 def test_new_fine_group_needs_multiple_members(self):
  def change(p,r):r['identityGroups']=[{'id':'i0','representative':0,'title':'Common scoped question','reason':'Same target and premises.','definingDifferences':[],'refs':['d0']}];r['units'][0]['identity']='i0'
  self.reject(change)
 def test_unknown_reference(self):self.reject(lambda p,r:r['cardReviews'][0].update(refs=['not-in-packet']))
 def test_wrong_primary_basis(self):self.reject(lambda p,r:r['units'][1].update(b='excerpt',refs=['e0']))
 def test_changed_card_not_independently_accepted(self):self.reject(lambda p,r:r['cardReviews'][0].update(scopeChange='narrower'))
 def test_every_prior_card_judged(self):self.reject(lambda p,r:r.update(cardReviews=[]))
 def test_historical_factor_retained_but_counted_separately(self):
  p,r=fixture();r['factors']=[{'id':'f0','kind':'assumption','label':'Withdrawn universal bound','status':'historical_or_rejected','qualification':'Historical proposed claim, not an asserted premise.','refs':['d0']}];r['units'][0]['f']=['f0'];self.assertEqual(validate(p,r)['historicalFactorsExcludedFromActivePremises'],1)
if __name__=='__main__':unittest.main()
