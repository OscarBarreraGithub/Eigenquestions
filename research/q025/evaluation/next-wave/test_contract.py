import copy,unittest
from validate_contract import SCHEMA,validate

def empty(s):
 if 'const' in s:return s['const']
 if 'enum' in s:return s['enum'][0]
 t=s['type'];t=t[0] if isinstance(t,list) else t
 if t=='object':return {k:empty(v) for k,v in s['properties'].items()}
 if t=='array':return [empty(s['items']) for _ in range(s.get('minItems',0))]
 return {'string':'','integer':0,'boolean':False,'null':None}[t]
def fixture():
 p={'familyId':'synthetic','stage':'proposal','reservedUnreviewedCount':1,'existingQuestionRefs':[], 'sourceRelations':[],
    'units':[{'unitIndex':0,'unitId':'immutable-source0','paperId':'synthetic-paper','description':'Scalar field inflation observables','sourceEvidenceIds':['e1']}],
    'evidence':[{'id':'e1','text':'An explicitly specified scalar model is considered.'}]}
 o=empty(SCHEMA);o.update(familyId='synthetic',stage='proposal',verdict='usable_with_limits',summary='Synthetic contract test only.')
 q=o['questionCards'][0];q.update(localId='q0',title='Inflation observables',question='What observables does the stated scalar model predict?',summary='Synthetic.',evidenceIds=['e1'],scientificStatus='source_reviewed_proposal',existingQuestionRef='')
 q['scope']['targets']=['inflation observables'];q['sourceContributions']=[{'unitIndex':0,'role':'addresses','basis':'source_excerpt_checked','evidenceIds':['e1']}]
 d=o['regionCard']['directions'][0];d.update(id='d0',title='Observables',question=q['question'],targetQuestionRef='q0',relationType='narrows',rationale='Specific target.')
 f={'id':'f0','status':'supported_reading_proposal','supportingUnitIndices':[0],'kind':'system','label':'Scalar field','basis':'description_checked','evidenceRefs':[{'kind':'description','id':'0','start':0,'end':12}],'attachmentScope':'explicit_question_description','uncertainty':''}
 o['factorDictionary']=[f]
 o['unitAssessments']=[{'unitIndex':0,'priorAssignmentAgreement':'first_proposal','basis':'source_excerpt_checked','disposition':'include','questionRefs':['q0'],'factorRefs':['f0'],'unknownRoles':['target','regime','method','assumption'],'reasonCode':'central_target','note':'Synthetic test.','alternateHome':'','evidenceIds':['e1']}]
 o['coverage'].update(providedDescriptionCount=1,reviewedDescriptionCount=1,sourceExcerptCheckedUnitCount=1,reservedUnreviewedCount=1,allProvidedDescriptionsReviewed=True)
 return p,o
class ContractTests(unittest.TestCase):
 def reject(self,mut):
  p,o=fixture();mut(p,o)
  with self.assertRaises(AssertionError):validate(p,o)
 def test_valid(self):
  p,o=fixture();self.assertTrue(validate(p,o)['valid'])
 def test_duplicate_omits_unit(self):self.reject(lambda p,o:o['unitAssessments'].append(copy.deepcopy(o['unitAssessments'][0])))
 def test_fresh_cannot_reuse_prior_evidence(self):self.reject(lambda p,o:o['questionCards'][0]['evidenceIds'].append('prior-stage-only'))
 def test_source_basis_needs_source(self):self.reject(lambda p,o:o['unitAssessments'][0].update(evidenceIds=[]))
 def test_context_cannot_claim_direct_premise(self):self.reject(lambda p,o:o['factorDictionary'][0].update(attachmentScope='direct_record_relation'))
 def test_literal_span_must_resolve(self):self.reject(lambda p,o:o['factorDictionary'][0]['evidenceRefs'][0].update(end=500))
 def test_unsupported_factor_cannot_assign(self):self.reject(lambda p,o:o['factorDictionary'][0].update(status='unsupported'))
 def test_excluded_member_needs_alternate(self):self.reject(lambda p,o:o['unitAssessments'][0].update(disposition='exclude'))
 def test_unknown_roles_recorded(self):self.reject(lambda p,o:o['unitAssessments'][0].update(unknownRoles=[]))
 def test_reserved_coverage_not_hidden(self):self.reject(lambda p,o:o['coverage'].update(reservedUnreviewedCount=0))
 def test_changed_premise_not_alias(self):
  def mut(p,o):o['identityAssessments']=[{'leftQuestionRef':'q0','rightQuestionRef':'q0','decision':'alias_equivalent','basis':'Bad merge','evidenceRefs':[{'kind':'source_anchor','id':'e1','start':None,'end':None}],'changedPremises':['a different regime'],'redirectProposal':''}]
  self.reject(mut)
 def test_scientific_implication_not_navigation(self):
  def mut(p,o):o['navigationRelations']=[{'sourceQuestionRef':'q0','targetQuestionRef':'q0','type':'implies','rationale':'Bad','evidenceRefs':[],'status':'navigation_proposal'}]
  self.reject(mut)
if __name__=='__main__':unittest.main()
