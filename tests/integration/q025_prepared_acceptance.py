#!/usr/bin/env python3
"""Prepared atlas structural/browser acceptance. Run only in authorized Slurm.

Uses clearly synthetic data to test state/transport mechanics, not scientific
quality. Product scientific acceptance uses the separately reviewed journeys.
The process-local bridge exercises real MCP -> SSE -> controller -> render ack.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
from playwright.sync_api import sync_playwright


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--node', default='node')
    parser.add_argument('--draft-atlas')
    parser.add_argument('--scale-atlas')
    parser.add_argument('--source-context-pack')
    parser.add_argument('--source-context-manifest-sha')
    args = parser.parse_args()
    if not os.environ.get('SLURM_JOB_ID'):
        raise SystemExit('Run Q-025 browser acceptance only in the authorized Slurm environment.')
    root, output = Path(args.project).resolve(), Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    temp = Path(tempfile.mkdtemp(prefix='eigenquestions-q025-'))
    server = mcp = None
    report = {'schemaVersion': '1.0.0', 'request': 'Q-025', 'checks': [], 'screenshots': [],
              'scope': 'Isolated Slurm Chromium, synthetic prepared atlas, actual shared controller and local MCP bridge. Not the owner Chrome and not scientific acceptance.'}

    def passed(name, **details):
        report['checks'].append({'name': name, 'passed': True, **details})

    try:
        # Fixture is only installed in the copied test build. It is never product data.
        fixture_script = """
