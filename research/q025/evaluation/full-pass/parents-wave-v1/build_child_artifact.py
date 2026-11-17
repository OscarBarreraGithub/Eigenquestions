"""Preserve reusable parent question frontiers and inherited evidence status."""
import importlib.util,json,sys
from pathlib import Path
B=Path(__file__).resolve().parent;P=B.parent/'parents-v1';spec=importlib.util.spec_from_file_location('q025_frozen_child_builder',P/'build_child_artifact.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)

def augment_parent_frontier(artifact,packet,reply):
 if packet.get('kind')!='parent':return artifact
 existing={c['id']:c for c in packet.get('existingCards',[])};selected={l['target'] for l in reply['links'] if l['source']=='r' and l['target'] in existing};questions=artifact['questions'];known={q['candidateId'] for q in questions}
 for ref in sorted(selected):
  q=existing[ref]
  if q['candidateId'] in known:continue
  known.add(q['candidateId']);questions.append({'candidateId':q['candidateId'],'localRef':ref,'scopeStatus':q['scopeStatus'],'definition':{k:q[k] for k in ['title','question','summary','scope','readingLimit']},'sourceUnitIds':[packet['refRegistry'][f'u{a["i"]}']['unitId'] for a in reply['units'] if any(x['id']==ref for x in a['q'])],'inherited':True,'primaryReadingClaim':False,'inheritanceBasis':'Exact existing child-question identity selected in parent frontier; original child scope status retained, parent route does not independently certify descendant science.'})
 artifact['reusedQuestionFrontierCount']=len(selected);artifact['inheritedExistingQuestionCount']=len(existing);artifact['parentProposedLinks']=reply['links'];artifact['parentLinkInterpretation']='Unadmitted proposals. Explicit relation decisions distinguish public navigation from review-batch provenance; no textual heuristic creates containment.'
 return artifact

def build(jobdir,region,members):
 d=Path(jobdir);r=json.loads((d/'receipt.json').read_text());assert r['status']=='complete' and not r.get('toolUseAttempted')
 packet_path=d/('packet.actual.json' if (d/'packet.actual.json').exists() else 'packet.json')
 assert base.hfile(d/'reply.raw.txt')==r['replySha256'],'Child raw reply changed'
 if r.get('inputPins',{}).get('packetSha256'):assert base.hfile(packet_path)==r['inputPins']['packetSha256'],'Child source packet changed'
 artifact=base.build(d,region,members);packet=json.loads(packet_path.read_text());reply=json.loads((d/'reply.json').read_text());reviews={a['id']:a for a in reply['cardReviews']};prior={c['id']:c for c in packet['priorCards']}
 # A limitation caveat is not by itself a rewritten scope or an admission.
 for q in artifact['questions']:
  a=reviews.get(q['localRef'])
  if a and a['decision']=='supported_with_limits' and a['scopeChange']=='same':q['scopeStatus']='limits_require_adjudication'
 a=reviews['r']
 if a['decision']=='supported_with_limits' and a['scopeChange']=='same':
  artifact['scopeStatus']='limits_require_adjudication';artifact['region']={k:prior['r'][k] for k in ['title','question','summary','scope','readingLimit']};artifact['scopeCandidateId']=base.content_id('region',artifact['region'])
 return augment_parent_frontier(artifact,packet,reply)
