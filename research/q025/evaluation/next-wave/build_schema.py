#!/usr/bin/env python3
"""Produce a strict, portable output schema for the next source-review calibration."""
import json
from pathlib import Path
B=Path(__file__).resolve().parent
S={'type':'string'}; I={'type':'integer','minimum':0}; BO={'type':'boolean'}
def enum(*xs): return {'type':'string','enum':list(xs)}
def arr(x,**kw): return {'type':'array','items':x,**kw}
def obj(**ps): return {'type':'object','properties':ps,'required':list(ps),'additionalProperties':False}
def short(n):return {'type':'string','maxLength':n}
strings=arr(S)
basis=enum('description_checked','source_excerpt_checked')
role=enum('addresses','instantiates','specializes','method','boundary','comparison')
nullableOffset={'type':['integer','null'],'minimum':0}
ref=obj(kind=enum('description','source_anchor','source_relation','existing_question'),id=S,start=nullableOffset,end=nullableOffset)
scope=obj(physicalSystems=strings,targets=strings,regimes=strings,assumptions=strings,conventions=strings,includes=strings,excludes=strings)
factor=obj(id=S,status=enum('supported_reading_proposal','uncertain_reading','unsupported'),supportingUnitIndices=arr(I),kind=enum('system','target','regime','method','assumption'),label=short(160),basis=basis,evidenceRefs=arr(ref),attachmentScope=enum('explicit_question_description','direct_record_relation','contextual_source_reading','unknown'),uncertainty=short(220))
contribution=obj(unitIndex=I,role=role,basis=basis,evidenceIds=strings)
direction=obj(id=S,title=short(90),question=short(260),relationType=enum('narrows','broadens','method','application','comparison','premise_check','related','gap'),targetQuestionRef=S,rationale=short(220),evidenceRefs=arr(ref))
card=obj(localId=S,title=short(90),question=short(360),summary=short(700),scope=scope,methods=strings,proposedQueryAliases=strings,sourceContributions=arr(contribution),evidenceIds=strings,readingLimit=short(450),identityStatus=enum('new_scoped_question_proposal','existing_question_reuse_proposal','unresolved'),existingQuestionRef=S,scientificStatus=enum('source_reviewed_proposal','description_only_proposal'),nextDirections=arr(direction,maxItems=15))
unit=obj(unitIndex=I,priorAssignmentAgreement=enum('first_proposal','agrees_as_written','changed_assignment','not_comparable'),basis=basis,disposition=enum('include','overlap','exclude','unresolved'),questionRefs=strings,factorRefs=strings,unknownRoles=arr(enum('system','target','regime','method','assumption')),reasonCode=enum('central_target','specialized_case','distinct_target_same_family','method_bridge','application_bridge','scope_mismatch','changed_regime','weak_source_support','ambiguous_description','unresolved_placement'),note=short(160),alternateHome=short(260),evidenceIds=strings)
identity=obj(leftQuestionRef=S,rightQuestionRef=S,decision=enum('alias_equivalent','distinct_scoped_questions','unresolved'),basis=short(400),evidenceRefs=arr(ref),changedPremises=strings,redirectProposal=S)
rel=obj(sourceQuestionRef=S,targetQuestionRef=S,type=enum('narrows','broadens','method','application','comparison','premise_check','related'),rationale=short(320),evidenceRefs=arr(ref),status=enum('navigation_proposal'))
coverage=obj(providedDescriptionCount=I,reviewedDescriptionCount=I,sourceExcerptCheckedUnitCount=I,reservedUnreviewedCount=I,allProvidedDescriptionsReviewed=BO,fullPaperReadingCertified=enum('no'),fullMembershipScientificCertification=enum('no'))
priorcard=obj(priorQuestionRef=S,decision=enum('supported_as_written','supported_with_explicit_limits','revision_required','insufficient_evidence','not_evaluable_from_this_packet'),scopeAgreement=enum('unchanged','broadened','narrowed','different','unclear'),agreedUnitIndices=arr(I),disputedUnitIndices=arr(I),rationale=short(500),evidenceRefs=arr(ref),replacementQuestionRef=S)
schema=obj(schemaVersion={'type':'string','const':'q025-leaf-review/2'},familyId=S,stage=enum('proposal','challenge','fresh'),verdict=enum('usable_with_limits','needs_revision','insufficient_evidence'),summary=short(1800),
 regionCard=obj(title=short(90),question=short(360),summary=short(900),scope=scope,scientificStatus=enum('description_reviewed_source_sampled_proposal'),readingLimit=short(500),directions=arr(direction,minItems=1,maxItems=15)),
 questionCards=arr(card,minItems=1,maxItems=8),priorCardAssessments=arr(priorcard),factorDictionary=arr(factor),unitAssessments=arr(unit),identityAssessments=arr(identity),navigationRelations=arr(rel),coverage=coverage,unresolvedQuestions=strings,limitations=strings)
(B/'output.schema.json').write_text(json.dumps(schema,indent=2)+'\n')
print('Wrote strict q025-leaf-review/2 schema; no jobs prepared.')
