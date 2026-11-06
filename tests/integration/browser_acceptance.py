#!/usr/bin/env python3
"""Run only in the authorized Slurm Playwright environment, never via a local browser workaround.

Example: PYTHONPATH=<ui-deps> PLAYWRIGHT_BROWSERS_PATH=<browsers> <python>
  tests/integration/browser_acceptance.py --project <checkout> --output <artifact-dir>

Starts a temporary loopback bridge and MCP child unless --connection is supplied.
Published reports contain no token, local path, or private connection URL.
"""
import argparse
import json
import os
from pathlib import Path
import re
import select
import shutil
import subprocess
import tempfile
import time
from urllib.parse import quote, urlsplit
from playwright.sync_api import sync_playwright


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--connection')
    parser.add_argument('--node', default='node')
    parser.add_argument('--public-origin', default='https://eigenquestions.com')
    parser.add_argument('--public-ui', action='store_true', help='After release, also verify public renderer attachment when browser policy permits it')
    args = parser.parse_args()
    root = Path(args.project).resolve()
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix='eigenquestions-browser-'))
    bridge = None
    mcp = None
    report = {'schemaVersion': '1.0.0', 'environment': 'authorized Slurm Chromium', 'checks': [], 'publicOrigin': args.public_origin}
    try:
        connection_file = Path(args.connection) if args.connection else temporary / 'connection.json'
        if not args.connection:
            bridge = subprocess.Popen([args.node, str(root / 'bin/navigate.mjs'), 'serve', '--port', '0', '--connection', str(connection_file)], cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
            deadline = time.monotonic() + 90
            while not connection_file.exists() and time.monotonic() < deadline:
                if bridge.poll() is not None:
                    raise RuntimeError('Bridge failed to start; inspect process stderr privately')
                time.sleep(.1)
            if not connection_file.exists():
                raise RuntimeError('Bridge start timed out')
        connection = json.loads(connection_file.read_text())
        def sanitize(value):
            text = str(value).replace(connection['token'], '[redacted]')
            return re.sub(r'https?://[^\s\"\'<>]+', '[url]', text)[:700]
        mcp = subprocess.Popen([args.node, str(root / 'bin/mcp-navigator.mjs'), '--connection', str(connection_file)], cwd=root, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
        sequence = 0

        def rpc(method, params):
            nonlocal sequence
            sequence += 1
            mcp.stdin.write(json.dumps({'jsonrpc': '2.0', 'id': sequence, 'method': method, 'params': params}) + '\n')
            mcp.stdin.flush()
            ready, _, _ = select.select([mcp.stdout], [], [], 90)
            if not ready:
                raise RuntimeError('MCP response timed out')
            result = json.loads(mcp.stdout.readline())
            if result.get('error'):
                raise RuntimeError(result['error']['message'])
            return result['result']

        def tool(name, arguments=None):
            result = rpc('tools/call', {'name': name, 'arguments': arguments or {}})
            if result.get('isError'):
                raise RuntimeError(result['content'][0]['text'])
            return result.get('structuredContent') or json.loads(result['content'][0]['text'])

        rpc('initialize', {'protocolVersion': '2025-06-18', 'clientInfo': {'name': 'independent-browser-acceptance', 'version': '1.0.0'}, 'capabilities': {}})
        assert len(rpc('tools/list', {})['tools']) == 6

        with sync_playwright() as playwright:
            # No mixed-content/private-network security bypass flags.
            browser = playwright.chromium.launch(headless=True)
            report['browserVersion'] = browser.version
            context = browser.new_context(viewport={'width': 1440, 'height': 1080}, accept_downloads=True)
            page = context.new_page()
            page_errors = []
            page.on('pageerror', lambda error: page_errors.append(str(error)))
            page.goto(connection['url'] + '#token=' + quote(connection['token']), wait_until='domcontentloaded')
            page.wait_for_function("document.documentElement.dataset.ready === 'true'")
            page.wait_for_function("document.querySelector('#connection-status').textContent.includes('Agent connected')")

            def show_geometry(target):
                # Q-002 makes text primary; Q-001 geometry checks explicitly
                # open its optional tab rather than requiring a primary chart.
                if target.locator('#view-geometry').count():
                    target.locator('#view-geometry').click()

            def navigate(action, label):
                result = tool('navigator_navigate', action)
                state = result['state']
                page.wait_for_function('(id) => document.documentElement.dataset.stateId === id', arg=state['id'])
                assert page.locator('#current-question').inner_text() == state['query']
                show_geometry(page)
                if result['view']['chart'].get('fitScope') == 'direction-centroids':
                    assert page.locator('.chart-direction').count() == len(result['view']['directions'])
                else:
                    assert page.locator('.chart-node[data-source-id]').count() == result['view']['nodeCount']
                assert page.locator('#directions .direction').count() == len(result['view']['directions'])
                deadline = time.monotonic() + 10
                while not tool('navigator_state')['browserStatus']['acknowledgedCurrent'] and time.monotonic() < deadline:
                    page.wait_for_timeout(100)
                assert tool('navigator_state')['browserStatus']['acknowledgedCurrent']
                report['checks'].append({'name': label, 'passed': True, 'stateId': state['id'], 'nodeCount': result['view']['nodeCount'], 'directionCount': len(result['view']['directions']), 'renderAcknowledged': True})
                return result

            kk = navigate({'type': 'navigate', 'query': 'KK towers'}, 'MCP KK query visibly updates browser')
            if kk['view']['chart'].get('fitScope') == 'direction-centroids':
                page.locator('#show-sources').check()
                assert page.locator('.chart-node[data-source-id]').count() == kk['view']['nodeCount']
                page.locator('#show-sources').uncheck()
                report['checks'].append({'name': 'five-direction primary chart and optional full source overlay', 'passed': True})
            dm = navigate({'type': 'refine', 'query': 'what if they are dark matter?', 'intent': 'phenomenology'}, 'pronoun refinement preserves context')
            assert any('dark dimension' in n['title'].lower() for n in dm['view']['nodes'][:12])
            assert kk['view']['nodes'][0]['id'] != dm['view']['nodes'][0]['id']
            decay = navigate({'type': 'refine', 'query': 'how do they decay?'}, 'deeper follow-up uses refreshed context')
            assert any('dark dimension' in n['title'].lower() for n in decay['view']['nodes'][:12])
            dark = navigate({'type': 'refine', 'query': 'Dark Dimension swampland dark matter'}, 'Dark Dimension is source-grounded')
            page.screenshot(path=str(output / 'owner-journey.png'), full_page=True)
            back = navigate({'type': 'back'}, 'back restores exact state')
            assert back['state']['id'] == decay['state']['id']
            exported = tool('navigator_export')
            assert connection['token'] not in json.dumps(exported)
            navigate({'type': 'pivot', 'query': 'black hole evaporation'}, 'held-out cross-field pivot')
            navigate({'type': 'refine', 'query': 'the information paradox'}, 'held-out information refinement')
            islands = navigate({'type': 'refine', 'query': 'islands and replica wormholes', 'intent': 'derive'}, 'held-out islands refinement')
            assert any('replica wormhole' in (n['title'] + n['evidence']['text']).lower() or 'island' in n['evidence']['text'].lower() for n in islands['view']['nodes'][:12])
            imported = tool('navigator_import', {'payload': exported})
            page.wait_for_function('(id) => document.documentElement.dataset.stateId === id', arg=imported['state']['id'])
            assert imported['state']['id'] == decay['state']['id']
            report['checks'].append({'name': 'MCP export/import restores geometry and browser', 'passed': True})
            page.reload(wait_until='domcontentloaded')
            page.wait_for_function("document.querySelector('#connection-status').textContent.includes('Agent connected')")
            mobile_state = navigate({'type': 'refine', 'query': 'KK dark matter cosmological constraints'}, 'reload reconnects and subsequent agent operation updates browser')
            page.set_viewport_size({'width': 390, 'height': 844})
            page.locator('.compact-chart').wait_for()
            assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 1')
            markers = page.locator('.chart-direction')
            assert markers.count() == 5
            chart_box = page.locator('#chart').bounding_box()
            for index in range(markers.count()):
                marker = markers.nth(index)
                assert marker.is_visible()
                box = marker.locator('.direction-dot').bounding_box()
                assert box['width'] >= 30 and box['height'] >= 30
                hit = marker.locator('.direction-hit-target').bounding_box()
                assert hit['width'] >= 43 and hit['height'] >= 43
                assert marker.locator('.direction-marker').evaluate('(el) => parseFloat(getComputedStyle(el).fontSize)') >= 12
                assert box['x'] >= max(0, chart_box['x']) - 1
                assert box['x'] + box['width'] <= min(390, chart_box['x'] + chart_box['width']) + 1
                assert box['y'] >= chart_box['y'] - 1 and box['y'] + box['height'] <= chart_box['y'] + chart_box['height'] + 1
            assert page.locator('#directions h3').all_inner_texts() == [direction['label'] for direction in mobile_state['view']['directions']]
            page.screenshot(path=str(output / 'mobile-view.png'), full_page=True)
            page.locator('#chart').scroll_into_view_if_needed()
            page.screenshot(path=str(output / 'mobile-chart-viewport.png'), full_page=False)
            report['checks'].append({'name': 'mobile viewport has no horizontal overflow', 'passed': True})
            report['checks'].append({'name': 'five mobile markers have legible numbers, touch targets and matching full direction cards', 'passed': True})
            selected_query = mobile_state['view']['directions'][0]['query']
            selected_from = mobile_state['state']['id']
            page.locator('.chart-direction .direction-dot').first.click()
            page.wait_for_function('(old) => document.documentElement.dataset.stateId !== old', arg=selected_from)
            assert page.locator('#current-question').inner_text() == selected_query
            page.locator('#back').click()
            page.wait_for_function('(expected) => document.documentElement.dataset.stateId === expected', arg=selected_from)
            report['checks'].append({'name': 'human mobile marker selection changes the question and Back restores the state', 'passed': True})
            report['localBrowserErrors'] = page_errors
            assert not page_errors

            # Run an actual browser fetch from the public HTTPS origin. A Node
            # Origin header test cannot establish private-network browser policy.
            public_page = context.new_page()
            diagnostics = {'console': [], 'requestFailures': [], 'permissionChanges': 'None: read-only queries; no permission grants or browser security bypasses.'}
            def public_console(message):
                if message.type in ('warning', 'error') and len(diagnostics['console']) < 12:
                    diagnostics['console'].append({'type': message.type, 'text': sanitize(message.text)})
            def public_request_failed(request):
                if len(diagnostics['requestFailures']) < 12:
                    target = 'loopback' if urlsplit(request.url).hostname in ('127.0.0.1', 'localhost', '::1') else 'public-or-other'
                    diagnostics['requestFailures'].append({'target': target, 'resourceType': request.resource_type, 'reason': sanitize(request.failure)})
            public_page.on('console', public_console)
            public_page.on('requestfailed', public_request_failed)
            def permission_states():
                return public_page.evaluate("""async () => {
                  const out={};
                  for(const name of ['local-network-access','local-network','loopback-network']) {
                    try {out[name]=(await navigator.permissions.query({name})).state;}
                    catch(e) {out[name]='unsupported:'+e.name;}
                  }
                  return out;
                }""")
            report['publicOriginDiagnostics'] = diagnostics
            outcome = None
            try:
                public_response = public_page.goto(args.public_origin, wait_until='domcontentloaded', timeout=60000)
                diagnostics['contentSecurityPolicy'] = sanitize(public_response.headers.get('content-security-policy', 'absent'))
                diagnostics['permissionsPolicy'] = sanitize(public_response.headers.get('permissions-policy', 'absent'))
                diagnostics['permissionsBefore'] = permission_states()
                outcome = public_page.evaluate("""async ({url,token}) => {
                  try {
                    const r = await fetch(new URL('/api/session',url), {headers:{Authorization:`Bearer ${token}`}, signal:AbortSignal.timeout(15000)});
                    return {reachable:r.ok,httpStatus:r.status};
                  } catch(e) { return {reachable:false,errorName:e.name,errorMessage:e.message}; }
                }""", {'url': connection['url'], 'token': connection['token']})
                if 'errorMessage' in outcome:
                    outcome['errorMessage'] = sanitize(outcome['errorMessage'])
                diagnostics['permissionsAfter'] = permission_states()
                report['publicOriginProbe'] = outcome
                if outcome.get('reachable') and args.public_ui:
                    public_page = context.new_page()
                    public_page.on('console', public_console)
                    public_page.on('requestfailed', public_request_failed)
                    public_page.goto(args.public_origin + '/#bridge=' + quote(connection['url'], safe='') + '&token=' + quote(connection['token']), wait_until='domcontentloaded')
                    public_page.wait_for_function("document.querySelector('#connection-status')?.textContent.includes('Agent connected')")
                    result = tool('navigator_navigate', {'type': 'refine', 'query': 'KK dark matter observational bounds'})
                    public_page.wait_for_function('(id) => document.documentElement.dataset.stateId === id', arg=result['state']['id'])
                    report['checks'].append({'name': 'public-origin attached renderer visibly updates', 'passed': True})
                elif not outcome.get('reachable'):
                    report['publicOriginProbe']['interpretation'] = 'Browser policy, CSP or network blocked public-to-loopback access; same-origin fallback was separately verified.'
            except Exception as error:
                if args.public_ui and outcome and outcome.get('reachable'):
                    raise
                # No token/URL-bearing error text is published.
                report['publicOriginProbe'] = {'reachable': False, 'errorType': type(error).__name__, 'interpretation': 'Public-origin probe could not complete in this browser environment; same-origin fallback was separately verified.'}

            if args.public_ui and not report['publicOriginProbe'].get('reachable'):
                # Opening a printed launch link creates a new document. Changing
                # only the fragment on the already-loaded probe page would not
                # rerun the app's startup code and would test a different action.
                public_page = context.new_page()
                public_page.on('console', public_console)
                public_page.on('requestfailed', public_request_failed)
                public_page.goto(args.public_origin + '/#bridge=' + quote(connection['url'], safe='') + '&token=' + quote(connection['token']), wait_until='domcontentloaded', timeout=60000)
                public_page.wait_for_function("document.documentElement.dataset.ready === 'true'", timeout=180000)
                assert public_page.locator('#connection-status').inner_text() == 'Browser session'
                show_geometry(public_page)
                assert public_page.locator('.chart-direction').count() == 5
                public_page.locator('#agent-open').click()
                public_page.locator('#agent-dialog details summary').click()
                fallback_message = public_page.locator('#bridge-message')
                diagnostics['blockedLaunchFallback'] = {'documentLaunch': 'fresh-tab', 'connectionStatus': public_page.locator('#connection-status').inner_text(), 'messageAfterOpeningAgentDetails': sanitize(fallback_message.inner_text()), 'messageVisible': fallback_message.is_visible(), 'neverClaimedConnected': 'Agent connected' not in public_page.locator('#connection-status').inner_text()}
                assert fallback_message.is_visible()
                assert re.search(r'local URL|same.origin|loopback', fallback_message.inner_text(), re.I)
                assert 'Agent connected' not in public_page.locator('#connection-status').inner_text()
                diagnostics['permissionsAfterBlockedLaunch'] = permission_states()
                report['checks'].append({'name': 'blocked public launch recovers browser computation and shows same-origin guidance without claiming connection', 'passed': True})

            # The public static app must work independently even when its origin
            # cannot reach loopback. Use a clean context without bridge state.
            if args.public_ui:
                public_context = browser.new_context(viewport={'width': 1440, 'height': 1080}, accept_downloads=True)
                standalone = public_context.new_page()
                public_errors = []
                standalone.on('pageerror', lambda error: public_errors.append(str(error)))
                standalone.goto(args.public_origin, wait_until='domcontentloaded', timeout=60000)
                standalone.wait_for_function("document.documentElement.dataset.ready === 'true'", timeout=180000)
                assert standalone.locator('#connection-status').inner_text() == 'Browser session'
                show_geometry(standalone)
                assert standalone.locator('.chart-direction').count() == 5

                def public_question(query, intent='explore', relation='either', transition='refine'):
                    old_id = standalone.locator('html').get_attribute('data-state-id')
                    standalone.locator('#question').fill(query)
                    standalone.locator('#intent').select_option(intent)
                    standalone.locator('#work-relation').select_option(relation)
                    standalone.locator('#transition').select_option(transition)
                    standalone.locator('#explore-button').click()
                    standalone.wait_for_function('(old) => document.documentElement.dataset.stateId !== old', arg=old_id, timeout=60000)
                    assert standalone.locator('#current-question').inner_text() == query
                    assert standalone.locator('#directions .direction').count() == 5
                    return standalone.locator('html').get_attribute('data-state-id')

                public_question('KK towers as dark matter', 'phenomenology')
                assert 'dark dimension' in standalone.locator('#evidence').inner_text().lower()
                report['checks'].append({'name': 'public static app independently loads corpus and computes contextual UI question', 'passed': True})
                on_id = public_question('KK towers', 'recent', 'on', 'pivot')
                on_sources = standalone.locator('.evidence-card').evaluate_all('(nodes) => nodes.map(n => n.dataset.sourceId)')
                using_id = public_question('KK towers', 'recent', 'using', 'pivot')
                using_sources = standalone.locator('.evidence-card').evaluate_all('(nodes) => nodes.map(n => n.dataset.sourceId)')
                assert on_id != using_id and on_sources != using_sources
                report['checks'].append({'name': 'public ON versus USING controls change ranked evidence', 'passed': True})
                label_layout = standalone.evaluate("""() => {
                  const box=el=>{const r=el.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height};};
                  const overlaps=(a,b,pad=1)=>a.x<b.x+b.w+pad&&a.x+a.w+pad>b.x&&a.y<b.y+b.h+pad&&a.y+a.h+pad>b.y;
                  const labels=[...document.querySelectorAll('.direction-label')];
                  const markers=[...document.querySelectorAll('.direction-dot')];
                  const labelBoxes=labels.map(box),markerBoxes=markers.map(box);
                  return {
                    labelCount:labels.length,markerCount:markers.length,
                    markerNumberCount:document.querySelectorAll('.direction-marker').length,
                    labelMarkerOverlap:labelBoxes.some(a=>markerBoxes.some(b=>overlaps(a,b))),
                    labelLabelOverlap:labelBoxes.some((a,i)=>labelBoxes.slice(i+1).some(b=>overlaps(a,b))),
                    labelsPaintedBeforeMarkers:labels.every(label=>markers.every(marker=>Boolean(label.compareDocumentPosition(marker)&Node.DOCUMENT_POSITION_FOLLOWING)))
                  };
                }""")
                assert label_layout['markerCount'] == 5 and label_layout['markerNumberCount'] == 5
                assert not label_layout['labelMarkerOverlap'] and not label_layout['labelLabelOverlap']
                assert label_layout['labelsPaintedBeforeMarkers']
                report['publicUsingLabelLayout'] = label_layout
                report['checks'].append({'name': 'public USING chart labels avoid every marker and label with markers painted on top', 'passed': True})
                before_select = using_id
                standalone.locator('#directions .direction').first.click()
                standalone.wait_for_function('(old) => document.documentElement.dataset.stateId !== old', arg=before_select)
                standalone.locator('#back').click()
                standalone.wait_for_function('(expected) => document.documentElement.dataset.stateId === expected', arg=using_id)
                with standalone.expect_download() as download_info:
                    standalone.locator('#export').click()
                export_path = output / 'public-browser-session.json'
                download_info.value.save_as(str(export_path))
                assert connection['token'] not in export_path.read_text()
                public_question('black hole evaporation', transition='pivot')
                standalone.locator('#import-file').set_input_files(str(export_path))
                standalone.wait_for_function('(expected) => document.documentElement.dataset.stateId === expected', arg=using_id)
                standalone.reload(wait_until='domcontentloaded')
                standalone.wait_for_function('(expected) => document.documentElement.dataset.stateId === expected', arg=using_id, timeout=180000)
                report['checks'].append({'name': 'public direction selection, backtracking, export/import and reload reproduce the same state', 'passed': True})
                standalone.screenshot(path=str(output / 'public-static-view.png'), full_page=True)
                report['publicBrowserErrors'] = public_errors
                assert not public_errors
                public_context.close()
            browser.close()
        report['passed'] = True
    except Exception as error:
        report['passed'] = False
        report['failureType'] = type(error).__name__
        # Keep the report shareable; paths and session URLs may occur in traceback.
        raise
    finally:
        (output / 'browser-acceptance.json').write_text(json.dumps(report, indent=2) + '\n')
        if mcp:
            mcp.terminate()
            try: mcp.wait(timeout=10)
            except subprocess.TimeoutExpired: mcp.kill()
        if bridge:
            bridge.terminate()
            try: bridge.wait(timeout=10)
            except subprocess.TimeoutExpired: bridge.kill()
        shutil.rmtree(temporary, ignore_errors=True)


if __name__ == '__main__':
    main()
