#!/usr/bin/env python3
"""Pin the proposed calibration families and estimate whole-atlas work; launch nothing."""
import hashlib,json,statistics
from pathlib import Path
B=Path(__file__).resolve().parent; E=B.parent; R=E.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
regions={}; paths={}
for v,rd in [('multiview_preserve_candidates','round3'),('extra_facet_context','round3'),('local_spectral_consensus','round2')]:
 p=R/'geometry'/rd/v/'regions.json'; d=json.loads(p.read_text()); regions[v]={x['id']:x for x in (d['regions'] if isinstance(d,dict) else d)};paths[v]=p
# No held-out text is read or exported; only paper IDs are used to exclude every unit from those papers.
reserved={x['paperId'] for x in json.loads((E/'final-holdout-reservation.local.json').read_text())['records']}
rows={x['unit_id']:x for x in map(json.loads,(R/'geometry/round1/source-rows.jsonl').read_text().splitlines())}
P='multiview_preserve_candidates';X='extra_facet_context';C='local_spectral_consensus'
def ids(v,*suffixes):return [(v,f'{v}:region:{s}') for s in suffixes]
choices=[
 ('kk-production-decay','Extra dimensions, dark-sector production and decay',ids(P,'0403944f92af04eaed4a')+[(C,f'{C}:spectral:bfee9d43254b967793c9')]+ids(X,'1a59e9c1af68ec589759'),'Compare the small KK/GZK false merge, broader dark-sector production neighborhood, and extra-facet placement. Retain flat/warped and production/decay/signature distinctions; challenge the four existing draft question cards.'),
 ('effective-actions-vacua','Effective descriptions, flux vacua and stability',ids(P,'c3339e1f151b5c739eb5','917023476c8ed7e389e0')+ids(X,'6afc0d9c421931234feb','d27ad088c4dfcf5e3854'),'Separate construction of effective data, existence/stabilization, stability and control. Permit useful common parents across dimensions; sufficient instability tests are not stability proofs.'),
 ('distance-emergence','Field-space limits, light towers and emergence',ids(P,'adcc4556537d69777acf')+ids(X,'6cee53cc87faacd94178'),'Compare limits, spectra, emergence mechanisms and finite-range diagnostics without assuming every distance calculation proves the Distance Conjecture.'),
 ('gauge-geometry-anomaly','Gauge sectors, geometric realization and anomaly constraints',ids(X,'8d9d4d04cfaed30bba4e'),'Distinguish anomaly cancellation from geometric realization and from a complete consistency proof; retain bridges across the overlapping family.'),
 ('inflation-dynamics','Inflation, perturbation dynamics and warm-PBH applications',ids(P,'431e39adaf172dcc211a','ccbf22b7e49aec0dfecf')+ids(X,'6db85b9a8a960a0c5f50','c669854c0351421af172'),'Explicitly include ordinary and pre-Swampland dynamical questions. Preserve the noninflation sound-speed method connection and distinguish strong-throughout from weak-CMB/strong-late histories.'),
 ('axions','Axion dynamics, potentials and field ranges',ids(P,'3d1118c04f114f9ecdc6')+ids(X,'6061678943a20012a9e8'),'Retain periodicity/normalization, potential generation, alignment and phenomenological targets as distinct scoped questions; avoid a conjecture-vocabulary gate.'),
 ('neutrinos','Neutrino masses and cosmological constraints',ids(P,'76e3d3dd115e5b73a21b')+ids(X,'3ebd2decc41cd7dcd6f1'),'Separate mechanisms, effective descriptions and conditional cosmological/conjectural tests; do not identify observational assumptions across papers.'),
 ('scattering-positivity','Scattering, analyticity and gravitational consistency',ids(P,'2bb36b2ccecd56449d47')+ids(X,'16cd2f1226965bfbabde'),'Distinguish physical systems and amplitudes from shared dispersion/positivity methods; retain regulator, dimensional and asymptotic hypotheses.')]
families=[];union=set();paperunion=set()
for fid,title,refs,purpose in choices:
 members=set(); rr=[]
 for v,rid in refs:
  region=regions[v][rid]; mm=region['memberIds']; members.update(mm)
  rr.append({'candidate':v,'regionId':rid,'regionFile':str(paths[v].relative_to(E.parents[2])),'regionFileSha256':sha(paths[v]),'memberCount':len(mm),'memberIdOrderSha256':hashlib.sha256(('\n'.join(mm)+'\n').encode()).hexdigest()})
 visible=sorted(u for u in members if rows[u]['paper_id'] not in reserved); withheld=members-set(visible)
 union.update(members); paperunion.update(rows[u]['paper_id'] for u in visible)
 families.append({'familyId':fid,'workingTitle':title,'purpose':purpose,'candidateRegions':rr,'unionMemberCount':len(members),'unionMemberIdsSha256':hashlib.sha256(('\n'.join(sorted(members))+'\n').encode()).hexdigest(),'providedDescriptionCount':len(visible),'reservedUnreviewedUnitCount':len(withheld),'sourceExcerptTargetPapers':{'central':4,'boundary':3,'outsideOrContradictory':3},'freshStageUnusedPaperCount':6,'questionsExpected':'3–8 where supported; fewer acceptable with an explicit reason; no forced partitions','status':'planned_not_prepared_not_launched'})
