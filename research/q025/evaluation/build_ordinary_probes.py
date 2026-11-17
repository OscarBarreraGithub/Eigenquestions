#!/usr/bin/env python3
import json,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=Path('/Users/emmy/Developer/physics-atlas-swampland')
P=ROOT/'graph-design/20261105-v1/publication-v1/coarse/reviews'
reviews={}
for f in P.glob('*.json'):
 x=json.loads(f.read_text());reviews[x['topic_id']]=(f,x)
specs=[
('O01','topic-q-c226794ed837','How do I get from a compactification ansatz to an effective action, then test whether it actually admits a controlled stable vacuum?',['effective action is not vacuum existence','escaping a sufficient tachyon criterion is not full stability','flux/source constraints and control regimes remain visible']),
('O02','topic-q-c226794ed837','At an infinite-distance limit, how can I tell decompactification from an emergent string, and what can BPS indices or couplings test?',['decompactification versus emergent-string target','5D asymptotics versus 4D rigid-limit gauge scale','reported tested examples versus universal theorem']),
('O03','topic-q-c226794ed837','How do anomaly conditions compare with geometric realizability of a gauge sector in string compactification?',['anomaly-compatible matter is not automatically geometrically tunable','global anomaly cancellation versus local gauge enhancement','geometry and effective action are useful cross-links']),
('O04','topic-q-311aeb08af0a','I want to understand how an inflationary model connects its potential and field trajectory to observables, reheating, and quantum-gravity consistency.',['phenomenological potential versus derived compactification','slow-roll predictions versus reheating history','observational fit versus conjectural consistency']),
('O05','topic-m-e48813698aab','For several axions, how do I identify the physical light direction and decide whether integrating out the heavier fields is justified?',['canonical kinetic normalization versus unnormalized coordinate range','mass eigenvectors versus assumed light direction','hierarchy and validity of truncation']),
('O06','topic-q-c19465f2ae8b','Which distinct mechanisms generate neutrino masses, and how can extra dimensions or quantum-gravity arguments constrain them?',['model mechanism versus conditional exclusion','Dirac/Majorana and dimensional assumptions','experimental targets and model-dependent couplings']),
('O07','topic-m-8c8c725baad2','How are scattering dispersion relations used to constrain effective interactions when gravity is present, and which assumptions complicate positivity?',['subtraction/analyticity conditions','massless gravitational exchange and infrared treatment','factorization versus positivity']),
('O08','topic-q-c9647665e1ab','How does a boundary description account for bulk gravity and black-hole information, and where do AdS and de Sitter constructions differ?',['AdS versus proposed dS dictionary','information counting versus dynamical consistency','boundary unitarity versus an imported conjecture'])]
out=[]
for cid,tid,prompt,dist in specs:
 f,x=reviews[tid];c=x['challenge']
 samples=[]
 for s in x['samples']:
  samples.append(dict(unitId=s['organization_unit_id'],paperId=s['paper_id'],role=s['role'],question=s['description'],nodeId=s['node_id'],sourceSha256=s['source_sha256'],evidenceIds=[a['evidence_id'] for a in s['anchors']],sourceUrls=[a['source_url'] for a in s['anchors']],readingScope=s['source_context_scope']))
 out.append(dict(id=cid,topicId=tid,prompt=prompt,requiredDistinctions=dist,reviewedTitle=c['title'],sourceBackedScope=c['summary'],scopeLimits=c['assumptions_and_regimes'],sampledDistinctions=c['important_distinctions'],samples=samples,reviewPath=str(f.relative_to(ROOT)),reviewSha256=hashlib.sha256(f.read_bytes()).hexdigest(),status='development_probe_from_existing_sampled_review; not complete_region_gold',acceptance=['A fresh reader can describe the current question and predict what each next direction offers','Central evidence fits stated scope; boundary evidence has an explicit reason to include, overlap, split, or exclude','Omitted/outside evidence remains reachable when relevant and is not silently used as a positive member','At least two successive moves add scientific specificity without merely renaming the same evidence','Source conditions remain local to the claim or model; no paper-specific static regime is made universal']))
(HERE/'ordinary-exploration.json').write_text(json.dumps(dict(schemaVersion='q025-ordinary-exploration/1',purpose='Broad reading/coherence probes. Existing assignments are sampling metadata, never gold truth. Ordinary exploration complements the 12 fine boundary cases.',cases=out),indent=2)+'\n')
print('wrote',len(out),'ordinary probes')
