#!/usr/bin/env python3
"""Bounded final-data checks in a separate scripted bridge/browser, never the fresh observer."""
import argparse,hashlib,json,os,shutil,subprocess,tempfile,time,urllib.request
from pathlib import Path
from urllib.parse import urlencode,quote
from playwright.sync_api import sync_playwright

def main():
 p=argparse.ArgumentParser()
 for key in ['project','atlas','node','output']:p.add_argument('--'+key,required=True)
 a=p.parse_args();assert os.environ.get('SLURM_JOB_ID'),'Authorized isolated Slurm only'
 root=Path(a.project);atlas=Path(a.atlas);out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
 manifest=json.loads((atlas/'manifest.json').read_text());catalog=json.loads((atlas/'catalog.json').read_text());idx={d['id']:d for d in catalog['destinations']};cache={}
 def detail(d):
  sid=d['detail']['shardId']
  if sid not in cache:cache[sid]=json.loads((atlas/catalog['detailShards'][sid]['path']).read_text())
  return cache[sid]['destinations'][d['id']]['destination']
 zero=next(d for d in catalog['destinations']if d.get('membershipCount')==0 and not d.get('metadataOnly') and detail(d).get('sourceContributions'))
 examples=json.loads((root/'research/q025/integration/presentation-v1/examples.json').read_text())['records']
 private=Path(tempfile.mkdtemp(prefix='q025-supplement-'));connection=private/'connection.json';server=browser=page=None;token=''
 report={'kind':'final-scripted-supplement','jobId':os.environ['SLURM_JOB_ID'],'manifestSha256':hashlib.sha256((atlas/'manifest.json').read_bytes()).hexdigest(),'freshObserverTouched':False,'checks':[],'screenshots':[],'pageErrors':[],'passed':False}
 def check(name,**extra):report['checks'].append({'name':name,'passed':True,**extra})
 try:
  server=subprocess.Popen([a.node,str(root/'bin/navigate.mjs'),'serve','--atlas',str(atlas),'--port','0','--connection',str(connection)],cwd=root,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
  until=time.monotonic()+60
  while not connection.exists()and time.monotonic()<until:
   if server.poll()is not None:raise RuntimeError('Separate companion exited')
   time.sleep(.05)
  conn=json.loads(connection.read_text());token=conn['token'];origin=conn['url'].rstrip('/')
  def api(route,payload=None,revision=None):
   headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'}
   if revision is not None:headers['If-Match']=str(revision)
   with urllib.request.urlopen(urllib.request.Request(origin+route,data=json.dumps(payload).encode()if payload is not None else None,headers=headers),timeout=60)as response:return json.load(response)
  def selector(id):return {'kind':'atlas-destination','atlasId':manifest['atlasId'],'atlasVersion':manifest['atlasVersion'],'destinationId':id}
  def move(action):
   before=api('/api/session');result=api('/api/action',action,before['revision']);page.wait_for_function('id=>document.documentElement.dataset.stateId===id',arg=result['view']['stateId']);return result
  def navigate(id):return move({'type':'navigate','selector':selector(id)})
  with sync_playwright()as pw:
   browser=pw.chromium.launch(headless=True);context=browser.new_context(viewport={'width':1180,'height':900},accept_downloads=True);page=context.new_page();page.set_default_timeout(30000);page.on('pageerror',lambda error:report['pageErrors'].append(str(error)))
   page.goto(origin+'/#token='+token,wait_until='domcontentloaded');page.wait_for_function("window.eigenquestionsNavigator?.read().mode==='local-companion'")
   report['phase']='contributions-and-filters';current=navigate(zero['id']);assert current['view']['atlas']['membershipCount']==0
   before=api('/api/session');contrib=api('/api/sources',{'destinationId':zero['id'],'collection':'contributions','limit':2});remaining=api('/api/sources',{'destinationId':zero['id'],'collection':'contributions','offset':2,'limit':20});assert contrib['total']==len(contrib['items'])+len(remaining['items']);assert all(r['source']['evidence']['text']and r['evidenceRefs']for r in contrib['items']+remaining['items']);assert api('/api/sources',{'destinationId':zero['id']})['total']==0;assert api('/api/sources',{'destinationId':zero['id'],'workRelation':'using'})['total']==0;assert api('/api/session')['revision']==before['revision']
   disclosure=page.locator('.source-contributions');disclosure.locator(':scope > summary').click();page.wait_for_function('document.querySelector(".source-contributions").textContent.includes("loaded")');assert disclosure.locator('details').count()>0
   page.screenshot(path=str(out/'contribution-only.png'),full_page=True);report['screenshots'].append('contribution-only.png')
   check('Real zero-member question retains paged source contributions and zero USING without mutating state',destinationId=zero['id'],contributions=contrib['total'])
   production='q-kk-graviton-thermal-production';navigate(production)
   rows=api('/api/sources',{'destinationId':production,'lens':'physical_question','workRelation':'on','limit':100});methods=api('/api/sources',{'destinationId':production,'lens':'method','includeContext':True,'limit':100});using=api('/api/sources',{'destinationId':production,'lens':'method','includeContext':True,'workRelation':'using','limit':100})
   assert rows['total']>0 and methods['total']>0 and using['total']==0;assert all(r['associationScope']=='same_paper_context'for r in methods['items'])
   check('Actual source filters distinguish primary questions, contextual methods and USING',primary=rows['total'],contextMethods=methods['total'],using=using['total'])
   inventory=manifest['files']['unrepresentedPapers'];url=origin+'/data/atlas/'+manifest['atlasId']+'/'+manifest['atlasVersion']+'/'+inventory['path'];response=page.request.get(url);assert response.ok;records=response.json();assert any(r['scientificStatus']=='withdrawn'and r['sourceSha256']is None for r in records)
   page.locator('#atlas-panel > details').filter(has=page.locator('summary',has_text='Scope, assumptions and sources')).first.locator(':scope > summary').click();assert page.get_by_role('link',name='Bibliographic records without source text',exact=True).count()==1
   check('Unavailable-source inventory is linked and retains withdrawn no-text record')
   report['phase']='notes-and-manual-view';note='Synthetic final acceptance note; never a researcher private note.';section=page.locator('#atlas-panel > details').filter(has=page.locator('summary',has_text='Your work on this question'));section.locator(':scope > summary').click();page.get_by_label('Local research work note',exact=True).fill(note)
   original=api('/api/session');navigate('q-kk-graviton-threshold-decay');move({'type':'back'});assert page.get_by_label('Local research work note',exact=True).input_value()==note
   navigate('q-kk-graviton-threshold-decay');move({'type':'replay','index':original['session']['cursor']});assert page.get_by_label('Local research work note',exact=True).input_value()==note
   section=page.locator('#atlas-panel > details').filter(has=page.locator('summary',has_text='Your work on this question'));section.locator(':scope > summary').click()
   with page.expect_download()as event:page.get_by_role('button',name='Export note',exact=True).click()
   note_path=private/'note.json';event.value.save_as(note_path);exported_note=json.loads(note_path.read_text());assert exported_note['text']==note and exported_note['target']['destinationId']==production
   page.locator('.session-tools > summary').click()
   with page.expect_download()as event:page.locator('#export-view').click()
   capsule_path=private/'view.json';event.value.save_as(capsule_path);capsule=json.loads(capsule_path.read_text());assert note not in capsule_path.read_text()
   page.locator('#reset').click();page.wait_for_function('id=>document.documentElement.dataset.destinationId===id',arg=manifest['entryDestinationId']);navigate(production);assert page.get_by_label('Local research work note',exact=True).input_value()==note
   check('Synthetic work note survives scripted companion updates, Back, replay and New path; exported view omits note')
   compact=origin+'/#'+urlencode({'atlas':manifest['atlasId'],'version':manifest['atlasVersion'],'destination':production});assert note not in compact
   other=browser.new_context(viewport={'width':1180,'height':900});fresh=other.new_page();fresh.goto(compact,wait_until='domcontentloaded');fresh.wait_for_function('id=>document.documentElement.dataset.destinationId===id',arg=production);assert fresh.get_by_label('Local research work note',exact=True).input_value()==''
   fresh.set_input_files('#import-file',str(capsule_path));fresh.wait_for_function('id=>document.documentElement.dataset.stateId===id',arg=capsule['snapshot']['view']['stateId']);imported=fresh.evaluate('window.eigenquestionsNavigator.export()');assert imported['snapshot']['view']['atlas']['selector']==capsule['snapshot']['view']['atlas']['selector'];assert note not in json.dumps(imported)
   fresh.screenshot(path=str(out/'manual-view-import.png'),full_page=True);report['screenshots'].append('manual-view-import.png');other.close();check('Compact prepared URL and actual downloaded capsule import preserve selector without publishing note')
   report['phase']='five-editorial-pages';editorial=[]
   for i,example in enumerate(examples):
    current=navigate(example['id']);raw=current['view']['atlas']['destination'];assert raw['scopeContentSha256']==example['scopeContentSha256'];history=page.locator('#atlas-panel > details').filter(has=page.locator('summary',has_text='Reading and record history')).first;assert history.count()==1 and not history.evaluate('(node)=>node.open');history.locator(':scope > summary').click();assert all(n['originalText']in history.inner_text()for n in example['displayEditorial']['relocations']);scope=page.locator('#atlas-panel > details').filter(has=page.locator('summary',has_text='Scope, assumptions and sources')).first;scope.locator(':scope > summary').click();assert all(n['originalText']not in scope.inner_text()for n in example['displayEditorial']['relocations']);html=page.request.get(origin+'/atlas/'+manifest['atlasId']+'/'+manifest['atlasVersion']+'/'+quote(example['id'],safe='')+'.html').text();assert 'Reading and record history'in html;assert all(n['originalText']not in html.split('<h2>Scope</h2>')[1].split('<h2>Methods')[0]for n in example['displayEditorial']['relocations']);name='editorial-'+str(i+1)+'.png';page.screenshot(path=str(out/name),full_page=True);report['screenshots'].append(name);editorial.append(example['id'])
   check('Five exact approved display treatments separate workflow history in actual browser and static pages',destinations=editorial)
   assert not report['pageErrors'];report['passed']=True;browser.close();browser=None
 except Exception as e:
  report['error']=str(e).replace(token,'[redacted-session-token]')if token else str(e)
  if page:
   try:report['failureBody']=page.locator('body').inner_text();page.screenshot(path=str(out/'failure.png'),full_page=True)
   except Exception:pass
 finally:
  if browser:browser.close()
  if server:
   server.terminate()
   try:server.wait(timeout=5)
   except subprocess.TimeoutExpired:server.kill()
  body=json.dumps(report,ensure_ascii=False,indent=2)+'\n';(out/'report.json').write_text(body.replace(token,'[redacted-session-token]')if token else body);shutil.rmtree(private,ignore_errors=True)
 if not report['passed']:raise SystemExit(report['error'])
if __name__=='__main__':main()