# Resource forecasts use observed pilot usage; no cached-token discount or dollar conversion.
pilot=json.loads((E/'pilot-review-summary.json').read_text());mean={k:pilot['usage'][k]/6 for k in pilot['usage']};minutes=statistics.mean(x['elapsedSeconds']/60 for x in pilot['records'])
scenarios=[]
for v in [X,P]:
 rs=list(regions[v].values());L=sum(not r['childIds'] for r in rs);H=len(rs)-L
 for mode in ['complete_two_pass_plus_targeted_checks','three_stage_leaves_plus_parent_two_pass']:
  # 32 fresh checks +24 reconciliation jobs are planning allocations, not outcome guarantees.
  jobs=2*(L+H)+32+24 if mode.startswith('complete') else 3*L+2*H+24
  scenarios.append({'candidate':v,'leaves':L,'parentsIncludingRoot':H,'mode':mode,'coverageJobs':2*(L+H) if mode.startswith('complete') else 3*L+2*H,'freshCheckJobs':32 if mode.startswith('complete') else L,'freshCountAlreadyIncludedInCoverage':not mode.startswith('complete'),'reconciliationJobs':24,'totalJobs':jobs,'pilotEquivalentInputTokens':round(jobs*mean['inputTokens']),'pilotEquivalentOutputTokens':round(jobs*mean['outputTokens']),'pilotEquivalentReasoningOutputTokensIncludedInOutput':round(jobs*mean['reasoningOutputTokens']),'tokenSensitivityRangeFactor':[0.65,1.5],'activeWorkerHours':round(jobs*minutes/60,1),'idealWallHoursByConcurrency':{str(c):round(jobs*minutes/60/c,2) for c in [4,12,24]},'planningWallHoursWithQueueDependencyAndReviewOverhead':{str(c):[round(jobs*minutes/60/c*1.3,1),round(jobs*minutes/60/c*2,1)] for c in [4,12,24]}})
out={'schemaVersion':'q025-next-wave-plan/1','status':'proposal_no_jobs_prepared_or_launched','calibrationFamilies':families,'calibrationTotals':{'families':len(families),'requests':3*len(families),'unionUnits':len(union),'uniqueVisibleUnits':sum(rows[u]['paper_id'] not in reserved for u in union),'descriptionOccurrences':sum(f['providedDescriptionCount'] for f in families),'uniqueVisiblePapers':len(paperunion),'sourceExcerptPaperOccurrencesTarget':10*len(families),'freshPaperOccurrences':6*len(families),'initialConcurrency':4,'pilotEquivalentInputTokens':round(24*mean['inputTokens']),'pilotEquivalentOutputTokens':round(24*mean['outputTokens']),'idealWallHours':round(24*minutes/60/4,2)},'holdoutPolicy':{'reservedPaperCount':len(reserved),'reservationFileSha256':sha(E/'final-holdout-reservation.local.json'),'excludedFrom':['reviewer descriptions','source excerpts','disposition rows','canonicalization prompts','fresh checks'],'numericalVectorsMayBeIncluded':'transductive unsupervised construction; semantic holdout remains unseen'},'wholeAtlasScenarios':scenarios,'pilotObserved':{'meanMinutes':minutes,'meanTokens':mean,'sampleJobs':6},'costCaveat':'Forecasts are planning estimates from two sampled large-family pilots, not guarantees. Recalibrate from eight-family packets with all descriptions. Output tokens include reasoning tokens; do not add them twice. No current dollar-price assumption.'}
(B/'plan.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'families':[(f['familyId'],f['unionMemberCount'],f['providedDescriptionCount'],f['reservedUnreviewedUnitCount']) for f in families],'totals':out['calibrationTotals'],'scenarios':[(s['candidate'],s['mode'],s['totalJobs'],s['pilotEquivalentInputTokens'],s['pilotEquivalentOutputTokens'],s['planningWallHoursWithQueueDependencyAndReviewOverhead']['24']) for s in scenarios]},indent=2))
