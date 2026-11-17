#!/usr/bin/env python3
"""QA16: exact reviewed source endpoints follow through the existing controller."""
import argparse,hashlib,json,os,select,subprocess,tempfile,time,shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

def main():
 p=argparse.ArgumentParser();p.add_argument('--project',required=True);p.add_argument('--output',required=True);p.add_argument('--node',default='node');args=p.parse_args()
 if not os.environ.get('SLURM_JOB_ID'):raise SystemExit('Browser QA requires authorized isolated Slurm.')
 root=Path(args.project).resolve();out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=True);private=Path(tempfile.mkdtemp(prefix='q025-source-endpoint-'));connection=private/'connection.json';server=mcp=None;token='';seq=0
 atlas=root/'data/atlas/q025-source-endpoint-qa/2026-11-17-protocol-v1';manifest=json.loads((atlas/'manifest.json').read_text());report={'kind':'q025-exact-source-endpoint-browser','scope':'Isolated Slurm Chromium; protocol destination and exact recorded source-method relations. Scripted MCP/browser proof, not independent agent routing or complete scientific acceptance.','manifestSha256':hashlib.sha256((atlas/'manifest.json').read_bytes()).hexdigest(),'checks':[],'passed':False}
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
  conn=json.loads(connection.read_text());token=conn['token'];mcp=subprocess.Popen([args.node,str(root/'bin/mcp-navigator.mjs'),'--connection',str(connection)],cwd=root,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);rpc('initialize',{'protocolVersion':'2025-06-18','clientInfo':{'name':'qa17','version':'1'}})
  with sync_playwright() as pw:
   browser=pw.chromium.launch(headless=True);context=browser.new_context(viewport={'width':1180,'height':900});page=context.new_page();report['browserVersion']=browser.version;report['pageErrors']=[];page.on('pageerror',lambda e:report['pageErrors'].append(str(e)))
   page.goto(conn['url']+'#token='+token,wait_until='domcontentloaded');page.wait_for_function("window.eigenquestionsNavigator.read().mode==='local-companion'")
   cases=json.loads((atlas/'fixture-cases.json').read_text());case=cases[0];parent=state();assert parent['revision']==0;physical=parent['state']['selector'];physical_state_id=parent['state']['id']
   # The agent reads a real relation page, then submits one of its exact actions.
   page_result=call('navigator_context',{'unitId':case['originUnitId'],'section':'relations'});assert not page_result['isError'];routes=page_result['structuredContent']['sourceRoutes']['items'];route=next(r for r in routes if r['relationId']==case['relationId']);target=next(e for e in route['endpoints'] if e['side']=='target')['choices'][0]['action']
   first=call('navigator_navigate',{**target,'expectedRevision':parent['revision']});assert not first['isError'];first=first['structuredContent'];render(page,1,first['state']['id']);assert first['state']['selector']==physical and first['state']['workRelation']=='either';assert first['view']['atlas']['membershipCount']==0
   page.wait_for_selector('#source-inspection-panel');assert page.evaluate('document.documentElement.dataset.sourceObjectId')==case['targetObjectId'];assert page.locator('#current-question').inner_text()==parent['view']['atlas']['destination']['title']
   passed('MCP follows the exact reviewed target method with unchanged physical selector, membership and USING',revision=1,relationId=case['relationId'],sourceObjectId=case['targetObjectId'])
   # Open the target context and follow its recorded source endpoint in the UI.
   disclosure=page.locator('#source-inspection-panel > details.source-scientific-context');disclosure.locator(':scope > summary').click();button=disclosure.get_by_role('button',name='Inspect source method · 2309.16542',include_hidden=True).first
   try:button.wait_for(state='attached')
   except Exception:
    report['failurePanelText']=page.locator('#source-inspection-panel').inner_text()[:12000];page.screenshot(path=str(out/'failure-panel.png'),full_page=True);raise
   button.evaluate('(button)=>{let p=button.parentElement;while(p){if(p.tagName==="DETAILS")p.open=true;p=p.parentElement;}}');button.click();page.wait_for_function('id=>document.documentElement.dataset.sourceObjectId===id',arg=case['sourceObjectId'])
   second=state();render(page,2,second['state']['id']);inspection=second['view']['atlas']['sourceInspection'];assert second['state']['selector']==physical;assert inspection['endpointSide']=='source' and inspection['relation']['source']==case['sourceObjectId'] and inspection['relation']['target']==case['targetObjectId'];assert inspection['relation']['premises'];passed('Browser follows the source endpoint without reversing the original relation or changing the physics destination',revision=2)
   page.screenshot(path=str(out/'source-endpoint-desktop.png'),full_page=True)
   stale=call('navigator_navigate',{**target,'expectedRevision':1});assert stale['isError'] and stale['structuredContent']['code']=='revision_conflict';assert state()['revision']==2
   back=call('navigator_navigate',{'type':'back','expectedRevision':2})['structuredContent'];render(page,3,back['state']['id']);assert back['state']['sourceInspection']['objectId']==case['targetObjectId']
   replay=call('navigator_navigate',{'type':'replay','index':2,'expectedRevision':3})['structuredContent'];render(page,4,replay['state']['id']);assert replay['state']['sourceInspection']['objectId']==case['sourceObjectId'];passed('Back/replay restore exact source inspections and a stale inspection cannot replace the browser state',revision=4)
   page.set_viewport_size({'width':390,'height':844});page.locator('#source-inspection-panel').scroll_into_view_if_needed();assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');page.screenshot(path=str(out/'source-endpoint-mobile.png'),full_page=True);passed('Focused source inspection has no horizontal overflow at 390 pixels')
   exported=call('navigator_export')['structuredContent'];closed=call('navigator_navigate',{'type':'close-source','expectedRevision':4})['structuredContent'];render(page,5,closed['state']['id']);assert closed['state']['id']==physical_state_id and 'sourceInspection' not in closed['state']
   restored=call('navigator_import',{'payload':exported,'expectedRevision':5})['structuredContent'];render(page,6,restored['state']['id']);assert restored['state']['sourceInspection']['objectId']==case['sourceObjectId'];passed('Closing inspection restores the exact original view; session import restores the focused source',revision=6)
   report['screenshots']=['source-endpoint-desktop.png','source-endpoint-mobile.png'];assert not report['pageErrors'];report['passed']=True;browser.close()
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
