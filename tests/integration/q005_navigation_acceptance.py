#!/usr/bin/env python3
"""Q-005 real-source navigation, explicit restoration and bounded return checks.

Run only in authorized Slurm. Uses the actual frozen corpus and browser worker;
no browser launch on the owner's Mac, injected engine outputs or storage API.
"""
import argparse
import base64
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
from playwright.sync_api import sync_playwright


TARGET_ID = 'unit:0b1a39f68a400ae50d1d97ab6a9bd3e1b087d101231f4ebe49d49088b10b5b81'
CAPSULE_STORAGE = 'eigenquestions:view:v1'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--node', default='node')
    parser.add_argument('--origin')
    args = parser.parse_args()
    if not os.environ.get('SLURM_JOB_ID'):
        raise SystemExit('Run Q-005 browser acceptance only in the authorized Slurm environment.')
    root, output = Path(args.project).resolve(), Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    temp = Path(tempfile.mkdtemp(prefix='eigenquestions-q005-'))
    server = None
    report = {'schemaVersion': '1.0.0', 'request': 'Q-005', 'checks': [], 'screenshots': [],
              'scope': 'Real frozen-corpus Node companion serves the static frontend; navigation runs in the real browser worker. Tests exact source preservation, visible choices and explicit state returns, not semantic optimality or hosted storage.'}

    def passed(name, **detail):
        report['checks'].append({'name': name, 'passed': True, **detail})

    try:
        target = next(unit for unit in json.loads((root / 'data/navigation/units-005.json').read_text()) if unit['id'] == TARGET_ID)
        assert target['lens'] == 'method' and target['paperId'] == '1303.2661'
        if args.origin:
            origin = args.origin.rstrip('/')
        else:
            receipt = temp / 'connection.json'
            server = subprocess.Popen([args.node, str(root / 'bin/navigate.mjs'), 'serve', '--port', '0', '--connection', str(receipt)],
                                      cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            deadline = time.monotonic() + 90
            while not receipt.exists() and time.monotonic() < deadline:
                if server.poll() is not None:
                    raise RuntimeError('The Q-005 test companion failed to start.')
                time.sleep(.1)
            if not receipt.exists():
                raise RuntimeError('The Q-005 test companion startup timed out.')
            origin = json.loads(receipt.read_text())['url'].rstrip('/')
        report['origin'] = origin
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            report['browserVersion'] = browser.version
            context = browser.new_context(viewport={'width': 1440, 'height': 1000}, accept_downloads=True)
            page = context.new_page()
            page.set_default_timeout(30000)
            errors, requests = [], []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.on('request', lambda request: requests.append(request.url))

            def ready(target_page=page):
                target_page.wait_for_function("Boolean(window.eigenquestionsNavigator)&&document.documentElement.dataset.ready==='true'", timeout=180000)

            def idle(target_page=page):
                target_page.wait_for_function("!document.body.classList.contains('busy')", timeout=180000)

            def capsule(target_page=page):
                return target_page.evaluate('window.eigenquestionsNavigator.export()')

            def revision(target_page=page):
                return target_page.evaluate('window.eigenquestionsNavigator.read().revision')

            def changed(previous, target_page=page):
                target_page.wait_for_function('previous=>window.eigenquestionsNavigator.read().revision>previous', arg=previous, timeout=180000)
                idle(target_page)

            def apply(value, target_page=page):
                target_page.evaluate('value=>window.eigenquestionsNavigator.apply(value,{expectedRevision:window.eigenquestionsNavigator.read().revision})', value)
                idle(target_page)

            def current_button(direction_id, target_page=page):
                # Native IDs contain a colon but no selector quotes.
                return target_page.locator(f'.miller-column[data-current="true"] .direction[data-direction-id="{direction_id}"]')

            page.goto(origin, wait_until='domcontentloaded')
            ready()
            assert page.locator('#home-heading').is_visible()
            assert page.locator('#exploration-workspace').is_hidden()
            assert page.locator('#question').input_value() == ''
            assert not any('/data/' in url or '/api/session' in url for url in requests)
            passed('fresh bare home is neutral and ready without corpus or companion requests')

            before = revision()
            page.locator('#question').fill('KK towers')
            page.locator('#explore-button').click()
            changed(before)
            initial = capsule()
            initial_session = initial['snapshot']['session']
            initial_cursor = initial_session['cursor']
            choices = initial['snapshot']['view']['directions']
            assert len(choices) == 5
            target_index = next(index for index, choice in enumerate(choices) if TARGET_ID in choice['seedIds'])
            assert target_index == 3, 'The reported real KK method must still be the fourth representative in this frozen case.'
            chosen = choices[target_index]
            assert chosen['query'] == target['text']
            button = current_button(chosen['id'])
            assert button.locator('.direction-kind').inner_text() == 'Method'
            assert 'Chern' in button.locator('.direction-source-title').inner_text()
            assert len(button.locator('h3').inner_text()) <= 72
            before = revision()
            button.click()
            changed(before)
            selected = capsule()
            selected_session = selected['snapshot']['session']
            selected_state = selected_session['states'][selected_session['cursor']]
            assert selected_state['query'] == target['text']
            assert selected_state['focusIds'] == [TARGET_ID]
            assert selected['context']['question'] == target['text']
            heading = page.locator('#current-question').inner_text()
            assert heading.startswith('Sum one-loop contributions') and len(heading) <= 90 and heading != target['text']
            assert page.locator('#question').input_value() == ''
            assert page.locator('#full-question-details').is_visible()
            page.locator('#full-question-details > summary').click()
            assert page.locator('#full-question-text').inner_text() == target['text']
            assert '1303.2661' in page.locator('#full-question-source').get_attribute('href')
            assert [node for node in selected['snapshot']['view']['nodes'] if node['id'] == TARGET_ID][0]['evidence']['text'] == target['text']
            if page.locator('.session-tools').get_attribute('open') is None:
                page.locator('.session-tools > summary').click()
            with page.expect_download() as download:
                page.locator('#export-view').click()
            exported_file = temp / 'reported-kk-view.json'
            download.value.save_as(str(exported_file))
            assert json.loads(exported_file.read_text()) == selected
            passed('reported fourth KK method keeps its full scientific query, anchor and exact export while heading and blank draft stay concise',
                   seedId=TARGET_ID, fullQueryCharacters=len(target['text']), displayedHeading=heading)

            page.locator('.session-tools').evaluate('(node)=>node.removeAttribute("open")')
            page.locator('#full-question-details').evaluate('(node)=>node.removeAttribute("open")')
            for width, height in [(1440, 1000), (390, 844)]:
                page.set_viewport_size({'width': width, 'height': height})
                page.evaluate('()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
                page.evaluate('()=>{const columns=document.querySelector("#columns");columns.scrollLeft=columns.scrollWidth;window.scrollTo(0,0)}')
                for suffix, full_page in [('full', True), ('viewport', False)]:
                    filename = f'q005-reported-method-{width}-{suffix}.png'
                    page.screenshot(path=str(output / filename), full_page=full_page)
                    report['screenshots'].append(filename)
            page.set_viewport_size({'width': 1440, 'height': 1000})
            page.evaluate('()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')

            previous_column = page.locator(f'.miller-column[data-history-index="{initial_cursor}"]')
            assert previous_column.locator('.direction').count() == 5
            assert previous_column.locator('.direction').evaluate_all('(nodes)=>nodes.map(node=>node.dataset.directionId)') == [choice['id'] for choice in choices]
            followed = previous_column.locator(f'.direction[data-direction-id="{chosen["id"]}"]')
            assert followed.get_attribute('aria-current') == 'step'
            assert followed.locator('.direction-state').inner_text() == 'Followed'
            sibling = choices[0]
            before = revision()
            previous_column.locator(f'.direction[data-direction-id="{sibling["id"]}"]').click()
            changed(before)
            branched = capsule()['snapshot']['session']
            assert branched['states'][:initial_cursor + 1] == initial_session['states'][:initial_cursor + 1]
            assert branched['states'][branched['cursor']]['query'] == sibling['query']
            assert branched['cursor'] == initial_cursor + 1 and len(branched['states']) == initial_cursor + 2
            assert branched['states'][branched['cursor']]['focusIds'] == sorted(set(sibling['seedIds']))
            passed('historical column retains all five genuine sibling choices, marks Followed, and a different sibling branches from its own state')

            # Reproduce the pre-repair six-selection walk. Expected target fields
            # come from the actual clicked choice and current canonical state.
            # A repeated canonical state must be an explicit return, not depth.
            apply(initial)
            walk, walk_capsules, returns = [], [], 0
            for step in range(6):
                before_capsule = capsule()
                before_session = before_capsule['snapshot']['session']
                before_state = before_session['states'][before_session['cursor']]
                directions = before_capsule['snapshot']['view']['directions']
                direction = next(choice for choice in directions if TARGET_ID in choice['seedIds']) if step == 0 else directions[0]
                expected = dict(before_state)
                expected.update(query=' '.join(direction['query'].split()), focusIds=sorted(set(direction['seedIds'])))
                for key in ['intent', 'lens', 'workRelation']:
                    expected[key] = direction.get(key, before_state[key])
                expected.pop('id', None)
                prior_index = next((index for index, state in enumerate(before_session['states'][:before_session['cursor'] + 1])
                                    if {key: value for key, value in state.items() if key != 'id'} == expected), -1)
                button = current_button(direction['id'])
                if prior_index >= 0:
                    visible_step = sum(bool(state['query'].strip()) for state in before_session['states'][:prior_index + 1])
                    assert button.locator('.direction-state').inner_text() == f'Return to step {visible_step}'
                before_revision = revision()
                button.click()
                changed(before_revision)
                after_session = capsule()['snapshot']['session']
                if prior_index >= 0:
                    returns += 1
                    assert after_session['cursor'] == prior_index
                    assert after_session['states'] == before_session['states'], 'Return appended or altered a scientific history state.'
                else:
                    assert after_session['cursor'] == before_session['cursor'] + 1
                    assert len(after_session['states']) == before_session['cursor'] + 2
                after_state = after_session['states'][after_session['cursor']]
                assert {key: value for key, value in after_state.items() if key != 'id'} == expected
                walk_capsules.append(capsule())
                walk.append({'selection': step + 1, 'seedId': direction['seedIds'][0], 'stateId': after_state['id'],
                             'cursor': after_session['cursor'], 'historyLength': len(after_session['states']), 'returnIndex': prior_index})
            assert returns >= 1, 'The known real-data repeat was not exercised.'
            assert max(item['historyLength'] for item in walk) <= len(initial_session['states']) + 4
            assert page.locator('.miller-column[data-current="true"] .direction-state').filter(has_text='Return to step').count() >= 1
            passed('six real selections expose the known cycle as an annotated exact return without false appended depth', returns=returns, walk=walk)

            page.locator('.session-tools').evaluate('(node)=>node.removeAttribute("open")')
            page.locator('#full-question-details').evaluate('(node)=>node.removeAttribute("open")')
            for width, height in [(1440, 1000), (390, 844), (320, 740)]:
                page.set_viewport_size({'width': width, 'height': height})
                page.evaluate('()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'), f'Outer horizontal overflow at {width}px'
                assert page.locator('.miller-column[data-current="true"] .direction').count() == 5
                for position in ['current', 'earlier']:
                    page.evaluate('position=>{const columns=document.querySelector("#columns");columns.scrollLeft=position==="current"?columns.scrollWidth:0;document.querySelector("#path").scrollLeft=position==="current"?100000:0;window.scrollTo(0,0)}', position)
                    page.evaluate('()=>new Promise(resolve=>requestAnimationFrame(resolve))')
                    filename = f'q005-{width}-{position}-full.png'
                    page.screenshot(path=str(output / filename), full_page=True)
                    report['screenshots'].append(filename)
                    filename = f'q005-{width}-{position}-viewport.png'
                    page.screenshot(path=str(output / filename), full_page=False)
                    report['screenshots'].append(filename)
                assert page.locator('.miller-column[data-current="false"] .direction').count() >= 5
            passed('desktop, 390px and 320px preserve full path, current choices and scrollable earlier alternatives without outer overflow')

            # Keep this separate from the native walk: two scientific authored
            # displays can share a native canonical state. A native API return
            # must restore its exact accepted object, not newly computed groups.
            native_a, native_b = walk_capsules[2], walk_capsules[3]
            authored = json.loads(json.dumps(native_a))
            authored['builder'] = {'id': 'q005-author', 'version': '1'}
            authored['context']['question'] = 'Authored interpretation of the Chern-Simons comparison'
            authored['context']['assumptions'] = ['Retain this authored scientific distinction on return.']
            authored['snapshot']['view']['directions'][0]['label'] = 'The author’s retained comparison'
            b_session = native_b['snapshot']['session']
            b_state = b_session['states'][b_session['cursor']]
            b_action = {'type': 'navigate', **{key: b_state[key] for key in ['query', 'focusIds', 'intent', 'lens', 'workRelation', 'constraints']}}
            authored['continuation']['actions'] = [{'id': authored['snapshot']['view']['directions'][0]['id'],
                                                   'label': 'Continue to the neighboring native question', 'action': b_action}]
            authored['continuation']['description'] = 'An explicit native action; return must preserve this authored interpretation.'
            apply(authored)
            page.evaluate('async action=>{await window.eigenquestionsNavigator.navigate(action,{expectedRevision:window.eigenquestionsNavigator.read().revision})}', b_action)
            idle()
            b_with_history = capsule()
            assert b_with_history['snapshot']['view']['stateId'] == native_b['snapshot']['view']['stateId']
            return_direction = next(direction for direction in b_with_history['snapshot']['view']['directions']
                                    if direction['query'] == native_a['snapshot']['view']['query'] and
                                    sorted(set(direction['seedIds'])) == native_a['snapshot']['session']['states'][native_a['snapshot']['session']['cursor']]['focusIds'])
            return_action = {'type': 'select', 'directionId': return_direction['id']}
            page.evaluate('async action=>{await window.eigenquestionsNavigator.navigate(action,{expectedRevision:window.eigenquestionsNavigator.read().revision})}', return_action)
            idle()
            restored_author = capsule()
            assert restored_author['builder'] == authored['builder']
            assert restored_author['context'] == authored['context']
            assert restored_author['snapshot']['view'] == authored['snapshot']['view']
            passed('native API selection returning to a cached authored state restores its exact context, labels, groups and evidence')

            page.evaluate('async action=>{await window.eigenquestionsNavigator.navigate(action,{expectedRevision:window.eigenquestionsNavigator.read().revision})}', b_action)
            idle()
            b_with_history = capsule()
            page.wait_for_function("ids=>{const columns=JSON.parse(localStorage.getItem('eigenquestions:columns:v2')||'[]');return columns.some(item=>item.stateId===ids.a&&item.authored)&&columns.some(item=>item.stateId===ids.b)}",
                                   arg={'a': authored['snapshot']['view']['stateId'], 'b': b_with_history['snapshot']['view']['stateId']})
            # Reload really clears the full in-memory capsule cache while retaining
            # the compact authored-history marker. No test code edits either cache.
            page.reload(wait_until='domcontentloaded')
            ready()
            assert page.locator('#home-heading').is_visible()
            page.locator('#resume-view').click()
            idle()
            assert capsule() == b_with_history
            before_revision = revision()
            rejected = page.evaluate('async action=>{try{await window.eigenquestionsNavigator.navigate(action,{expectedRevision:window.eigenquestionsNavigator.read().revision});return {rejected:false}}catch(error){return {rejected:true,message:error.message}}}', return_action)
            assert rejected['rejected'] and 'no longer cached' in rejected['message']
            assert revision() == before_revision and capsule() == b_with_history
            assert 'no longer cached' in page.locator('#status').inner_text()
            passed('native API return after authored full-cache loss rejects visibly without replacing the current view or fabricating authored history')

            # Seed a saved view, then reload normally: a real explicit Resume
            # must restore it, rather than the test initializer doing so.
            home_context = browser.new_context(viewport={'width': 390, 'height': 844})
            home = home_context.new_page()
            home.on('pageerror', lambda error: errors.append(str(error)))
            home_requests = []
            home.on('request', lambda request: home_requests.append(request.url))
            home.goto(origin, wait_until='domcontentloaded')
            ready(home)
            home.evaluate('({key,value})=>localStorage.setItem(key,JSON.stringify(value))', {'key': CAPSULE_STORAGE, 'value': selected})
            home_requests.clear()
            home.reload(wait_until='domcontentloaded')
            ready(home)
            assert home.locator('#home-heading').is_visible() and home.locator('#exploration-workspace').is_hidden()
            assert home.locator('#question').input_value() == ''
            assert home.locator('#resume-prior').is_visible() and home.locator('#resume-label').inner_text().strip()
            assert not any('/data/' in url or '/api/session' in url for url in home_requests)
            home.screenshot(path=str(output / 'q005-saved-neutral-home-390.png'), full_page=True)
            report['screenshots'].append('q005-saved-neutral-home-390.png')
            before = revision(home)
            home.locator('#resume-view').click()
            changed(before, home)
            assert capsule(home) == selected
            assert home.locator('#exploration-workspace').is_visible()
            assert not any('/data/' in url or '/api/session' in url for url in home_requests)
            passed('bare home with a saved native view remains neutral and cheap; explicit Resume restores the exact full capsule without recomputation')

            home.locator('#reset').click()
            ready(home)
            idle(home)
            assert home.locator('#home-heading').is_visible() and home.locator('#exploration-workspace').is_hidden()
            assert home.evaluate('key=>JSON.parse(localStorage.getItem(key))', CAPSULE_STORAGE) == selected
            home.reload(wait_until='domcontentloaded')
            ready(home)
            assert home.locator('#resume-view').is_visible()
            before = revision(home)
            home.locator('#resume-view').click()
            changed(before, home)
            assert capsule(home) == selected
            passed('New path and subsequent bare reload preserve the last nonempty view for explicit resumption')

            home.add_init_script("""window.__q005Headings=[];new MutationObserver(()=>{const node=document.querySelector('#current-question');if(node&&node.textContent)window.__q005Headings.push(node.textContent)}).observe(document,{childList:true,subtree:true,characterData:true});""")
            focus_state = initial_session['states'][initial_cursor]
            encoded = base64.urlsafe_b64encode(json.dumps(focus_state, ensure_ascii=False, separators=(',', ':')).encode()).decode().rstrip('=')
            home.goto(origin + '/#focus=' + encoded, wait_until='domcontentloaded')
            ready(home)
            idle(home)
            focused = capsule(home)
            assert focused['context']['question'] == 'KK towers'
            assert focused['snapshot']['view']['stateId'] == focus_state['id']
            assert home.locator('#home-heading').is_hidden() and home.locator('#exploration-workspace').is_visible()
            assert home.locator('html').get_attribute('data-accepted-count') == '1'
            assert not any('Sum one-loop contributions' in text for text in home.evaluate('window.__q005Headings'))
            assert home.evaluate('location.hash').startswith('#focus=')
            passed('an explicit focus URL takes precedence over saved history with one accepted view and no transient restored method')

            report['pageErrors'] = errors
            assert not errors
            browser.close()
        report['passed'] = True
    except Exception as error:
        report['passed'] = False
        report['failureType'] = type(error).__name__
        report['failure'] = str(error)[:1500]
        raise
    finally:
        (output / 'q005-navigation-acceptance.json').write_text(json.dumps(report, indent=2) + '\n')
        if server:
            server.terminate()
            try:
                server.wait(timeout=10)
            except subprocess.TimeoutExpired:
                server.kill()
        shutil.rmtree(temp, ignore_errors=True)


if __name__ == '__main__':
    main()
