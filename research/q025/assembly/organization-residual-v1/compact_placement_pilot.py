"""Lossless scientific projection; machine repetition stays in pinned sidecars."""
import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent; ROOT=B.parents[3]
def pin(p):
    b=p.read_bytes();return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
index=json.loads((B/'placement-pilot-index.json').read_text()); out=[]
for item in index['packets']:
    side=ROOT/item['path']; assert pin(side)['sha256']==item['sha256']
    p=json.loads(side.read_text()); ids={s['id']:s['ref'] for s in p['scopes']}
    review_ids=sorted({a['reviewId'] for u in p['units'] for a in u['proposalAttributions']+u['challengeAttributions']})
    review_refs={v:'r'+str(i) for i,v in enumerate(review_ids)}
    rows=[]
    for u in p['units']:
        contexts=[]
        prior={a['reviewId']:a for a in u['proposalAttributions']}; challenge={a['reviewId']:a for a in u['challengeAttributions']}
        assert prior.keys()==challenge.keys()
        for rid,a in prior.items():
            b=challenge[rid]; h=a['homeAgreement']
            contexts.append({'reviewRef':review_refs[rid],'sourceOrigin':a['sourceOrigin'],
                'proposal':a['original'],'challenge':b['original'],
                'resolvedContributions':a['resolvedTypedContributions'],
                'resolvedProposalHomeRef':ids.get(h['proposal'].get('candidateId')),
                'resolvedChallengeHomeRef':ids.get(h['challenge'].get('candidateId')),
                'sameExplicitScientificCard':h['sameExplicitScientificCard'],
                'proposalDefinitionMatchesPinnedOriginal':h['proposalDefinitionMatchesPinnedOriginal'],
                'unchangedSupportedScope':h['unchangedSupportedScope'],
                'placementAlreadyAdmitted':False})
        issues=[{'reviewRef':review_refs[x['reviewId']],'candidateHomeRef':ids.get(x['destinationId']),
                 'exclusionReasons':x['exclusionReasons']} for x in u['coverageIssue']['priorCensus']]
        rows.append({'ref':u['ref'],'paperId':u['paperId'],'description':u['description'],
                     'priorContexts':contexts,'candidateHomeRefs':u['candidateHomeRefs'],
                     'existingHomeRefs':u['existingHomeRefs'],'coverageIssue':{'bucket':u['coverageIssue']['bucket'],'contexts':issues},
                     'originalSourceQuestionMustRemainWhole':True})
        # All scientific source descriptions and both complete original annotations survive.
        assert rows[-1]['description']==u['description']
        assert [c['proposal'] for c in contexts]==[a['original'] for a in u['proposalAttributions']]
        assert [c['challenge'] for c in contexts]==[challenge[a['reviewId']]['original'] for a in u['proposalAttributions']]
    scope_fields=('kind','title','question','summary','scope','readingCoverage','methods','aliases','scientificStatus')
    scopes=[{'ref':s['ref'],**{k:s['destination'][k] for k in scope_fields if k in s['destination']}} for s in p['scopes']]
    view={'schemaVersion':'q025-placement-scientific-view/1','familyId':p['familyId'],'units':rows,'scopes':scopes,
          'readingLimits':p['readingLimits']+[
          'Original p*/q*/x*/f*/e* identifiers inside prior annotations belong to that reviewRef namespace; they are not current global scope IDs. Use only the resolved q* scope refs for new placement choices. An unresolved old reference is not an invented candidate.',
          'Exact source IDs, description hashes, complete destination metadata and all original review/source pins are retained in the checksummed machine sidecar. No primary text was removed: none was supplied.'],
          'selection':p['selection'],'sidecar':pin(side),
          'reviewNamespaces':{v:k for k,v in review_refs.items()}}
    path=side.with_suffix('.view.json');path.write_text(json.dumps(view,ensure_ascii=False,separators=(',',':'))+'\n')
    out.append({'familyId':p['familyId'],'view':pin(path),'sidecar':pin(side),'units':len(rows),'scopes':len(scopes),'priorContexts':sum(len(x['priorContexts']) for x in rows),
                'completeDescriptionsAndBothAnnotationsVerified':True})
result={'schemaVersion':'q025-placement-pilot-delivery/1','status':'source_inputs_only_no_native_launch','inputIndex':pin(B/'placement-pilot-index.json'),'script':pin(Path(__file__)),
        'packets':out,'distinctSources':index['distinctSources'],'admissionPolicy':'New proposal/challenge judgments remain pending coordinator admission; no home, scope, identity, contribution or navigation is admitted by source export.'}
(B/'placement-pilot-delivery.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
