"""Continue disjoint pending work while adopting four existing source reviews by receipt."""
import json,shutil,sys
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent;C=F/'compact-v1';sys.path.insert(0,str(C));from compact_pipeline import dump,hfile
L=F/'native-local/full-leaf-wave-v3';OLD=F/'native-local/full-leaf-wave-v2'
if (L/'campaign.json').exists():raise SystemExit('Continuation already prepared; no implicit overwrite.')
prior=json.loads((OLD/'campaign.json').read_text());state=json.loads((OLD/'state.json').read_text());imports={j for j,s in state['jobs'].items() if s['status']!='pending' and j.endswith('-proposal')};assert len(imports)==4,imports
old_instructions=(C/'PRODUCTION-INSTRUCTIONS.md').read_text();new_instructions=(B/'INSTRUCTIONS.md').read_text();jobs=[]
for job in prior['jobs']:
 jid=job['jobId'];source=OLD/'jobs'/jid;d=L/'jobs'/jid;req=json.loads((source/'request.json').read_text())
 if not job['dependsOn']:
  d.mkdir(parents=True,exist_ok=True);shutil.copyfile(source/'packet.json',d/'packet.json');text=(source/'prompt-base.txt').read_text();assert text.startswith(old_instructions);(d/'prompt-base.txt').write_text(new_instructions+text[len(old_instructions):]);req['promptBaseSha256']=hfile(d/'prompt-base.txt')
 else:req.update(compilerSha256=hfile(C/'production_pipeline.py'),instructionsSha256=hfile(B/'INSTRUCTIONS.md'))
 if jid in imports:req['executionMode']='external_import_only';req['importedRequestWasNotExecutedHere']=True
 dump(d/'request.json',req);entry={**job,'requestSha256':hfile(d/'request.json')}
 if jid in imports:entry.update(importFrom=str(source.relative_to(E)),importRequestSha256=hfile(source/'request.json'))
 jobs.append(entry)
campaign={**prior,'schemaVersion':'q025-compact-production-continuation/3','jobs':jobs,'validatorSha256':hfile(B/'contract.py'),'baseNormalizerSha256':hfile(C/'production_contract.py'),'instructionsSha256':hfile(B/'INSTRUCTIONS.md'),'continuationOfCampaignSha256':hfile(OLD/'campaign.json'),'importedProposalCount':4,'nativeProposalCount':182,'nativeChallengeCount':186,'representationPolicy':'Preserve factor revision/context conversions and additionally map not_compared to initial ONLY for proposals with empty prior assignments; preserve exact original/derived trace. Imported native failures remain failures in their original lineage.'};dump(L/'campaign.json',campaign)
for name in ['execution.json','review-schema.json']:shutil.copyfile(OLD/name,L/name)
dump(L/'control.json',{'enabled':False,'maxActive':8,'maxStartsPerMinute':6,'minStartIntervalMs':5000,'stopWhenComplete':True,'quotaResumeAcknowledgement':None,'validationResumeAcknowledgement':None})
public={**campaign,'campaignSha256':hfile(L/'campaign.json'),'runnerSha256':hfile(B/'runner.mjs'),'coverage':{'eligibleUniqueQuestionUnits':8430,'reservedUnreviewedQuestionUnits':43,'totalQuestionUnits':8473},'nativeLaunches':0,'globalConcurrencyAtPreparation':{'thisCampaignInitialCap':8,'externalActiveOrImportable':4,'maximumInitialCombined':12},'launchGate':'Root launch; four imported reviews are never re-run. Each validated proposal immediately enables its independent challenge.'};dump(B/'manifest.json',public);print(json.dumps({'jobs':len(jobs),'imports':sorted(imports),'nativeCallsPrepared':368,'nativeLaunches':0},indent=2))
