#!/usr/bin/env python3
"""Frozen full-candidate browser/MCP acceptance core, confined to authorized Slurm."""
import argparse, hashlib, json, os, select, shutil, subprocess, tempfile, time
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    parser = argparse.ArgumentParser()
    for name in ['project', 'output', 'node', 'cases']: parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    if not os.environ.get('SLURM_JOB_ID'): raise SystemExit('Isolated Slurm browser only')
    root, out = Path(args.project).resolve(), Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=True)
    cases_path=Path(args.cases).resolve(); cases=json.loads(cases_path.read_text())
    assert cases['finalAccounting'] is True, 'Bind the final accounted package before this test'
    atlas = root / 'data/atlas' / cases['atlasId'] / cases['atlasVersion']
    private = Path(tempfile.mkdtemp(prefix='q025-final-browser-'))
    connection = private / 'connection.json'
    server = mcp = page = browser = pw = None
    token = ''; seq = 0
    report = {'kind':'q025-full-candidate-browser', 'passed':False, 'partialCandidate':False,
              'casesSha256':hashlib.sha256(cases_path.read_bytes()).hexdigest(),
              'scope':'Exact frozen fully accounted package in isolated Slurm Chromium. Scripted MCP/browser transport; fresh-agent interpretation and public HTTPS remain separate gates.',
              'manifestSha256':hashlib.sha256((atlas/'manifest.json').read_bytes()).hexdigest(), 'checks':[], 'pageErrors':[]}

    assert report['manifestSha256']==cases['manifestSha256'], 'Cases are not bound to this frozen manifest'

    def rpc(method, params):
        nonlocal seq
        seq += 1
        mcp.stdin.write(json.dumps({'jsonrpc':'2.0','id':seq,'method':method,'params':params})+'\n'); mcp.stdin.flush()
        if not select.select([mcp.stdout], [], [], 60)[0]: raise RuntimeError('MCP timeout')
        value=json.loads(mcp.stdout.readline()); assert not value.get('error'), value.get('error')
        return value['result']
    def call(name, arguments=None):
        value=rpc('tools/call', {'name':name,'arguments':arguments or {}})
        assert not value.get('isError'), value
        return value['structuredContent']
    def state(): return call('navigator_state')
    def render(snapshot):
        page.wait_for_function('id=>document.documentElement.dataset.stateId===id',arg=snapshot['state']['id'])
        for _ in range(100):
            current=state()
            if current['revision']==snapshot['revision'] and current['browserStatus']['acknowledgedCurrent']: return current
            time.sleep(.05)
        raise AssertionError('No exact browser render acknowledgement')
    def navigate(destination):
        before=state(); begin=time.monotonic()
        result=call('navigator_navigate',{'type':'navigate','selector':{**before['state']['selector'],'destinationId':destination},'expectedRevision':before['revision']})
        render(result)
        return result, round((time.monotonic()-begin)*1000,2)
    def check(name, **fields): report['checks'].append({'name':name,'passed':True,**fields})
    def menu(snapshot):
        directions=snapshot['view']['directions']; ids=[d['selector']['destinationId']for d in directions]
        assert len(ids)==len(set(ids))
        for d in directions:
            assert d['routeCount']==len(d['relations'])
            assert isinstance(d.get('summary'),str) and isinstance(d.get('query'),str)
        return [{'destinationId':d['selector']['destinationId'],'label':d['label'],'routeCount':d['routeCount']}for d in directions]
    try:
        server=subprocess.Popen([args.node,str(root/'bin/navigate.mjs'),'serve','--atlas',str(atlas),'--port','0','--connection',str(connection)],cwd=root,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        deadline=time.monotonic()+60
        while not connection.exists() and time.monotonic()<deadline:
            if server.poll() is not None: raise RuntimeError('Companion failed to start: '+server.stderr.read().decode()[:1000])
            time.sleep(.05)
        conn=json.loads(connection.read_text()); token=conn['token']
        index=json.loads((root/'dist/data/atlas/index.json').read_text()); assert index['home']=={'atlasId':cases['atlasId'],'atlasVersion':cases['atlasVersion'],'destinationId':cases['entryDestinationId']}, 'Missing exact prepared default home'
        report['phase']='cold-default-home'
        mcp=subprocess.Popen([args.node,str(root/'bin/mcp-navigator.mjs'),'--connection',str(connection)],cwd=root,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        rpc('initialize',{'protocolVersion':'2025-06-18','clientInfo':{'name':'q025-final-acceptance','version':'1'}})
        pw=sync_playwright().start()
        browser=pw.chromium.launch(headless=True)
        context=browser.new_context(viewport={'width':1180,'height':900})
        context.add_init_script("""window.__qaLong=[];window.__qaParse=[];
          new PerformanceObserver(list=>{for(const e of list.getEntries())window.__qaLong.push({start:e.startTime,duration:e.duration});}).observe({type:'longtask',buffered:true});
          const original=JSON.parse;JSON.parse=function(text,...args){const t=performance.now();try{return original.call(this,text,...args);}finally{if(typeof text==='string'&&text.length>50000)window.__qaParse.push({characters:text.length,milliseconds:performance.now()-t});}};""")
        page=context.new_page(); page.set_default_timeout(60000)
        page.on('pageerror',lambda error:report['pageErrors'].append(str(error)))
        report['browserVersion']=browser.version
        begin=time.monotonic(); page.goto(conn['url'],wait_until='domcontentloaded')
        page.wait_for_function('id=>window.eigenquestionsNavigator?.read().capsule?.snapshot.view.atlas?.destination.id===id',arg=cases['entryDestinationId'])
        page.wait_for_function('window.eigenquestionsNavigator.read().renderedRevision===window.eigenquestionsNavigator.read().revision')
        ready_ms=(time.monotonic()-begin)*1000
        cold=page.evaluate("({longTasks:window.__qaLong,parses:window.__qaParse,resources:performance.getEntriesByType('resource').map(e=>({path:new URL(e.name).pathname,transferSize:e.transferSize,decodedBodySize:e.decodedBodySize,duration:e.duration}))})")
        report['coldHome']={'readyMilliseconds':round(ready_ms,2),**cold,'network':'Uncompressed same-host HTTP; not a public-network estimate.'}
        assert not any('/data/embeddings' in r['path'] or '.f32' in r['path'] for r in cold['resources'])
        check('Cold all-physics entry loads actual frozen package with measured parsing and main-thread tasks',readyMilliseconds=round(ready_ms,2))
        page.screenshot(path=str(out/'physics-desktop.png'),full_page=True)
        page.goto(conn['url']+'#token='+token,wait_until='domcontentloaded')
        page.wait_for_function("window.eigenquestionsNavigator.read().mode==='local-companion'")
        render(state())
        current, latency=navigate(cases['journey'][0]); menu(current)
        page.screenshot(path=str(out/'dark-sectors-desktop.png'),full_page=True)
        journey=[{'destinationId':cases['journey'][0],'mode':'MCP entry','latencyMilliseconds':latency,'choices':menu(current)}]
        for target in cases['journey'][1:]:
            before=state(); choice=next((d for d in before['view']['directions'] if d['selector']['destinationId']==target),None)
            begin=time.monotonic()
            if choice:
                page.locator('#directions button.direction[data-direction-id="'+choice['id']+'"]').click()
                page.wait_for_function('id=>window.eigenquestionsNavigator.read().capsule.snapshot.view.atlas.destination.id===id',arg=target)
                current=render(state()); mode='browser foreground choice'
            else:
                links=call('navigator_connections',{'destinationId':before['state']['selector']['destinationId'],'limit':100})
                assert any(row['destinationId']==target for row in links['items'])
                current,_=navigate(target); mode='MCP exact recorded connection beyond foreground'
            journey.append({'destinationId':target,'mode':mode,'latencyMilliseconds':round((time.monotonic()-begin)*1000,2),'choices':menu(current)})
            if target==cases['production']: page.screenshot(path=str(out/'kk-production-desktop.png'),full_page=True)
        assert current['view']['atlas']['destination']['id']==cases['linear']
        check('Broad dark-sector entry reaches KK production, threshold rates and linear cosmology through recorded routes',journey=journey)
        page.screenshot(path=str(out/'linear-desktop.png'),full_page=True)
        old=next(k for k,v in cases['aliases'].items() if v==cases['linear']); old_state,_=navigate(old)
        assert old_state['state']['id']==current['state']['id']
        assert page.locator('details').filter(has=page.locator('summary',has_text='Earlier reviewed definitions and reading limits')).count()==1
        check('Old scoped-question URL selector converges to canonical linear-cosmology state and retains original definitions')
        # The actual broad-parent preview must show physics, not its retained review summary.
        preview=cases['preview']; current,_=navigate(preview['currentId']); direction=next(d for d in current['view']['directions'] if d['selector']['destinationId']==preview['targetId'])
        assert direction['summary']==preview['subtitle']
        page.locator('#question').fill(preview['choiceTitle']); page.locator('#question-form').evaluate('(form)=>form.requestSubmit()')
        page.wait_for_selector('#atlas-lookup button')
        lookup=page.locator('#atlas-lookup').inner_text(); assert preview['subtitle'] in lookup and preview['rawReviewHistoryRetained'] not in lookup
        check('Actual broad-parent choices and visible lexical search use exact scientific questions; history remains in details')
        current,latency=navigate(cases['largest']['id']); assert page.locator('#atlas-lookup').inner_text().strip()=='', 'Stale lexical results survived an accepted destination change'; assert current['view']['atlas']['connectionCount']==cases['largest']['connectionCount']; menu(current)
        disclosure=page.locator('#atlas-panel > details').filter(has=page.locator('summary',has_text='All connections')).first
        begin=time.monotonic(); disclosure.locator(':scope > summary').click(); page.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
        open_ms=(time.monotonic()-begin)*1000
        assert disclosure.locator('.atlas-connection-list > div').count()==cases['largest']['connectionCount']
        check('Largest real incident collection retains all routes in browser disclosure',destinationId=cases['largest']['id'],relations=cases['largest']['connectionCount'],navigationMilliseconds=latency,disclosureMilliseconds=round(open_ms,2),browserPaging=False)
        current,_=navigate(cases['blackHole']); assert current['view']['atlas']['destination']['title']=='Black holes and ultraviolet gravitational dynamics'; menu(current)
        check('Independent black-hole entry loads exact scope, sources and distinct destinations',choices=menu(current))
        follow=cases['blackHoleFollow']; current,_=navigate(follow['targetId']); assert current['state']['selector']['destinationId']==follow['targetId'], 'Black-hole application target did not render'
        check('Independent black-hole entry follows its admitted RG application route',**follow)
        # Verify the same complete checked proof through MCP and the browser disclosure.
        links=call('navigator_connections',{'relationId':follow['relationId'],'includeProof':True}); proof=links['items'][0]['proof']; assert proof['source']==cases['blackHole'] and proof['target']==follow['targetId'] and proof['type']=='application_of', 'Proof endpoint/type changed'
        box=page.locator('#atlas-panel > details').filter(has=page.locator('summary',has_text='All connections')).first; box.locator(':scope > summary').click()
        proof_box=box.locator('[data-relation-id="'+follow['relationId']+'"] > details').filter(has=page.locator('summary',has_text='Sources and review record')).first; proof_box.locator(':scope > summary').click(); proof_box.get_by_role('link',name='Complete evidence, qualifications and review history').wait_for()
        check('Browser and MCP resolve complete hash-bound relation proof lazily',relationId=follow['relationId'],evidenceCount=len(proof['evidenceIds']))
        # Exact source inspection remains a secondary path at the same physical destination.
        source=cases['source']; context_page=call('navigator_context',{'unitId':source['originUnitId'],'section':'relations'})
        route=next(r for r in context_page['sourceRoutes']['items'] if r['relationId']==source['relationId'])
        target=next(e for e in route['endpoints'] if e['side']=='target')['choices'][0]['action']; before=state(); physical=before['state']['selector']; columns=page.locator('#columns > .miller-column').count()
        inspected=call('navigator_navigate',{**target,'expectedRevision':before['revision']}); render(inspected)
        assert inspected['state']['selector']==physical and inspected['state']['sourceInspection']['objectId']==source['targetObjectId'], 'Source inspection changed selector or exact endpoint'
        assert page.locator('#columns > .miller-column').count()==columns, 'Source inspection added a physics column'
        assert page.locator('#source-inspection-panel').count()==1, 'Source inspection panel missing'
        check('MCP reads and follows exact source method without a new scientific destination or extra physics column',relationId=source['relationId'])
        page.screenshot(path=str(out/'source-desktop.png'),full_page=True)
        closed=call('navigator_navigate',{'type':'close-source','expectedRevision':inspected['revision']}); render(closed)
        report['phase']='compound-source-coverage'
        compound=cases['compound']; current,_=navigate(compound['destinationId'])
        node=next(row for row in current['view']['nodes'] if row['id']==compound['unitId'])
        full_node=next(row for row in call('navigator_state',{'full':True})['view']['nodes'] if row['id']==compound['unitId'])
        browser_node=page.evaluate('id=>window.eigenquestionsNavigator.read().capsule.snapshot.view.nodes.find(node=>node.id===id)',compound['unitId'])
        for field in ['coverageMode','wholeQuestionCoveredByEachHome','targetCoverage','coverageNotice','coverageProvenance']:
            assert node[field]==full_node[field]==browser_node[field], 'Compact/full/browser compound qualification differs: '+field
        assert node['coverageMode']=='explicit_compound_union' and node['wholeQuestionCoveredByEachHome'] is False
        assert node['targetCoverage']==compound['targetCoverage'] and node['evidence']['text']==compound['sourceText']
        assert node['coverageNotice']=='This view covers one part of the source’s question.'
        more=page.locator('#evidence > button')
        if more.count(): more.click()
        source_card=page.locator('[data-source-id="'+compound['unitId']+'"]')
        if not source_card.count(): page.locator('#evidence .source-paper[data-paper-id="'+node['paperId']+'"] > .source-facets > summary').click()
        source_card.get_by_text(node['coverageNotice'],exact=True).wait_for(state='attached')
        provenance=source_card.locator(':scope > details').filter(has=page.locator('summary',has_text='Source scope & provenance')).first
        assert not provenance.evaluate('(node)=>node.open'), 'Coverage provenance should begin collapsed'
        provenance.locator(':scope > summary').click()
        for part in compound['targetCoverage']: assert part['sourceSpan'] in provenance.inner_text()
        result=call('navigator_sources',{'destinationId':compound['destinationId'],'offset':compound['sourceOffset'],'limit':1})
        assert result['items'][0]['unitId']==compound['unitId'] and result['items'][0]['targetCoverage']==compound['targetCoverage']
        page.screenshot(path=str(out/'compound-source-desktop.png'),full_page=True)
        check('Compound source remains one unchanged question with precise component-home coverage in browser and agent reads',unitId=compound['unitId'],destinationId=compound['destinationId'])
        report['phase']='dated-placement-notice'
        unresolved=cases['unresolved']; current,_=navigate(unresolved['destinationId'])
        record=current['view']['atlas']['destination']
        assert record['sourceHomeStatus']=='unresolved' and record['sourceHomeNotice']==unresolved['notice'] and record['sourceHomeReason']==unresolved['reason']
        scope=page.locator('#atlas-panel > details').filter(has=page.locator('summary',has_text='Scope, assumptions and sources')).first
        assert not scope.evaluate('(node)=>node.open'); scope.locator(':scope > summary').click()
        scope.get_by_text(unresolved['notice'],exact=True).wait_for(state='visible')
        reason=scope.locator('details').filter(has=page.locator('summary',has_text='Placement context')).first
        assert not reason.evaluate('(node)=>node.open'); reason.locator(':scope > summary').click()
        assert unresolved['reason'] in reason.inner_text() and 'More source context is needed' not in scope.inner_text()
        page.screenshot(path=str(out/'placement-notice-desktop.png'),full_page=True)
        check('Dated unresolved source shows explicit placement notice and unchanged reason without inventing missing context',destinationId=unresolved['destinationId'])
        current,_=navigate(cases['production']); page.set_viewport_size({'width':390,'height':844}); page.evaluate('window.scrollTo(0,0)')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        page.screenshot(path=str(out/'kk-production-mobile.png'),full_page=True)
        check('Actual KK production choices and source disclosures fit a 390px mobile viewport')
        report['screenshots']=['placement-notice-desktop.png','compound-source-desktop.png','physics-desktop.png','dark-sectors-desktop.png','kk-production-desktop.png','linear-desktop.png','source-desktop.png','kk-production-mobile.png']
        # The separate overview is exercised on the actual final geometry, not a fixture.
        report['phase']='overview-classification'
        from urllib.parse import urlencode
        overview=cases['overview']; chart=context.new_page();chart.on('pageerror',lambda error:report['pageErrors'].append(str(error)))
        chart.set_default_timeout(60000)
        base=conn['url'].rstrip('/')+'/atlas-overview.html#'
        fragment={'atlas':cases['atlasId'],'version':cases['atlasVersion'],'destination':cases['entryDestinationId'],'space':'classification'}
        chart.goto(base+urlencode(fragment),wait_until='domcontentloaded')
        chart.wait_for_function('n=>document.querySelectorAll(".atlas-fixed-node").length===n',arg=overview['classificationNodeCount'])
        assert chart.locator('#atlas-topics button').count()==17
        assert chart.locator('.classification-edge').count()==overview['classificationEdgeCount']
        assert chart.locator('.atlas-map-label').evaluate_all('nodes=>nodes.filter(n=>getComputedStyle(n).display!=="none").length')==17
        chart.screenshot(path=str(out/'overview-physics-desktop.png'),full_page=True)
        assert overview['portalSteps'], 'Final physics-to-detail portal route must be bound'
        chart.locator('.atlas-map-node[data-destination-id="'+overview['classificationFieldId']+'"] .atlas-map-hit').click()
        for step in overview['portalSteps']:
            chart.locator('#atlas-selected').get_by_role('button',name=step['buttonLabel'],exact=True).click()
            chart.wait_for_function('id=>new URLSearchParams(location.hash.slice(1)).get("destination")===id',arg=step['destinationId'])
        assert chart.locator('#atlas-space').input_value()=='detail'
        assert chart.evaluate('new URLSearchParams(location.hash.slice(1)).get("destination")')==overview['detailEntryId']
        chart.wait_for_function('title=>document.querySelector("#atlas-selected h2")?.textContent===title',arg=overview['detailEntryTitle'])
        assert chart.locator('#atlas-map .atlas-map-node').count()==overview['detailNodeCount']
        assert chart.locator('#atlas-map .atlas-map-edge').count()==overview['detailEdgeCount']
        assert chart.locator('#atlas-topics button').count()==15
        if overview['kind']=='navigation_schematic': assert 'distances have no meaning' in chart.locator('#atlas-map-caption').inner_text()
        chart.screenshot(path=str(out/'overview-detail-entrance-desktop.png'),full_page=True)
        width_before=float(chart.locator('#atlas-map').get_attribute('viewBox').split()[2]);chart.locator('#atlas-zoom-in').click()
        width_after=float(chart.locator('#atlas-map').get_attribute('viewBox').split()[2]);assert width_after<width_before
        target=chart.locator('.atlas-map-node[data-destination-id="'+overview['clickTargetId']+'"] .atlas-map-hit')
        assert target.count()==1;target.click()
        chart.wait_for_function('title=>document.querySelector("#atlas-selected h2")?.textContent===title',arg=overview['clickTargetTitle'])
        chart.screenshot(path=str(out/'overview-detail-zoom-desktop.png'),full_page=True)
        detail_metrics=chart.evaluate('({nodes:document.querySelectorAll(".atlas-map-node").length,labels:[...document.querySelectorAll(".atlas-map-label")].filter(n=>getComputedStyle(n).display!=="none").length,bodyWidth:document.documentElement.scrollWidth,viewport:innerWidth,longTasks:window.__qaLong,parses:window.__qaParse})')
        assert detail_metrics['bodyWidth']<=detail_metrics['viewport']+1
        chart.set_viewport_size({'width':390,'height':844});chart.screenshot(path=str(out/'overview-detail-mobile.png'),full_page=True)
        assert chart.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        report['phase']='overview-mobile-return'
        chart.locator('#atlas-map-breadcrumb').get_by_role('button',name='All physics fields',exact=True).click()
        chart.wait_for_function('document.querySelectorAll("#atlas-topics button").length===17')
        assert chart.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        assert all(r['height']>=44 for r in chart.locator('#atlas-topics button').evaluate_all('nodes=>nodes.map(n=>({height:n.getBoundingClientRect().height}))'))
        chart.screenshot(path=str(out/'overview-physics-mobile.png'),full_page=True);chart.close()
        report['screenshots']+=['overview-physics-desktop.png','overview-detail-entrance-desktop.png','overview-detail-zoom-desktop.png','overview-detail-mobile.png','overview-physics-mobile.png']
        check('Final overview retains the actual classification graph and detailed geometry, zooms and follows a plotted destination',detail=detail_metrics,clickedDestinationId=overview['clickTargetId'],classificationNodes=overview['classificationNodeCount'])
        report['longTasksAll']=page.evaluate('window.__qaLong'); assert not report['pageErrors']; report['passed']=True; browser.close()
    except Exception as error:
        report['error']=str(error).replace(token,'[redacted-session-token]') if token else str(error)
        if 'chart' in locals() and not chart.is_closed():
            try:
                report['overviewFailure']={'url':chart.url,'body':chart.locator('body').inner_text(),'selectedSpace':chart.locator('#atlas-space').input_value()}
                chart.screenshot(path=str(out/'overview-failure.png'),full_page=True)
            except Exception: pass
        if page:
            try:
                report['failureState']=page.evaluate("({title:document.title,body:document.body.innerText.slice(0,12000),read:window.eigenquestionsNavigator?.read(),longTasks:window.__qaLong,parses:window.__qaParse})")
            except Exception: pass
            try: page.screenshot(path=str(out/'failure.png'),full_page=True)
            except Exception: pass
    finally:
        text=json.dumps(report,indent=2)+'\n'; (out/'report.json').write_text(text.replace(token,'[redacted-session-token]') if token else text)
        if browser:
            try: browser.close()
            except Exception: pass
        if pw:
            try: pw.stop()
            except Exception: pass
        for process in [mcp,server]:
            if process:
                process.terminate()
                try: process.wait(timeout=5)
                except subprocess.TimeoutExpired: process.kill()
        shutil.rmtree(private,ignore_errors=True)
    if not report['passed']: raise SystemExit(report.get('error','Failed'))
if __name__=='__main__': main()
