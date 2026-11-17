"""Authoritative authored-scope intake; no scientific or identity admission."""
import collections,datetime,hashlib,json,sys
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent
sys.path.insert(0,str(F/'findings-v1'));from audit_field_completeness import screen

def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def fingerprint(kind,d):return hashlib.sha256(json.dumps({'kind':kind,'question':d['question'],'scope':d['scope']},ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def build(root):
 records=[];factors=[];reviews=[];unique_units=set();sealed={r['paperId'] for r in json.loads((E/'final-holdout-reservation.local.json').read_text())['records']}
 for d in sorted(Path(root).glob('*-challenge')):
  if not (d/'receipt.json').exists():continue
  receipt=json.loads((d/'receipt.json').read_text())
  if receipt['status']!='complete':continue
  pfile=d/'packet.actual.json';p=json.loads(pfile.read_text());reply=json.loads((d/'reply.json').read_text());raw=json.loads((d/'reply.raw.txt').read_text());flags,_=screen(raw)
  assert h(d/'reply.json')==receipt['normalizedReplySha256']
  units={u['i']:u for u in p['units']};assert len(reply['units'])==len(units)
  assert not sealed&{u['paperId'] for u in units.values()}
  uid=lambda i:p['refRegistry'][f'u{i}']['unitId']
  prior={a['i']:a for a in p.get('priorAssignments',[])};assess={a['id']:a for a in reply['cardReviews']};pins={'challengeReceiptSha256':h(d/'receipt.json'),'challengeReplySha256':h(d/'reply.json'),'challengeRawSha256':h(d/'reply.raw.txt'),'challengePacketSha256':h(pfile),'normalizationSha256':h(d/'normalization.json')}
  proposal=d.parent/(d.name[:-9]+'proposal')
  if (proposal/'receipt.json').exists():pins['proposalReceiptSha256']=h(proposal/'receipt.json')
  review={'reviewId':d.name,'reviewKey':p['familyId'],'pins':pins,'unitCount':len(units),'sourceExcerptRows':sum(a['b']=='excerpt' for a in reply['units']),'rawFieldFlags':flags};reviews.append(review)
  # A factor registry keeps complete qualifications once; screening never completes them.
  fs={f['id']:f for f in p.get('priorFactors',[])};fs.update({f['id']:f for f in reply['factors']})
  for local,f in fs.items():
   flag=[x for x in flags if x.get('factorId')==local]
   factors.append({'factorRef':d.name+':'+local,'reviewId':d.name,'localRef':local,'definition':f,'completeness':'screening_flag' if flag else 'not_flagged_not_independently_certified','flags':flag,'evidenceRefs':[{'localRef':r,**p['refRegistry'][r]} for r in f['refs']]})
  cards=[(c,assess[c['id']],'prior') for c in p['priorCards']]+[(c,None,'new_challenger') for c in reply['cards']]
  for c,a,origin in cards:
   local=c['id'];kind='region' if local=='r' else 'question'
   if a and a['decision']=='supported_as_written' and a['scopeChange']=='same':status='independently_supported'
   elif a and a['decision']=='supported_with_limits' and a['scopeChange']=='same':status='limits_require_adjudication'
   elif a:status='unresolved_scope_change'
   else:status='new_challenger_proposal'
   definition={k:c[k] for k in ['title','question','summary','scope','readingLimit']};contributions=[]
   for row in reply['units']:
    pairs=[q for q in row['q'] if q['id']==local];old=prior.get(row['i']);oldpairs={(q['id'],q['role']) for q in old['q']} if old else set()
    for q in pairs:
     u=units[row['i']];unitid=uid(row['i']);unique_units.add(unitid);refs=list(dict.fromkeys([u['descriptionRef']]+row['refs']))
     contributions.append({'unitId':unitid,'paperId':u['paperId'],'unitIndex':row['i'],'role':q['role'],'independentRoleAgreement':(local,q['role']) in oldpairs,'basis':'source_excerpt_checked' if row['b']=='excerpt' else 'description_checked','evidenceRefs':[{'localRef':r,**p['refRegistry'][r]} for r in refs],'sourceOrigin':u.get('selectionRole'),'disposition':row['d'],'dispositionAgreement':old is not None and old['d']==row['d'],'materialScopeFlag':row['reason'] in ['changed_regime','scope_mismatch'],'factorRefs':[d.name+':'+f for f in row['f']],'identityState':row['identity']})
   scope_flags=[x for x in flags if x.get('cardId')==local and x['impact']=='scope_definition'];just_flags=[x for x in flags if x.get('cardId')==local and x['impact']=='admission_justification']
   records.append({'recordId':d.name+':'+local,'candidateId':'q025-candidate-'+kind+':'+fingerprint(kind,definition)[:24],'kind':kind,'reviewId':d.name,'reviewKey':p['familyId'],'localRef':local,'scopeStatus':status,'definition':definition,'methods':c.get('methods',[]),'assessment':a,'scopeDefinitionFlags':scope_flags,'admissionJustificationFlags':just_flags,'contributions':contributions,'evidenceRefs':[{'localRef':r,**p['refRegistry'][r]} for r in c.get('refs',[])],'pins':pins,'identityStatus':'unreconciled_authored_scope_not_accepted_canonical_id'})
 return {'schemaVersion':'q025-authored-scope-registry/1','createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':records,'factors':factors,'reviews':reviews,'counts':{'completedLeafPairs':len(reviews),'authoredScopes':len(records),'authoredQuestions':sum(r['kind']=='question' for r in records),'scopeStatuses':dict(collections.Counter(r['scopeStatus'] for r in records)),'uniqueContributingSourceUnits':len(unique_units),'sourceContributionRecords':sum(len(r['contributions']) for r in records),'reservedPapersExcluded':len(sealed),'acceptedCanonicalQuestionsByThisCompiler':0},'semantics':'Every authored scope remains inspectable, including disagreements/new proposals. Exact shared sources, reviewed factors and text may nominate reconciliation but never establish equivalence. Candidate IDs/content fingerprints are not accepted canonical identities. Same-source repetitions preserve unitId and do not add source mass. Scope, contribution, factor, placement and identity agreement remain separate.'}
if __name__=='__main__':
 out=build(F/'native-local/full-leaf-wave-v3/jobs');p=B/'authored-scope-registry.json';p.write_text(json.dumps(out,ensure_ascii=False,separators=(',',':'))+'\n');report={'schemaVersion':'q025-authored-scope-registry-report/1','createdAt':out['createdAt'],'registrySha256':h(p),'registryBytes':p.stat().st_size,'counts':out['counts'],'compilerSha256':h(__file__)};(B/'authored-scope-registry-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
