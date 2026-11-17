"""Versioned whole-registry intake snapshots; active source/native inputs unchanged."""
import datetime,hashlib,json,sys
from pathlib import Path
from build_authored_registry import build
B=Path(__file__).resolve().parent;F=B.parent;sys.path.insert(0,str(F/'findings-v1'));from audit_field_completeness import screen
out=build(F/'native-local/full-leaf-wave-v3/jobs')
# Screen inherited definitions too, rather than only newly emitted factors.
for factor in out['factors']:
 flags,_=screen({'factors':[factor['definition']]});factor['flags']=flags;factor['completeness']='screening_flag' if flags else 'not_flagged_not_independently_certified'
assessments=[];groups=[]
for review in out['reviews']:
 d=F/'native-local/full-leaf-wave-v3/jobs'/review['reviewId'];p=json.loads((d/'packet.actual.json').read_text());r=json.loads((d/'reply.json').read_text());units={u['i']:u for u in p['units']};prior={a['i']:a for a in p['priorAssignments']};norm=json.loads((d/'normalization.json').read_text())
 for row in r['units']:
  u=units[row['i']];old=prior.get(row['i']);uid=p['refRegistry'][u['sourceRef']]['unitId'];oldq={(q['id'],q['role']) for q in old['q']} if old else set()
  assessments.append({'reviewId':review['reviewId'],'reviewKey':p['familyId'],'unitId':uid,'paperId':u['paperId'],'sourceOrigin':u.get('selectionRole'),'descriptionSha256':p['refRegistry'][u['descriptionRef']]['textSha256'],'basis':'source_excerpt_checked' if row['b']=='excerpt' else 'description_checked','disposition':row['d'],'dispositionAgreement':old is not None and old['d']==row['d'],'title':row['title'],'home':row['home'],'note':row['note'],'reason':row['reason'],'questionContributions':[{'recordId':review['reviewId']+':'+q['id'],'role':q['role'],'independentRoleAgreement':(q['id'],q['role']) in oldq} for q in row['q']],'factorRefs':[review['reviewId']+':'+f for f in row['f']],'fineIdentityState':row['identity'],'canonicalUniquenessCertified':False,'otherUnitDescriptionContext':[x for x in norm.get('crossUnitDescriptionContext',[]) if x['unitIndex']==row['i']]})
 for group in r['identityGroups']:groups.append({'reviewId':review['reviewId'],'group':group,'memberUnitIds':[p['refRegistry'][f'u{a["i"]}']['unitId'] for a in r['units'] if a['identity']==group['id']],'status':'new_challenger_group_proposal_not_canonical_admission'})
out['unitAssessments']=assessments;out['fineGroupProposals']=groups;out['counts']['unitAssessmentRecords']=len(assessments);out['counts']['uniqueAssessedUnits']=len({a['unitId'] for a in assessments});out['counts']['questionlessUnitAssessments']=sum(not a['questionContributions'] for a in assessments);out['counts']['fineGroupProposals']=len(groups);stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');p=B/f'authored-scope-registry-{stamp}.json';p.write_text(json.dumps(out,ensure_ascii=False,separators=(',',':'))+'\n');report={'schemaVersion':'q025-authored-registry-version/2','path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'counts':out['counts'],'compilerSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'activeInputsChanged':False};q=B/f'registry-report-{stamp}.json';q.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
