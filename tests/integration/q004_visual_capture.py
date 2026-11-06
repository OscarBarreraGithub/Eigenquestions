#!/usr/bin/env python3
"""Capture actual Q-004 layouts in authorized Slurm Chromium.

This is a visual fixture, not startup/storage acceptance. It works with the prior
runtime and the new HTML/CSS. Build the frozen project before invoking it.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
from urllib.parse import quote


VIEWPORTS = [(1440, 1000), (1024, 900), (390, 844), (320, 740)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--node', default='node')
    args = parser.parse_args()
    if not os.environ.get('SLURM_JOB_ID'):
        raise SystemExit('Run visual captures only in the authorized Slurm environment.')
    from playwright.sync_api import sync_playwright

    root, output = Path(args.project).resolve(), Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix='eigenquestions-q004-visual-'))
    receipt = temporary / 'connection.json'
    bridge = None
    report = {
        'schemaVersion': '1.0.0', 'request': 'Q-004',
        'scope': 'Visual fixture using the frozen runtime and real physics engine; no startup or stored-view acceptance.',
        'environment': 'authorized Slurm Chromium', 'captures': [],
    }
    try:
        bridge = subprocess.Popen(
            [args.node, str(root / 'bin/navigate.mjs'), 'serve', '--port', '0', '--connection', str(receipt)],
            cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True,
        )
        deadline = time.monotonic() + 90
        while not receipt.exists() and time.monotonic() < deadline:
            if bridge.poll() is not None:
                raise RuntimeError('Visual fixture companion failed to start.')
            time.sleep(.1)
        if not receipt.exists():
            raise RuntimeError('Visual fixture companion startup timed out.')
        connection = json.loads(receipt.read_text())

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            report['browserVersion'] = browser.version
            context = browser.new_context(viewport={'width': 1440, 'height': 1000})
            page = context.new_page()
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error).replace(connection['token'], '[redacted]')))
            page.goto(connection['url'] + '#token=' + quote(connection['token']), wait_until='domcontentloaded')
            page.wait_for_function("document.documentElement.dataset.ready === 'true'", timeout=180000)

            def wait_idle():
                page.wait_for_function("!document.body.classList.contains('busy')", timeout=90000)

            def options(opened):
                toggle = page.locator('#options-toggle')
                if (toggle.get_attribute('aria-expanded') == 'true') != opened:
                    toggle.click()

            def submit(query, intent='explore', transition='refine'):
                before = page.locator('html').get_attribute('data-state-id')
                options(True)
                page.locator('#question').fill(query)
                page.locator('#intent').select_option(intent)
                page.locator('#transition').select_option(transition)
                page.locator('#explore-button').click()
                page.wait_for_function('(before) => document.documentElement.dataset.stateId !== before', arg=before, timeout=90000)
                wait_idle()
                options(False)
                assert page.locator('.miller-column[data-current="true"] .direction').count() == 5

            def capture(name, width, height, top=True):
                page.set_viewport_size({'width': width, 'height': height})
                page.evaluate("""() => {
                  const host = document.querySelector('#columns'); host.scrollLeft = host.scrollWidth;
                  const current = document.querySelector('.miller-column[data-current="true"]');
                  if (current) current.scrollTop = 0;
                }""")
                if top:
                    page.evaluate("scrollTo({top: 0, behavior: 'instant'})")
                page.evaluate('() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))')
                filename = f'{name}-{width}.png'
                page.screenshot(path=str(output / filename), full_page=False)
                metrics = page.evaluate("""() => {
                  const box = selector => {const el=document.querySelector(selector);if(!el)return null;const r=el.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height};};
                  const selectors='#agent-open,#reset,#explore-button,#options-toggle,#back,#broaden,#browse-prev,#browse-next,#path button,.miller-column[data-current="true"] .direction,.miller-column[data-current="true"] .direction-evidence';
                  const smallTargets=[...document.querySelectorAll(selectors)].filter(el=>el.getClientRects().length).map(el=>({id:el.id||el.className,width:el.getBoundingClientRect().width,height:el.getBoundingClientRect().height})).filter(r=>r.width<43.9||r.height<43.9);
                  const direction=document.querySelector('.miller-column[data-current="true"] .direction h3');
                  return {documentWidth:document.documentElement.scrollWidth,viewportWidth:innerWidth,firstDirection:box('.miller-column[data-current="true"] .direction'),directionFont:direction?getComputedStyle(direction).fontSize:null,smallTargets};
                }""")
                report['captures'].append({'file': filename, 'width': width, 'height': height, **metrics})

            wait_idle()
            submit('KK towers', transition='pivot')
            for width, height in VIEWPORTS:
                capture('kk', width, height)
            submit('KK towers as dark matter', intent='phenomenology')
            for width, height in VIEWPORTS:
                capture('dark-matter', width, height)

            for width, height in [VIEWPORTS[0], VIEWPORTS[2]]:
                page.set_viewport_size({'width': width, 'height': height})
                options(True)
                capture('options', width, height)
                options(False)
                page.locator('#agent-open').click()
                capture('agent-dialog', width, height)
                page.locator('#agent-close').click()
                page.locator('.miller-column[data-current="true"] .direction-evidence').first.click()
                page.locator('.reading-pane').scroll_into_view_if_needed()
                capture('sources', width, height, top=False)

            before_reset = page.locator('html').get_attribute('data-state-id')
            page.locator('#reset').click()
            page.wait_for_function('(before) => document.documentElement.dataset.stateId !== before', arg=before_reset, timeout=90000)
            wait_idle()
            page.wait_for_function("document.querySelector('#question').value === ''")
            assert page.locator('.miller-column[data-current="true"] .direction').count() == 0
            for width, height in VIEWPORTS:
                capture('new-path', width, height)
            report['pageErrors'] = errors
            report['passed'] = not errors
            browser.close()
    except Exception as error:
        report['passed'] = False
        report['failureType'] = type(error).__name__
        raise
    finally:
        (output / 'q004-visual-capture.json').write_text(json.dumps(report, indent=2) + '\n')
        if bridge:
            bridge.terminate()
            try:
                bridge.wait(timeout=10)
            except subprocess.TimeoutExpired:
                bridge.kill()
                bridge.wait()
        shutil.rmtree(temporary, ignore_errors=True)


if __name__ == '__main__':
    main()
