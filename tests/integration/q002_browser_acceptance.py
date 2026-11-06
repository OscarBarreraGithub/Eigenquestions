#!/usr/bin/env python3
"""Q-002 text navigation/interaction acceptance; run only in authorized Slurm.

Uses real engine/worker/MCP results. Test-only delivery delays expose races without
changing numerical results or production code. No browser security bypasses.
"""
import argparse
import json
import os
from pathlib import Path
import select
import shutil
import subprocess
import tempfile
import time
from urllib.parse import quote
from playwright.sync_api import sync_playwright


INSTRUMENTATION = r"""
(() => {
  const qa = window.__eqQa = {workerDelayMs:0,fetchDelayMs:0,holdWorkerResults:false,heldWorkerResults:[],holdEvents:false,heldEvents:[],holdImports:false,pendingImports:0,releaseImports:[],delayedWorkerResults:0,delayedFetchResponses:0,frames:[],longTasks:[],events:[]};
  qa.releaseWorker=()=>{const work=qa.heldWorkerResults.splice(0);for(const deliver of work)deliver();};
  qa.releaseEvents=()=>{const work=qa.heldEvents.splice(0);for(const deliver of work)deliver();};
  qa.releaseImport=()=>{const work=qa.releaseImports.splice(0);for(const release of work)release();};
  try { new PerformanceObserver(list => {
    for (const item of list.getEntries()) qa.longTasks.push({start:item.startTime,duration:item.duration});
  }).observe({type:'longtask',buffered:true}); } catch {}
  for (const type of ['click','input','change','keydown']) document.addEventListener(type,event=>{
    const target=event.target.closest?.('button,input,select,summary') || event.target;
    const record={type,id:target.id||'',start:performance.now(),busy:document.body?.classList.contains('busy')||false};
    qa.events.push(record);
    requestAnimationFrame(()=>requestAnimationFrame(()=>qa.frames.push({...record,paintOpportunityMs:performance.now()-record.start})));
  },true);
  const NativeWorker=window.Worker;
  window.Worker=class extends EventTarget {
    constructor(...args) {
      super();this.native=new NativeWorker(...args);this.alive=true;
      this.native.addEventListener('message',event=>{
        const delay=event.data?.id ? qa.workerDelayMs : 0;
        const deliver=()=>{if(!this.alive)return;const copy=new MessageEvent('message',{data:event.data});this.dispatchEvent(copy);this.onmessage?.(copy);};
        if(qa.holdWorkerResults&&event.data?.id){qa.delayedWorkerResults++;qa.heldWorkerResults.push(deliver);}
        else if(delay){qa.delayedWorkerResults++;setTimeout(deliver,delay);}else deliver();
      });
      this.native.addEventListener('error',event=>{const copy=new ErrorEvent('error',{message:event.message,filename:event.filename,lineno:event.lineno});this.dispatchEvent(copy);this.onerror?.(copy);});
    }
    postMessage(...args){return this.native.postMessage(...args);}
    terminate(){this.alive=false;return this.native.terminate();}
  };
  const NativeEventSource=window.EventSource;
  window.EventSource=class extends EventTarget {
    constructor(...args){
      super();this.native=new NativeEventSource(...args);this.alive=true;
      this.native.addEventListener('message',event=>{const deliver=()=>{if(!this.alive)return;const copy=new MessageEvent('message',{data:event.data});this.dispatchEvent(copy);this.onmessage?.(copy);};if(qa.holdEvents)qa.heldEvents.push(deliver);else deliver();});
      for(const type of ['open','error'])this.native.addEventListener(type,()=>{const event=new Event(type);this.dispatchEvent(event);this['on'+type]?.(event);});
    }
    get readyState(){return this.native.readyState;}
    close(){this.alive=false;return this.native.close();}
  };
  const originalFetch=window.fetch.bind(window);
  window.fetch=async(...args)=>{
    const url=new URL(args[0] instanceof Request?args[0].url:String(args[0]),location.href);
    if(url.pathname==='/api/import'&&qa.holdImports){qa.pendingImports++;await new Promise(resolve=>qa.releaseImports.push(resolve));}
    const response=await originalFetch(...args);
    if(url.pathname==='/api/action'&&qa.fetchDelayMs){qa.delayedFetchResponses++;await new Promise(resolve=>setTimeout(resolve,qa.fetchDelayMs));}
    return response;
  };
})();
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--node', default='node')
    parser.add_argument('--connection')
    parser.add_argument('--standalone-origin', help='Public origin after release; defaults to local static renderer without attachment')
    args = parser.parse_args()
    if not os.environ.get('SLURM_JOB_ID'):
        raise SystemExit('Run this browser acceptance only in the authorized Slurm environment.')
    root, output = Path(args.project).resolve(), Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    temp = Path(tempfile.mkdtemp(prefix='eigenquestions-q002-'))
    bridge = mcp = None
    report = {'schemaVersion':'1.0.0','request':'Q-002','checks':[], 'performanceScope':'Headless Slurm, no CPU/network throttling; next-frame opportunities are measured, not guaranteed display frames. Real response delivery is delayed only for race checks.'}
    try:
        receipt = Path(args.connection) if args.connection else temp / 'connection.json'
        if not args.connection:
            bridge = subprocess.Popen([args.node,str(root/'bin/navigate.mjs'),'serve','--port','0','--connection',str(receipt)],cwd=root,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True)
            deadline=time.monotonic()+90
            while not receipt.exists() and time.monotonic()<deadline:
                if bridge.poll() is not None: raise RuntimeError('Companion failed to start; inspect stderr privately')
                time.sleep(.1)
            if not receipt.exists(): raise RuntimeError('Companion startup timed out')
        connection=json.loads(receipt.read_text())
        mcp=subprocess.Popen([args.node,str(root/'bin/mcp-navigator.mjs'),'--connection',str(receipt)],cwd=root,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)
        sequence=0
        def rpc(method,params):
            nonlocal sequence
            sequence+=1
            mcp.stdin.write(json.dumps({'jsonrpc':'2.0','id':sequence,'method':method,'params':params})+'\n');mcp.stdin.flush()
            ready,_,_=select.select([mcp.stdout],[],[],90)
            if not ready:raise RuntimeError('MCP response timed out')
            response=json.loads(mcp.stdout.readline())
            if response.get('error'):raise RuntimeError(response['error']['message'])
            return response['result']
        def tool(name,arguments=None):
            result=rpc('tools/call',{'name':name,'arguments':arguments or {}})
            if result.get('isError'):raise RuntimeError(result['content'][0]['text'])
            return result.get('structuredContent') or json.loads(result['content'][0]['text'])
        rpc('initialize',{'protocolVersion':'2025-06-18','clientInfo':{'name':'q002-acceptance','version':'1.0.0'},'capabilities':{}})
        def passed(name,**detail):report['checks'].append({'name':name,'passed':True,**detail})

        with sync_playwright() as playwright:
            browser=playwright.chromium.launch(headless=True)
            report['browserVersion']=browser.version
            context=browser.new_context(viewport={'width':1440,'height':1000},accept_downloads=True)
            context.add_init_script(INSTRUMENTATION)
            page=context.new_page();errors=[]
            page.on('pageerror',lambda error:errors.append(str(error)))
            start=time.monotonic()
            page.goto(args.standalone_origin or connection['url'],wait_until='domcontentloaded')
            page.wait_for_function("document.documentElement.dataset.ready==='true'",timeout=180000)
            report['coldReadySeconds']=round(time.monotonic()-start,3)
            report['styles']=page.evaluate("""() => ({bodyFont:getComputedStyle(document.body).fontFamily,bodyColor:getComputedStyle(document.body).color,bodyBackground:getComputedStyle(document.body).backgroundColor,hardwareConcurrency:navigator.hardwareConcurrency})""")

            def state_id(target=page):return target.locator('html').get_attribute('data-state-id')
            def wait_id(expected,target=page):target.wait_for_function('(id)=>document.documentElement.dataset.stateId===id',arg=expected,timeout=60000)
            def wait_changed(previous,target=page):target.wait_for_function('(id)=>document.documentElement.dataset.stateId!==id',arg=previous,timeout=60000)
            def wait_idle(target=page):target.wait_for_function("!document.body.classList.contains('busy')",timeout=60000)
            def current_directions(target=page):return target.locator('.miller-column[data-current="true"] #directions .direction')
            def export_ui(target=page):
                with target.expect_download() as info:target.locator('#export').click()
                filename=temp/f'export-{time.monotonic_ns()}.json';info.value.save_as(str(filename))
                exported=json.loads(filename.read_text());assert connection['token'] not in json.dumps(exported)
                return exported['session']
            def submit(query,intent='explore',transition='pivot',target=page):
                before=state_id(target)
                target.locator('#question').fill(query);target.locator('#intent').select_option(intent)
                target.locator('#transition').select_option(transition);target.locator('#explore-button').click()
                wait_changed(before,target);wait_idle(target)
                return state_id(target)

            kk=submit('KK towers')
            assert current_directions().count()==5
            assert page.locator('#chartpanel').is_hidden()
            assert page.locator('#reset').is_visible() and 'new path' in page.locator('#reset').inner_text().lower()
            labels_before=current_directions().all_inner_texts()
            source_before=page.locator('.evidence-card').evaluate_all('(nodes)=>nodes.map(n=>n.dataset.sourceId)')
            page.screenshot(path=str(output/'text-primary-desktop.png'),full_page=True)
            page.screenshot(path=str(output/'desktop-viewport.png'),full_page=False)
            passed('text-first default exposes five computed choices and a prominent New path')

            dm=submit('KK towers as dark matter','phenomenology','refine')
            assert current_directions().count()==5 and current_directions().all_inner_texts()!=labels_before
            assert page.locator('.evidence-card').evaluate_all('(nodes)=>nodes.map(n=>n.dataset.sourceId)')!=source_before
            assert page.locator('.miller-column').count()>=2
            dm_session=export_ui();dm_cursor=dm_session['cursor']
            assert dm_session['states'][dm_cursor]['focusIds']
            page.locator('.miller-column[data-current="true"]').scroll_into_view_if_needed()
            page.screenshot(path=str(output/'multicolumn-path-viewport.png'),full_page=False)
            passed('new context changes labels/evidence and appends a navigable column path')

            current_directions().first.click();wait_changed(dm);wait_idle()
            selected=state_id();assert page.locator('.miller-column[data-current="true"]').get_attribute('data-state-id')==selected
            page.locator('#back').click();wait_id(dm);wait_idle()
            passed('human direction click followed by Back restores the exact canonical state')

            # Delay actual worker response delivery so local interactions can be
            # observed during a reproducible wait, independent of fast hardware.
            page.evaluate('window.__eqQa.workerDelayMs=900')
            previous=state_id();page.locator('#question').fill('KK dark matter decay constraints');page.locator('#explore-button').click()
            page.wait_for_function("document.body.classList.contains('busy')")
            assert current_directions().count()==5 and page.locator('.miller-column').count()>=2
            draft='Draft: keep this while results arrive'
            page.locator('#question').fill(draft)
            page.locator('#view-geometry').click();assert page.locator('#chartpanel').is_visible()
            page.locator('#view-sources').click();assert page.locator('#chartpanel').is_hidden()
            wait_changed(previous);wait_idle()
            assert page.locator('#question').input_value()==draft
            assert page.locator('#chartpanel').is_hidden()
            passed('typing and reading tabs stay responsive during delayed compute; result preserves draft and tab')

            # Back means the previous step in the last displayed state, even if
            # another future computation has already started in the worker.
            visible=export_ui();expected_back=visible['states'][visible['cursor']-1]['id']
            page.locator('#question').fill('KK dark matter cosmological bounds');page.locator('#explore-button').click()
            page.wait_for_function("document.body.classList.contains('busy')")
            page.locator('#back').click();wait_id(expected_back);wait_idle();page.wait_for_timeout(1100)
            assert state_id()==expected_back
            passed('Back during computation supersedes the pending result using the displayed path')

            page.locator('#question').fill('KK dark matter production');page.locator('#explore-button').click()
            page.wait_for_function("document.body.classList.contains('busy')")
            page.locator('#reset').click()
            page.wait_for_function("document.activeElement?.id==='question'&&document.querySelector('#question').value===''",timeout=1000)
            wait_idle();page.wait_for_timeout(1100)
            reset=export_ui();active=reset['states'][reset['cursor']]
            assert len(reset['states'])==1 and reset['cursor']==0
            assert active['query']=='' and active['focusIds']==[] and active['constraints']=={'excludeIds':[]}
            assert page.locator('#question').input_value()==''
            assert page.locator('.miller-column').count()<=1
            page.locator('#question').scroll_into_view_if_needed()
            page.screenshot(path=str(output/'new-path-viewport.png'),full_page=False)
            page.evaluate('window.__eqQa.workerDelayMs=0')
            report['delayedWorkerResults']=page.evaluate('window.__eqQa.delayedWorkerResults')
            assert report['delayedWorkerResults']>=3
            passed('New path immediately focuses an empty query and stale computation cannot restore old focus/history')

            submit('black hole evaporation')
            page.locator('#question').fill('black hole information paradox')
            before=state_id();page.locator('#explore-button').dblclick();wait_changed(before);wait_idle()
            rapid=export_ui();assert len([s for s in rapid['states'] if s['query']=='black hole information paradox'])==1
            passed('rapid repeated submit does not create duplicate path entries')

            # Gate A's actual result until B has been submitted; B must refine
            # the last visible state, not inherit the unseen A in worker memory.
            submit('axion weak gravity conjecture')
            base=export_ui();base_id=state_id();base_focus=sorted(page.locator('.evidence-card').evaluate_all('(nodes)=>nodes.slice(0,5).map(n=>n.dataset.sourceId)'))
            page.locator('#transition').select_option('refine')
            page.evaluate('window.__eqQa.holdWorkerResults=true')
            page.locator('#question').fill('axion instanton action');page.locator('#explore-button').click()
            page.wait_for_function('window.__eqQa.heldWorkerResults.length>0')
            assert state_id()==base_id
            page.locator('#question').fill('axion early dark energy');page.locator('#explore-button').click()
            page.evaluate('window.__eqQa.holdWorkerResults=false;window.__eqQa.releaseWorker()')
            page.wait_for_function("document.querySelector('#current-question').textContent==='axion early dark energy'");wait_idle()
            replaced=export_ui();result_state=replaced['states'][replaced['cursor']]
            assert len(replaced['states'])==base['cursor']+2
            assert all(state['query']!='axion instanton action' for state in replaced['states'])
            assert result_state['focusIds']==base_focus
            passed('latest submit replaces unseen queued question without contaminating history or scientific focus')

            # Warm presentation-only work: no worker delay or numerical request.
            page.evaluate('window.__eqQa.frames=[];window.__eqQa.longTasks=[]')
            for _ in range(5):
                page.locator('#view-geometry').click();page.locator('#view-sources').click()
            page.locator('#question').fill('A responsive draft')
            page.wait_for_timeout(150)
            measurements=page.evaluate('({frames:window.__eqQa.frames,longTasks:window.__eqQa.longTasks})')
            timings=sorted(x['paintOpportunityMs'] for x in measurements['frames'] if x['id'] in ('view-sources','view-geometry','question'))
            assert timings
            p95=timings[min(len(timings)-1,int(.95*(len(timings)-1)))]
            maximum_long_task=max((x['duration'] for x in measurements['longTasks']),default=0)
            report['warmLocalInteraction']={'samples':len(timings),'medianPaintOpportunityMs':round(timings[len(timings)//2],2),'p95PaintOpportunityMs':round(p95,2),'maxLongTaskMs':round(maximum_long_task,2),'longTaskCount':len(measurements['longTasks'])}
            assert p95<250 and maximum_long_task<250
            passed('warm local input/tab work stays below measured 250ms acceptance ceilings; not a 60fps guarantee')

            # Attach while an old standalone result is held. Transport generation
            # must protect the agent's state when that real worker result arrives.
            connected=context.new_page();connected.on('pageerror',lambda error:errors.append(str(error)))
            connected.goto(connection['url'],wait_until='domcontentloaded')
            connected.wait_for_function("document.documentElement.dataset.ready==='true'",timeout=180000)
            connected.evaluate('window.__eqQa.holdWorkerResults=true')
            connected.locator('#question').fill('old standalone KK tower request');connected.locator('#explore-button').click()
            connected.wait_for_function('window.__eqQa.heldWorkerResults.length>0')
            attached=tool('navigator_navigate',{'type':'navigate','query':'black hole evaporation'})
            connected.locator('#agent-open').click();connected.locator('#agent-dialog details summary').click()
            connected.locator('#bridge-origin').fill(connection['url']);connected.locator('#bridge-token').fill(connection['token'])
            connected.locator('#bridge-form button[type="submit"]').click()
            connected.wait_for_function("document.querySelector('#connection-status').textContent.includes('Agent connected')")
            wait_id(attached['state']['id'],connected)
            connected.locator('#bridge-token').fill('');connected.locator('#agent-close').click()
            connected.evaluate('window.__eqQa.holdWorkerResults=false;window.__eqQa.releaseWorker()')
            connected.wait_for_timeout(150)
            assert state_id(connected)==attached['state']['id']
            passed('transport generation suppresses a delayed standalone worker response after agent attachment')

            # Same companion and real MCP tools, now viewed as text columns.
            observed=tool('navigator_navigate',{'type':'navigate','query':'KK towers'})
            wait_id(observed['state']['id'],connected)
            assert current_directions(connected).evaluate_all('(nodes)=>nodes.map(n=>n.dataset.directionId)')==[d['id'] for d in observed['view']['directions']]
            connected.locator('#question').fill('A draft during external agent updates')
            newer=tool('navigator_navigate',{'type':'refine','query':'KK towers as dark matter','intent':'phenomenology'})
            wait_id(newer['state']['id'],connected)
            assert connected.locator('#question').input_value()=='A draft during external agent updates'
            connected.locator('#reset').click();wait_idle(connected)
            connected.wait_for_function("document.querySelector('#question').value===''")
            empty=tool('navigator_export')['session'];empty_state=empty['states'][empty['cursor']]
            assert len(empty['states'])==1 and empty_state['query']=='' and not empty_state['focusIds']
            assert 'Agent connected' in connected.locator('#connection-status').inner_text()
            assert current_directions(connected).count()==0
            after_reset=tool('navigator_navigate',{'type':'navigate','query':'black hole evaporation'})
            wait_id(after_reset['state']['id'],connected)
            passed('MCP and Miller columns agree; external update preserves draft; New path clears shared session but keeps attachment')

            # An old POST response must not replace a later real MCP/SSE revision.
            connected.evaluate('window.__eqQa.fetchDelayMs=1000')
            connected.locator('#question').fill('black hole information');connected.locator('#explore-button').click()
            connected.wait_for_function("document.body.classList.contains('busy')")
            external=tool('navigator_navigate',{'type':'pivot','query':'axion weak gravity conjecture'})
            wait_id(external['state']['id'],connected);connected.wait_for_timeout(1200);wait_idle(connected)
            assert state_id(connected)==external['state']['id']
            connected.evaluate('window.__eqQa.fetchDelayMs=0')
            report['delayedBridgeResponses']=connected.evaluate('window.__eqQa.delayedFetchResponses')
            assert report['delayedBridgeResponses']>=1
            passed('delayed old bridge response cannot overwrite a newer MCP/SSE revision')

            # Hold a real UI rebase before it sends; an external MCP mutation
            # commits between the UI's revision decision and guarded import.
            baseline=tool('navigator_navigate',{'type':'pivot','query':'KK towers'});wait_id(baseline['state']['id'],connected)
            connected.evaluate('window.__eqQa.holdEvents=true;window.__eqQa.holdImports=true;window.__eqQa.fetchDelayMs=700')
            connected.locator('#question').fill('KK tower derivation');connected.locator('#transition').select_option('refine');connected.locator('#explore-button').click()
            connected.wait_for_function('window.__eqQa.heldEvents.length>0')
            assert state_id(connected)==baseline['state']['id']
            conflict_draft='KK towers as dark matter'
            connected.locator('#question').fill(conflict_draft);connected.locator('#explore-button').click()
            connected.wait_for_function('window.__eqQa.pendingImports>0',timeout=10000)
            intervening=tool('navigator_navigate',{'type':'pivot','query':'black hole information paradox'})
            connected.evaluate('window.__eqQa.holdImports=false;window.__eqQa.releaseImport()')
            wait_id(intervening['state']['id'],connected);wait_idle(connected)
            connected.evaluate('window.__eqQa.holdEvents=false;window.__eqQa.releaseEvents();window.__eqQa.fetchDelayMs=0')
            connected.wait_for_timeout(100)
            assert state_id(connected)==intervening['state']['id']
            assert tool('navigator_state')['state']['id']==intervening['state']['id']
            assert connected.locator('#question').input_value()==conflict_draft
            conflict_status=connected.locator('#status').inner_text()
            assert any(word in conflict_status.lower() for word in ('conflict','newer','changed','updated'))
            passed('atomic revision guard preserves intervening MCP state and the UI draft during a rebase conflict',status=conflict_status)
            external=intervening

            connected.reload(wait_until='domcontentloaded');wait_id(external['state']['id'],connected)
            connected.wait_for_function("document.querySelector('#connection-status').textContent.includes('Agent connected')")
            deadline=time.monotonic()+10
            while not tool('navigator_state')['browserStatus']['acknowledgedCurrent'] and time.monotonic()<deadline:connected.wait_for_timeout(100)
            assert tool('navigator_state')['browserStatus']['acknowledgedCurrent']
            passed('attachment reload and exact rendered-state acknowledgement survive the new layout')

            page.set_viewport_size({'width':1024,'height':900});page.locator('#view-sources').click()
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            page.locator('.miller-column[data-current="true"]').scroll_into_view_if_needed()
            page.screenshot(path=str(output/'narrow-desktop-viewport.png'),full_page=False)
            page.set_viewport_size({'width':390,'height':844})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            controls=page.locator('#reset,#explore-button,#view-sources,#view-geometry,.miller-column[data-current="true"] .direction')
            small=[]
            for index in range(controls.count()):
                control=controls.nth(index)
                if not control.is_visible():continue
                box=control.bounding_box()
                if box['height']<43:small.append({'id':control.get_attribute('id'),'height':round(box['height'],2)})
            assert not small
            page.locator('#reset').focus();page.keyboard.press('Enter')
            page.wait_for_function("document.activeElement?.id==='question'&&document.querySelector('#question').value===''")
            wait_idle();page.locator('#question').fill('axions');before=state_id();page.keyboard.press('Enter');wait_changed(before);wait_idle()
            assert current_directions().count()==5
            page.screenshot(path=str(output/'text-primary-mobile.png'),full_page=True)
            page.locator('.miller-column[data-current="true"]').scroll_into_view_if_needed();page.screenshot(path=str(output/'mobile-column-viewport.png'),full_page=False)
            passed('mobile primary controls have 44px-scale hit areas and keyboard New path/Enter navigation works')
            page.set_viewport_size({'width':320,'height':740})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            assert current_directions().count()==5 and page.locator('#reset').is_visible()
            page.locator('.miller-column[data-current="true"]').scroll_into_view_if_needed();page.screenshot(path=str(output/'narrow-mobile-viewport.png'),full_page=False)
            passed('1024px, 390px and 320px layouts contain horizontal scrolling within navigation strips')
            report['pageErrors']=errors;assert not errors
            browser.close()
        report['passed']=True
    except Exception as error:
        report['passed']=False;report['failureType']=type(error).__name__
        raise
    finally:
        (output/'q002-browser-acceptance.json').write_text(json.dumps(report,indent=2)+'\n')
        for process in (mcp,bridge):
            if process:
                process.terminate()
                try:process.wait(timeout=10)
                except subprocess.TimeoutExpired:process.kill()
        shutil.rmtree(temp,ignore_errors=True)


if __name__=='__main__':main()
