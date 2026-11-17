"""Compact model view plus exact external reference registry; original source packet stays pinned."""
import hashlib,json
from pathlib import Path
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def scope(s):return {'systems':s.get('physicalSystems',s.get('systems',[])),'targets':s.get('targets',[]),'regimes':s.get('regimes',[]),'assumptions':s.get('assumptions',[]),'conventions':s.get('conventions',[]),'includes':s.get('includes',[]),'excludes':s.get('excludes',[])}
def make_packet(original,derived=None,stage='challenge'):
 registry={};alias={};units=[]
 for u in original['units']:
  i=u['unitIndex'];registry[f'd{i}']={'kind':'description','unitIndex':i,'unitId':u['unitId'],'textSha256':hashlib.sha256(u['description'].encode()).hexdigest()};registry[f'u{i}']={'kind':'source_unit','unitIndex':i,'unitId':u['unitId']};alias[f'/units/{i}/description']=alias[f'unitIndex:{i}']=alias[f'd{i}']=f'd{i}';alias[f'/units/{i}']=f'u{i}'
 for n,e in enumerate(original['evidence']):
  ref=f'e{n}';alias[e['id']]=ref;registry[ref]={'kind':'primary','sourceId':e['id'],'paperId':e['paper_id'],'sourceSha256':e['source_sha256'],'sourceContext':{k:v for k,v in e['sourceContext'].items() if k!='text'}}
 object_by_id={o['id']:o for o in original['sourceObjects']}
 for u in original['units']:
  for n,kind in zip(u['sourceNodeIds'],u.get('sourceNodeKinds',[])):
   object_by_id.setdefault(n,{'id':n,'kind':kind,'paperId':u['paperId'],'text':u['description'],'evidenceIds':u['sourceEvidenceIds'],'evidenceScope':'retrieval_facet_description_for_parent_node; full source object not separately supplied'})
 for n,(oid,o) in enumerate(sorted(object_by_id.items())):
  ref=f'o{n}';alias[oid]=ref;registry[ref]={'kind':'source_object','sourceId':oid,'objectKind':o['kind'],'paperId':o.get('paperId')}
 for n,e in enumerate(original['sourceRelations']):
  ref=f'g{n}';alias[e['id']]=ref;registry[ref]={'kind':'source_relation','sourceId':e['id'],'source':e['source'],'target':e['target'],'semanticStatus':e['semanticStatus'],'directUnitIndices':e['directUnitIndices']}
 def refs(ids):return list(dict.fromkeys(alias[x] for x in ids if x in alias))
 for u in original['units']:
  units.append({'i':u['unitIndex'],'descriptionRef':f'd{u["unitIndex"]}','sourceRef':f'u{u["unitIndex"]}','paperId':u['paperId'],'description':u['description'],'primaryRefs':refs(u['sourceEvidenceIds']),'sourceObjectRefs':[alias[n] for n in u['sourceNodeIds'] if n in alias],'selectionRole':u.get('selectionRole','member_description')})
 evidence=[{'ref':alias[e['id']],'paperId':e['paper_id'],'page':e['sourceContext']['pdfPage'],'text':e['sourceContext']['text'],'readingScope':e['sourceContext'].get('scope','Bounded original text; no complete paper or image verification.')} for e in original['evidence']]
 objects=[{'ref':alias[oid],'kind':o['kind'],'paperId':o.get('paperId'),'text':o.get('text',''),'evidenceRefs':refs(o.get('evidenceIds',[])),'omittedEvidenceCount':sum(x not in alias for x in o.get('evidenceIds',[])),'scope':o.get('evidenceScope')} for oid,o in sorted(object_by_id.items())]
 relations=[{'ref':alias[e['id']],'source':alias[e['source']],'target':alias[e['target']],'type':e['type'],'semanticStatus':e['semanticStatus'],'unitIndices':e['directUnitIndices'],'primaryRefs':refs(e.get('evidenceIds',[]))} for e in original['sourceRelations']]
 existing=[]
 for n,c in enumerate(original.get('existingQuestionCandidates',[])):
  ref=f'x{n}';alias[c['id']]=ref;existing.append({'id':ref,'title':c.get('title',''),'question':c.get('question',''),'scope':c.get('scope',{}),'status':'existing_draft_not_accepted_identity'});registry[ref]={'kind':'existing_question','sourceId':c['id']}
 priorcards=[];priorfactors=[];priorrows=[];priorwarnings=[];priorregion=None
 if derived:
  r=derived['normalizedReview'];priorregion={'title':r['regionCard']['title'],'question':r['regionCard']['question'],'summary':r['regionCard']['summary'],'scope':scope(r['regionCard']['scope']),'readingLimit':r['regionCard']['readingLimit'],'originalVerdict':r['verdict']}
  for n,c in enumerate(r['questionCards']):
   ref=f'p{n}';alias[c['localId']]=ref;priorcards.append({'id':ref,'originalId':c['localId'],'title':c['title'],'question':c['question'],'summary':c['summary'],'scope':scope(c['scope']),'methods':c['methods'],'refs':refs(c['evidenceIds']),'readingLimit':c['readingLimit'],'scientificStatus':c['scientificStatus']});registry[ref]={'kind':'prior_question','sourceId':c['localId']}
  for n,f in enumerate(r['factorDictionary']):
   ref=f'pf{n}';alias[f['id']]=ref;priorfactors.append({'id':ref,'kind':f['kind'],'label':f['label'],'status':'historical_or_rejected' if f['status']=='unsupported' else 'uncertain' if f['status']=='uncertain_reading' else 'scope_candidate','qualification':f['uncertainty'],'refs':refs([x['id'] for x in f['evidenceRefs']])})
  for a in r['unitAssessments']:
   priorrows.append({'i':a['unitIndex'],'overviewRefs':[alias[q] for q in a['questionRefs'] if q in alias and alias[q].startswith(('p','x'))],'sourceFacetRefs':[alias[q] for q in a['questionRefs'] if q in alias and alias[q].startswith(('u','o'))],'factors':refs(a['factorRefs']),'disposition':a['disposition'],'basis':a['basis'],'note':a['note'],'alternateHome':a['alternateHome']})
  if len(priorrows)!=len(units):priorwarnings.append(f'Prior output provided{len(priorrows)} of{len(units)} unit assessments. Claimed coverage was not established; independently provide all rows now.')
  priorwarnings+=['Original native receipt failed. Reference formats are deterministically resolved in a derived artifact; failure/status is preserved.','Source-facet references are context access, not authored canonical questions.','Unknown-role and reverse membership lists were inconsistent/redundant; derive them from the new authoritative unit mapping.','Historical/rejected factors remain visible context and must never become asserted premises.','Prior overview cards do not cap fine scientific resolution. Give every unit an explicit fine singleton/group/unresolved state.']
 packet={'version':'q025-compact-packet/1','familyId':original['familyId'],'stage':stage,'units':units,'evidence':evidence,'objects':objects,'relations':relations,'refRegistry':registry,'existingCards':existing,'priorCards':priorcards,'priorFactors':priorfactors,'priorGroups':[],'priorAssignments':priorrows,'priorRegion':priorregion,'priorWarnings':priorwarnings,'reservedUnreviewedCount':original['reservedUnreviewedCount'],'originalPacketStatus':'Numerical memberships are candidates; scientific source objects are extraction context unless independently stated otherwise.','sourceOnly':True}
 view={k:v for k,v in packet.items() if k!='refRegistry'};view['referenceRules']={'d':'exact unit description; whole description is implicit for its own unit row','u':'source-facet access only, never a canonical question ID','e':'supplied primary excerpt','o':'exact source object context','g':'exact source-object relation, not necessarily a question premise','p':'previous proposed overview card, must be assessed once','x':'existing candidate question, optional separate assessment','pf':'previous factor definition, reusable with its explicit status','q':'new overview card you author','i':'new fine equivalence-candidate group you author','s':'unit-row fine identity value: proposed singleton using that exact unit statement','?':'unit-row fine identity value: unresolved; explain briefly','r':'current broad family'}
 return packet,view,alias
