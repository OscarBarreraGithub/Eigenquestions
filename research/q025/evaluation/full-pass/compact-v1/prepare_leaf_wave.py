"""Prepare186 proposals plus streaming dependent challenges; launch nothing."""
import json,shutil
from pathlib import Path
from compact_pipeline import dump,hfile
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent;L=F/'native-local/full-leaf-wave-v1';P=F/'native-local/full-leaf-proposals-v1'
def main():
 if (L/'campaign.json').exists():raise SystemExit('Leaf wave exists; preserve lineage.')
 previous=json.loads((P/'campaign.json').read_text());jobs=[]
 for job in previous['jobs']:
  jid=job['jobId'];source=P/'jobs'/jid;d=L/'jobs'/jid;shutil.copytree(source,d);jobs.append(job)
  proposal=json.loads((source/'request.json').read_text());cid=jid.removesuffix('-proposal')+'-challenge';cd=L/'jobs'/cid
  req={k:v for k,v in proposal.items() if k not in ['packetSha256','promptBaseSha256']};req.update(jobId=cid,stage='challenge',dependsOn=jid,inputMaterialization='after_validated_immutable_proposal',compilerSha256=hfile(B/'compact_pipeline.py'),instructionsSha256=hfile(B/'COMPACT-INSTRUCTIONS.md'))
  dump(cd/'request.json',req);jobs.append({'jobId':cid,'dependsOn':jid,'requestSha256':hfile(cd/'request.json')})
 campaign={**previous,'schemaVersion':'q025-compact-dependent-campaign/1','jobs':jobs,'status':'prepared_not_authorized_to_launch','maxAuthorizedConcurrency':24,'challengePolicy':'Compile immediately from each validated frozen proposal and pinned source packet; preserve actual dependency/request hashes before native dispatch. No proposal-level permission or automatic retry.'};dump(L/'campaign.json',campaign)
 for name in ['execution.json','review-schema.json']:shutil.copyfile(P/name,L/name)
 dump(L/'control.json',{'enabled':False,'maxActive':4,'maxStartsPerMinute':6,'minStartIntervalMs':5000,'stopWhenComplete':True})
 public={**campaign,'campaignSha256':hfile(L/'campaign.json'),'runnerSha256':hfile(B/'leaf-wave-runner.mjs'),'sourceProposalManifestSha256':hfile(B/'leaf-proposal-manifest.json'),'coverage':{'eligibleUniqueQuestionUnits':8430,'reservedUnreviewedQuestionUnits':43,'totalQuestionUnits':8473},'launchGate':'Root authorization after varied compact calibration; pending challenged scopes are not automatically accepted.'};dump(B/'leaf-wave-manifest.json',public);print(json.dumps({'preparedJobs':len(jobs),'proposals':186,'dependentChallenges':186,'nativeLaunches':0},indent=2))
if __name__=='__main__':main()
