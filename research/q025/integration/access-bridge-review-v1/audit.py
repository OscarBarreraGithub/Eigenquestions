"""Read-only audit of proposed incidence access; grants no navigation admission."""
import collections,hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent;ROOT=B.parents[3]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=ROOT/'research/q025/assembly/organization-residual-v1/coverage-paths.json';data=json.loads(source.read_text())
for pin in data['inputs']:assert sha(ROOT/pin['path'])==pin['sha256'],'Changed diagnostic input'
packet=json.loads((ROOT/data['inputs'][0]['path']).read_text());dest={x['id']:x for x in packet['destinations']}
homes={(x['unitId'],x['destinationId'],x['decisionId']):x for x in packet['placements']if x['role']!='context'}
roles={(x['unitId'],x['destinationId'],x['role'],x['decisionId']):x for x in packet['sourceContributions']}
routes=data['candidateSupportRoutes'];pairs=set();witnesses=set();kind_counts=collections.Counter();home_roles=collections.Counter();positive_roles=collections.Counter();nonquestion=[];rows=0
for link in routes:
 key=(link['source'],link['target']);assert key not in pairs;pairs.add(key);assert key[0]!=key[1];units=set();kind_counts['→'.join(dest[x]['kind']for x in key)]+=1
 if dest[link['target']]['kind']!='question':nonquestion.append({**link,'sourceTitle':dest[link['source']]['title'],'targetTitle':dest[link['target']]['title']})
 for support in link['supports']:
  assert support['unitId']not in units;units.add(support['unitId']);witnesses.add(support['unitId']);rows+=1
  h=homes[(support['unitId'],link['source'],support['placementDecisionId'])];r=roles[(support['unitId'],link['target'],support['role'],support['contributionDecisionId'])]
  assert r.get('qualification')==support['qualification'];assert h['status']=='accepted'and h['allocationWeight']>0;assert support['role']in ['addresses','instantiates','specializes'];home_roles[h['role']]+=1;positive_roles[support['role']]+=1
examples=[]
for unit in ['unit:72ea9aab8c7f5e8693cf643cf866542b0d281605ac7ff1e4ba53d25d90f232a3','unit:68b2460dbd5e441bfa56c8a9dfb9ce0ee2a84d74f21591cdc3ecd5e4763aa332','unit:c08ed44e9a45a52485ff76bf4c063f66dd76f751a04cfe3e43f57aef9fe48bab']:
 link=next(x for x in routes if len(x['supports'])==1 and x['supports'][0]['unitId']==unit);examples.append({**link,'sourceTitle':dest[link['source']]['title'],'targetTitle':dest[link['target']]['title']})
result={'schemaVersion':'q025-organizational-access-review/1','input':{'path':str(source.relative_to(ROOT)),'sha256':sha(source)},'inputPinsVerified':len(data['inputs']),'exactCandidateJoinsVerified':rows,'candidateRoutes':len(routes),'uniqueSupportingUnits':len(witnesses),'routeEndpointKinds':dict(kind_counts),'homeRoles':dict(home_roles),'positiveRoles':dict(positive_roles),'singleWitnessRoutes':sum(len(x['supports'])==1 for x in routes),'duplicateEndpoints':0,'duplicateUnitsWithinRoute':0,'nonquestionTargets':nonquestion,'scopeQualificationExamples':examples,'noPrimarySourceReadingPerformed':True,'scientificOrNavigationAdmission':False,'limits':['Exact join audit against already admitted inputs, not independent certification of their scientific judgments.','Coverage probe also uses paired native routes that are not yet admitted and treats them as traversable in either direction.','Final complete accepted graph and source-filter behavior still require separate checks.']}
(B/'audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:result[k]for k in ['inputPinsVerified','exactCandidateJoinsVerified','candidateRoutes','routeEndpointKinds','scientificOrNavigationAdmission']}))
