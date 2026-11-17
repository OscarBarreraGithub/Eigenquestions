"""Production wrapper retains typed comparison context through independent stages."""
import json,sys
from pathlib import Path
from compact_pipeline import compile_packet,model_view,dump,hfile

def compile_production(original,stage='proposal',prior=None,prior_derivation=None):
 packet,view=compile_packet(original,stage,prior=prior)
 if prior_derivation:
  assert prior_derivation['normalizedReview']==prior,'Prior derivation/reply mismatch'
  packet['priorCrossUnitDescriptionContext']=prior_derivation['crossUnitDescriptionContext']
  packet['priorFactorRevisionTrace']=[{k:v for k,v in x.items() if k not in ['originalDefinition','outputDefinition']} for x in prior_derivation['factorTransformations']]
 view=model_view(packet);view['referenceRules']['d']='exact supplied description; own row implicit, other-unit citations remain explicitly comparison/context and never certify own primary reading'
 return packet,view
if __name__=='__main__':
 req=json.loads(Path(sys.argv[1]).read_text());assert hfile(req['originalPacketPath'])==req['originalPacketSha256'];original=json.loads(Path(req['originalPacketPath']).read_text());prior=json.loads(Path(req['priorReplyPath']).read_text()) if req.get('priorReplyPath') else None;derivation=json.loads(Path(req['priorNormalizationPath']).read_text()) if req.get('priorNormalizationPath') else None
 packet,view=compile_production(original,req['stage'],prior,derivation);dump(sys.argv[2],packet);Path(sys.argv[3]).write_text(Path(req['instructionsPath']).read_text()+'\n\nEXACT COMPACT SOURCE PACKET\n'+json.dumps(view,ensure_ascii=False,separators=(',',':'))+'\n')
