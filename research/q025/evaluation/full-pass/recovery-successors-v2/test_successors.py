import copy,json,sys,unittest
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;L=F/'native-local/recovery-successors-v2';sys.path.insert(0,str(B));import contract
from prefix import assemble,extract
from materialize import verified_review

class RecoveryTests(unittest.TestCase):
 def setUp(self):
  self.d=L/'adopted/successor-leaf-ce36cae0274019373c8a-proposal';self.packet=json.loads((self.d/'packet.actual.json').read_text());self.reply=json.loads((self.d/'reply.raw.txt').read_text())
 def test_structural_adoption_preserves_all_scientific_content(self):
  out=contract.evaluate(self.packet,self.reply);composite=assemble(self.packet['preservedComponents'],self.reply['remaining']);plain=contract.v1.base.evaluate(self.packet,composite);self.assertEqual(out['normalizedReview'],plain['normalizedReview']);self.assertEqual(len(out['normalizedReview']['units']),51);self.assertEqual(len(out['streamVariantAssessments']),27);self.assertEqual(len(out['structuralVariantEvidence']),3)
  for proof in out['structuralVariantEvidence']:self.assertFalse(proof['primaryReadingClaim']);self.assertEqual(proof['comparedValue'],[]);self.assertTrue(proof['origin']['packetSha256']);self.assertTrue(proof['origin']['prefixSha256'])
 def test_empty_scientific_references_need_exact_structural_proof(self):
  packet=copy.deepcopy(self.packet);packet.pop('structuralVariantEvidence')
  with self.assertRaisesRegex(AssertionError,'structural evidence'):contract.evaluate(packet,self.reply)
  reply=copy.deepcopy(self.reply);next(r for r in reply['variantAssessments'] if r['refs'])['refs']=[]
  with self.assertRaisesRegex(AssertionError,'structural evidence'):contract.evaluate(self.packet,reply)
 def test_structural_absence_does_not_excuse_a_material_scientific_conflict(self):
  reply=copy.deepcopy(self.reply);next(r for r in reply['variantAssessments'] if not r['refs'])['decision']='material_conflict'
  with self.assertRaisesRegex(AssertionError,'structural evidence'):contract.evaluate(self.packet,reply)
 def test_failed_original_and_raw_response_are_unchanged(self):
  review,normal,r=verified_review(self.d);old=F.parent/r['originalJobPath'];self.assertEqual((old/'reply.raw.txt').read_bytes(),(self.d/'reply.raw.txt').read_bytes());self.assertEqual(json.loads((old/'receipt.json').read_text())['status'],'failed');self.assertFalse(r['nativeTurnStartedHere']);self.assertFalse(r['scientificAdmission'])
 def test_partial_first_card_fields_are_locked(self):
  p=json.loads((L/'prefixes/27b96c79f67176367791.json').read_text());self.assertEqual(len(p['lockedValues']),14);self.assertEqual(p['completeArrayPrefixes']['cards'],[]);self.assertEqual(p['streamVariants'],[])
  with self.assertRaises((AssertionError,KeyError,IndexError)):assemble(p,{'cards':[{'id':'q0','title':'Changed scope'}]})
 def test_only_six_blocked_parent_families_are_rewired(self):
  m=json.loads((B/'manifest.json').read_text());self.assertEqual(len(m['jobs']),15);parents=[]
  for j in m['jobs']:
   r=json.loads((L/'jobs'/j['jobId']/'request.json').read_text());self.assertEqual(r['timeoutSeconds'],1800);self.assertEqual(r['maxOutputCharacters'],120000)
   if r['kind']=='parent' and r['stage']=='proposal':parents.append(r['familyId'])
   for dep in r['childDependencies']:
    if dep['reviewKey'] in m['replacements']:self.assertEqual(dep['jobPath'],m['replacements'][dep['reviewKey']])
  self.assertEqual(len(set(parents)),6)
 def test_challenge_sees_structural_evidence_without_new_primary_references(self):
  p=L/'preflight/run-001/jobs/successor2-leaf-ce36cae0274019373c8a-challenge/packet.actual.json';packet=json.loads(p.read_text());self.assertEqual(len(packet['structuralVariantEvidence']),3);self.assertEqual(len(packet['streamVariants']),27)
  for proof in packet['structuralVariantEvidence']:self.assertNotIn(proof['variantRef'],packet['refRegistry']);self.assertFalse(proof['primaryReadingClaim'])
 def test_no_per_string_caps(self):
  def walk(v):
   if isinstance(v,dict):self.assertNotIn('maxLength',v);[walk(x) for x in v.values()]
   elif isinstance(v,list):[walk(x) for x in v]
  walk(contract.regular_schema(True));walk(contract.completion_schema(json.loads((L/'prefixes/27b96c79f67176367791.json').read_text())))
if __name__=='__main__':unittest.main()
