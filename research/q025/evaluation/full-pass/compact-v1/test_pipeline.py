import copy,sys,unittest
from pathlib import Path
from compact_pipeline import compile_packet,assignment_comparison
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'recovery'))
from test_compact import blank
from compact_contract import SCHEMA,validate

def fixture():
 original={'familyId':'test','units':[{'unitIndex':i,'unitId':'unit:'+str(i),'paperId':'paper'+str(i),'description':'Exact distinct question '+str(i),'sourceNodeIds':[],'sourceNodeKinds':[],'sourceEvidenceIds':[]} for i in range(2)],'evidence':[],'sourceObjects':[],'sourceRelations':[],'reservedUnreviewedCount':1,'candidateRegionId':'candidate-region'}
 p,_=compile_packet(original);r=blank(SCHEMA);r.update(familyId='test',stage='proposal',summary='Synthetic only.')
 c=blank(SCHEMA['properties']['cards']['items']);c.update(id='q0',title='A test question',question='What is the exact target?',summary='Test scope.',refs=['d0']);c['scope']['targets']=['target'];r['cards']=[c]
 for i in range(2):
  a=blank(SCHEMA['properties']['units']['items']);a.update(i=i,b='description',d='member',q=[{'id':'q0','role':'addresses'}],a='initial',reason='central',identity='s',title='Distinct scoped target '+str(i));r['units'].append(a)
 r['links']=[{'source':'r','target':'q0','type':'narrows','reason':'A scoped target.','refs':['d0']}]
 return original,p,r
class PipelineTests(unittest.TestCase):
 def test_proposal_preserves_full_descriptions(self):
  original,p,r=fixture();self.assertTrue(validate(p,r)['valid']);self.assertEqual(p['units'][0]['description'],original['units'][0]['description']);self.assertEqual(p['candidateRegionId'],'candidate-region');self.assertEqual(p['reservedUnreviewedCount'],1)
 def test_challenge_has_explicit_region_assessment(self):
  o,p,r=fixture();c,v=compile_packet(o,'challenge',prior=r);self.assertEqual([x['id'] for x in c['priorCards']],['p0','r']);self.assertEqual(c['priorAssignments'][0]['q'],[{'id':'p0','role':'addresses'}]);self.assertEqual(c['priorRegion'],r['region']);self.assertNotIn('refRegistry',v)
 def test_reject_incomplete_prior(self):
  o,p,r=fixture();r['units']=[]
  with self.assertRaises(AssertionError):compile_packet(o,'challenge',prior=r)
 def test_exact_agreement_is_derived(self):
  o,p,r=fixture();c,_=compile_packet(o,'challenge',prior=r);new=copy.deepcopy(r);new['units']=copy.deepcopy(c['priorAssignments']);new['units'][0]['a']='same';new['units'][1]['q']=[];new['units'][1]['a']='same';comp=assignment_comparison(c,new);self.assertTrue(comp[0]['matches']);self.assertEqual(comp[1]['differences'],['card_contributions'])
 def test_fine_groups_keep_members(self):
  o,p,r=fixture();r['identityGroups']=[{'id':'i0','representative':0,'title':'Shared scoped question','reason':'Synthetic equivalent target.','definingDifferences':[],'refs':['d0','d1']}]
  for a in r['units']:a['identity']='i0'
  c,_=compile_packet(o,'challenge',prior=r);self.assertEqual(c['priorGroups'][0]['memberIndices'],[0,1]);self.assertEqual(c['priorAssignments'][0]['identity'],'pi0')
if __name__=='__main__':unittest.main()
