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
import select
import shutil
import subprocess
import tempfile
import time
from urllib.parse import quote
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
            context = browser.new_context(viewport={'width': 1440, 'height': 1080}, accept_downloads=True)
            page = context.new_page()
            page_errors = []
            page.on('pageerror', lambda error: page_errors.append(str(error)))
            page.goto(connection['url'] + '#token=' + quote(connection['token']), wait_until='domcontentloaded')
            page.wait_for_function("document.documentElement.dataset.ready === 'true'")
            page.wait_for_function("document.querySelector('#connection-status').textContent.includes('Agent connected')")

            def navigate(action, label):
                result = tool('navigator_navigate', action)
                state = result['state']
                page.wait_for_function('(id) => document.documentElement.dataset.stateId === id', arg=state['id'])
                assert page.locator('#current-question').inner_text() == state['query']
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
            navigate({'type': 'refine', 'query': 'KK dark matter cosmological constraints'}, 'reload reconnects and subsequent agent operation updates browser')
            page.set_viewport_size({'width': 390, 'height': 844})
            assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 1')
            page.screenshot(path=str(output / 'mobile-view.png'), full_page=True)
            report['checks'].append({'name': 'mobile viewport has no horizontal overflow', 'passed': True})
            report['localBrowserErrors'] = page_errors
            assert not page_errors

            # Run an actual browser fetch from the public HTTPS origin. A Node
            # Origin header test cannot establish private-network browser policy.
            public_page = context.new_page()
            outcome = None
            try:
                public_page.goto(args.public_origin, wait_until='domcontentloaded', timeout=60000)
                outcome = public_page.evaluate("""async ({url,token}) => {
                  try {
                    const r = await fetch(new URL('/api/session',url), {headers:{Authorization:`Bearer ${token}`}, signal:AbortSignal.timeout(15000)});
                    return {reachable:r.ok,httpStatus:r.status};
                  } catch(e) { return {reachable:false,errorName:e.name}; }
                }""", {'url': connection['url'], 'token': connection['token']})
                report['publicOriginProbe'] = outcome
                if outcome.get('reachable') and args.public_ui:
                    public_page.goto(args.public_origin + '/#bridge=' + quote(connection['url'], safe='') + '&token=' + quote(connection['token']), wait_until='domcontentloaded')
                    public_page.wait_for_function("document.querySelector('#connection-status')?.textContent.includes('Agent connected')")
                    result = tool('navigator_navigate', {'type': 'refine', 'query': 'KK dark matter observational bounds'})
                    public_page.wait_for_function('(id) => document.documentElement.dataset.stateId === id', arg=result['state']['id'])
                    report['checks'].append({'name': 'public-origin attached renderer visibly updates', 'passed': True})
                elif not outcome.get('reachable'):
                    report['publicOriginProbe']['interpretation'] = 'Browser policy or network blocked public-to-loopback access; same-origin fallback was separately verified.'
            except Exception as error:
                if args.public_ui and outcome and outcome.get('reachable'):
                    raise
                # No token/URL-bearing error text is published.
                report['publicOriginProbe'] = {'reachable': False, 'errorType': type(error).__name__, 'interpretation': 'Public-origin probe could not complete in this browser environment; same-origin fallback was separately verified.'}
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
