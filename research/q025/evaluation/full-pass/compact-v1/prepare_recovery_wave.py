"""Prepare seven diverse compact reviews from pinned calibration work; launch nothing."""
import json,shutil
from pathlib import Path
from compact_pipeline import compile_packet,dump,hfile
B=Path(__file__).resolve().parent;E=B.parent.parent;L=B.parent/'native-local/compact-v1';R=E/'recovery'
def main():
 if (L/'campaign.json').exists():raise SystemExit('Prepared campaign exists; preserve lineage.')
 families=[('effective-actions-vacua','challenge'),('gauge-geometry-anomaly','challenge'),('axions','challenge'),('inflation-dynamics','challenge'),('distance-emergence','proposal'),('neutrinos','proposal'),('scattering-positivity','proposal')]
 # Source family names are verified against actual prepared job directories, never guessed.
 jobs=[];stats=[];instruction=(B/'COMPACT-INSTRUCTIONS.md').read_text()
 for family,stage in families:
  origin=E/'next-wave/native-local/jobs'/f'{family}-proposal';source=origin/'packet.json'
  if not source.exists():raise SystemExit(f'Missing source packet {source}')
  derived=R/'native-local/derived'/f'{family}-proposal'/'derived.json' if stage=='challenge' else None
  packet,view=compile_packet(json.loads(source.read_text()),stage,derived=json.loads(derived.read_text()) if derived else None)
  jid=f'{family}-compact-{stage}';d=L/'jobs'/jid;dump(d/'packet.json',packet)
  prompt=instruction+'\n\nEXACT COMPACT SOURCE PACKET\n'+json.dumps(view,ensure_ascii=False,separators=(',',':'))+'\n';(d/'prompt-base.txt').write_text(prompt)
  req={'schemaVersion':'q025-compact-native-request/1','jobId':jid,'familyId':family,'stage':stage,'model':'gpt-6-astra','effort':'xhigh','sandbox':'read-only','sourceOnly':True,'timeoutSeconds':1800,'maxOutputCharacters':120000,'packetSha256':hfile(d/'packet.json'),'promptBaseSha256':hfile(d/'prompt-base.txt'),'schemaSha256':hfile(R/'compact.schema.json'),'dependsOn':None,'originalPacketPath':str(source.relative_to(E)),'originalPacketSha256':hfile(source)}
  if derived:req.update(derivedReviewPath=str(derived.relative_to(E)),derivedReviewSha256=hfile(derived),originalFailedReceiptSha256=hfile(origin/'receipt.json'))
  dump(d/'request.json',req);jobs.append({'jobId':jid,'dependsOn':None,'requestSha256':hfile(d/'request.json')})
  stats.append({'jobId':jid,'stage':stage,'unitCount':len(packet['units']),'primaryUnitCount':sum(bool(u['primaryRefs']) for u in packet['units']),'priorCards':len(packet['priorCards']),'priorRecordedUnits':len(packet['priorAssignments']),'promptCharacters':len(prompt),'estimatedCombinedTokens':(len(prompt)+len((R/'compact.schema.json').read_text())+120000+2)//3+16000,'sourcePacketSha256':hfile(source)})
 assert max(x['estimatedCombinedTokens'] for x in stats)<220000
 source=json.loads((R/'recovery-manifest.json').read_text());campaign={'schemaVersion':'q025-compact-bounded-campaign/1','status':'prepared_not_authorized_to_launch','jobs':jobs,'model':'gpt-6-astra','effort':'xhigh','maxAuthorizedConcurrency':8,'sourceRowsSha256':source['sourceRowsSha256'],'inputManifestSha256':source['inputManifestSha256'],'foundationManifestSha256':source['foundationManifestSha256'],'validatorSha256':hfile(R/'compact_contract.py'),'schemaSha256':hfile(R/'compact.schema.json'),'instructionsSha256':hfile(B/'COMPACT-INSTRUCTIONS.md'),'compilerSha256':hfile(B/'compact_pipeline.py'),'priorReviewStatus':'Four recovered prior proposals remain failed originals; distance has no retained answer, inflation lacks per-unit records. No semantic admission from original verdicts.','nativeLaunches':0}
 dump(L/'campaign.json',campaign);dump(L/'control.json',{'enabled':False,'maxActive':4,'maxStartsPerMinute':6,'minStartIntervalMs':5000,'stopWhenComplete':True});shutil.copyfile(R/'native-local/execution.json',L/'execution.json');shutil.copyfile(R/'compact.schema.json',L/'review-schema.json')
 manifest={**campaign,'campaignSha256':hfile(L/'campaign.json'),'runnerSha256':hfile(B/'runner.mjs'),'packets':stats,'launchGate':'Root must inspect the first compact KK challenge and explicitly launch this lineage. No original queue resumes.'};dump(B/'campaign-manifest.json',manifest);print(json.dumps({'preparedJobs':len(jobs),'units':sum(x['unitCount'] for x in stats),'maxEstimatedCombinedTokens':max(x['estimatedCombinedTokens'] for x in stats),'nativeLaunches':0},indent=2))
if __name__=='__main__':main()
