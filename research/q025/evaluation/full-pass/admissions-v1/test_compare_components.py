import copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'compact-v1'))
from test_pipeline import fixture
from compact_pipeline import compile_packet
from compare_components import compare
class Tests(unittest.TestCase):
 def make(self):
  o,p,r=fixture();p,_=compile_packet(o,'challenge',prior=r);r=copy.deepcopy(r);r['units']=copy.deepcopy(p['priorAssignments']);r['cardReviews']=[{'id':x,'decision':'supported_as_written','scopeChange':'same'} for x in ['p0','r']];return p,r
 def test_factor_and_identity_changes_do_not_erase_role_placement_agreement(self):
  p,r=self.make();r['factors']=[{'id':'f0','kind':'method','label':'Additional source method','status':'scope_candidate','qualification':'Candidate annotation.','refs':['d0']}];r['units'][0]['f']=['f0'];r['units'][0]['identity']='?';out=compare(p,r)['units'][0];self.assertTrue(out['broadDisposition']['candidateForAcceptedPlacement']);self.assertTrue(out['exactContributionAgreements'][0]['scopeSupportedUnchanged']);self.assertFalse(out['factorChanges']['sameAssignmentIds']);self.assertFalse(out['fineIdentity']['canonicalUniquenessCertified'])
 def test_material_changed_regime_is_flagged(self):
  p,r=self.make();r['units'][0]['reason']='changed_regime';out=compare(p,r)['units'][0];self.assertFalse(out['broadDisposition']['candidateForAcceptedPlacement']);self.assertTrue(out['exactContributionAgreements'][0]['requiresSubstantiveScopeAdjudication'])
if __name__=='__main__':unittest.main()
