#!/usr/bin/env python3
"""Bounded visual-reference capture; run only in the authorized Slurm environment.

Does not test or modify the product. Visits three public arXiv references, plus
optional loopback-hosted old viewers, at desktop and mobile sizes. No browser
security overrides, account actions, external clicks, or consent changes.

Example:
  python tests/design/reference_capture.py --output <artifacts>
    --old-viewer-url http://127.0.0.1:4180/explore/tree/
    --v4-viewer-url http://127.0.0.1:4181/

The coordinator stages/serves historical source separately. Local-browser
execution is intentionally refused; syntax checking does not launch a browser.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from urllib.parse import urlsplit


SELECTORS = [
    'body', 'header', '.ds-site-header', 'h1', 'h1.title',
    '#dlpage', '#dlpage .list-title', '#dlpage .list-authors',
    '#dlpage .list-subjects', '#dlpage .list-identifier a',
    '.arxiv-result', '.arxiv-result .title', '.arxiv-result .abstract',
    '#abs', '#abs .authors', '#abs blockquote.abstract',
    '.site-head', '.brand', '#search', '.breadcrumb', '.crumb',
    '.columns', '.column', '.column-head', '.col-row', '.col-label',
    '.detail-inner', '.node-title', '.summary', '.source-description',
    'input[type="text"]', 'input[type="search"]', 'button', 'a',
]

STYLE_CAPTURE = """(selectors) => {
  const props = ['fontFamily', 'fontSize', 'fontWeight', 'lineHeight',
    'letterSpacing', 'color', 'backgroundColor', 'borderTop', 'borderBottom',
    'borderLeft', 'borderRight', 'borderRadius', 'padding', 'margin',
    'maxWidth', 'minHeight', 'display', 'overflowX', 'overflowY'];
  const visible = el => el.getClientRects().length &&
    getComputedStyle(el).visibility !== 'hidden';
  const elements = selectors.map(selector => {
    const el = [...document.querySelectorAll(selector)].find(visible);
    if (!el) return {selector, found: false};
    const style = getComputedStyle(el), box = el.getBoundingClientRect();
    return {selector, found: true, tag: el.tagName,
      text: (el.innerText || el.getAttribute('aria-label') || '').trim().slice(0, 180),
      box: {x: box.x, y: box.y, width: box.width, height: box.height},
      styles: Object.fromEntries(props.map(p => [p, style[p]]))};
  });
  return {title: document.title, href: location.href,
    viewport: {width: innerWidth, height: innerHeight},
    document: {width: document.documentElement.scrollWidth,
      height: document.documentElement.scrollHeight},
    stylesheets: [...document.querySelectorAll('link[rel="stylesheet"]')].map(x => x.href),
    elements};
}"""


def loopback_url(value):
    parsed = urlsplit(value)
    if parsed.scheme not in ('http', 'https') or parsed.hostname not in ('127.0.0.1', 'localhost', '::1'):
        raise argparse.ArgumentTypeError('Historical viewers must be served on loopback')
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    parser.add_argument('--old-viewer-url', type=loopback_url)
    parser.add_argument('--v4-viewer-url', type=loopback_url)
    args = parser.parse_args()
    if not os.environ.get('SLURM_JOB_ID'):
        parser.error('Run this capture only inside an authorized Slurm job')
    from playwright.sync_api import sync_playwright

    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    references = [
        ('arxiv-list', 'https://arxiv.org/list/hep-th/recent', None),
        ('arxiv-search', 'https://arxiv.org/search/?query=quantum+gravity&searchtype=all&abstracts=show&order=-announced_date_first&size=50', None),
        ('arxiv-abstract', 'https://arxiv.org/abs/2209.09249', None),
    ]
    if args.old_viewer_url:
        references.append(('old-tree', args.old_viewer_url, '.col-row'))
    if args.v4_viewer_url:
        references.append(('text-explorer-v4', args.v4_viewer_url, '.col-row'))
    report = {'capturedAt': datetime.now(timezone.utc).isoformat(),
              'environment': 'authorized Slurm Chromium', 'references': []}
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        report['browserVersion'] = browser.version
        for name, url, historical_selector in references:
            for size, width, height in [('desktop', 1440, 1000), ('mobile', 390, 844)]:
                context = browser.new_context(viewport={'width': width, 'height': height},
                                              device_scale_factor=1, reduced_motion='reduce')
                page = context.new_page()
                page.set_default_timeout(12000)
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)[:300]))
                entry = {'name': name, 'size': size, 'requestedUrl': url, 'pageErrors': errors}
                try:
                    response = page.goto(url, wait_until='domcontentloaded', timeout=25000)
                    entry['status'] = response.status if response else None
                    page.wait_for_function('document.fonts.status === "loaded"', timeout=12000)
                    if historical_selector:
                        page.locator(historical_selector).first.wait_for()
                    page.screenshot(path=str(output / f'{name}-{size}.png'), full_page=False)
                    entry['screenshot'] = f'{name}-{size}.png'
                    entry['computed'] = page.evaluate(STYLE_CAPTURE, SELECTORS)
                    if historical_selector:
                        # Two bounded drill-ins reveal path/column behavior. No
                        # data mutation occurs: both references are static viewers.
                        for _ in range(2):
                            rows = page.locator('.column').last.locator(historical_selector)
                            if not rows.count():
                                break
                            rows.first.click()
                        page.screenshot(path=str(output / f'{name}-{size}-path.png'), full_page=False)
                        entry['pathScreenshot'] = f'{name}-{size}-path.png'
                        entry['pathComputed'] = page.evaluate(STYLE_CAPTURE, SELECTORS)
                except Exception as error:
                    entry['captureError'] = str(error)[:700]
                report['references'].append(entry)
                context.close()
        browser.close()
    (output / 'reference-capture.json').write_text(json.dumps(report, indent=2) + '\n')
    failures = [f"{x['name']} {x['size']}" for x in report['references']
                if x.get('captureError') or (x.get('status') or 0) >= 400]
    print(json.dumps({'captured': len(report['references']), 'failed': failures,
                      'report': 'reference-capture.json'}))
    return bool(failures)


if __name__ == '__main__':
    raise SystemExit(main())
