#!/usr/bin/env python3
"""Final public-origin acceptance, run only in an authorized isolated Slurm job.

No browser security flags, request interception or proxying. Default and explicitly
scoped simulated-consent cases run separately; neither operates the owner browser.
The local --atlas must be the exact accepted package deployed at the public URL.
This is a prepared test harness until a successful executed receipt exists.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import select
import shutil
import subprocess
import tempfile
import time
from urllib.parse import quote, urlparse
from playwright.sync_api import sync_playwright


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--project',required=True)
    parser.add_argument('--atlas',required=True)
    parser.add_argument('--destination',required=True)
    parser.add_argument('--output',required=True)
    parser.add_argument('--public-origin',default='https://eigenquestions.com')
    parser.add_argument('--node',default='node')
    parser.add_argument('--permission-mode',choices=['default','consent'],default='default')
    args=parser.parse_args()
    if not os.environ.get('SLURM_JOB_ID'):raise SystemExit('Run public browser acceptance only in authorized Slurm.')
    if args.public_origin!='https://eigenquestions.com':raise SystemExit('This receipt is specifically for the authorized public origin.')
    root,atlas,output=Path(args.project).resolve(),Path(args.atlas).resolve(),Path(args.output).resolve()
    output.mkdir(parents=True,exist_ok=True)
    manifest_bytes=(atlas/'manifest.json').read_bytes();manifest=json.loads(manifest_bytes)
    selector={'kind':'atlas-destination','atlasId':manifest['atlasId'],'atlasVersion':manifest['atlasVersion'],'destinationId':args.destination}
    base='/data/atlas/'+quote(manifest['atlasId'],safe='')+'/'+quote(manifest['atlasVersion'],safe='')
    temp=Path(tempfile.mkdtemp(prefix='q025-public-bridge-'));connection=temp/'connection.json'
    server=mcp=None;token='';seq=0
    report={'kind':'q025-public-origin-bridge-acceptance','scope':'Isolated Slurm Chromium at real public HTTPS origin; not the owner Chrome. Exact accepted package, normal browser security. Permission mode is recorded separately; a scoped API grant simulates consent, not a native prompt click.','publicOrigin':args.public_origin,'permissionMode':args.permission_mode,'selector':selector,'localManifestSha256':hashlib.sha256(manifest_bytes).hexdigest(),'checks':[],'screenshots':[],'passed':False}
    def passed(name,**fields):report['checks'].append({'name':name,'passed':True,**fields})
    def rpc(name,arguments):
        nonlocal seq
        seq+=1;mcp.stdin.write(json.dumps({'jsonrpc':'2.0','id':seq,'method':'tools/call','params':{'name':name,'arguments':arguments}})+'\n');mcp.stdin.flush()
        if not select.select([mcp.stdout],[],[],45)[0]:raise RuntimeError('MCP response timed out')
        response=json.loads(mcp.stdout.readline())
        if response.get('error') or response.get('result',{}).get('isError'):raise RuntimeError('MCP operation failed: '+name)
        return response['result']['structuredContent']
    try:
        server=subprocess.Popen([args.node,str(root/'bin/navigate.mjs'),'serve','--atlas',str(atlas),'--port','0','--connection',str(connection)],cwd=root,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        deadline=time.monotonic()+45
        while not connection.exists() and time.monotonic()<deadline:
            if server.poll() is not None:raise RuntimeError('Local companion failed to start')
            time.sleep(.05)
        if not connection.exists():raise RuntimeError('Local companion startup timed out')
        conn=json.loads(connection.read_text());token=conn['token']
        mcp=subprocess.Popen([args.node,str(root/'bin/mcp-navigator.mjs'),'--connection',str(connection)],cwd=root,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        mcp.stdin.write(json.dumps({'jsonrpc':'2.0','id':0,'method':'initialize','params':{'protocolVersion':'2025-06-18','clientInfo':{'name':'q025-public-origin-acceptance','version':'1'}}})+'\n');mcp.stdin.flush()
        if not select.select([mcp.stdout],[],[],30)[0]:raise RuntimeError('MCP initialization timed out')
        if json.loads(mcp.stdout.readline()).get('error'):raise RuntimeError('MCP initialization failed')
        with sync_playwright() as playwright:
            browser=playwright.chromium.launch(headless=True)
            report['browserVersion']=browser.version
            context=browser.new_context(viewport={'width':1180,'height':900})
            context.add_init_script("window.__longTasks=[];try{new PerformanceObserver(list=>{for(const e of list.getEntries())window.__longTasks.push({start:e.startTime,duration:e.duration})}).observe({type:'longtask',buffered:true})}catch{}")
            page=context.new_page();report['pageErrors']=[]
            page.on('pageerror',lambda error:report['pageErrors'].append(str(error)))
            route=args.public_origin+'/#atlas='+quote(selector['atlasId'])+'&version='+quote(selector['atlasVersion'])+'&destination='+quote(args.destination)
            page.goto(route,wait_until='networkidle');page.wait_for_function('id=>document.documentElement.dataset.destinationId===id',arg=args.destination)
            response=page.request.get(args.public_origin+base+'/manifest.json');assert response.ok
            assert hashlib.sha256(response.body()).hexdigest()==report['localManifestSha256']
            prepared=page.evaluate('window.eigenquestionsNavigator.export()');prepared_state=prepared['snapshot']['view']['stateId']
            assert prepared['snapshot']['view']['atlas']['selector']==selector
            passed('public compact URL independently renders exact pinned accepted destination without upload',stateId=prepared_state)
            page.screenshot(path=str(output/'public-prepared-destination.png'),full_page=True);report['screenshots'].append('public-prepared-destination.png')
            permission_states="async()=>{const out={};for(const name of ['local-network-access','local-network','loopback-network']){try{out[name]=(await navigator.permissions.query({name})).state}catch(error){out[name]='unsupported'}}return out}"
            report['permissionStatesBefore']=page.evaluate(permission_states)
            report['consentSimulation']={'enabled':args.permission_mode=='consent','origin':args.public_origin,'permission':'local-network-access','mechanism':'Playwright BrowserContext.grant_permissions with exact origin in a fresh nonpersistent context','nativePromptClickDemonstrated':False,'ownerBrowserModified':False}
            if args.permission_mode=='consent':
                context.grant_permissions(['local-network-access'],origin=args.public_origin)
            report['permissionStatesAfter']=page.evaluate(permission_states)
            if args.permission_mode=='consent':
                effective=report['permissionStatesAfter'].get('loopback-network');effective=report['permissionStatesAfter'].get('local-network-access') if effective=='unsupported' else effective
                assert effective=='granted','The normal scoped permission grant did not grant loopback access in this browser.'
            page.locator('#agent-open').click();page.locator('#agent-dialog details>summary').first.click();page.locator('#bridge-origin').fill(conn['url']);page.locator('#bridge-token').fill(token);page.locator('#bridge-form button[type=submit]').click()
            try:page.wait_for_function("window.eigenquestionsNavigator.read().mode==='local-companion'",timeout=30000)
            except Exception:
                report['connectionOutcome']={'connected':False,'message':page.locator('#bridge-message').inner_text(),'status':page.locator('#connection-status').inner_text(),'consentSimulated':args.permission_mode=='consent','note':'This recorded permission case did not complete public-to-loopback attachment. Inspect its actual network/permission message; the compact prepared URL already worked independently.'}
                page.locator('#bridge-token').fill('');page.screenshot(path=str(output/'public-connection-unavailable.png'),full_page=True);report['screenshots'].append('public-connection-unavailable.png')
                raise RuntimeError('Public-origin connection did not complete under the recorded permission policy')
            page.locator('#bridge-token').fill('');page.locator('#agent-close').click()
            rpc('navigator_navigate',{'type':'navigate','selector':selector})
            page.wait_for_function('id=>document.documentElement.dataset.stateId===id',arg=prepared_state)
            acknowledged=False
            for _ in range(80):
                state=rpc('navigator_state',{})
                if state['browserStatus']['acknowledgedCurrent']:acknowledged=True;break
                time.sleep(.05)
            assert acknowledged and state['state']['id']==prepared_state
            assert page.evaluate('window.eigenquestionsNavigator.read().mode')=='local-companion'
            passed('actual public HTTPS origin accepts local stdio MCP update through SSE and acknowledges exact rendered state',stateId=prepared_state,consentSimulated=args.permission_mode=='consent')
            agent_sources=rpc('navigator_sources',{'destinationId':args.destination,'limit':5})
            browser_sources=page.evaluate('async selector=>window.eigenquestionsNavigator.sources(selector,{limit:5})',selector)
            ids=[row['unitId'] for row in agent_sources['items']]
            assert ids and ids==[row['unitId'] for row in browser_sources['items']]
            context_page=page.evaluate('async ({id,selector})=>window.eigenquestionsNavigator.context(id,selector)',{'id':ids[0],'selector':selector})
            assert context_page['availability']=='available' and context_page['page']['returned']<=20
            static=page.request.get(args.public_origin+'/atlas/'+quote(selector['atlasId'])+'/'+quote(selector['atlasVersion'])+'/'+quote(args.destination)+'.html')
            assert static.ok and ids[0] in static.text()
            passed('public static source discovery and lazy context agree with the connected agent',sourceIds=ids,contextAvailability=context_page['availability'])
            report['performance']=page.evaluate("({sampleMs:performance.now(),longTasks:window.__longTasks,paint:performance.getEntriesByType('paint').map(e=>({name:e.name,at:e.startTime})),resources:performance.getEntriesByType('resource').map(e=>({origin:new URL(e.name).origin,path:new URL(e.name).pathname,transferSize:e.transferSize,decodedBodySize:e.decodedBodySize}))})")
            assert not report['pageErrors'],report['pageErrors']
            page.screenshot(path=str(output/'public-mcp-connected.png'),full_page=True);report['screenshots'].append('public-mcp-connected.png')
            report['passed']=True;browser.close()
    except Exception as error:
        report['error']=str(error).replace(token,'[redacted-session-token]') if token else str(error)
        raise RuntimeError(report['error']) from None
    finally:
        body=json.dumps(report,indent=2)+'\n'
        if token:body=body.replace(token,'[redacted-session-token]')
        (output/'report.json').write_text(body)
        for process in [mcp,server]:
            if process:
                process.terminate()
                try:process.wait(timeout=5)
                except subprocess.TimeoutExpired:process.kill()
        shutil.rmtree(temp,ignore_errors=True)


if __name__=='__main__':main()
