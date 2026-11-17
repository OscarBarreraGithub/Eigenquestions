"""Exact second-cut policy checks plus the evaluator's bounded scientific reading."""
import importlib.util,json,hashlib
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;W=F.parents[3]
s=importlib.util.spec_from_file_location('prior',F/'placement-scope-review-v1/prepare.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
p=W/'research/q025/assembly/placement-incremental-v1/cut-02/exception-intake.json'
assert m.sha(p)=='ca05168e8f4b9345884d4383d0cc053d69ae7fe28284b096275b93af9edbedba'
d=m.read(p)
notes=[
'Beyond-BPS general-observable perturbation on nonlinear field space is not identical to instanton solution construction or protected interaction coefficients. The anti-instanton-suppressing limit is explicit; convergence remains unproved.',
'The AdS-family zero-cosmological-constant spectral target is distinct from the nominated light-spin-two/local-CFT/discrete-gap regimes. No tower, dimension or exponent is supplied. The old home is unavailable; the current whole description is sufficient to define this question.',
'The general homogeneous force-balance question and curved-geometry quasi-de Sitter application can share this compound destination without source equivalence. The broader inflation family does not make all homogeneous motion inflationary or supply perturbation claims.',
'Domain-wall entropy as a landscape probability functional is a distinct proposed measure question, adjacent to transition-network populations. No unique normalized probability measure or common quantum-state-space interpretation is inferred.',
'The complex-scalar regular-saddle to real expanding-cosmology target differs from named axion/AdS wormhole or D-instanton continuations. No contour, wave-function weight or specific wormhole sector is added.',
'The question asks for an independent principle excluding non-invertible topological operators rather than using completeness circularly. Sector-specific endability/completeness diagnostics are relevant but not identical to that foundational premise question.',
'Schwinger–Dyson consistency and moment positivity for large-N random Dirac spectra do not become a CFT crossing problem because both use positivity. No exact finite-N result or universal spectral classification is supplied.',
'Comparing distinct quantum-gravity approaches and shared questions/mathematical techniques is a meaningful finer target than the cross-field research-agenda portfolio. The distinction is target coverage, not survey date, and no common mechanism is asserted.',
'Purity of the specified KM-state sequence relative to an emergent limiting operator algebra differs from symmetry emerging under theory averaging. The KM abbreviation, purity result and limiting algebra are not invented or expanded beyond supplied text.',
'The exponential-quintessence/NEC-preserving CRF embedding question retains source-dated observational admissibility and named restrictions. It establishes neither a no-go theorem nor current observational bounds; the absent historical home is not reconstructed.',
'Scalar–fluid scaling stability under spatial curvature and past/future Robertson–Walker asymptotics differ from kinetic field-space curvature. No scalar potential or equation of state is added.',
'The minimal MSSM quiver periodic-cascade endpoint with one additional gauge node and Higgs/generation restrictions is finer than the broad quiver construction family. No compactification realization follows. The recovered empty revision marker supplies no revision target.',
'Automorphism-valued target gluing and its concrete two-dimensional realization are a construction target, not an inferred physical global symmetry. No unspecified branes, supersymmetry, gravity or duality group is introduced. The recovered revision marker remains provenance only.'
]
rows=[]
for i,n in enumerate(d['newScopes']):
 m.check_scope(n)
 rows.append({'index':i,'familyId':n['familyId'],'localRef':n['localRef'],'definitionSha256':n['definitionSha256'],'sourceUnitIds':[s['unitId']for s in n['sources']],'review':notes[i],'globalContrastIds':[c['id']for c in n['globalExistingScopeLookup']['candidates']],'historicalContextPreserved':True})
assert len(rows)==13 and len({u for r in rows for u in r['sourceUnitIds']})==14
m.frozen(B/'scientific-review.json',{'schemaVersion':'q025-delegated-scope-class-review/1','input':m.pin(p),'authority':'Root authorized continuation of the unchanged independently retained whole-scope class after the first-cut review; evaluator performs the full source-qualified definition review and bounded identity comparison.','rows':rows,'additionalFullContrasts':['q025-candidate-question:e2c4083adb09d23e9f378897','q025-candidate-question:bf84639ac97f2d0633f3b3d1','q025-candidate-question:779f0a1b4e7a47d76b4ddee6','q025-candidate-question:552965597638ad3f895b1783'],'remainingUnresolved':[{'unitId':r['unitId'],'paperId':r['paperId'],'judgment':r['challengeJudgment']}for r in d['rows']if r['challengeJudgment']['status']=='unresolved'],'newPrimaryReading':False,'globalUniquenessCertified':False,'homesRemainWithGeometryCompiler':True})
print(json.dumps({'scopes':13,'sources':14,'unresolvedRows':3,'review':m.pin(B/'scientific-review.json')}))
