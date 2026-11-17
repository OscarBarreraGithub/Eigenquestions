#!/usr/bin/env python3
"""Passive isolated browser observer for fresh agents using the existing CLI/bridge."""
import argparse,hashlib,json,os,shutil,subprocess,tempfile,time,urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

def main():
 p=argparse.ArgumentParser()
 for key in ['project','atlas','node','output']:p.add_argument('--'+key,required=True)
 p.add_argument('--minutes',type=int,default=40);p.add_argument('--public-origin');p.add_argument('--permission-mode',choices=['default','consent'],default='default');a=p.parse_args()
 if not os.environ.get('SLURM_JOB_ID'):raise SystemExit('Authorized isolated Slurm only')
 if not 1<=a.minutes<=55:raise SystemExit('Observer must fit the authorized one-hour allocation')
 if a.public_origin not in [None,'https://eigenquestions.com']:raise SystemExit('Only the existing exact public origin is supported')
 root=Path(a.project).resolve();atlas=Path(a.atlas).resolve();out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=True);os.chmod(out,0o700)
 private=Path(tempfile.mkdtemp(prefix='q025-agent-observer-'));connection=private/'connection.json';manifest_bytes=(atlas/'manifest.json').read_bytes();manifest=json.loads(manifest_bytes)
 server=browser=pw=page=None;token='';report={'kind':'independent-agent-browser-observer','scientificPackage':{'atlasId':manifest['atlasId'],'atlasVersion':manifest['atlasVersion'],'manifestSha256':hashlib.sha256(manifest_bytes).hexdigest()},'jobId':os.environ['SLURM_JOB_ID'],'origin':a.public_origin or 'same-origin loopback','permissionMode':a.permission_mode,'observerSendsNavigationCommands':False,'freshAgentTranscriptRequiredSeparately':True,'events':[],'pageErrors':[],'finished':False}
 def save(name,value):
  text=json.dumps(value,ensure_ascii=False,indent=2)+'\n';(out/name).write_text(text.replace(token,'[redacted-session-token]')if token else text)
 def bridge_read():
  with urllib.request.urlopen(urllib.request.Request(conn['url']+'api/session',headers={'Authorization':'Bearer '+token}),timeout=10)as response:return json.load(response)
 try:
  server=subprocess.Popen([a.node,str(root/'bin/navigate.mjs'),'serve','--atlas',str(atlas),'--port','0','--connection',str(connection)],cwd=root,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
  deadline=time.monotonic()+60
  while not connection.exists()and time.monotonic()<deadline:
   if server.poll()is not None:raise RuntimeError('Companion startup failed')
   time.sleep(.05)
  conn=json.loads(connection.read_text());token=conn['token'];pw=sync_playwright().start();browser=pw.chromium.launch(headless=True);report['browserVersion']=browser.version;context=browser.new_context(viewport={'width':1180,'height':900});page=context.new_page();page.on('pageerror',lambda error:report['pageErrors'].append(str(error)));page.set_default_timeout(60000)
  if a.public_origin:
   entry=manifest['entryDestinationId'];from urllib.parse import urlencode,quote
   page.goto(a.public_origin+'/#'+urlencode({'atlas':manifest['atlasId'],'version':manifest['atlasVersion'],'destination':entry}),wait_until='domcontentloaded');page.wait_for_function('id=>document.documentElement.dataset.destinationId===id',arg=entry)
   response=page.request.get(a.public_origin+'/data/atlas/'+quote(manifest['atlasId'])+'/'+quote(manifest['atlasVersion'])+'/manifest.json');assert response.ok and hashlib.sha256(response.body()).hexdigest()==report['scientificPackage']['manifestSha256'],'Public manifest differs from local accepted package'
   if a.permission_mode=='consent':context.grant_permissions(['local-network-access'],origin=a.public_origin)
   report['consentSimulation']={'enabled':a.permission_mode=='consent','mechanism':'Exact-origin Playwright permission grant; not a native prompt click or owner-browser grant.'}
   page.locator('#agent-open').click();page.locator('#agent-dialog details>summary').first.click();page.locator('#bridge-origin').fill(conn['url']);page.locator('#bridge-token').fill(token);page.locator('#bridge-form button[type=submit]').click();page.wait_for_function("window.eigenquestionsNavigator.read().mode==='local-companion'");page.locator('#bridge-token').fill('');page.locator('#agent-close').click()
  else:page.goto(conn['url']+'#token='+token,wait_until='domcontentloaded');page.wait_for_function("window.eigenquestionsNavigator.read().mode==='local-companion'")
  deadline=time.monotonic()+45
  while True:
   initial=bridge_read();initial_read=page.evaluate('window.eigenquestionsNavigator.read()');initial_dom=page.evaluate('document.documentElement.dataset.stateId')
   if initial['browserStatus']['acknowledgedCurrent']and initial_dom==initial['view']['stateId']and initial_read['renderedRevision']==initial_read['revision']:break
   if time.monotonic()>=deadline:raise RuntimeError('Browser did not acknowledge the companion state under the recorded permission policy')
   page.wait_for_timeout(250)
  ready={'jobId':os.environ['SLURM_JOB_ID'],'project':str(root),'node':a.node,'connectionFile':str(connection),'sameOriginStaticBase':conn['url'],'publicOrigin':a.public_origin,'manifestSha256':report['scientificPackage']['manifestSha256'],'initialBridgeRevision':initial['revision'],'initialStateId':initial['view']['stateId'],'noTokenIncluded':True}
  save('agent-run.json',ready);save('ready.json',{'ready':True,'browserAcknowledgedCurrent':True,'observerDoesNotChooseDestinations':True,'manifestSha256':ready['manifestSha256']});end=time.monotonic()+a.minutes*60;last=None;last_event=None;awaiting_ack=True
  while time.monotonic()<end and not(out/'stop.json').exists():
   read=page.evaluate('window.eigenquestionsNavigator.read()');capsule=read.get('capsule');view=capsule['snapshot']['view']if capsule else {};key=(read['revision'],read['renderedRevision'],view.get('stateId'))
   if key!=last or awaiting_ack:
    bridge=bridge_read();ack=bridge['browserStatus']['acknowledgedCurrent'];dom=page.evaluate('document.documentElement.dataset.stateId');event_key=(*key,bridge['revision'],ack,dom);awaiting_ack=not(ack and dom==bridge['view']['stateId']and read['renderedRevision']==read['revision']);last=key
    if event_key!=last_event:
     event={'at':time.time(),'uiRevision':read['revision'],'renderedRevision':read['renderedRevision'],'bridgeRevision':bridge['revision'],'stateId':view.get('stateId'),'domStateId':dom,'selector':view.get('atlas',{}).get('selector'),'title':view.get('atlas',{}).get('destination',{}).get('title'),'browserAcknowledgedCurrent':ack};report['events'].append(event);last_event=event_key
     page.screenshot(path=str(out/('revision-'+str(len(report['events'])).zfill(3)+'.png')),full_page=True);save('observer-report.json',report)
     if len(report['events'])>250:raise RuntimeError('Observer event limit reached; stop rather than silently drop events')
   page.wait_for_timeout(500)
  report['finished']=True;report['stopReason']='root stop marker'if(out/'stop.json').exists()else'observer deadline';save('observer-report.json',report)
 except Exception as error:
  report['error']=str(error).replace(token,'[redacted-session-token]')if token else str(error)
  if page:
   try:
    page.locator('#bridge-token').fill('')if page.locator('#bridge-token').count()else None;page.screenshot(path=str(out/'failure.png'),full_page=True);report['failureBody']=page.locator('body').inner_text()[:12000]
   except Exception:pass
  save('observer-report.json',report);raise RuntimeError(report['error']) from None
 finally:
  if browser:browser.close()
  if pw:pw.stop()
  if server:
   server.terminate()
   try:server.wait(timeout=5)
   except subprocess.TimeoutExpired:server.kill()
  shutil.rmtree(private,ignore_errors=True)
if __name__=='__main__':main()
