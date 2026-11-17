import copy,sys,unittest
from pathlib import Path
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B.parent/'compact-v1'))
from test_pipeline import fixture
from parent_pipeline import make_parent_packet
from production_contract import evaluate
class ParentTests(unittest.TestCase):
 def make(self):
  o,p,r=fixture();o['fullMemberCount']=100;o['kind']='parent';region=copy.deepcopy(r['region']);region.update(title='A broad parent family',question='How are these source targets connected?',summary='Synthetic scope.');child={'candidateRegionId':'child-a','artifactSha256':'1'*64,'scopeStatus':'independently_supported','region':region,'memberIdsSha256':'2'*64,'fullMemberCount':100,'reviewedDescriptionCount':98,'reservedUnreviewedCount':2,'unresolvedAssignmentCount':3,'questions':[]};return o,[child],r
 def test_real_contrasts_are_not_fabricated_descendant_rows(self):
  o,c,r=self.make();p,v=make_parent_packet(o,c);self.assertEqual(len(p['units']),2);self.assertEqual(p['parentCoverage']['fullDescendantMembers'],100);self.assertEqual(p['childScopes'][0]['reviewedDescriptionCount'],98);self.assertEqual(p['priorCards'][0]['id'],'c0');self.assertFalse(p['refRegistry']['c0']['primaryReadingClaim'])
 def test_parent_proposal_and_challenge_cover_child_scope(self):
  o,c,r=self.make();p,_=make_parent_packet(o,c);r['cards']=[]
  for a in r['units']:a['q']=[{'id':'c0','role':'comparison'}]
  r['links'][0]['target']='c0';r['cardReviews']=[{'id':'c0','decision':'supported_as_written','scopeChange':'same','replacement':'','note':'Synthetic compatible child scope.','refs':['d0']}];self.assertTrue(evaluate(p,r)['validation']['valid']);nextp,_=make_parent_packet(o,c,'challenge',r);self.assertEqual([x['id'] for x in nextp['priorCards']],['c0','r']);self.assertEqual(nextp['priorAssignments'][0]['q'],[{'id':'c0','role':'comparison'}])
 def test_missing_child_assessment_rejected(self):
  o,c,r=self.make();p,_=make_parent_packet(o,c);r['cards']=[]
  for a in r['units']:a['q']=[{'id':'c0','role':'comparison'}]
  r['links'][0]['target']='c0'
  with self.assertRaises(AssertionError):evaluate(p,r)
if __name__=='__main__':unittest.main()
