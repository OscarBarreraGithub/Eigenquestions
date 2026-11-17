"""Existing paired evidence only: quantify broader homes and genuine residuals.
This emits candidates for coordinator review, never placement admissions.
"""
import collections,hashlib,json,re,sys
from pathlib import Path
B=Path(__file__).resolve().parent;ROOT=B.parents[3];E=ROOT/'research/q025/evaluation';F=E/'full-pass';sys.path.insert(0,str(F/'findings-v1'));from audit_field_completeness import screen as field_screen
def read(p):
    raw=p.read_bytes();return json.loads(raw),{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
registry,rpin=read(F/'reconciliation-v1/authored-scope-registry-v3-20261117T121953Z.json');component,cpin=read(F/'admissions-v1/supported-scope-role-component-v1.json');simple,spin=read(F/'native-local/uncomplicated-home-candidates-v1.json');records={r['recordId']:r for r in registry['records']};reviews={r['reviewId']:r for r in registry['reviews']};known_simple={r['unitId']for r in simple['candidates']};assessed={a['unitId']for a in registry['unitAssessments']};rawcache={};pins={};candidates=[];excluded=[];joint_before=set()
for a in registry['unitAssessments']:
    r=records.get(a['reviewId']+':r')
    if not r or r['kind']!='region' or r['scopeStatus']!='independently_supported' or not a['dispositionAgreement'] or a['disposition']not in ['member','overlap']:continue
    joint_before.add(a['unitId']);rid=r['reviewId']
    if rid not in rawcache:
        d=E/reviews[rid]['artifactDirectory'];p,pp=read(d/'packet.actual.json');reply,rp=read(d/'reply.json');assert pp['sha256']==r['pins']['challengePacketSha256'];assert rp['sha256']==r['pins']['challengeReplySha256'];pins[rid]={'packet':pp,'reply':rp};rawcache[rid]=(p,{p['refRegistry'][u['descriptionRef']]['unitId']:u for u in p['units']},{u['i']:u for u in p['priorAssignments']},{u['i']:u for u in reply['units']})
    p,umap,prior,current=rawcache[rid];u=umap[a['unitId']];old=prior[u['i']];now=current[u['i']];assert old['d']==now['d']==a['disposition'];reasons=[]
    if r.get('scopeDefinitionFlags'):reasons.append('unresolved_scope_definition_flag')
    if r.get('admissionJustificationFlags'):reasons.append('unresolved_scope_admission_annotation')
    flags=field_screen({'units':[old,now]})[0]
    if flags:reasons.append('unresolved_unit_annotation_screen')
    if any(x['reason'] in ['changed_regime','scope_mismatch'] for x in [old,now]):reasons.append('explicit_changed_regime_or_scope_mismatch')
    ref=p['refRegistry'][u['descriptionRef']];assert hashlib.sha256(u['description'].encode()).hexdigest()==ref['textSha256']
    def own_primary(row):
        out={}
        for key in row['refs']:
            e=p['refRegistry'][key]
            if e.get('kind')in['primary','source_excerpt'] and e.get('paperId')==u['paperId']:
                c=e['sourceContext'];out[(c['path'],c['pdfPage'],c['start'],c['end'],c['textSha256'])]=e
        return out
    left=own_primary(old);right=own_primary(now);common=[right[k] for k in sorted(set(left)&set(right))]
    exact_home=old['home']==now['home'];compound_note=bool(re.search(r'compound|distinct.{0,30}target|linked.{0,20}target|multi[- ]target',old['note']+' '+now['note'],re.I));context_note=bool(re.search(r'inherit|context|not (?:a |the )?direct|only (?:a )?method|outside|excluded|beyond',old['note']+' '+now['note'],re.I))
    row={'unitId':a['unitId'],'paperId':u['paperId'],'description':u['description'],'descriptionSha256':ref['textSha256'],'sourceOrigin':a['sourceOrigin'],'regionRecordId':r['recordId'],'destinationId':r['candidateId'],'title':r['definition']['title'],'question':r['definition']['question'],'scope':r['definition']['scope'],'readingLimit':r['definition']['readingLimit'],'jointDisposition':a['disposition'],'proposalHomeRef':old['home'],'challengeHomeRef':now['home'],'exactRawHomeRefAgreement':exact_home,'proposalReason':old['reason'],'challengeReason':now['reason'],'proposalNote':old['note'],'challengeNote':now['note'],'pairedQuestionRoles':a['questionContributions'],'fineIdentityStates':[old['identity'],now['identity']],'compoundTargetLanguage':compound_note,'contextOrExclusionLanguage':context_note,'basis':'source_excerpt_checked' if old['b']==now['b']=='excerpt' and common else 'description_checked','evidenceRefs':[{'kind':'description','unitId':a['unitId'],'textSha256':ref['textSha256']}]+common,'reviewPins':pins[rid],'scopePins':r['pins'],'excludedReasons':reasons,'unitAnnotationFlags':flags,'status':'requires_explicit_home_policy_and_canonical_mapping','wholeQuestionCoverage':'Joint overlap or compound/context notes require retaining all source targets and explicit home weights; no partial target is silently discarded.'}
    (excluded if reasons else candidates).append(row)
byunit=collections.defaultdict(list)
for row in candidates:byunit[row['unitId']].append(row)
broad_extra=set(byunit)-known_simple;remaining=assessed-known_simple-set(byunit);roles=collections.defaultdict(set);positive_dest=collections.defaultdict(set)
for row in component['sourceContributions']:
    roles[row['unitId']].add(row['role'])
    if row['role']in['addresses','instantiates','specializes']:positive_dest[row['unitId']].add(row['destinationId'])
categories=collections.defaultdict(list)
for uid in sorted(remaining):
    if not roles[uid]:kind='no_currently_admitted_typed_question_role'
    elif 'addresses'in roles[uid]:kind='admitted_addresses_but_no_simple_or_unflagged_broad_home'
    elif positive_dest[uid]:kind='admitted_instantiates_or_specializes_without_home'
    else:kind='method_boundary_or_comparison_only_no_home'
    categories[kind].append(uid)
examples=[];used=set();extra_rows=[r for r in candidates if r['unitId']in broad_extra]
for label,pattern in [('holography',r'holograph|AdS/CFT'),('gauge_geometry',r'gauge|anomal'),('cosmology',r'inflat|cosmolog|dark matter'),('compactification',r'compactif|moduli'),('quantum_or_mathematical_methods',r'entangl|topological|amplitud|quantum')]:
    choices=[r for r in extra_rows if r['unitId']not in used and r['jointDisposition']=='member' and re.search(pattern,r['question'],re.I)]
    if choices:
        r=sorted(choices,key=lambda r:(r['basis']!='source_excerpt_checked',not bool(r['proposalNote']or r['challengeNote']),r['unitId']))[0];examples.append({'selectionPurpose':label,**r});used.add(r['unitId'])
for purpose,filterfn in [('joint_overlap_with_explicit_qualification',lambda r:r['jointDisposition']=='overlap' and bool(r['proposalNote']or r['challengeNote'])),('compound_target_requires_coverage_decision',lambda r:r['compoundTargetLanguage'])]:
    choices=[r for r in extra_rows if r['unitId']not in used and filterfn(r)]
    if choices:
        r=sorted(choices,key=lambda r:(r['basis']!='source_excerpt_checked',r['unitId']))[0];examples.append({'selectionPurpose':purpose,**r});used.add(r['unitId'])
weak=[r for r in excluded if r['unitId']not in used and r['unitId']not in known_simple]
if weak:
    r=sorted(weak,key=lambda r:(not r['contextOrExclusionLanguage'],r['unitId']))[0];examples.append({'selectionPurpose':'withheld_borderline_annotation_or_premise_case',**r})
assert len(examples)==8
payload={'candidates':candidates,'excluded':excluded,'residualBuckets':dict(categories)};payloadpath=B/'broader-home-candidates.local.json';payloadpath.write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':'))+'\n');_,payloadpin=read(payloadpath)
raw_known=known_simple|joint_before
report={'schemaVersion':'q025-broader-home-lane-audit/1','status':'candidate_evidence_audit_not_new_home_admission','inputs':{'registry':rpin,'scopeRoleComponent':cpin,'simpleHomeCandidates':spin,'fullCandidates':payloadpin},'counts':{'eligiblePreHoldoutQuestions':8430,'uniqueAssessedUnitsInSnapshot':len(assessed),'notYetAssessedInSnapshot':8430-len(assessed),'approvedSimpleClassUnits':len(known_simple),'jointMemberOrOverlapBeforeFlagExclusions':len(joint_before),'additionalBroadUnitsBeforeFlags':len(joint_before-known_simple),'unflaggedBroadUnits':len(byunit),'additionalUnflaggedBroadUnits':len(broad_extra),'assessedRemainingAfterSimpleAndBroadCandidates':len(remaining),'rawResidualBeforeFlags':len(assessed-raw_known),'flaggedAttributionRows':len(excluded),'flaggedRowsByReason':dict(collections.Counter(x for r in excluded for x in r['excludedReasons'])),'additionalUnflaggedBroadUniqueMemberOnly':sum(any(r['jointDisposition']=='member' for r in byunit[u]) for u in broad_extra),'additionalUnflaggedBroadOnlyOverlap':sum(all(r['jointDisposition']=='overlap' for r in byunit[u]) for u in broad_extra),'additionalBroadWithCompoundLanguage':sum(any(r['compoundTargetLanguage']for r in byunit[u])for u in broad_extra),'additionalBroadWithContextOrExclusionLanguage':sum(any(r['contextOrExclusionLanguage']for r in byunit[u])for u in broad_extra),'additionalBroadHomeCandidateMultiplicity':dict(collections.Counter(str(len({r['destinationId']for r in byunit[u]}))for u in broad_extra)),'residualBuckets':{k:len(v)for k,v in categories.items()}},'examples':examples,'interpretation':['An unchanged reviewed broad scientific scope plus exact paired member attribution can justify a broader organizational home by explicit coordinator policy; this is not fallback to an original numerical bin.','Overlap does not by itself establish coverage of an entire compound source question. Preserve remaining targets and admit explicit normalized weights; do not promote all positive contribution roles automatically.','Fine identity may remain unresolved while a broad scientific family placement is sound. Missing fine equivalence is not a reason to hide the source or invent a question identity.','Excluded annotation flags are screening findings requiring resolution, not automatic proof that the source or family is scientifically wrong.','The raw1050 residual grows after conservative unresolved-annotation exclusions. New completed reviews should update this same census; do not send absent snapshot rows to redundant review.','Final H uses reconciled retained scientific destinations only, deduplicating aliases before normalization and rejecting simultaneous direct ancestor/descendant mass.'],'homesAdmittedByThisAudit':0,'noSealedHoldoutOpened':True,'scriptSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()};out=B/'broader-home-audit.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'report':read(out)[1],'counts':report['counts']},indent=2))
