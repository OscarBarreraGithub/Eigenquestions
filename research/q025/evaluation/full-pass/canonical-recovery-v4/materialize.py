import copy,hashlib,json,sys
from pathlib import Path
from extract import model_components
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
def materialize(request_path,runtime):
 d=Path(request_path).resolve().parent;req=json.loads(Path(request_path).read_text());assert not(d/'dispatch-request.json').exists(),'Already materialized; no retry'
 for pin in req['recoveryPins']:assert sha(E/pin['path'])==pin['sha256'],'Frozen recovery input changed'
 source=E/req['originalPacketPath'];assert sha(source)==req['originalPacketSha256'];packet=json.loads(source.read_text());p=E/req['componentsPath'];assert sha(p)==req['componentsSha256'];packet['preservedChallenge']=json.loads(p.read_text());packet['preservedChallengeArtifactSha256']=sha(p)
 view={k:copy.deepcopy(v)for k,v in packet.items()if k not in ['sourceReviews','refRegistry','preservedChallenge']}
 # Full reference metadata and full prior ledgers stay in the hashed validator
 # packet. The narrow task needs exact prior definitions and reading limits, not
 # another copy of already challenged reverse source-role/compound tables.
 view['refRegistry']={k:({'kind':'description','unitId':v['unitId'],'paperId':v['paperId']}if v['kind']=='description'else {'kind':'primary','sourceId':v['sourceId'],'paperId':v['paperId'],'pdfPage':v['sourceContext']['pdfPage'],'scope':v['sourceContext']['scope'],'quoteExactInPage':v['sourceContext']['quoteExactInPage']})for k,v in packet['refRegistry'].items()}
 view['priorReview']={k:copy.deepcopy(packet['priorReview'][k])for k in ['version','familyId','stage','summary','newQuestions','decisions','limitations','unresolved']}
 view['priorReviewProjectionNotice']='Exact prior definitions, decisions, limitations and unresolved items retained for narrow variant review. Previously challenged role/compound/pair/disposition ledgers remain pinned in the complete validation packet; no source or scientific record is deleted.'
 view['preservedChallenge']=model_components(packet['preservedChallenge'])
 # Redundant hashes/range metadata are host receipts; scientific values and exact
 # variant/path identifiers remain in the source-only prompt.
 for row in view['preservedChallenge']['attemptVariants']:row.pop('alternateValueSha256',None);row.pop('alternatePath',None)
 dump(d/'packet.actual.json',packet);instructions=(B/'INSTRUCTIONS.md').read_text();assert instructions.count('{{MAX_OUTPUT_CHARACTERS}}')==1;instructions=instructions.replace('{{MAX_OUTPUT_CHARACTERS}}',str(req['maxOutputCharacters']));(d/'prompt-base.actual.txt').write_text(instructions+'\n\nEXACT MISSING-FIELD AND VARIANT PACKET\n'+json.dumps(view,ensure_ascii=False,separators=(',',':'))+'\n')
 actual={**req,'baseRequestSha256':sha(request_path),'packetSha256':sha(d/'packet.actual.json'),'promptBaseSha256':sha(d/'prompt-base.actual.txt')};dump(d/'dispatch-request.json',actual);return actual
if __name__=='__main__':print(json.dumps({'materialized':materialize(sys.argv[1],sys.argv[2])['jobId']}))