import {atlasFixture} from './tests/integration/prepared-atlas.test.mjs';
import {mkdir,writeFile} from 'node:fs/promises';
const {manifest,catalog}=atlasFixture(),directory=`dist/data/atlas/${manifest.atlasId}/${manifest.atlasVersion}`;
await mkdir(directory,{recursive:true});
await writeFile(`${directory}/manifest.json`,JSON.stringify(manifest));
await writeFile(`${directory}/catalog.json`,JSON.stringify(catalog));
await writeFile('dist/data/atlas/index.json',JSON.stringify({schemaVersion:'1.0.0',atlases:[{atlasId:manifest.atlasId,atlasVersion:manifest.atlasVersion,entryDestinationId:manifest.entryDestinationId,title:'Synthetic acceptance atlas',scope:'Test-only data; no scientific claims.'}]}));
"""
        subprocess.run([args.node, '--input-type=module', '-e', fixture_script], cwd=root, check=True, stdout=subprocess.DEVNULL)
        draft_manifest=None
        if args.draft_atlas:
            draft_directory=Path(args.draft_atlas).resolve();draft_manifest=json.loads((draft_directory/'manifest.json').read_text())
            target=root/'dist/data/atlas'/draft_manifest['atlasId']/draft_manifest['atlasVersion'];shutil.copytree(draft_directory,target,dirs_exist_ok=True)
            draft_catalog=json.loads((draft_directory/'catalog.json').read_text())
            discovery=json.loads((root/'dist/data/atlas/index.json').read_text());discovery['atlases'].append({'atlasId':draft_manifest['atlasId'],'atlasVersion':draft_manifest['atlasVersion'],'entryDestinationId':draft_manifest['entryDestinationId'],'title':'Physics classification research preview','scope':draft_manifest['scope']['description']});(root/'dist/data/atlas/index.json').write_text(json.dumps(discovery))
            if args.source_context_pack:
                pack=Path(args.source_context_pack).resolve();pack_bytes=(pack/'manifest.json').read_bytes();pack_manifest=json.loads(pack_bytes)
                if hashlib.sha256(pack_bytes).hexdigest()!=args.source_context_manifest_sha:raise RuntimeError('Pinned source-context package manifest changed')
                descriptors=[pack_manifest['sourceContextIndex'],pack_manifest['sourceContextSummary'],*pack_manifest['unitIndexFiles'].values(),*pack_manifest['files'].values()]
                for descriptor in descriptors:
                    source=pack/descriptor['path'];body=source.read_bytes()
                    if hashlib.sha256(body).hexdigest()!=descriptor['sha256']:raise RuntimeError('Source-context package checksum mismatch: '+descriptor['path'])
                    destination=target/descriptor['path'];destination.parent.mkdir(parents=True,exist_ok=True)
                    if destination.exists():destination.unlink()
                    try:os.link(source,destination)
                    except OSError:shutil.copyfile(source,destination)
                original_hash=hashlib.sha256((target/'manifest.json').read_bytes()).hexdigest()
                draft_manifest['files']['sourceContextIndex']=pack_manifest['sourceContextIndex'];draft_manifest['files']['sourceContextSummary']=pack_manifest['sourceContextSummary'];(target/'manifest.json').write_text(json.dumps(draft_manifest,separators=(',',':')))
                report['contextPackage']={'manifestSha256':hashlib.sha256(pack_bytes).hexdigest(),'indexSha256':pack_manifest['sourceContextIndex']['sha256'],'verifiedFiles':len(descriptors),'originalCandidateManifestSha256':original_hash,'testDerivedManifestSha256':hashlib.sha256((target/'manifest.json').read_bytes()).hexdigest(),'scope':'Isolated QA derivative; candidate science/catalog unchanged, full pinned source context staged from existing Slurm artifact.'}

        scale_manifest=None
        if args.scale_atlas:
            scale_directory=Path(args.scale_atlas).resolve();scale_manifest=json.loads((scale_directory/'manifest.json').read_text())
            discovery=json.loads((root/'dist/data/atlas/index.json').read_text());discovery['atlases'].append({'atlasId':scale_manifest['atlasId'],'atlasVersion':scale_manifest['atlasVersion'],'entryDestinationId':scale_manifest['entryDestinationId'],'title':'Full-scale delivery diagnostic','scope':scale_manifest['scope']['description']});(root/'dist/data/atlas/index.json').write_text(json.dumps(discovery))
            report['staticScaleBuild']=json.loads((root/'dist/build-info.json').read_text())
        connection = temp / 'connection.json'
        atlas_dir = root / 'dist/data/atlas/acceptance-fixture/2026-11-17-test'
        server = subprocess.Popen([args.node, str(root/'bin/navigate.mjs'), 'serve', '--atlas', str(atlas_dir), '--port', '0', '--connection', str(connection)], cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        deadline = time.monotonic()+45
        while not connection.exists() and time.monotonic()<deadline:
            if server.poll() is not None:
                raise RuntimeError('Prepared companion failed: '+server.stderr.read().decode()[-2000:])
            time.sleep(.05)
        if not connection.exists():
            raise RuntimeError('Prepared companion startup timed out')
        conn = json.loads(connection.read_text()); origin=conn['url'].rstrip('/')
        mcp = subprocess.Popen([args.node,str(root/'bin/mcp-navigator.mjs'),'--connection',str(connection)],cwd=root,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        seq=0
        def rpc(method,params):
            nonlocal seq
            seq+=1;mcp.stdin.write(json.dumps({'jsonrpc':'2.0','id':seq,'method':method,'params':params})+'\n');mcp.stdin.flush()
            result=json.loads(mcp.stdout.readline())
            if result.get('error'):raise RuntimeError(str(result['error']))
            return result['result']
        rpc('initialize',{'protocolVersion':'2025-06-18','clientInfo':{'name':'q025-browser-acceptance','version':'1'}})
        selector={'kind':'atlas-destination','atlasId':'acceptance-fixture','atlasVersion':'2026-11-17-test','destinationId':'root'}
        with sync_playwright() as playwright:
            browser=playwright.chromium.launch(headless=True)
            context=browser.new_context(viewport={'width':1440,'height':1050})
            context.add_init_script("""window.__q025LongTasks=[];try{new PerformanceObserver(list=>{for(const entry of list.getEntries())window.__q025LongTasks.push({start:entry.startTime,duration:entry.duration});}).observe({type:'longtask',buffered:true});}catch{}""")
            page=context.new_page();errors=[];requests=[]
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.on('request',lambda request:requests.append(request.url))
            route=origin+'/#atlas=acceptance-fixture&version=2026-11-17-test&destination=root'
            page.goto(route,wait_until='networkidle');page.wait_for_function("document.documentElement.dataset.destinationId==='root'")
            assert not any('.f32' in url or '/graph-' in url for url in requests)
            passed('prepared route renders without native vectors or graph shards')
            report['fixturePerformance']=page.evaluate("({readyMs:performance.now(),longTasks:window.__q025LongTasks,resources:performance.getEntriesByType('resource').map(r=>({name:new URL(r.name).pathname,duration:r.duration,transferSize:r.transferSize,decodedBodySize:r.decodedBodySize}))})")
            page.locator('#directions button.direction').filter(has_text='Fixture left').click()
            page.wait_for_function("document.documentElement.dataset.destinationId==='left'")
            page.locator('#directions button.direction').filter(has_text='Fixture shared').click()
            page.wait_for_function("document.documentElement.dataset.destinationId==='shared'")
            left_id=page.evaluate('window.eigenquestionsNavigator.read().capsule.snapshot.view.stateId')
            page.screenshot(path=str(output/'prepared-shared.png'),full_page=True);report['screenshots'].append('prepared-shared.png')
            page.locator('#atlas-panel summary').filter(has_text='Your work').click()
            page.get_by_label('Local research work note').fill('Private synthetic note for route equivalence.')
            page.get_by_role('button',name='Save note locally',exact=True).click()
            shared_url=page.url
            assert 'Private' not in shared_url
            assert 'Private' not in json.dumps(page.evaluate('window.eigenquestionsNavigator.export()'))
            page.go_back(wait_until='networkidle');page.wait_for_function("document.documentElement.dataset.destinationId==='left'")
            page.go_back(wait_until='networkidle');page.wait_for_function("document.documentElement.dataset.destinationId==='root'")
            page.locator('#directions button.direction').filter(has_text='Fixture right').click()
            page.wait_for_function("document.documentElement.dataset.destinationId==='right'")
            page.locator('#directions button.direction').filter(has_text='Fixture shared').click()
            page.wait_for_function("document.documentElement.dataset.destinationId==='shared'")
            assert page.evaluate('window.eigenquestionsNavigator.read().capsule.snapshot.view.stateId')==left_id
            page.locator('#atlas-panel summary').filter(has_text='Your work').click()
            assert page.get_by_label('Local research work note').input_value()=='Private synthetic note for route equivalence.'
            passed('manual alternate routes converge; browser Back restores path; local work note follows destination without public export')
            before=page.evaluate('window.eigenquestionsNavigator.read()')
            oriented=page.evaluate("async selector=>window.eigenquestionsNavigator.orient('An original synthetic paragraph',{selector})",{**selector,'destinationId':'left'})
            assert page.evaluate('window.eigenquestionsNavigator.read().revision')==before['revision']
            page.evaluate("async selector=>window.eigenquestionsNavigator.navigate({type:'navigate',selector},{expectedRevision:window.eigenquestionsNavigator.read().revision})",{**selector,'destinationId':'contrast'})
            stale=page.evaluate("({capsule,revision})=>{try{window.eigenquestionsNavigator.apply(capsule,{expectedRevision:revision});return false}catch(error){return error.code==='revision_conflict'}}",{'capsule':oriented,'revision':before['revision']})
            assert stale
            passed('read-only orientation leaves path intact and stale result cannot replace newer destination')
            page.goto(shared_url,wait_until='networkidle');page.wait_for_function("document.documentElement.dataset.destinationId==='shared'")
            page.reload(wait_until='networkidle');page.wait_for_function("document.documentElement.dataset.destinationId==='shared'")
            assert page.evaluate('window.eigenquestionsNavigator.read().capsule.snapshot.view.stateId')==left_id
            passed('compact URL and reload restore exact prepared destination')
            page.goto(origin+'/#token='+conn['token'],wait_until='networkidle');page.wait_for_function("window.eigenquestionsNavigator.read().mode==='local-companion'")
            response=rpc('tools/call',{'name':'navigator_navigate','arguments':{'type':'navigate','selector':{**selector,'destinationId':'shared'}}})
            assert not response['isError'];page.wait_for_function("document.documentElement.dataset.destinationId==='shared'")
            page.wait_for_function('window.eigenquestionsNavigator.read().renderedRevision===window.eigenquestionsNavigator.read().revision')
            acknowledged=False
            for _ in range(40):
                state=rpc('tools/call',{'name':'navigator_state','arguments':{}})['structuredContent']
                if state['browserStatus']['acknowledgedCurrent']:
                    acknowledged=True;break
                time.sleep(.05)
            assert acknowledged
            passed('actual stdio MCP mutation reaches prepared browser through SSE and receives state/revision render acknowledgement',destinationId=state['state']['selector']['destinationId'])
            page.screenshot(path=str(output/'prepared-connected.png'),full_page=True);report['screenshots'].append('prepared-connected.png')
            if draft_manifest:
                real_selector={'kind':'atlas-destination','atlasId':draft_manifest['atlasId'],'atlasVersion':draft_manifest['atlasVersion'],'destinationId':'q-kk-decay-linear-cosmology'}
                real_url=origin+'/#atlas='+real_selector['atlasId']+'&version='+real_selector['atlasVersion']+'&destination='+real_selector['destinationId']
                page.set_viewport_size({'width':1180,'height':900});page.goto(real_url,wait_until='networkidle');page.wait_for_function("document.documentElement.dataset.destinationId==='q-kk-decay-linear-cosmology'")
                assert page.evaluate('window.eigenquestionsNavigator.read().mode')=='browser'
                assert page.locator('#current-question').inner_text()==page.evaluate('window.eigenquestionsNavigator.read().capsule.snapshot.view.atlas.destination.title')
                assert page.locator('#question').get_attribute('placeholder')=='Find a topic or question'
                assert not page.locator('#atlas-entrances').is_visible()
                page.locator('#full-question-details>summary').click()
                assert page.locator('#atlas-current-summary').inner_text().find('threshold')>=0
                page.locator('#full-question-details>summary').click()
                assert page.locator('#directions button.direction').first.bounding_box()['y']<720
                assert 'draft_not_accepted' in json.dumps(page.evaluate('window.eigenquestionsNavigator.read().capsule'))
                assert not any('.f32' in item['name'] for item in page.evaluate("performance.getEntriesByType('resource').map(r=>({name:r.name}))"))
                scoped=page.evaluate("async selector=>({questions:await window.eigenquestionsNavigator.sources(selector,{lens:'physical_question'}),methods:await window.eigenquestionsNavigator.sources(selector,{lens:'method'})})",real_selector)
                expected_context=sum(1 for row in draft_catalog['memberships'] if row['destinationId']==real_selector['destinationId'] and row.get('associationScope'))
                assert scoped['questions']['primaryTotal']==1 and scoped['methods']['contextTotal']==expected_context
                assert page.evaluate("async selector=>(await window.eigenquestionsNavigator.sources(selector,{lens:'method',workRelation:'using'})).total",real_selector)==0
                if expected_context:
                    method_view=page.evaluate("async selector=>{const api=window.eigenquestionsNavigator,parent=api.read();await api.navigate({type:'navigate',selector,lens:'method'},{expectedRevision:parent.revision});return api.read().capsule.snapshot.view;}",real_selector)
                    assert method_view['atlas']['membershipCount']==1 and method_view['atlas']['matchingContextCount']==expected_context
                    assert any(n.get('atlasContextScope')=='same_paper_context' and n.get('atlasContextMatchesFilters') for n in method_view['nodes'])
                    page.screenshot(path=str(output/'real-method-context.png'),full_page=True);report['screenshots'].append('real-method-context.png')
                    page.goto(real_url,wait_until='networkidle');page.wait_for_function("window.eigenquestionsNavigator.read().capsule.snapshot.session.states.at(-1).lens==='combined'")
                    passed('method perspective exposes exact co-paper context without changing primary membership or asserting USING',contextCount=expected_context)
                page.screenshot(path=str(output/'real-draft-desktop.png'),full_page=True);report['screenshots'].append('real-draft-desktop.png')
                report['draftPerformance']=page.evaluate("({readyMs:performance.now(),longTasks:window.__q025LongTasks,resources:performance.getEntriesByType('resource').map(r=>({name:new URL(r.name).pathname,duration:r.duration,transferSize:r.transferSize,decodedBodySize:r.decodedBodySize}))})")
                context_id=page.evaluate('window.eigenquestionsNavigator.read().capsule.snapshot.view.atlas.destination.evidenceIds[0]')
                before_context=page.evaluate("performance.getEntriesByType('resource').filter(r=>r.name.endsWith('.json.gz')).length")
                assert before_context==0
                context_result=page.evaluate('async id=>window.eigenquestionsNavigator.context(id)',context_id)
                context_evidence=page.evaluate("async id=>window.eigenquestionsNavigator.context(id,undefined,{section:'evidence'})",context_id)
                assert context_result['availability']=='available' and 0<len(context_result['sourceObjects'])<=20 and len(context_evidence['sourceEvidence'])>0
                page.locator('.source-scientific-context summary').first.click()
                page.wait_for_function("document.querySelector('.source-scientific-context').textContent.includes('source objects')")
                assert page.locator('.source-scientific-context details').count()<100
                page.locator('.source-scientific-context>summary').first.click()
                passed('checksummed real gzip source context loads only on request, preserves exact evidence and bounds initial object DOM',objects=len(context_result['sourceObjects']),evidenceTotal=context_evidence['unfilteredTotals']['evidence'])
                passed('real source-reading draft keeps conditional 2026 challenge visible, labels draft identity, distinguishes listed-source filters and shows primary choices above disclosures')
                page.set_viewport_size({'width':390,'height':844});page.goto(real_url,wait_until='networkidle');page.wait_for_function("document.documentElement.dataset.destinationId==='q-kk-decay-linear-cosmology'")
                page.evaluate('window.scrollTo(0,0)')
                layout=page.evaluate("({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,choicesY:document.querySelector('#directions button.direction').getBoundingClientRect().top,choiceHeight:document.querySelector('#directions button.direction').getBoundingClientRect().height})")
                assert layout['scrollWidth']<=layout['width']+1,layout
                assert 0<=layout['choicesY']<570 and layout['choiceHeight']>=44,layout
                page.locator('#atlas-panel details').filter(has=page.locator('textarea')).locator('summary').click()
                page.locator('#atlas-panel textarea').fill('Unsaved-button mobile note')
                page.locator('#directions button.direction').filter(has_text='near-threshold').click();page.wait_for_function("document.documentElement.dataset.destinationId==='q-kk-graviton-threshold-decay'")
                page.screenshot(path=str(output/'real-draft-mobile.png'),full_page=True);report['screenshots'].append('real-draft-mobile.png')
                page.go_back(wait_until='networkidle');page.wait_for_function("document.documentElement.dataset.destinationId==='q-kk-decay-linear-cosmology'")
                assert page.locator('#atlas-panel textarea').input_value()=='Unsaved-button mobile note'
                passed('mobile real draft has no page overflow, readable touch targets and functional deeper navigation',layout=layout)
                if draft_catalog.get('orientation'):
                    overview_url=origin+'/atlas-overview.html#atlas='+draft_manifest['atlasId']+'&version='+draft_manifest['atlasVersion']+'&destination='+draft_manifest['entryDestinationId']+'&space=classification'
                    page.set_viewport_size({'width':1180,'height':900});page.goto(overview_url,wait_until='networkidle');page.wait_for_function("document.querySelectorAll('.atlas-map-node').length===17")
                    assert 'classification' in page.locator('#atlas-map-caption').inner_text().lower()
                    report['classificationPerformance']=page.evaluate("({readyMs:performance.now(),longTasks:window.__q025LongTasks,renderedNodes:document.querySelectorAll('.atlas-map-node').length,visibleLabels:[...document.querySelectorAll('.atlas-map-label')].filter(n=>getComputedStyle(n).display!=='none').length,resources:performance.getEntriesByType('resource').map(r=>({name:new URL(r.name).pathname,transferSize:r.transferSize,decodedBodySize:r.decodedBodySize}))})")
                    assert report['classificationPerformance']['visibleLabels']==17
                    targets=page.locator('.classification-card .atlas-map-hit').evaluate_all("nodes=>nodes.map(n=>{const r=n.getBoundingClientRect();return{x:r.x,y:r.y,width:r.width,height:r.height}})")
                    assert all(t['width']>=44 and t['height']>=44 for t in targets)
                    assert all(a['x']+a['width']<=b['x']+.5 or b['x']+b['width']<=a['x']+.5 or a['y']+a['height']<=b['y']+.5 or b['y']+b['height']<=a['y']+.5 for i,a in enumerate(targets) for b in targets[i+1:])
                    page.screenshot(path=str(output/'physics-classification-desktop.png'),full_page=True);report['screenshots'].append('physics-classification-desktop.png')
                    page.locator('.atlas-map-node[aria-label="Particles & Fields"] .atlas-map-hit').click();page.wait_for_function("document.querySelector('#atlas-selected h2').textContent==='Particles & Fields'")
                    page.screenshot(path=str(output/'physics-field-drill.png'),full_page=True);report['screenshots'].append('physics-field-drill.png')
                    page.get_by_role('button',name='Explore high energy theory',exact=True).click();page.wait_for_function("location.hash.includes('landmark%3Aarxiv-hep-th')")
                    assert 'landmark' in page.locator('#atlas-selected').inner_text().lower()
                    page.screenshot(path=str(output/'physics-hepth-portal.png'),full_page=True);report['screenshots'].append('physics-hepth-portal.png')
                    page.get_by_role('button',name='Open the source-reading research draft',exact=True).click();page.wait_for_function("document.querySelector('#atlas-space').value==='detail'")
                    assert 'no detailed source chart' in page.locator('#atlas-map-caption').inner_text().lower()
                    page.locator('#atlas-selected>a').click();page.wait_for_function("document.documentElement.dataset.destinationId==='q-kk-graviton-thermal-production'")
                    passed('classification frontier drills through exact children and explicit hep-th portal to draft source destination without inventing detailed coordinates')
                    page.set_viewport_size({'width':390,'height':844});page.goto(overview_url,wait_until='networkidle');page.wait_for_function("document.querySelectorAll('.atlas-map-node').length===17")
                    overview_layout=page.evaluate("({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,nodes:document.querySelectorAll('.atlas-map-node').length,visibleLabels:[...document.querySelectorAll('.atlas-map-label')].filter(n=>getComputedStyle(n).display!=='none').length,zoomY:[...document.querySelectorAll('.atlas-map-zoom button')].map(n=>n.getBoundingClientRect().y)})");assert overview_layout['scrollWidth']<=overview_layout['width']+1
                    assert overview_layout['visibleLabels']==17 and len(set(overview_layout['zoomY']))==1
                    page.screenshot(path=str(output/'physics-classification-mobile.png'),full_page=True);report['screenshots'].append('physics-classification-mobile.png')
                    passed('mobile classification map retains all17 selectable fields with no page overflow',layout=overview_layout)
                if args.source_context_pack:
                    page.set_viewport_size({'width':1180,'height':900});page.goto(real_url,wait_until='networkidle');page.wait_for_function("document.documentElement.dataset.destinationId==='q-kk-decay-linear-cosmology'")
                    worst='unit:0f56d055e5fd6027bbab4d22fa399093344b4c734afa5b6c32ff7abfaf369749'
                    worst_page=page.evaluate('async id=>window.eigenquestionsNavigator.context(id)',worst);assert worst_page['unfilteredTotals']['objects']==2073 and worst_page['page']['returned']<=20
                    before_state=page.evaluate('document.documentElement.dataset.stateId')
                    component=page.evaluate("""async ({selector,unitId})=>{const {loadAtlas,createAtlasContextReader}=await import('/lib/geometry/prepared-atlas.mjs'),{sourceContextDisclosure}=await import('/source-context.mjs'),base=`/data/atlas/${selector.atlasId}/${selector.atlasVersion}`,atlas=await loadAtlas(base),read=createAtlasContextReader(atlas,{base}),context=await read(unitId),details=sourceContextDisclosure(async()=>context);details.id='qa-worst-context';document.querySelector('#evidence').prepend(details);details.open=true;return {objects:context.sourceObjects.length,relations:context.sourceRelations.length};}""",{'selector':real_selector,'unitId':worst})
                    page.wait_for_function("document.querySelector('#qa-worst-context').textContent.includes('source objects')");assert page.locator('#qa-worst-context details').count()<200
                    assert page.evaluate('document.documentElement.dataset.stateId')==before_state
                    report['worstContextPerformance']=page.evaluate("({longTasks:window.__q025LongTasks,contextDomDetails:document.querySelectorAll('#qa-worst-context details').length,totalDomElements:document.querySelectorAll('*').length})")
                    page.screenshot(path=str(output/'worst-source-context-component.png'),full_page=True);report['screenshots'].append('worst-source-context-component.png')
                    passed('largest source shard remains complete internally while agent output and real disclosure component remain bounded',**component,defaultPageBytes=len(json.dumps(worst_page).encode()),scope='Isolated source-context component fixture; it does not invent a scientific destination or change navigation.')

            if scale_manifest:
                scale_selector={'kind':'atlas-destination','atlasId':scale_manifest['atlasId'],'atlasVersion':scale_manifest['atlasVersion'],'destinationId':scale_manifest['entryDestinationId']}
                def scale_url(destination):return origin+'/#atlas='+scale_manifest['atlasId']+'&version='+scale_manifest['atlasVersion']+'&destination='+destination
                def performance_receipt():return page.evaluate("({readyMs:performance.now(),longTasks:window.__q025LongTasks,domElements:document.querySelectorAll('*').length,resources:performance.getEntriesByType('resource').map(r=>({name:new URL(r.name).pathname,duration:r.duration,transferSize:r.transferSize,decodedBodySize:r.decodedBodySize}))})")
                page.set_viewport_size({'width':1180,'height':900});page.goto(scale_url(scale_manifest['entryDestinationId']),wait_until='networkidle');page.wait_for_function("document.documentElement.dataset.destinationId==='classification:physics'")
                report['scalePhysicsEntrance']=performance_receipt();paths=[r['name'] for r in report['scalePhysicsEntrance']['resources']]
                assert not any('fine-index' in p or 'fine-lookup' in p or 'destination-memberships' in p or '/vectors' in p for p in paths)
                assert page.locator('#directions button.direction').count()==17
                page.screenshot(path=str(output/'scale-physics-entrance.png'),full_page=True);report['screenshots'].append('scale-physics-entrance.png')
                known_unit=draft_catalog['destinations'][next(i for i,d in enumerate(draft_catalog['destinations']) if d['id']=='q-kk-decay-linear-cosmology')]['evidenceIds'][0]
                fine_id='source-question:'+known_unit.removeprefix('unit:');page.goto(scale_url(fine_id),wait_until='networkidle');page.wait_for_function('id=>document.documentElement.dataset.destinationId===id',arg=fine_id)
                report['scaleDirectFine']=performance_receipt();paths=[r['name'] for r in report['scaleDirectFine']['resources']]
                assert any('fine-lookup-' in p for p in paths) and not any('fine-index.json' in p or 'destination-memberships' in p for p in paths)
                fine_before=page.evaluate('window.eigenquestionsNavigator.read().capsule.snapshot.view')
                parent=next(c['destinationId'] for c in fine_before['atlas']['connections'] if c['navigationKind']=='source_question' and c['traversal']=='incoming')
                page.goto(scale_url(parent),wait_until='networkidle');page.wait_for_function('id=>document.documentElement.dataset.destinationId===id',arg=parent)
                parent_before=page.evaluate('window.eigenquestionsNavigator.read().capsule.snapshot.view');assert any(c['destinationId']==fine_id for c in parent_before['atlas']['connections'])
                parent_selector={**scale_selector,'destinationId':parent}
                page.evaluate("async selector=>{const api=window.eigenquestionsNavigator,parent=api.read();await api.navigate({type:'navigate',selector},{expectedRevision:parent.revision});}",{**scale_selector,'destinationId':fine_id})
                assert not any('fine-index.json' in r['name'] for r in performance_receipt()['resources'])
                report['scaleLocalDrill']=performance_receipt()
                lookup=page.evaluate("async selector=>window.eigenquestionsNavigator.lookup('dark dimension',selector)",scale_selector);assert lookup
                report['scaleGlobalLookup']=performance_receipt();assert any('fine-index.json' in r['name'] for r in report['scaleGlobalLookup']['resources'])
                assert page.evaluate('window.eigenquestionsNavigator.read().capsule.snapshot.view')==fine_before
                page.goto(scale_url('diagnostic:all-source-questions'),wait_until='networkidle');page.wait_for_function("document.documentElement.dataset.destinationId==='diagnostic:all-source-questions'")
                root_before=page.evaluate('window.eigenquestionsNavigator.read().capsule.snapshot.view');assert root_before['atlas']['membershipCount']==8473 and root_before['atlas']['contextMembershipCount']==17937
                report['scaleAllSourcesParent']=performance_receipt();assert not any('destination-memberships' in r['name'] for r in report['scaleAllSourcesParent']['resources'])
                root_selector={**scale_selector,'destinationId':'diagnostic:all-source-questions'}
                filtered=page.evaluate("async selector=>window.eigenquestionsNavigator.sources(selector,{offset:0,limit:5,lens:'physical_question',constraints:{yearMin:2024,excludeIds:[]}})",root_selector)
                assert filtered['total']>5 and all(r['year']>=2024 and r['source']['id']==r['unitId'] for r in filtered['items'])
                report['scaleFilteredSources']=performance_receipt();assert any('destination-memberships' in r['name'] for r in report['scaleFilteredSources']['resources'])
                assert page.evaluate('window.eigenquestionsNavigator.read().capsule.snapshot.view')==root_before
                methods=page.evaluate("async selector=>window.eigenquestionsNavigator.sources(selector,{offset:0,limit:5,lens:'method',includeContext:true})",root_selector)
                assert methods['contextTotal']==17937 and all(r['associationScope']=='same_paper_context' for r in methods['items'])
                actual_using=page.evaluate("async selector=>window.eigenquestionsNavigator.sources(selector,{offset:0,limit:5,lens:'method',workRelation:'using'})",root_selector);assert actual_using['total']==0
                static_url=origin+'/atlas/'+scale_manifest['atlasId']+'/'+scale_manifest['atlasVersion']+'/'+fine_id+'.html'
                static_body=page.request.get(static_url);assert static_body.ok and known_unit in static_body.text()
                passed('full-scale physics, direct fine URL, local drill, global lookup and large-parent filtering use separate pinned lazy reads with stable views',destinations=8928,primary=8473,context=17937,staticFineReadable=True)

            assert not errors,errors
            passed('no browser page errors',errorCount=len(errors))
            browser.close()
        report['passed']=True
    except Exception as error:
        report['passed']=False;report['error']=str(error)
        try:
            report['failedDom']=page.evaluate("({title:document.querySelector('#current-question')?.textContent,summaryText:document.querySelector('#atlas-current-summary')?.textContent,summaryInnerText:document.querySelector('#atlas-current-summary')?.innerText,detailsOpen:document.querySelector('#full-question-details')?.open,status:document.querySelector('#status')?.textContent})")
            page.screenshot(path=str(output/'failure.png'),full_page=True);report['screenshots'].append('failure.png')
        except Exception:pass
        raise
    finally:
        (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        if mcp:mcp.terminate()
        if server:server.terminate()
        shutil.rmtree(temp,ignore_errors=True)


if __name__=='__main__':main()
