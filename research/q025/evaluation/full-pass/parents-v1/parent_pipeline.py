"""Bottom-up parent inputs: real source contrasts plus attributed child scopes."""
import copy,hashlib,json,sys
from pathlib import Path
B=Path(__file__).resolve().parent;C=B.parent/'compact-v1';sys.path.insert(0,str(C))
from compact_pipeline import compile_packet,model_view,dump,hfile
from production_contract import evaluate

def make_parent_packet(original,children,stage='proposal',prior=None):
 packet,_=compile_packet(original,stage);registry=packet['refRegistry'];packet['kind']='parent';packet['childScopes']=[];packet['priorCards']=[];packet['existingCards']=[]
 for i,child in enumerate(children):
  ref=f'c{i}';definition=child['region'];card=copy.deepcopy(definition);card.update(id=ref,kind='region',refs=[],methods=card.get('methods',[]),aliases=[]);packet['priorCards'].append(card)
  registry[ref]={'kind':'attributed_child_review','childRegionId':child['candidateRegionId'],'artifactSha256':child['artifactSha256'],'scopeStatus':child['scopeStatus'],'primaryReadingClaim':False}
  packet['childScopes'].append({'ref':ref,'candidateRegionId':child['candidateRegionId'],'scopeStatus':child['scopeStatus'],'memberIdsSha256':child['memberIdsSha256'],'fullMemberCount':child['fullMemberCount'],'reviewedDescriptionCount':child['reviewedDescriptionCount'],'reservedUnreviewedCount':child['reservedUnreviewedCount'],'unresolvedAssignmentCount':child['unresolvedAssignmentCount'],'readingBasis':'Attributed child review and exact coverage ledger; parent reviewer has not independently reread every descendant description.','artifactSha256':child['artifactSha256'],'unresolved':child.get('unresolved',[])})
  for j,q in enumerate(child.get('questions',[])):
   x=f'x{i}_{j}';card=copy.deepcopy(q['definition']);card.update(id=x,childRef=ref,scopeStatus=q['scopeStatus'],candidateId=q['candidateId']);packet['existingCards'].append(card);registry[x]={'kind':'attributed_child_question','childRegionId':child['candidateRegionId'],'candidateId':q['candidateId'],'scopeStatus':q['scopeStatus'],'primaryReadingClaim':False}
 packet['parentCoverage']={'fullDescendantMembers':original.get('fullMemberCount'),'providedContrastDescriptions':len(packet['units']),'providedPrimaryContrastUnits':sum(bool(u['primaryRefs']) for u in packet['units']),'completeMemberIdsPinnedExternally':True,'descendantCoverage':'Only the child ledgers establish descendant description coverage; this parent pass reviews supplied contrasts and scope synthesis.'}
 packet['parentRules']=['Assess every c* child scope once for parent compatibility; this is not a fresh verification of all child science.','Use links r→c* to distinguish narrowing, method, application and comparison. Different systems need not share one mechanism.','Child questions x* may be reused; do not author a duplicate merely because a different route reaches it. A suggested equivalence still needs a separate scoped decision.','Unadmitted child replacements remain unadmitted; a parent inclusion assessment alone does not cure missing independent child-scope support.','The actual unit rows are bounded primary contrasts, not substitutes for complete descendant mappings. Never claim to have read unsupplied descendants.','Preserve alternate homes and nonpositive outcomes. No question is excluded merely for lacking Swampland vocabulary.']
 if prior is not None:
  base,_=make_parent_packet(original,children,'proposal');normalized=evaluate(base,prior)['normalizedReview'];aliases={'r':'r'};aliases.update({q['id']:f'p{i}' for i,q in enumerate(normalized['cards'])});aliases.update({f['id']:f'pf{i}' for i,f in enumerate(normalized['factors'])});aliases.update({g['id']:f'pi{i}' for i,g in enumerate(normalized['identityGroups'])})
  for q in normalized['cards']:
   q=copy.deepcopy(q);old=q['id'];q['id']=aliases[old];packet['priorCards'].append(q);registry[q['id']]={'kind':'prior_parent_question','sourceId':old}
  region=copy.deepcopy(normalized['region']);region.update(id='r',kind='region',refs=[],methods=[],aliases=[]);packet['priorCards'].append(region);registry['r']={'kind':'prior_parent_region','sourceId':'r'};packet['priorRegion']=normalized['region']
  packet['priorFactors']=[dict(copy.deepcopy(f),id=aliases[f['id']]) for f in normalized['factors']];packet['priorGroups']=[dict(copy.deepcopy(g),id=aliases[g['id']]) for g in normalized['identityGroups']]
  packet['priorAssignments']=[]
  for a in normalized['units']:
   a=copy.deepcopy(a);a['q']=[dict(q,id=aliases.get(q['id'],q['id'])) for q in a['q']];a['f']=[aliases[x] for x in a['f']];a['identity']=aliases.get(a['identity'],a['identity']);packet['priorAssignments'].append(a)
  packet['priorParentLinks']=[dict(copy.deepcopy(l),source=aliases.get(l['source'],l['source']),target=aliases.get(l['target'],l['target'])) for l in normalized['links']];packet['priorChildAssessments']=[a for a in normalized['cardReviews'] if a['id'].startswith('c')]
 return packet,model_view(packet)

if __name__=='__main__':
 request=json.loads(Path(sys.argv[1]).read_text());assert hfile(request['sourcePacketPath'])==request['sourcePacketSha256'];original=json.loads(Path(request['sourcePacketPath']).read_text());original['fullMemberCount']=request['fullMemberCount'];children=[]
 for c in request['childArtifacts']:
  assert hfile(c['path'])==c['sha256'];child=json.loads(Path(c['path']).read_text());child['artifactSha256']=c['sha256'];children.append(child)
 prior=json.loads(Path(request['priorReplyPath']).read_text()) if request.get('priorReplyPath') else None;packet,view=make_parent_packet(original,children,request['stage'],prior);dump(sys.argv[2],packet);Path(sys.argv[3]).write_text(Path(request['instructionsPath']).read_text()+'\n\nPARENT SYNTHESIS PACKET\n'+json.dumps(view,ensure_ascii=False,separators=(',',':'))+'\n')
