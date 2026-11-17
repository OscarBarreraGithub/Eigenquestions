"""Pin the tested lossless production contract for372 source-only leaf reviews."""
import json,shutil
from pathlib import Path
from compact_pipeline import dump,hfile
from production_pipeline import compile_production
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent;L=F/'native-local/full-leaf-wave-v2';P=F/'native-local/full-leaf-wave-v1';R=E/'recovery'
def main():
 if (L/'campaign.json').exists():raise SystemExit('Production lineage already prepared; preserve bytes.')
 old=json.loads((P/'campaign.json').read_text());jobs=[];stats=[];instructions=(B/'PRODUCTION-INSTRUCTIONS.md').read_text()
 for job in old['jobs']:
  jid=job['jobId'];base=json.loads((P/'jobs'/jid/'request.json').read_text());d=L/'jobs'/jid
  if not job['dependsOn']:
   original=json.loads((E/base['originalPacketPath']).read_text());packet,view=compile_production(original);dump(d/'packet.json',packet);prompt=instructions+'\n\nEXACT COMPACT SOURCE PACKET\n'+json.dumps(view,ensure_ascii=False,separators=(',',':'))+'\n';(d/'prompt-base.txt').write_text(prompt);base.update(packetSha256=hfile(d/'packet.json'),promptBaseSha256=hfile(d/'prompt-base.txt'));stats.append({'jobId':jid,'unitCount':len(packet['units']),'promptCharacters':len(prompt),'estimatedCombinedTokens':(len(prompt)+len((R/'compact.schema.json').read_text())+120000+2)//3+16000})
  else:base.update(compilerSha256=hfile(B/'production_pipeline.py'),instructionsSha256=hfile(B/'PRODUCTION-INSTRUCTIONS.md'))
  dump(d/'request.json',base);jobs.append({**job,'requestSha256':hfile(d/'request.json')})
 campaign={**old,'schemaVersion':'q025-compact-production-campaign/2','jobs':jobs,'validatorSha256':hfile(B/'production_contract.py'),'baseValidatorSha256':hfile(R/'compact_contract.py'),'compilerSha256':hfile(B/'production_pipeline.py'),'baseCompilerSha256':hfile(B/'compact_pipeline.py'),'instructionsSha256':hfile(B/'PRODUCTION-INSTRUCTIONS.md'),'representationPolicy':'Exact duplicate factor declarations reuse prior; changed declarations get new candidate IDs with full trace; cross-unit descriptions retain typed contextual references; no scientific repair or implication.'}
 dump(L/'campaign.json',campaign)
 for name in ['execution.json','review-schema.json']:shutil.copyfile(P/name,L/name)
 dump(L/'control.json',{'enabled':False,'maxActive':4,'maxStartsPerMinute':6,'minStartIntervalMs':5000,'stopWhenComplete':True,'quotaResumeAcknowledgement':None,'validationResumeAcknowledgement':None})
 public={**campaign,'campaignSha256':hfile(L/'campaign.json'),'runnerSha256':hfile(B/'production-runner.mjs'),'coverage':{'eligibleUniqueQuestionUnits':8430,'reservedUnreviewedQuestionUnits':43,'totalQuestionUnits':8473},'proposalPackets':stats,'maxProposalContextEstimate':max(x['estimatedCombinedTokens'] for x in stats),'maxChallengeContextPolicy':'Measure actual compiled prompt including normalized prior and typed comparison context; stop above220k conservative combined estimate, never truncate sources.','launchGate':'Root starts at4 after varied compact validation, may ramp after valid actual proposal/challenge pairs; no native call made by preparation.'};dump(B/'production-wave-manifest.json',public);print(json.dumps({'jobs':len(jobs),'maxProposalContextEstimate':public['maxProposalContextEstimate'],'nativeLaunches':0},indent=2))
if __name__=='__main__':main()
