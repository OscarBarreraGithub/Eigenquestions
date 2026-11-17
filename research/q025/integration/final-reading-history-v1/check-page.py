import argparse,hashlib,json,os,subprocess,tempfile,time,shutil
from pathlib import Path
from urllib.parse import urlencode,quote
from playwright.sync_api import sync_playwright
p=argparse.ArgumentParser();p.add_argument('--project',required=True);p.add_argument('--node',required=True);p.add_argument('--output',required=True);a=p.parse_args();assert os.environ.get('SLURM_JOB_ID')
r=Path(a.project);out=Path(a.output);out.mkdir(parents=True,exist_ok=True);am=json.loads((out/'amendment.json').read_text());atlas=r/'data/atlas/q025-approved-organization-candidate/2026-11-17-post-test-accounted-v1';m=json.loads((atlas/'manifest.json').read_text());private=Path(tempfile.mkdtemp());conn=private/'connection.json';server=None;report={'manifestSha256':hashlib.sha256((atlas/'manifest.json').read_bytes()).hexdigest(),'amendmentSha256':hashlib.sha256((out/'amendment.json').read_bytes()).hexdigest(),'passed':False,'pageErrors':[],'observerTouched':False}
try:
 server=subprocess.Popen([a.node,str(r/'bin/navigate.mjs'),'serve','--atlas',str(atlas),'--port','0','--connection',str(conn)],cwd=r,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
 until=time.monotonic()+60
 while not conn.exists() and time.monotonic()<until:time.sleep(.05)
 origin=json.loads(conn.read_text())['url'].rstrip('/');id=am['destinationId'];sentence='This authored region remains a proposal requiring independent review.'
 with sync_playwright()as pw:
  browser=pw.chromium.launch(headless=True);page=browser.new_page(viewport={'width':1180,'height':900});page.on('pageerror',lambda e:report['pageErrors'].append(str(e)));page.goto(origin+'/#'+urlencode({'atlas':m['atlasId'],'version':m['atlasVersion'],'destination':id}),wait_until='domcontentloaded');page.wait_for_function('id=>document.documentElement.dataset.destinationId===id',arg=id)
  scope=page.locator('#atlas-panel > details').filter(has=page.locator('summary',has_text='Scope, assumptions and sources')).first;scope.locator(':scope > summary').click();current='\n'.join(scope.locator(':scope > p').all_text_contents());assert am['readingLimit']['text']in current and sentence not in current
  history=page.locator('#atlas-panel > details').filter(has=page.locator('summary',has_text='Reading and record history')).first;assert not history.evaluate('(e)=>e.open');history.locator(':scope > summary').click();assert am['readingLimit']['originalText']in history.inner_text();page.screenshot(path=str(out/'reading-history-corrected.png'),full_page=True)
  page.goto(origin+'/atlas/'+quote(m['atlasId'])+'/'+quote(m['atlasVersion'])+'/'+quote(id)+'.html',wait_until='domcontentloaded');paragraphs=page.locator('main > p').all_text_contents();assert am['readingLimit']['text']in paragraphs;assert not any(sentence in x for x in paragraphs);assert am['readingLimit']['originalText']in page.locator('body').text_content();report['passed']=True;report['checks']=['Current browser reading paragraph retains exact limits/counts without historical status','Collapsed record history preserves full original field','Static page has same projected paragraph and full original history'];browser.close()
finally:
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 if server:server.terminate();server.wait(timeout=5)
 shutil.rmtree(private,ignore_errors=True)
