"""Pin the reviewed first-cut scope class; does not admit scopes or homes."""
import collections, hashlib, json
from pathlib import Path
B = Path(__file__).resolve().parent
F = B.parent
W = F.parents[3]
INPUT = W/'research/q025/assembly/placement-incremental-v1/cut-01/exception-intake.json'
EXPECTED = '71263a9f0021efdb21ad157d46dc559b5271318bbabb074cf7b3d6ec8a9658a9'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def vh(x): return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def pin(p): return {'path':str(p.relative_to(W)), 'sha256':sha(p), 'bytes':p.stat().st_size}
def read(p): return json.loads(p.read_text())
def frozen(p,x):
    raw=json.dumps(x,ensure_ascii=False,indent=2)+'\n'
    if p.exists(): assert p.read_text()==raw, ('Frozen output changed',p)
    else: p.write_text(raw)
def check_scope(n):
    assert n['stage']=='proposal' and n['independentAssessment']['verdict']=='retain'
    assert n['definition']['revisesRef']==''
    assert len(n['sources'])==n['currentSelectedSourceCount']
    for s in n['sources']:
        p,c=s['proposalJudgment'],s['challengeJudgment']
        assert p['status']==c['status']=='new_scope_proposed'
        assert p['coverageMode']==c['coverageMode']=='whole_question_per_home'
        assert p['wholeTargetCoverage']==c['wholeTargetCoverage']=='complete'
        assert p['homes']==c['homes'] and len(c['homes'])==1
        assert c['homes'][0]['scopeRef']==n['localRef'] and c['homes'][0]['weight']==1
        assert p['targetCoverage']==c['targetCoverage'] and c['targetCoverage']
        assert not p['missingPremises'] and not c['missingPremises']
        assert s['independentPriorPlacementReview']['verdict']=='retain'
        assert hashlib.sha256(s['description'].encode()).hexdigest()==s['descriptionSha256']
    return True
