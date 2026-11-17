import json,sys
from pathlib import Path
A=Path(__file__).resolve().parents[1];j=json.load(open(A/'placement-incremental-v1/cut-03/exception-intake.json'));l=json.load(open(A/'placement-latent-lookup-v1/supplement.json'));lm={(r['familyId'],r['stage'],r['localRef']):r for r in l['rows']}
preferred={67:'f2cef2fc577c8f015fe72e9e',69:'5bd03e3b39d5ff867121e8a2',70:'16e7a3854c88582d05e83321',71:'2ba94e8886d522b048bb6a7c',74:'5b66a682ce39a3040cedd3b8',81:'4723858a27075d6ac6ef24e2',59:'5f32da21add50f21c423db3b',62:'cf0edc500f72f14549b02c65',63:'45f6412f0b685bf8bf595207',64:'4d1b8eaacc588a97f0dc88cd',65:'f412f1abf63acf2a1fa8b2e4',49:'1bcaf78e5b3155dd86bc9363',50:'3b3cef107f1cba22638adb2a',51:'29e3b8f98b7d5cd4d4d5a10d',52:'aed6eac98dd91f2b2da7e827',53:'374623f65e03eab654c343ac',54:'152f97698847f68bfd74d7d0',55:'3c16774a3e2b5fe8d043246c',56:'ca506aab62df94e6f71a67b0',57:'6bb50a3f2b3a551bc4972c3a',58:'12fbf695d2c00ead28a95c19'}
for i in map(int,sys.argv[1:]):
 n=j['newScopes'][i];c=n['globalExistingScopeLookup']['candidates'];ll=lm[n['familyId'],n['stage'],n['localRef']]['candidates'];pick=[c[0]]
 extra=next((x for x in ll if x['destinationId'].endswith(preferred.get(i,''))),None)if i in preferred else ll[0]if ll else None
 if extra and all(x['id']!=extra['destinationId']for x in pick):pick.append({'id':extra['destinationId'],'definition':extra['definition']})
 def definition(x):return {k:x[k]for k in ['kind','title','question','summary','scope','readingCoverage']if k in x}
 sources=[{k:s[k]for k in ['unitId','paperId','description','proposalJudgment','challengeJudgment','independentPriorPlacementReview','proposalAttributions','challengeAttributions']}for s in n['sources']]
 value={'index':i,'familyId':n['familyId'],'localRef':n['localRef'],'definitionSha256':n['definitionSha256'],'definition':n['definition'],'independentScopeAssessment':n['independentAssessment'],'sources':sources,'contrasts':[{'id':x['id'],'definition':definition(x['definition'])}for x in pick]}
 # All scientific fields/notes and current judgments are lossless; omit only duplicated registry metadata.
 for s in value['sources']:
  for key in ['proposalAttributions','challengeAttributions']:
   s[key]=[{'reviewId':r['reviewId'],'sourceOrigin':r['sourceOrigin'],'original':r['original']}for r in s[key]]
 for source in value['sources']:
  pj=source['proposalJudgment'];cj=source['challengeJudgment'];source['challengeJudgment']={'sameAsProposalKeys':[k for k,v in cj.items() if k in pj and v==pj[k]],'changedOrAdded':{k:v for k,v in cj.items() if k not in pj or v!=pj[k]}}
 print(json.dumps(value,ensure_ascii=False,separators=(',',':')))
