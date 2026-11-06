#!/usr/bin/env python3
"""Real Q-006 fixed-map checks. Launch only in the authorized Slurm environment."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import time
import traceback
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--origin')
    parser.add_argument('--node', default='node')
    args = parser.parse_args()
    if not os.environ.get('SLURM_JOB_ID'):
        raise SystemExit('Run the overview browser checks only in the authorized Slurm environment.')
    root, out = Path(args.project).resolve(), Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((root / 'data/overview/manifest.json').read_text())
    data = json.loads((root / 'data/overview/map.json').read_text())
    server = None
    report = {'request': 'Q-006', 'checks': [], 'screenshots': [], 'scope': 'Real fixed Swampland data, browser Canvas and input events. Headless Slurm timings are observations, not a 60-fps or production-latency guarantee.'}

    def passed(name, **values):
        report['checks'].append({'name': name, 'passed': True, **values})

    def expected_text(index):
        shard = next(item for item in manifest['files']['details'] if item['start'] <= index < item['start'] + item['count'])
        return json.loads((root / 'data/overview' / shard['path']).read_text())['texts'][index - shard['start']]

    try:
        if args.origin:
            origin = args.origin.rstrip('/')
        else:
            with socket.socket() as listener:
                listener.bind(('127.0.0.1', 0))
                port = listener.getsockname()[1]
            server = subprocess.Popen([args.node, 'scripts/site-serve.mjs', str(port)], cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            origin = f'http://127.0.0.1:{port}'
            import urllib.request
            for _ in range(100):
                try:
                    urllib.request.urlopen(origin + '/overview.html', timeout=.3).close()
                    break
                except Exception:
                    if server.poll() is not None:
                        raise RuntimeError('Static overview server failed to start.')
                    time.sleep(.05)
        report['origin'] = origin
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            report['browserVersion'] = browser.version
            context = browser.new_context(viewport={'width': 1440, 'height': 1000}, has_touch=True)
            context.add_init_script("""window.__overviewPerf={longTasks:[]};try{new PerformanceObserver(list=>{for(const e of list.getEntries())window.__overviewPerf.longTasks.push({start:e.startTime,duration:e.duration});}).observe({type:'longtask',buffered:true})}catch{}""")
            requests, errors = {}, {}

            def watch(page):
                requests[page], errors[page] = [], []
                page.on('request', lambda request: requests[page].append({'url': request.url, 'method': request.method}))
                page.on('pageerror', lambda error: errors[page].append(str(error)))

            context.on('page', watch)
            explorer = context.new_page()
            explorer.set_default_timeout(30000)
            explorer.goto(origin, wait_until='domcontentloaded')
            explorer.wait_for_function("document.documentElement.dataset.ready==='true'")
            # The real explorer keeps an exact authored history entry alive while
            # the independent map runs in the new tab.
            native = explorer.evaluate("async()=>await window.eigenquestionsNavigator.orient('KK towers')")
            authored = json.loads(json.dumps(native))
            authored['builder'] = {'id': 'overview-isolation-author', 'version': '1'}
            authored['context']['question'] = 'A KK comparison kept open while inspecting the global map'
            authored['context']['assumptions'] = ['Retain this exact authored interpretation.']
            group = authored['snapshot']['view']['directions'][0]
            group['label'] = 'My exact source-grounded KK comparison'
            authored['continuation']['actions'] = [{'id': group['id'], 'label': group['label'], 'action': {'type': 'refine', 'query': 'KK towers as dark matter', 'focusIds': group['seedIds']}}]
            explorer.evaluate('capsule=>window.eigenquestionsNavigator.apply(capsule,{expectedRevision:window.eigenquestionsNavigator.read().revision})', authored)
            explorer.locator(f'.miller-column[data-current="true"] .direction[data-direction-id="{group["id"]}"]').click()
            explorer.wait_for_function("!document.body.classList.contains('busy')&&window.eigenquestionsNavigator.export().context.question==='KK towers as dark matter'", timeout=180000)
            explorer.locator('#question').fill('Keep this unfinished physical question')
            before = explorer.evaluate('({capsule:window.eigenquestionsNavigator.export(),revision:window.eigenquestionsNavigator.read().revision,local:{...localStorage},session:{...sessionStorage},draft:document.querySelector("#question").value})')
            with explorer.expect_popup() as popup:
                explorer.locator('a[href="/overview.html"][target="_blank"]').click()
            page = popup.value
            page.set_default_timeout(30000)
            page.wait_for_function("window.eigenquestionsOverview?.read().ready&&document.querySelector('#overview-stage').dataset.ready==='true'")

            def read():
                return page.evaluate('window.eigenquestionsOverview.read()')

            def frame_after(previous):
                page.wait_for_function('frame=>window.eigenquestionsOverview.read().frame>frame', arg=previous)
                page.evaluate('()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')

            def click_control(selector):
                previous = read()['frame']
                page.locator(selector).click()
                frame_after(previous)

            def labels_check(label):
                current = read()
                labels = current['labels']
                for i, item in enumerate(labels):
                    assert item['fontSize'] >= 13, (label, item)
                    assert item['x'] >= 0 and item['y'] >= 0 and item['x'] + item['width'] <= current['width'] + .1 and item['y'] + item['height'] <= current['height'] + .1, (label, item)
                    for other in labels[i+1:]:
                        overlap = item['x'] < other['x'] + other['width'] and item['x'] + item['width'] > other['x'] and item['y'] < other['y'] + other['height'] and item['y'] + item['height'] > other['y']
                        assert not overlap, (label, item, other)
                assert labels, label
                return len(labels)

            def screenshot(name, full=False):
                page.screenshot(path=str(out / name), full_page=full)
                report['screenshots'].append(name)

            def find_point(index):
                paper_id = data['papers'][data['points'][index][1]][0]
                page.locator('#overview-find').fill(paper_id)
                button = page.locator(f'#overview-results button[data-point-index="{index}"]')
                button.wait_for(state='visible')
                previous = read()['frame']
                button.click()
                frame_after(previous)

            initial = read()
            assert (initial['pointCount'], initial['paperCount'], initial['topicCount']) == (8473, 6477, 12)
            assert initial['datasetSha256'] == manifest['files']['map']['sha256']
            assert page.locator('#overview-topics > li > button').count() == 5
            assert not initial['loadedDetailShards']
            initial_requests = [urlparse(item['url']).path for item in requests[page]]
            assert not any(path.startswith('/data/') and not path.startswith('/data/overview/') for path in initial_requests)
            assert not any('/details-' in path for path in initial_requests)
            passed('new-tab overview loads the pinned Swampland map and five genuine broad groups without source shards or query corpus', initialDataBytes=manifest['files']['map']['bytes'], initialLabels=labels_check('initial'))
            screenshot('overview-fit-1440.png')

            # Physical wheel input preserves the location under its pointer.
            canvas = page.locator('#overview-canvas')
            box = canvas.bounding_box()
            px, py = box['width'] * .37, box['height'] * .43
            camera = initial['camera']
            world = {'x': (px-initial['width']/2)/camera['k']+camera['x'], 'y': (initial['height']/2-py)/camera['k']+camera['y']}
            page.mouse.move(box['x']+px, box['y']+py)
            start = time.monotonic()
            page.mouse.wheel(0, -120)
            page.wait_for_function('k=>window.eigenquestionsOverview.read().camera.k>k', arg=camera['k'])
            frame_after(initial['frame'])
            wheel = read()
            actual = {'x': (px-wheel['width']/2)/wheel['camera']['k']+wheel['camera']['x'], 'y': (wheel['height']/2-py)/wheel['camera']['k']+wheel['camera']['y']}
            assert wheel['camera']['k'] > camera['k']
            assert abs(actual['x']-world['x']) < 1e-6 and abs(actual['y']-world['y']) < 1e-6
            wheel_ms = (time.monotonic()-start)*1000
            page.mouse.move(box['x']+box['width']/2, box['y']+box['height']/2)
            page.mouse.down()
            page.mouse.move(box['x']+box['width']/2+68, box['y']+box['height']/2+34, steps=12)
            page.mouse.up()
            page.wait_for_function('x=>window.eigenquestionsOverview.read().camera.x!==x', arg=wheel['camera']['x'])
            frame_after(wheel['frame'])
            dragged = read()
            assert dragged['camera']['x'] != wheel['camera']['x'] and dragged['selectedPoint'] is None
            canvas.focus()
            page.keyboard.press('ArrowRight')
            page.wait_for_function('x=>window.eigenquestionsOverview.read().camera.x>x', arg=dragged['camera']['x'])
            frame_after(dragged['frame'])
            keyed = read()
            assert keyed['camera']['x'] > dragged['camera']['x']
            page.keyboard.press('Home')
            frame_after(keyed['frame'])
            reset = read()
            for key in ('x','y','k'):
                assert abs(reset['camera'][key]-initial['camera'][key]) < 1e-8
            passed('wheel zoom is pointer-centered; real drag, keyboard pan and Home restore the fixed full-map camera', wheelFeedbackMs=round(wheel_ms,2))

            umbrella = next(i for i in initial['rootChildren'] if data['topics'][i]['children'])
            click_control(f'#overview-topics button[data-topic-index="{umbrella}"]')
            grouped = read()
            assert grouped['selectedMemberCount'] == data['topics'][umbrella]['unitCount']
            child_buttons = page.locator('#overview-details .details-list').first.locator('button[data-topic-index]')
            assert child_buttons.count() == len(data['topics'][umbrella]['children'])
            child = data['topics'][umbrella]['children'][0]
            click_control(f'#overview-details > .details-list button[data-topic-index="{child}"]')
            assert read()['selectedTopic'] == child
            assert read()['selectedMemberCount'] == data['topics'][child]['unitCount']
            labels_check('child group')
            screenshot('overview-finer-group-1440.png')
            click_control('#overview-fit')
            assert read()['selectedTopic'] is None and read()['selectedPoint'] is None
            # Click a real painted topic label, rather than a test-only action.
            label = next(item for item in read()['labels'] if item['type'] == 'topic')
            box = canvas.bounding_box()
            prior = read()['frame']
            page.mouse.click(box['x']+label['x']+label['width']/2, box['y']+label['y']+label['height']/2)
            frame_after(prior)
            assert read()['selectedTopic'] == label['index']
            passed('topic labels and reliable text list select actual descendant memberships; only genuine finer groups are offered')

            # Select two distinct lazy shards while the earlier detail response
            # is held. A stale excerpt must not attach to the newer paper.
            first_by_paper = {}
            for i, point in enumerate(data['points']):
                first_by_paper.setdefault(point[1], i)
            a = next(i for i in first_by_paper.values() if 512 <= i < 1024)
            b = next(i for i in first_by_paper.values() if 4096 <= i < 4608)
            held = []
            page.route('**/data/overview/details-001.json', lambda route: held.append(route))
            find_point(a)
            page.wait_for_function("document.querySelector('#overview-excerpt').textContent.includes('Loading')")
            assert held
            find_point(b)
            page.wait_for_function("document.querySelector('#overview-details').dataset.detailReady==='true'")
            assert page.locator('#overview-excerpt').inner_text() == expected_text(b)
            held.pop().fulfill(status=200, content_type='application/json', body=(root / 'data/overview/details-001.json').read_bytes())
            page.wait_for_timeout(70)
            assert read()['selectedPoint'] == b and page.locator('#overview-excerpt').inner_text() == expected_text(b)
            assert read()['selectedWorld'] == {'x': data['points'][b][2], 'y': data['points'][b][3]}
            assert page.locator('#overview-details a.detail-link').get_attribute('href') == data['papers'][data['points'][b][1]][2]
            page.unroute('**/data/overview/details-001.json')
            screenshot('overview-source-1440.png')
            passed('local Find selects genuine source coordinates and exact lazy excerpt; late older details cannot overwrite a newer source')

            # Reach an overlapping source through its actual paper result and
            # canvas point when that paper has multiple question excerpts.
            overlap = next(i for i, point in enumerate(data['points']) if len(point[5]) > 1 and first_by_paper[point[1]] == i)
            find_point(overlap)
            page.wait_for_function("document.querySelector('#overview-details').dataset.detailReady==='true'")
            assert read()['selectedHomes'] == data['points'][overlap][5]
            assert page.locator('#overview-details button[data-topic-index]').count() == len(data['points'][overlap][5])
            assert 'Overlapping group memberships' in page.locator('#overview-details').inner_text()
            unresolved = manifest['membershipRule']['unresolvedTopicIndex']
            click_control(f'#overview-topics button[data-topic-index="{unresolved}"]')
            assert read()['selectedMemberCount'] == 13
            passed('overlapping homes and the thirteen unresolved source descriptions remain explicitly reachable')

            for width in (1440, 1024, 390, 320):
                page.set_viewport_size({'width': width, 'height': 1000 if width > 760 else 844})
                click_control('#overview-fit')
                page.evaluate('()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
                geometry = page.evaluate("""()=>({overflow:document.documentElement.scrollWidth>innerWidth+1,controls:[...document.querySelectorAll('.map-controls button,#overview-search button,#overview-find')].map(e=>({id:e.id,width:e.getBoundingClientRect().width,height:e.getBoundingClientRect().height}))})""")
                assert not geometry['overflow'], (width, geometry)
                assert all(item['width'] >= 44 and item['height'] >= 44 for item in geometry['controls'])
                label_count = labels_check(f'width {width}')
                page.evaluate('scrollTo(0,0)')
                screenshot(f'overview-{width}-top.png')
                canvas.scroll_into_view_if_needed()
                screenshot(f'overview-{width}-map.png')
                screenshot(f'overview-{width}-full.png', full=True)
                passed(f'{width}px view keeps readable nonoverlapping labels, accessible controls and no page overflow', labels=label_count)

            # Actual browser touch input exercises the same pointer handlers.
            page.set_viewport_size({'width': 390, 'height': 844})
            click_control('#overview-fit')
            canvas.scroll_into_view_if_needed()
            box = canvas.bounding_box()
            cx, cy = box['x']+box['width']/2, box['y']+box['height']/2
            before_touch = read()
            cdp = context.new_cdp_session(page)
            cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': cx-35, 'y': cy, 'id': 1}, {'x': cx+35, 'y': cy, 'id': 2}]})
            cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': cx-70, 'y': cy+12, 'id': 1}, {'x': cx+70, 'y': cy+12, 'id': 2}]})
            cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
            page.wait_for_function('k=>window.eigenquestionsOverview.read().camera.k>k*1.5', arg=before_touch['camera']['k'])
            frame_after(before_touch['frame'])
            assert read()['camera']['k'] > before_touch['camera']['k'] * 1.5
            assert read()['selectedPoint'] is None
            screenshot('overview-touch-390-map.png')
            passed('real two-touch pinch zooms without accidental point selection')

            # Camera controls must not download data, compute layout or mutate
            # the original tab. Back proves the authored entry stayed alive.
            overview_paths = [urlparse(item['url']).path for item in requests[page]]
            assert all(item['method'] == 'GET' for item in requests[page])
            assert not any(path in ['/app.js','/compute-worker.js'] or path.startswith(('/lib/','/api/')) or (path.startswith('/data/') and not path.startswith('/data/overview/')) for path in overview_paths)
            after = explorer.evaluate('({capsule:window.eigenquestionsNavigator.export(),revision:window.eigenquestionsNavigator.read().revision,local:{...localStorage},session:{...sessionStorage},draft:document.querySelector("#question").value})')
            assert after == before
            explorer.locator('#back').click()
            explorer.wait_for_function("!document.body.classList.contains('busy')&&window.eigenquestionsNavigator.export().context.question==='A KK comparison kept open while inspecting the global map'", timeout=180000)
            restored = explorer.evaluate('window.eigenquestionsNavigator.export()')
            assert restored['snapshot']['view'] == authored['snapshot']['view'] and restored['context'] == authored['context']
            assert read()['datasetSha256'] == initial['datasetSha256']
            passed('overview has no query engine/API/storage side effects; original draft, session and exact authored Back restoration survive in its live tab')

            # Corrupt a static map response but leave its declared hash intact.
            bad = context.new_page()
            bad.route('**/data/overview/map.json', lambda route: route.fulfill(status=200, content_type='application/json', body=b'{"corrupt":true}'))
            bad.goto(origin+'/overview.html', wait_until='domcontentloaded')
            bad.wait_for_function("document.querySelector('#overview-stage').dataset.error==='true'")
            assert not bad.evaluate('window.eigenquestionsOverview.read().ready')
            assert bad.locator('#overview-selected-heading').inner_text() == 'Overview unavailable'
            assert 'match' in bad.locator('#overview-status').inner_text()
            passed('mismatched static data fails visibly before an invented or partial map is accepted')
            report['performance'] = page.evaluate("""async()=>{const frames=[];let last=performance.now(),start=last;await new Promise(resolve=>{function step(now){frames.push(now-last);last=now;if(now-start<500)requestAnimationFrame(step);else resolve()}requestAnimationFrame(step)});return{longTasks:window.__overviewPerf.longTasks,idleFrameIntervalsMs:frames,navigation:performance.getEntriesByType('navigation').map(e=>({domContentLoaded:e.domContentLoadedEventEnd,load:e.loadEventEnd})),resources:performance.getEntriesByType('resource').map(e=>({path:new URL(e.name).pathname,transferBytes:e.transferSize,decodedBytes:e.decodedBodySize,durationMs:e.duration}))}}""")
            report['browserErrors'] = {'overview': errors[page], 'explorer': errors[explorer], 'corruptDataPage': errors[bad]}
            assert not any(report['browserErrors'].values())
            report['overviewRequests'] = [{'path': urlparse(item['url']).path, 'method': item['method']} for item in requests[page]]
            report['passed'] = True
            browser.close()
    except Exception as error:
        report['passed'] = False
        report['failure'] = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}
        try:
            report['lastState'] = read()
            page.screenshot(path=str(out/'overview-failure.png'), full_page=True)
        except Exception:
            pass
    finally:
        if server:
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
        (out/'q006-overview-acceptance.json').write_text(json.dumps(report, indent=2)+'\n')
        print(json.dumps({'passed': report.get('passed', False), 'checks': len(report['checks']), 'report': str(out/'q006-overview-acceptance.json')}))
    if not report.get('passed'):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