NOTES = [
 'Metric fluctuations constrain three scalar parameters; conjectural scalar-force inequalities are a different mechanism. No background or numerical bound is supplied.',
 'The target is inference from astronomical mass, spin and magnetic-moment regularities, not an established acceleration mechanism or cosmological EFT.',
 'The acoustic preferred time and the coordinate boost using gravitational speed c are explicit; neither a sound-speed boost nor an ordering of the two speeds is invented.',
 'Scalar electrodynamics/MHD and the linked helical-coupling instabilities form the complete target; no acceleration or scalar-star mechanism is inferred.',
 'The complete SM+GR+LambdaCDM observational remit and all three uncertainty classes are preserved. A general cosmology home is broader in one direction but does not replace this complete inference question.',
 'The source explicitly combines infrared dark-sector and ultraviolet gravity problems with tested physics and predictions. No particular mechanism or cutoff criterion is supplied.',
 'The atomic Lamb-shift target depends on failure of the heavy-mass approximation and distinguishes fermions from spin zero; a higher-spin cutoff question is not equivalent.',
 'Geon spin-statistics, induced interactions and low-energy signatures remain conditional. Shared spin vocabulary does not identify the massive higher-spin target.',
 'The source is a compound naturalness/symmetry/strong-CP question; all clauses remain rather than reducing it to an electroweak mechanism.',
 'The Higgs scale regulates an instanton-size integral and point-instanton regime; this is not a question of electroweak scale selection.',
 'Two descriptions address conditional weak-coupling ultraviolet inference. The nominated spectra/multiplicity/cutoff scope is a broader multi-mechanism family, not the same complete scoped question.',
 'Pseudoscalar necessity is asked conditionally on B+L quality and gravity assumptions; it is not asserted, and differs from the explicit-violation baseline question.',
 'The source fixes explicit B+L violation and Standard Model running to the reduced Planck cutoff; these source-specific conventions distinguish the baseline from a general theta-removal question.',
 'The question retains weak versus stronger WGC formulations and heterotic large-charge/clockwork restrictions. The broader Higgsing/composite-monopole family does not make this completion question redundant.',
 'The region organizes the empirical scalar-force quantifier problem and a stated multifield possibility. The missing derivative structure and realization remain explicit; no escape mechanism is certified.',
 'Scalar versus fermion mass and kinetic dependence is the complete quantum-coupling target. The damaged old annotation is retained, without importing a Higgs-gradient or de Sitter application.',
 'ICHEP2018 and Snowmass source-dated survey remits differ from the nominated 2025-preface/2024-symposium historical scope. No all-BSM completeness or current experimental certification is claimed.',
 'Horizontal/electroweak scalar sectors and a possible bound-state origin are linked targets in the same source setting, without a demonstrated radiative hierarchy or bound-state spectrum.',
 'The radial-coordinate prescription is a finer metric-distance question; the nominated configuration-space-metric family is not full-scope equivalent. No general coordinate-invariance result is inferred.',
 'GRChombo adaptability is a software-capability question, distinct from neighboring physical results. No software execution, benchmark or primary-paper verification is claimed.',
 'Dilaton and dilaton-Maxwell energy conditions retain domain/frame qualifications and theorem applicability. The broader energy-condition/singularity family does not eliminate this meaningful finer question.',
 'Analytic continuation and torus tilt concern a proposed KK vacuum decay and its exponent, not a universal censorship or black-hole emission conclusion.',
 'The shared source-qualified phenomenology/consistency/typicality question preserves all three targets and allows the compactified-vacuum consistency source to specialize it; this is not source-statement equivalence.',
 'The supplied whole question explicitly combines stabilization, vacuum entropy and velocity-dependent dynamics. A single authored compound home is legitimate without inventing atomic identities or a common successful mechanism.',
 'Asymptotic Hodge theory links specified compactification couplings/vacuum loci to specified integrable models. The unsupported counting contribution stays removed; the method bridge does not equate systems.',
 'The supplied FN selection-rule question nominates gauged Z_10 without proving anomaly cancellation or a geometric realization. Existing broader discrete-symmetry families do not constitute the same scoped target.',
 'FI compensation by massless scalar charges is a narrow effective-theory target; no anomaly-cancellation proof, geometric completion or full stability is inferred.'
]
def main():
    assert sha(INPUT)==EXPECTED
    d=read(INPUT); ns=d['newScopes']; assert len(ns)==len(NOTES)==27
    checked={}
    ledger=[]
    for i,n in enumerate(ns):
        check_scope(n)
        for name,ref in n['inputs'].items():
            p=W/ref['path']; assert sha(p)==ref['sha256']; checked[str(p)]=pin(p)
        proposal=read(W/n['inputs']['proposal']['path']); challenge=read(W/n['inputs']['challenge']['path'])
        assert next(x for x in proposal['newScopes']if x['id']==n['localRef'])==n['definition']
        assert next(x for x in challenge['priorScopeReviews']if x['ref']==n['localRef'])==n['independentAssessment']
        assert not any(x['id']==n['localRef']for x in challenge['newScopes'])
        for s in n['sources']:
            assert next(x for x in proposal['placements']if x['unitRef']==s['unitRef'])==s['proposalJudgment']
            assert next(x for x in challenge['placements']if x['unitRef']==s['unitRef'])==s['challengeJudgment']
        candidates=n['globalExistingScopeLookup']['candidates']
        ledger.append({'index':i,'familyId':n['familyId'],'localRef':n['localRef'],'kind':n['definition']['kind'],'title':n['definition']['title'],'definitionSha256':n['definitionSha256'],'definitionExactValueSha256':vh(n['definition']),'independentAssessmentSha256':vh(n['independentAssessment']),'unitIds':[s['unitId']for s in n['sources']],'sourceCount':len(n['sources']),'evaluatorReview':NOTES[i],'globalNominatedScopeIds':[c['id']for c in candidates],'lookupLimit':n['globalExistingScopeLookup']['method'],'omittedSharedSourceCandidates':n['globalExistingScopeLookup']['omittedSharedSourceCandidates'],'status':'candidate_for_explicit_coordinator_class_admission','newPrimaryReading':False})
    assert len({s['unitId']for n in ns for s in n['sources']})==34
    private=F/'native-local/placement-scope-review-v1'; private.mkdir(exist_ok=True)
    examples=[]
    for i in [0,10,14,24,25]:
        n=ns[i]
        examples.append({'review':ledger[i],'definition':n['definition'],'independentAssessment':n['independentAssessment'],'sources':n['sources'],'globalExistingScopeLookup':n['globalExistingScopeLookup'],'inputs':n['inputs']})
    ep=private/'five-full-examples.json';frozen(ep,{'input':pin(INPUT),'examples':examples,'readingBasis':'Full supplied source descriptions, both historical notes, both placement judgments, complete authored scopes and bounded global scope contrasts. No fresh primary pages.'})
    xp=private/'eight-placement-exceptions.json'
    others=[x for x in d['rows']if x['challengeJudgment']['status']!='new_scope_proposed']
    assert len(others)==8
    frozen(xp,{'input':pin(INPUT),'items':others,'status':'Separate coordinator placement decisions or unresolved source-target cases; not covered by new-scope class.'})
    report={'schemaVersion':'q025-placement-new-scope-class-proposal/1','input':pin(INPUT),'counts':{'newScopes':27,'questions':25,'regions':2,'selectedSources':34,'exactRetainedDefinitions':27,'exactHomeAndTargetCoverageAgreements':34,'compoundUnionAllocations':0,'placementMissingPremises':0,'identifiedWholeScopedQuestionDuplicates':0,'separateExistingHomeRevisions':4,'separateUnresolvedSources':4},'classStatus':'proposed_not_admitted','classConditions':['Complete proposal definition explicitly retained by independent challenge with unchanged source coverage.','Whole question has one weight-one home; no compound union, changed target, unresolved consequential placement premise or reconstructed old note.','Evaluator read full scope, complete source description, both historical notes and both placement judgments.','Bounded exact-source/target-neighbor review found no existing same scoped question; a broader family or meaningful refinement is not equivalence.','Preserve all reading limits and source qualifications; description-level organization does not certify physical results, source equivalence or global uniqueness.'],'ledger':ledger,'examples':pin(ep),'otherPlacementExceptions':pin(xp),'verifiedInputFiles':list(checked.values()),'globalInventory':ns[0]['globalExistingScopeLookup']['inventory'],'candidateClassDoesNotAdmit':['homes','mass','aliases','source_statement_equivalence','physical_results','navigation_relations'],'basis':'No new model call or primary reading. All scientific claims remain source-described questions.','compiler':pin(Path(__file__))}
    frozen(B/'class-proposal.json',report)
    print(json.dumps({'report':pin(B/'class-proposal.json'),'examples':pin(ep),'exceptions':pin(xp),'counts':report['counts']}))
if __name__=='__main__': main()
