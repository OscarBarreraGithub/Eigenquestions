"""Lossless scientific display views and explicit candidate access, no admission."""
import importlib.util,json
from pathlib import Path
B=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('prep',B/'prepare.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
d=m.read(m.INPUT);ns=d['newScopes'];private=m.F/'native-local/placement-scope-review-v1'
def scope(x):return {k:x[k]for k in ['id','kind','title','question','summary','scope','methods','scientificStatus','readingCoverage','readingLimit','scopeContentSha256']if k in x}
def source(x):return {k:x[k]for k in ['familyId','unitRef','unitId','paperId','description','descriptionSha256','proposalJudgment','challengeJudgment','independentPriorPlacementReview','homes']}|{'proposalAttributions':[{'reviewId':a['reviewId'],'original':a['original']}for a in x['proposalAttributions']],'challengeAttributions':[{'reviewId':a['reviewId'],'original':a['original']}for a in x['challengeAttributions']],'inputs':x['inputs']}
examples=[]
for i,j in [(0,0),(10,3),(14,4),(24,2),(25,3)]:
 n=ns[i];c=n['globalExistingScopeLookup']['candidates'][j]
 examples.append({'index':i,'familyId':n['familyId'],'localRef':n['localRef'],'definition':n['definition'],'definitionSha256':n['definitionSha256'],'independentAssessment':n['independentAssessment'],'sources':[source(x)for x in n['sources']],'evaluatorReview':m.NOTES[i],'fullContrast':{'id':c['id'],'scopeContentSha256':c.get('scopeContentSha256',c['definition'].get('scopeContentSha256')),'definition':scope(c['definition']),'sharedSourceUnitIds':c['sharedSourceUnitIds']},'allOtherContrastIds':[a['id']for a in n['globalExistingScopeLookup']['candidates']if a['id']!=c['id']]})
ep=private/'five-scientific-examples.json';m.frozen(ep,{'input':m.pin(m.INPUT),'examples':examples,'omittedFields':'Repeated machine binding metadata only. Every displayed scientific definition, whole source statement, old note and new judgment is exact; all originals and additional contrasts remain pinned in the class input.'})
selections={0:0,1:2,3:0,4:2,5:6,7:1,8:0,10:3,11:3,13:1,14:1,16:3,17:1,18:4,19:3,20:4,21:0,22:1,23:1,24:2,25:3,26:3}
extra={2:'q025-candidate-region:beaaa0449eb11baa0bec0654',6:'q025-candidate-region:072557743b48c99c543e373c',9:'q025-candidate-question:4916978371350c65b64c5f8a',15:'q025-candidate-question:72c7ec910995c3167fd9cc65'}
basep=m.F/'admissions-v5/supported-scope-role-component-v5.json';base={x['id']:x for x in m.read(basep)['destinations']}
reasons=[
 'Compare gravity-induced restrictions on matter parameters. The new scalar question does not identify an ultraviolet fixed point or a particular RG completion, so containment is not asserted.',
 'Compare two source-specific attempts to infer gravitational scales from astronomical regularities. Mass/spin/magnetic-moment scaling and UHECR cutoff inference remain distinct observations and conditional interpretations; no shared scale identification is implied.',
 'The acoustic-medium example probes how a preferred-time retarded response is represented under a different reference-cone coordinate boost. It is a causal/propagation comparison, without turning acoustic and gravitational signal speeds into one cone.',
 'Compare scalar-driven electromagnetic dynamics with axion-driven vector production. Ordinary cosmological MHD, helical instabilities and dark-photon relic production retain different fields, masses and thermal histories; no transfer of a production law is asserted.',
 'CMB inference provides one observational context for the broader fundamental-observable and uncertainty question. The new remit also covers SM and GR extensions beyond CMB physics, so it is not contained wholly by the CMB family.',
 'Connect ultraviolet gravity with the source explicitly joining ultraviolet completion and infrared dark-sector aims. No common mechanism is asserted and the infrared clauses are not removed.',
 'The complete hydrogen question specializes laboratory constraints on the explicitly included millicharged matter sector. Its light-mass approximation and fermion/spin-zero comparison remain source-specific, without a cosmological-abundance assumption.',
 'Geon topology and noncanonical statistics give a concrete neighboring microscopic-gravity/particle-signature question. The broader program does not establish this proposed mechanism or its signatures.',
 'The new string-naturalness overview shares global/gauged symmetry and strong-CP premises with this existing question, but also retains the cosmological-constant target; no whole-scope equality or containment is asserted.',
 'The gauge-instanton size integral and Higgs infrared regulator are a scoped calculation/control question within instanton measures and coefficient calculation. This does not extend the regulator to other string or brane sectors.',
 'Small gauge coupling and cutoff inference share an explicit target with the existing gauge-spectrum family. The source inference question keeps its own assumptions without inheriting kinetic mixing, tower or compactification claims.',
 'Compare theta-vacuum removal and pseudoscalar realization with shift-symmetry quality. Electroweak theta, QCD axions and physical-axion removal remain distinct; no necessity theorem transfers.',
 'Compare two electroweak-theta questions: conditional pseudoscalar necessity versus the explicitly B+L-violating Standard-Model-running baseline. Neither source assumption or conclusion is inherited by the other.',
 'The Higgsing/WGC-descent target is shared, while heterotic large-charge and clockwork restrictions differ from composite-monopole assembly and localized towers. This is overlap, not equality of whole questions.',
 'Both questions address scalar couplings and long-range-force tests. The proposed universal or multifield force inequalities are not ordinary quintessence coupling assumptions, and the unformulated escape remains unestablished.',
 'Compare scalar-dependent kinetic and mass functions with matter-coupling parametrizations used in gravity tests. No quintessence background, common coupling or observational bound is inferred for the new quantum question.',
 'The source-dated particle-physics survey is an adjacent research-agenda direction. Preserve ICHEP2018 and Snowmass remits without equating their whole coverage to the broader cross-field survey.',
 'Separate horizontal/electroweak scalar sectors and possible bound-state origins are useful neighbors of microscopic weak-scale questions. A staged breaking construction does not by itself demonstrate a radiative hierarchy solution.',
 'The new question is a radial-coordinate comparison of one specified curvature-based black-hole metric distance, within the existing comparison of source-specific metrics and prescriptions. No universal metric or light-state conclusion is inferred.',
 'GRChombo capability is a concrete numerical-software neighbor. Flexible meshes and modified black-hole evolution do not establish an implementation dependency on the other named numerical packages.',
 'The new question specializes energy-condition and singularity-theorem applicability to stated dilaton/dilaton-Maxwell systems, domains and frames. Other barrier or quantum criteria are not imported into those systems.',
 'Compare the particular KK analytic-continuation vacuum decay with broader extremality/decay diagnostics. Torus tilt and a nucleation exponent are not black-hole emission or a universal consistency bound.',
 'The new whole question links particle-model reproduction, consistency exclusions and typicality. Existing string-background construction covers an important portion, but does not contain every statistical or exclusion target.',
 'The whole source links stabilization, cosmological-vacuum entropy and velocity-dependent dynamics. A vacuum-family entry provides access without claiming that its construction question alone contains or answers the entropy target.',
 'The new compound question explicitly links compactification Hodge data with specified integrable-model solutions. Preserve the existing integrable systems and compactification assumptions separately; no general system equivalence or universal method applicability is asserted.',
 'The nominated gauged discrete FN realization is a source-specific symmetry/charge-consistency neighbor. No anomaly cancellation, geometry or ultraviolet completion is established by this connection.',
 'The source asks which scalar charges can compensate an anomalous FI term, an explicit target within the broader flatness/spectral-reach family. The other positive-potential and gap questions are not premises of this compensation question.'
]
entries=[]
for i,n in enumerate(ns):
 if i==12:
  neighbor=ns[11]['definition']; bound={'kind':'new_scope_in_same_reviewed_class','familyId':ns[11]['familyId'],'localRef':ns[11]['localRef'],'definitionSha256':ns[11]['definitionSha256']}
 elif i in selections:
  c=n['globalExistingScopeLookup']['candidates'][selections[i]];neighbor=c['definition'];bound={'kind':'existing_scope','id':c['id'],'scopeContentSha256':base[c['id']]['scopeContentSha256']}
 else:neighbor=base[extra[i]];bound={'kind':'existing_scope','id':extra[i],'scopeContentSha256':neighbor['scopeContentSha256']}
 if bound['kind']=='existing_scope':
  for k in ['kind','title','question','summary','scope']:assert neighbor[k]==base[bound['id']][k]
 entries.append({'index':i,'newScope':{'familyId':n['familyId'],'localRef':n['localRef'],'definitionSha256':n['definitionSha256'],'definition':n['definition']},'entryNeighbor':bound,'entryNeighborDefinition':scope(neighbor),'proposedDirection':'entry_neighbor_to_new_scope','proposedType':'narrower'if i in [6,9,18,20]else'comparison'if i in [1,3,11,12,13,14,15,21,24]else'related_question','scopeRelationship':'whole_scope_refinement_candidate'if i in [6,9,18,20]else'overlap_or_scoped_comparison','rationale':reasons[i],'noContributionImpliesContainment':True,'noNewPrimaryReading':True,'status':'explicit_coordinator_navigation_candidate_not_admitted','isolatedUntilRouteAdmission':True})
np=private/'entry-neighbor-candidates.json';m.frozen(np,{'schemaVersion':'q025-new-scope-entry-candidates/1','input':m.pin(m.INPUT),'baseScopes':m.pin(basep),'entries':entries,'policy':'These explicit definition-level candidates do not admit a route, application, premise transfer or equality. Four narrower candidates require whole-scope confirmation; other routes deliberately retain overlap or comparison. Every new destination is flagged as requiring connectivity until its entry route is admitted.'})
idx={'classProposal':m.pin(B/'class-proposal.json'),'fiveFullScientificExamples':m.pin(ep),'entryNeighborCandidates':m.pin(np),'eightPlacementExceptions':m.pin(private/'eight-placement-exceptions.json'),'counts':{'newScopes':27,'sourceRows':34,'entryCandidates':27,'wholeScopeRefinementCandidates':4,'overlapOrComparisonCandidates':23},'notAdmitted':True,'preparation':m.pin(Path(__file__))};m.frozen(B/'coordinator-index.json',idx);print(json.dumps(idx))
