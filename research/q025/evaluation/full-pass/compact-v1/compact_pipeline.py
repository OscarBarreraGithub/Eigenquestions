"""Reusable compact source/proposal/challenge inputs; no native execution."""
import copy,hashlib,json,sys
from pathlib import Path
B=Path(__file__).resolve().parent;E=B.parent.parent
sys.path.insert(0,str(E/'recovery'))
from compact_inputs import make_packet
from compact_contract import validate

def hfile(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
def model_view(packet):
 view={k:v for k,v in packet.items() if k!='refRegistry'}
 view['referenceRules']={'d':'exact unit description; implicit for own unit row','u':'source-facet access, never canonical question identity','e':'supplied primary excerpt','o':'source object context','g':'source-object relation; not automatically a question premise','p':'prior overview card; assess unchanged text once','r':'prior broad family in cardReviews; current family in links','x':'existing draft, optional assessment','pf':'prior factor, with its original status','pi':'prior fine identity candidate group, assess once','q':'new overview card','i':'new fine equivalence candidate group','s':'proposed own-source singleton, not proved cross-source unique','?':'explicit unresolved fine identity'}
 return view

def compile_packet(original,stage='proposal',prior=None,derived=None):
 packet,_,_=make_packet(original,derived,stage)
 for key in ['kind','candidateRegionId','graphContextScope','graphContextCoverage','primaryReadingLimit','candidateMembershipStatus']:
  if key in original:packet[key]=original[key]
 if prior is not None:
  # Validate a frozen proposal against its own input, before translating aliases.
  proposal,_,_=make_packet(original,None,'proposal');validate(proposal,prior)
  aliases={'r':'r'}
  aliases.update({c['id']:f'p{n}' for n,c in enumerate(prior['cards'])})
  aliases.update({f['id']:f'pf{n}' for n,f in enumerate(prior['factors'])})
  aliases.update({g['id']:f'pi{n}' for n,g in enumerate(prior['identityGroups'])})
  packet['priorCards']=[]
  for c in prior['cards']:
   row=copy.deepcopy(c);row['originalId']=c['id'];row['id']=aliases[c['id']];packet['priorCards'].append(row)
   packet['refRegistry'][row['id']]={'kind':'prior_question','sourceId':c['id']}
  # Reuse the existing assessment schema for an explicit broad-scope decision.
  region=copy.deepcopy(prior['region']);region.update(id='r',originalId='r',kind='region',refs=[],methods=[],aliases=[])
  packet['priorCards'].append(region);packet['refRegistry']['r']={'kind':'prior_region','sourceId':'r'}
  packet['priorRegion']=copy.deepcopy(prior['region'])
  packet['priorFactors']=[dict(copy.deepcopy(f),id=aliases[f['id']]) for f in prior['factors']]
  packet['priorGroups']=[dict(copy.deepcopy(g),id=aliases[g['id']],memberIndices=[a['i'] for a in prior['units'] if a['identity']==g['id']]) for g in prior['identityGroups']]
  packet['priorAssignments']=[]
  for a in prior['units']:
   row=copy.deepcopy(a);row['q']=[dict(q,id=aliases[q['id']]) for q in a['q']];row['f']=[aliases[f] for f in a['f']];row['identity']=aliases.get(a['identity'],a['identity']);packet['priorAssignments'].append(row)
  packet['priorLinks']=[dict(copy.deepcopy(l),source=aliases.get(l['source'],l['source']),target=aliases.get(l['target'],l['target'])) for l in prior['links']]
  packet['priorVerdict']=prior['verdict'];packet['priorSummary']=prior['summary']
  packet['priorWarnings']=['Prior output is a proposal, not an accepted atlas. Independently reread every supplied description and pertinent excerpt.','Assess r once in cardReviews for the prior broad family, separately from each overview card. Reuse supported scopes; any new or rewritten scope remains a candidate.','Compare exact q-role pairs, factors, disposition and fine identity to priorAssignments. same means those fields agree, not merely a similar broad topic.','A singleton preserves a distinct source statement but is not proof of unique canonical identity. Prior equivalence groups require independent groupReviews.','Fine resolution is not capped by the overview-card count. Every unit needs a meaningful authored short title and explicit singleton/group/unresolved identity state.']
 if derived is not None and packet.get('priorRegion'):
  region=copy.deepcopy(packet['priorRegion']);region.pop('originalVerdict',None);region.update(id='r',originalId='r',kind='region',refs=[],methods=[],aliases=[])
  packet['priorCards'].append(region);packet['refRegistry']['r']={'kind':'prior_region','sourceId':'r'}
 return packet,model_view(packet)

def assignment_comparison(packet,reply):
 prior={a['i']:a for a in packet.get('priorAssignments',[]) if 'q' in a}
 checks=[]
 for row in reply['units']:
  old=prior.get(row['i']);differences=[]
  if old:
   if sorted((q['id'],q['role']) for q in row['q'])!=sorted((q['id'],q['role']) for q in old['q']):differences.append('card_contributions')
   if set(row['f'])!=set(old['f']):differences.append('factor_assignments')
   if row['d']!=old['d']:differences.append('disposition')
   if row['identity']!=old['identity']:differences.append('fine_identity')
  checks.append({'i':row['i'],'declared':row['a'],'comparable':old is not None,'differences':differences,'matches':old is not None and not differences})
 return checks

def main():
 request=json.loads(Path(sys.argv[1]).read_text());original=json.loads(Path(request['originalPacketPath']).read_text());assert hfile(request['originalPacketPath'])==request['originalPacketSha256']
 prior=json.loads(Path(request['priorReplyPath']).read_text()) if request.get('priorReplyPath') else None
 derived=json.loads(Path(request['derivedReviewPath']).read_text()) if request.get('derivedReviewPath') else None
 packet,view=compile_packet(original,request['stage'],prior,derived)
 dump(sys.argv[2],packet);Path(sys.argv[3]).write_text(Path(request['instructionsPath']).read_text()+'\n\nEXACT COMPACT SOURCE PACKET\n'+json.dumps(view,ensure_ascii=False,separators=(',',':'))+'\n')
if __name__=='__main__':main()
