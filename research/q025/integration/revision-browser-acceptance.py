#!/usr/bin/env python3
"""QA15: captured agent revision survives the real MCP/CLI/browser boundary."""
import argparse,hashlib,json,os,select,subprocess,tempfile,time,shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

def main():
 p=argparse.ArgumentParser();p.add_argument('--project',required=True);p.add_argument('--output',required=True);p.add_argument('--node',default='node');args=p.parse_args()
 if not os.environ.get('SLURM_JOB_ID'):raise SystemExit('Browser QA requires authorized isolated Slurm.')
 root=Path(args.project).resolve();out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=True);private=Path(tempfile.mkdtemp(prefix='q025-revision-'));connection=private/'connection.json';server=mcp=None;token='';seq=0
 atlas=root/'data/atlas/q025-contribution-qa/2026-11-17-synthetic-v1';manifest=json.loads((atlas/'manifest.json').read_text());report={'kind':'q025-captured-revision-browser','scope':'Isolated Slurm Chromium; synthetic transport fixture. Scripted CLI/MCP protocol proof, not independent agent routing or scientific acceptance.','manifestSha256':hashlib.sha256((atlas/'manifest.json').read_bytes()).hexdigest(),'checks':[],'passed':False}
 def rpc(method,params):
  nonlocal seq
  seq+=1;mcp.stdin.write(json.dumps({'jsonrpc':'2.0','id':seq,'method':method,'params':params})+'\n');mcp.stdin.flush()
  if not select.select([mcp.stdout],[],[],30)[0]:raise RuntimeError('MCP timeout')
  value=json.loads(mcp.stdout.readline());assert not value.get('error'),value.get('error');return value['result']
 def call(name,args={}):return rpc('tools/call',{'name':name,'arguments':args})
 def state():
  value=call('navigator_state');assert not value['isError'];return value['structuredContent']
 def render(page,revision,state_id):
  page.wait_for_function('id=>document.documentElement.dataset.stateId===id',arg=state_id)
  for _ in range(100):
   current=state()
   if current['revision']==revision and current['browserStatus']['acknowledgedCurrent']:return current
   time.sleep(.05)
  raise AssertionError('No exact browser render acknowledgement')
 def passed(name,**fields):report['checks'].append({'name':name,'passed':True,**fields})
 try:
  server=subprocess.Popen([args.node,str(root/'bin/navigate.mjs'),'serve','--atlas',str(atlas),'--port','0','--connection',str(connection)],cwd=root,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
  deadline=time.monotonic()+30
  while not connection.exists() and time.monotonic()<deadline:
   if server.poll() is not None:raise RuntimeError('Companion failed to start')
   time.sleep(.05)
  conn=json.loads(connection.read_text());token=conn['token'];mcp=subprocess.Popen([args.node,str(root/'bin/mcp-navigator.mjs'),'--connection',str(connection)],cwd=root,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);rpc('initialize',{'protocolVersion':'2025-06-18','clientInfo':{'name':'qa15','version':'1'}})
  with sync_playwright() as pw:
   browser=pw.chromium.launch(headless=True);context=browser.new_context(viewport={'width':1180,'height':900});page=context.new_page();report['browserVersion']=browser.version;report['pageErrors']=[];page.on('pageerror',lambda e:report['pageErrors'].append(str(e)))
   page.goto(conn['url']+'#token='+token,wait_until='domcontentloaded');page.wait_for_function("window.eigenquestionsNavigator.read().mode==='local-companion'")
   parent=state();assert parent['revision']==0;selector={'kind':'atlas-destination','atlasId':manifest['atlasId'],'atlasVersion':manifest['atlasVersion'],'destinationId':'contribution-only'}
   proposed={'type':'navigate','selector':selector,'expectedRevision':parent['revision']};first=call('navigator_navigate',proposed);assert not first['isError'];first=first['structuredContent'];render(page,1,first['state']['id']);passed('MCP captured revision zero commits and receives exact browser render acknowledgement',revision=1)
   exported=call('navigator_export')['structuredContent'];draft_file=private/'draft.json';draft_file.write_text(json.dumps(exported));draft_sha=hashlib.sha256(draft_file.read_bytes()).hexdigest();captured=state()['revision']
   # A distinct browser-originating request commits while the agent retains its
   # earlier parent. The agent proposal below must not overwrite this newer view.
   page.evaluate("async selector=>{const api=window.eigenquestionsNavigator,parent=api.read();await api.navigate({type:'navigate',selector},{expectedRevision:parent.revision});}",{**selector,'destinationId':'root'})
   newer=state();assert newer['revision']==2;render(page,2,newer['state']['id'])
   stale=call('navigator_navigate',{'type':'navigate','selector':selector,'expectedRevision':captured});assert stale['isError'] and stale['structuredContent']['code']=='revision_conflict';assert stale['structuredContent']['current']['state']['id']==newer['state']['id']
   stale_import=call('navigator_import',{'payload':exported,'expectedRevision':captured});assert stale_import['isError'] and stale_import['structuredContent']['current']['revision']==2
   cli=subprocess.run([args.node,str(root/'bin/navigate.mjs'),'import','--file',str(draft_file),'--connection',str(connection),'--expected-revision',str(captured)],text=True,capture_output=True,timeout=30);assert cli.returncode==1 and json.loads(cli.stderr)['code']=='revision_conflict';assert hashlib.sha256(draft_file.read_bytes()).hexdigest()==draft_sha
   unchanged=state();assert unchanged['revision']==2 and unchanged['state']['id']==newer['state']['id'];assert page.evaluate('document.documentElement.dataset.stateId')==newer['state']['id'];passed('stale MCP action, MCP import and CLI import preserve the newer browser state and original draft',capturedRevision=captured,currentRevision=2)
   # This is a new Back request, not the rejected proposal restamped with 2.
   back=call('navigator_navigate',{'type':'back','expectedRevision':unchanged['revision']});assert not back['isError'];back=back['structuredContent'];render(page,3,back['state']['id']);assert back['state']['id']==first['state']['id'];passed('distinct new guarded Back action renders and acknowledges the preserved prior state',revision=3)
   page.screenshot(path=str(out/'revision-guard-connected.png'),full_page=True);report['screenshots']=['revision-guard-connected.png'];assert not report['pageErrors'];report['passed']=True;browser.close()
 except Exception as e:report['error']=str(e).replace(token,'[redacted-session-token]') if token else str(e);raise RuntimeError(report['error']) from None
 finally:
  text=json.dumps(report,indent=2)+'\n';(out/'report.json').write_text(text.replace(token,'[redacted-session-token]') if token else text)
  for process in [mcp,server]:
   if process:
    process.terminate()
    try:process.wait(timeout=5)
    except subprocess.TimeoutExpired:process.kill()
  shutil.rmtree(private,ignore_errors=True)
if __name__=='__main__':main()
