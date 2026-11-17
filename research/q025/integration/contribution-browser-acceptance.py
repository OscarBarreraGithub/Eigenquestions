#!/usr/bin/env python3
"""QA11: synthetic contribution-only destination, isolated authorized Slurm only."""
import argparse, hashlib, json, os, select, shutil, subprocess, tempfile, time
from pathlib import Path
from playwright.sync_api import sync_playwright

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--project',required=True);parser.add_argument('--output',required=True);parser.add_argument('--node',default='node');args=parser.parse_args()
    if not os.environ.get('SLURM_JOB_ID'):raise SystemExit('Browser QA requires authorized isolated Slurm.')
    root,output=Path(args.project).resolve(),Path(args.output).resolve();output.mkdir(parents=True,exist_ok=True)
    atlas=root/'data/atlas/q025-contribution-qa/2026-11-17-synthetic-v1';manifest=json.loads((atlas/'manifest.json').read_text());fixture=json.loads((atlas/'qa-fixture.json').read_text())
    temp=Path(tempfile.mkdtemp(prefix='q025-qa11-'));connection=temp/'connection.json';server=mcp=None;token='';seq=0
    report={'kind':'q025-contribution-browser-acceptance','scope':'Isolated Slurm Chromium; synthetic transport fixture, not scientific acceptance or public HTTPS/owner browser evidence.','checks':[],'screenshots':[],'passed':False,'manifestSha256':hashlib.sha256((atlas/'manifest.json').read_bytes()).hexdigest()}
    def passed(name,**fields):report['checks'].append({'name':name,'passed':True,**fields})
    def wait(page,expression,**kwargs):
        report['waitingFor']=expression
        try:page.wait_for_function(expression,**kwargs)
        except Exception:
            report['failurePage']={'url':page.url.split('#')[0],'text':page.locator('body').inner_text(),'state':page.evaluate('({stateId:document.documentElement.dataset.stateId,destinationId:document.documentElement.dataset.destinationId,busy:document.documentElement.dataset.busy})')}
            page.screenshot(path=str(output/'failure.png'),full_page=True);report['screenshots'].append('failure.png');raise

    def message(method,params):
        nonlocal seq
        seq+=1;mcp.stdin.write(json.dumps({'jsonrpc':'2.0','id':seq,'method':method,'params':params})+'\n');mcp.stdin.flush()
        if not select.select([mcp.stdout],[],[],30)[0]:raise RuntimeError('MCP timed out')
        result=json.loads(mcp.stdout.readline());assert not result.get('error'),result.get('error');return result['result']
    def call(name,arguments={}):
        result=message('tools/call',{'name':name,'arguments':arguments});assert not result.get('isError'),name;return result['structuredContent']
    try:
        server=subprocess.Popen([args.node,str(root/'bin/navigate.mjs'),'serve','--atlas',str(atlas),'--port','0','--connection',str(connection)],cwd=root,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        deadline=time.monotonic()+30
        while not connection.exists() and time.monotonic()<deadline:
            if server.poll() is not None:raise RuntimeError('Companion did not start')
            time.sleep(.05)
        conn=json.loads(connection.read_text());token=conn['token'];origin=conn['url'].rstrip('/')
        mcp=subprocess.Popen([args.node,str(root/'bin/mcp-navigator.mjs'),'--connection',str(connection)],cwd=root,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        message('initialize',{'protocolVersion':'2025-06-18','clientInfo':{'name':'qa11','version':'1'}})
        before=call('navigator_state');rows=call('navigator_sources',{'destinationId':'contribution-only','collection':'contributions','limit':2});rest=call('navigator_sources',{'destinationId':'contribution-only','collection':'contributions','offset':2,'limit':2});after=call('navigator_state')
        assert rows['collection']=='contributions' and rows['total']==3 and len(rows['items'])==2 and len(rest['items'])==1
        assert [row['unitId'] for row in rows['items']+rest['items']]==fixture['unitIds'];assert all(row['source']['evidence']['text'] and row['qualification'] and row['evidenceRefs'] for row in rows['items'])
        assert before['revision']==after['revision'] and before['state']==after['state']
        assert call('navigator_sources',{'destinationId':'contribution-only'})['total']==0
        assert call('navigator_sources',{'destinationId':'contribution-only','workRelation':'using'})['total']==0
        assert call('navigator_context',{'unitId':fixture['unitIds'][0]})['page']['returned']==2
        passed('existing MCP source reader pages typed contributions and full excerpts without membership, USING or state mutation',contributions=3,primary=0,using=0)
        with sync_playwright() as playwright:
            browser=playwright.chromium.launch(headless=True);report['browserVersion']=browser.version;context=browser.new_context(viewport={'width':1180,'height':900});page=context.new_page();report['pageErrors']=[]
            page.on('pageerror',lambda error:report['pageErrors'].append(str(error)))
            selector={'kind':'atlas-destination','atlasId':manifest['atlasId'],'atlasVersion':manifest['atlasVersion'],'destinationId':'contribution-only'}
            page.goto(origin+'/#atlas='+manifest['atlasId']+'&version='+manifest['atlasVersion']+'&destination=contribution-only',wait_until='domcontentloaded');wait(page,"document.documentElement.dataset.destinationId==='contribution-only'")
            browser_rows=page.evaluate('async selector=>window.eigenquestionsNavigator.sources(selector,{collection:"contributions",limit:3})',selector)
            assert browser_rows['items']==rows['items']+rest['items'];assert page.evaluate('window.eigenquestionsNavigator.export().snapshot.view.atlas.membershipCount')==0
            disclosure=page.locator('.source-contributions');disclosure.locator(':scope > summary').click();wait(page,"document.querySelector('.source-contributions').textContent.includes('3 of 3 contributions loaded')")
            groups=disclosure.locator(':scope > div > details');assert groups.count()==2
            groups.nth(0).locator(':scope > summary').click();groups.nth(1).locator(':scope > summary').click()
            assert disclosure.get_by_role('heading',name='Method contribution',exact=True).is_visible();assert disclosure.get_by_role('heading',name='Comparison context',exact=True).is_visible();assert disclosure.get_by_role('heading',name='Boundary or limitation',exact=True).is_visible()
            assert disclosure.get_by_text('Synthetic source-specific qualification retained in full; this is not real scientific admission.',exact=True).count()==3
            source_context=disclosure.locator('.source-scientific-context').first;source_context.locator(':scope > summary').click();wait(page,"document.querySelector('.source-contributions .source-scientific-context').textContent.includes('Synthetic full assumption 0')")
            source_context.locator('details > summary').first.click()
            page.screenshot(path=str(output/'contribution-only-desktop.png'),full_page=True);report['screenshots'].append('contribution-only-desktop.png')
            passed('zero-member question visibly retains paper-grouped roles, qualification and lazy exact scientific context',paperGroups=2,sourceContextObjects=2)
            page.set_viewport_size({'width':390,'height':844});report['mobileLayout']=page.evaluate('({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,overflowing:[...document.querySelectorAll("body *")].filter(e=>{const r=e.getBoundingClientRect();return r.width>0&&r.right>innerWidth+1}).slice(0,10).map(e=>({tag:e.tagName,className:e.className,width:e.getBoundingClientRect().width}))})');page.screenshot(path=str(output/'contribution-only-mobile.png'),full_page=True);report['screenshots'].append('contribution-only-mobile.png');assert report['mobileLayout']['scrollWidth']<=report['mobileLayout']['width']+1,report['mobileLayout']
            passed('mobile contribution disclosure has no horizontal overflow')
            inventory=page.locator('#atlas-panel a').filter(has_text='Bibliographic records without source text');assert inventory.count()==1;response=page.request.get(origin+inventory.get_attribute('href'));assert response.ok and response.json()[0]['scientificStatus']=='withdrawn' and response.json()[0]['sourceSha256'] is None
            static=page.request.get(origin+'/atlas/'+manifest['atlasId']+'/'+manifest['atlasVersion']+'/contribution-only.html');assert static.ok;html=static.text();assert 'Source contributions (3)' in html and all(id in html for id in fixture['unitIds']) and 'Archived source locator' in html and 'source-context.json.gz' in html
            passed('ordinary static readers can inspect contributions, locators, optional rich context and unavailable-source inventory')
            page.set_viewport_size({'width':1180,'height':900});page.goto(origin+'/#token='+token,wait_until='domcontentloaded');wait(page,"window.eigenquestionsNavigator.read().mode==='local-companion'")
            result=call('navigator_navigate',{'type':'navigate','selector':selector});expected=result['state']['id'];wait(page,'id=>document.documentElement.dataset.stateId===id',arg=expected)
            ack=False
            for _ in range(80):
                state=call('navigator_state')
                if state['browserStatus']['acknowledgedCurrent']:ack=True;break
                time.sleep(.05)
            assert ack and state['state']['id']==expected;assert len(state['view']['atlas']['destination']['sourceContributions'])==3;assert state['view']['atlas']['membershipCount']==0
            page.locator('.source-contributions > summary').click();wait(page,"document.querySelector('.source-contributions').textContent.includes('3 of 3 contributions loaded')")
            assert page.evaluate('window.eigenquestionsNavigator.read().mode')=='local-companion';page.screenshot(path=str(output/'contribution-only-connected.png'),full_page=True);report['screenshots'].append('contribution-only-connected.png')
            passed('real MCP mutation selects contribution-only lazy question and receives exact browser render acknowledgement',stateId=expected,revision=state['revision'])
            assert not report['pageErrors'];report['passed']=True;browser.close()
    except Exception as error:
        report['error']=str(error).replace(token,'[redacted-session-token]') if token else str(error);raise RuntimeError(report['error']) from None
    finally:
        body=json.dumps(report,indent=2)+'\n';(output/'report.json').write_text(body.replace(token,'[redacted-session-token]') if token else body)
        for process in [mcp,server]:
            if process:
                process.terminate()
                try:process.wait(timeout=5)
                except subprocess.TimeoutExpired:process.kill()
        shutil.rmtree(temp,ignore_errors=True)
if __name__=='__main__':main()
