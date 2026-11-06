#!/usr/bin/env python3
"""Q003/Q004 real-browser capsule, page-object, routing and cold-start checks.
Only authorized Slurm may launch this. Storage HTTP is a deterministic test
adapter; durable R2/DO behavior is covered separately by backend tests.
"""
import argparse, gzip, hashlib, json, os, shutil, subprocess, tempfile, time
from pathlib import Path
from playwright.sync_api import sync_playwright


def fixture(question='Author comparison',suffix='a'):
    return {'schemaVersion':'1.0.0','kind':'eigenquestions-contextual-view','builder':{'id':'external-author','version':'7'},'context':{'question':question,'summary':'A supplied comparison with overlapping interpretations.','assumptions':['Keep source evidence distinct from interpretation.'],'openQuestions':['Which approximation fails?']},'snapshot':{'view':{'stateId':'authored-'+suffix,'corpusId':'external-reading-list','computationId':'external-v7','query':question,'nodes':[{'id':'source-a','title':'A source <img src=x onerror=alert(1)>','sourceUrl':'https://arxiv.org/abs/2209.09249','evidence':{'text':'Author-supplied evidence A.','claimStatus':'unverified extraction'}},{'id':'source-b','title':'A competing mechanism','sourceUrl':'javascript:alert(1)','evidence':{'text':'Author-supplied evidence B.'}}],'directions':[{'id':'author-group-a','label':'Exact authored <b>group A</b>','memberIds':['source-a','source-b'],'evidenceIds':['source-a']},{'id':'author-group-b','label':'An overlapping alternative','memberIds':['source-a'],'evidenceIds':['source-a']}],'edges':[{'source':'author-group-a','target':'author-group-b','type':'author-hypothesis','evidenceIds':['source-a']}],'chart':None,'diagnostics':{},'warnings':['A reading suggestion, not a physical proof.']}},'continuation':{'mode':'snapshot-only','originStateId':'authored-'+suffix,'description':'This builder is unavailable here. Read the supplied sources or start a new path.','actions':[]}}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--project',required=True);parser.add_argument('--output',required=True);parser.add_argument('--node',default='node');parser.add_argument('--origin');args=parser.parse_args()
    if not os.environ.get('SLURM_JOB_ID'):raise SystemExit('Run only in the authorized Slurm environment.')
    root=Path(args.project).resolve();output=Path(args.output).resolve();output.mkdir(parents=True,exist_ok=True)
    temp=Path(tempfile.mkdtemp(prefix='eq-capsule-'));server=None
    report={'request':'Q003/Q004','checks':[],'storageScope':'Browser HTTP adapter tests exact gzip roundtrip and failures; separate backend tests exercise durable storage. Timings are headless Slurm observations, not deployment guarantees.'}
    def passed(name,**data):report['checks'].append({'name':name,'passed':True,**data})
    try:
        if args.origin:origin=args.origin.rstrip('/')
        else:
            receipt=temp/'connection.json';server=subprocess.Popen([args.node,str(root/'bin/navigate.mjs'),'serve','--port','0','--connection',str(receipt)],cwd=root,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
            deadline=time.monotonic()+90
            while not receipt.exists() and time.monotonic()<deadline:
                if server.poll() is not None:raise RuntimeError('Test server failed')
                time.sleep(.1)
            origin=json.loads(receipt.read_text())['url'].rstrip('/')
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True);context=browser.new_context(viewport={'width':1440,'height':1000},accept_downloads=True)
            page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));requests=[];page.on('request',lambda r:requests.append(r.url.split('?')[0]))
            ids={'a':'A'*22,'b':'B'*22,'c':'C'*22,'bad':'D'*22};a=fixture();b=fixture('A different authored question','b');c=fixture('Latest route wins','c')
            objects={ids['a']:json.dumps(a).encode(),ids['b']:json.dumps(b).encode(),ids['c']:json.dumps(c).encode(),ids['bad']:b'{"kind":"wrong"}'}
            held={};hold={ids['a']};published=[];storage_off=False;hold_post=False;held_posts=[]
            def api(route):
                nonlocal storage_off,hold_post
                request=route.request
                if request.method=='POST':
                    if storage_off:route.fulfill(status=503,content_type='application/json',body=json.dumps({'error':{'code':'storage_unavailable','message':'Saved-view storage is not enabled.'}}));return
                    raw=request.post_data_buffer;assert request.headers.get('content-type')=='application/gzip';assert 'content-encoding' not in request.headers
                    decoded=json.loads(gzip.decompress(raw));published.append(decoded);sid='P'*22;objects[sid]=raw
                    receipt=json.dumps({'id':sid,'url':origin+'/#view='+sid,'readUrl':origin+'/api/views/'+sid,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'createdAt':'2026-11-06T00:00:00Z'})
                    if hold_post:held_posts.append((route,receipt));return
                    route.fulfill(status=201,content_type='application/json',body=receipt);return
                sid=request.url.rsplit('/',1)[-1]
                if sid in hold:held[sid]=route;return
                route.fulfill(status=200,content_type='application/gzip' if objects[sid][:2]==b'\x1f\x8b' else 'application/json',body=objects[sid])
            page.route('**/api/views**',api)
            start=time.monotonic();page.goto(origin+'/#view='+ids['a'],wait_until='domcontentloaded');page.wait_for_function('Boolean(window.eigenquestionsNavigator)')
            page.wait_for_timeout(80)
            assert page.locator('#question').input_value()==''
            assert 'Kaluza' not in page.locator('#current-question').inner_text()
            page.locator('#question').fill('A draft typed before the view arrived')
            assert not any('/data/' in url for url in requests)
            held.pop(ids['a']).fulfill(status=200,content_type='application/json',body=objects[ids['a']]);hold.clear()
            page.wait_for_function("document.documentElement.dataset.stateId==='authored-a'")
            assert page.locator('#question').input_value()=='A draft typed before the view arrived'
            assert page.locator('html').get_attribute('data-accepted-count')=='1'
            assert not any('/data/' in url for url in requests)
            assert page.evaluate('window.eigenquestionsNavigator.export()')==a
            assert page.evaluate('location.hash')=='#view='+ids['a']
            assert page.locator('#view-geometry').is_disabled()
            assert page.locator('.miller-column[data-current="true"] .direction').count()==2
            assert page.locator('.miller-column[data-current="true"] .direction').first.is_disabled()
            assert page.locator('#snapshot-notice').is_visible()
            assert '2 source descriptions' in page.locator('#status').inner_text() and '1 papers' not in page.locator('#status').inner_text()
            assert page.locator('.navigator-note').is_hidden()
            assert page.locator('#directions img,#directions b,.evidence-card img,a[href^="javascript:"]').count()==0
            page.screenshot(path=str(output/'authored-desktop-viewport.png'),full_page=False)
            passed('cold stored view displays exact authored overlap/evidence without corpus, fake topic, executable labels or draft overwrite',seconds=round(time.monotonic()-start,3))
            page.locator('.direction-evidence').nth(1).click();assert page.locator('.evidence-card').count()==1
            assert page.locator('.evidence-card').first.get_attribute('data-source-id')=='source-a'
            assert page.evaluate("document.activeElement.id")=='view-sources'
            passed('overlapping group Sources action reveals exact evidence with visible keyboard focus')
            page.locator('.session-tools > summary').click()
            with page.expect_download() as download:page.locator('#export-view').click()
            downloaded=temp/'view.json';download.value.save_as(str(downloaded));assert json.loads(downloaded.read_text())==a
            file=temp/'authored.json.gz';file.write_bytes(gzip.compress(json.dumps(b).encode()));page.locator('#import-file').set_input_files(str(file));page.wait_for_function("document.documentElement.dataset.stateId==='authored-b'")
            assert page.evaluate('window.eigenquestionsNavigator.export()')==b
            assert page.evaluate('location.hash')==''
            page.reload(wait_until='domcontentloaded');page.wait_for_function("document.documentElement.dataset.stateId==='authored-b'")
            assert page.evaluate('window.eigenquestionsNavigator.export()')==b
            page.locator('.session-tools > summary').click()
            page.locator('#publish-view').click();page.wait_for_function("document.querySelector('#stored-view-link').hidden===false")
            assert published==[b]
            assert 'Anyone with the link' in page.locator('#stored-view-status').inner_text()
            route_revision=page.evaluate('window.eigenquestionsNavigator.read().revision')
            page.evaluate("location.hash='view='+'P'.repeat(22)");page.wait_for_function('revision=>window.eigenquestionsNavigator.read().revision>revision',arg=route_revision)
            assert page.evaluate('window.eigenquestionsNavigator.export()')==b
            passed('gzip file, full-view download, HTTP publication and URL reopening preserve every authored field')
            for dropped in (a,b):
                page.evaluate("""capsule=>{const data=new DataTransfer();data.items.add(new File([JSON.stringify(capsule)],'dropped-view.json',{type:'application/json'}));document.dispatchEvent(new DragEvent('drop',{bubbles:true,cancelable:true,dataTransfer:data}));}""",dropped)
                page.wait_for_function('id=>document.documentElement.dataset.stateId===id',arg=dropped['snapshot']['view']['stateId'])
                assert page.evaluate('window.eigenquestionsNavigator.export()')==dropped
            passed('actual DataTransfer drop opens the same exact capsule as file import')
            before=page.evaluate('window.eigenquestionsNavigator.read().revision');storage_off=True
            page.locator('#publish-view').click();page.wait_for_function("document.querySelector('#stored-view-status').textContent.includes('not enabled')")
            assert page.evaluate('window.eigenquestionsNavigator.read().revision')==before
            assert page.evaluate('window.eigenquestionsNavigator.export()')==b
            passed('inactive storage reports a useful error and preserves downloadable current view')
            # Two route requests overlap. The earlier response cannot overwrite C.
            hold.add(ids['a']);page.evaluate('(id)=>location.hash="view="+id',ids['a']);page.wait_for_timeout(50)
            assert ids['a'] in held
            page.evaluate('(id)=>location.hash="view="+id',ids['c']);page.wait_for_function("document.documentElement.dataset.stateId==='authored-c'")
            try:held.pop(ids['a']).fulfill(status=200,content_type='application/json',body=objects[ids['a']])
            except Exception:pass  # Expected aborted request; newest route remains authoritative.
            page.wait_for_timeout(80);assert page.evaluate('window.eigenquestionsNavigator.export()')==c
            page.evaluate('(id)=>location.hash="view="+id',ids['bad']);page.wait_for_function("document.querySelector('#status').textContent.includes('Unable to open')")
            assert page.evaluate('window.eigenquestionsNavigator.export()')==c
            passed('hash changes load without reload, latest response wins, and malformed routes preserve prior view')
            # Delayed file reads and publication receipts are bound to their intents.
            page.evaluate("""()=>{const read=File.prototype.arrayBuffer;File.prototype.arrayBuffer=function(){if(this.name==='late.json')return new Promise(resolve=>{window.__releaseFile=async()=>resolve(await read.call(this));});return read.call(this);};}""")
            late=temp/'late.json';late.write_text(json.dumps(a));page.locator('#import-file').set_input_files(str(late));page.wait_for_function('Boolean(window.__releaseFile)')
            page.evaluate('capsule=>window.eigenquestionsNavigator.apply(capsule,{expectedRevision:window.eigenquestionsNavigator.read().revision})',b)
            page.evaluate('window.__releaseFile()');page.wait_for_timeout(80);assert page.evaluate('window.eigenquestionsNavigator.export()')==b
            storage_off=False;hold_post=True;page.locator('#publish-view').click();page.wait_for_timeout(50);assert held_posts
            page.evaluate('capsule=>window.eigenquestionsNavigator.apply(capsule,{expectedRevision:window.eigenquestionsNavigator.read().revision})',c)
            saved_route,saved_receipt=held_posts.pop();saved_route.fulfill(status=201,content_type='application/json',body=saved_receipt);hold_post=False
            page.wait_for_function("document.querySelector('#stored-view-status').textContent.includes('earlier view')")
            assert page.locator('#stored-view-link label').inner_text()=='Earlier view link'
            assert page.evaluate('window.eigenquestionsNavigator.export()')==c
            layout=json.loads(json.dumps(c));layout['snapshot']['view']['chart']={'kind':'display-layout'}
            for i,point in enumerate(layout['snapshot']['view']['nodes']+layout['snapshot']['view']['directions']):point.update({'x':i%2,'y':i//2})
            page.evaluate('capsule=>window.eigenquestionsNavigator.apply(capsule,{expectedRevision:window.eigenquestionsNavigator.read().revision})',layout)
            assert page.locator('#stored-view-link').is_hidden()
            page.locator('#view-geometry').click();assert page.locator('.chart-direction').count()==2
            assert page.locator('#chart line title').all_text_contents()==['Supplied relation: author-hypothesis']
            assert 'Author-supplied display layout' in page.locator('#chart-caption').inner_text()
            assert page.evaluate('window.eigenquestionsNavigator.export()')==layout
            page.evaluate('capsule=>window.eigenquestionsNavigator.apply(capsule,{expectedRevision:window.eigenquestionsNavigator.read().revision})',c)
            passed('late file reads cannot overwrite newer views; earlier save receipts are labeled; supplied layout shows groups and typed edges')
            # API operations share the controller. Orient computes without a UI commit.
            before=page.evaluate('window.eigenquestionsNavigator.read()');draft=page.locator('#question').input_value()
            native=page.evaluate("async()=>await window.eigenquestionsNavigator.orient('KK towers',{intent:'phenomenology'})")
            after=page.evaluate('window.eigenquestionsNavigator.read()')
            assert before['revision']==after['revision'] and before['capsule']==after['capsule']
            assert page.locator('#question').input_value()==draft and len(native['snapshot']['view']['directions'])==5
            assert any('/data/' in url for url in requests)
            passed('read-only orient uses the real worker yet leaves canonical view, history and draft unchanged')
            authored=json.loads(json.dumps(native));authored['builder']={'id':'agent-comparison','version':'2'};group=authored['snapshot']['view']['directions'][0];old_id=group['id'];group['id']='custom-agent-group';group['label']='Exact agent-authored continuation';authored['context']['question']='Compare KK dark-matter mechanisms under stated assumptions';authored['context']['assumptions']=['Keep the KK physical application explicit.'];authored['continuation']['actions']=[{'id':group['id'],'label':group['label'],'action':{'type':'refine','query':'KK towers as dark matter','focusIds':group['seedIds'],'intent':'phenomenology'}}]
            for edge in authored['snapshot']['view']['edges']:
                if edge['source']==old_id:edge['source']=group['id']
                if edge['target']==old_id:edge['target']=group['id']
            invalid_anchor=json.loads(json.dumps(authored));invalid_anchor['continuation']['actions'][0]['action']['focusIds']=['absent-authored-anchor']
            page.evaluate('capsule=>window.eigenquestionsNavigator.apply(capsule,{expectedRevision:window.eigenquestionsNavigator.read().revision})',invalid_anchor)
            page.locator('.direction[data-direction-id="custom-agent-group"]').click()
            page.wait_for_function("document.querySelector('#status').textContent.includes('not a source in the loaded corpus')")
            assert page.evaluate('window.eigenquestionsNavigator.export()')==invalid_anchor
            after=page.evaluate('window.eigenquestionsNavigator.read()')
            passed('unknown authored continuation anchors reject visibly without changing the supplied view')
            revision=after['revision'];page.evaluate('({capsule,revision})=>window.eigenquestionsNavigator.apply(capsule,{expectedRevision:revision})',{'capsule':authored,'revision':revision})
            assert page.evaluate('window.eigenquestionsNavigator.export()')==authored
            assert page.locator('#current-question').inner_text()==authored['context']['question']
            malformed=json.loads(json.dumps(authored));malformed['snapshot']['view']['nodes'][0]['evidence']['sourceRecordIds']='bad'
            invalid=page.evaluate('capsule=>{try{window.eigenquestionsNavigator.apply(capsule,{expectedRevision:window.eigenquestionsNavigator.read().revision});return false}catch{return true}}',malformed);assert invalid
            assert page.evaluate('window.eigenquestionsNavigator.export()')==authored
            stale=page.evaluate('revision=>{try{window.eigenquestionsNavigator.apply(window.eigenquestionsNavigator.export(),{expectedRevision:revision});return false}catch(e){return e.code==="revision_conflict"}}',revision);assert stale
            page.locator('.direction[data-direction-id="custom-agent-group"]').click();page.wait_for_function("document.querySelector('#current-question').textContent==='KK towers as dark matter'",timeout=60000)
            result=page.evaluate('window.eigenquestionsNavigator.export()');state=result['snapshot']['session']['states'][-1]
            assert state['focusIds']==sorted(set(group['seedIds']))
            assert result['context']['assumptions']==authored['context']['assumptions']
            passed('custom group continues by explicit resolved query and genuine anchors, with revision and malformed-metadata guards; no invented select ID')
            page.locator('#back').click();page.wait_for_function("document.querySelector('#current-question').textContent==='Compare KK dark-matter mechanisms under stated assumptions'")
            restored=page.evaluate('window.eigenquestionsNavigator.export()')
            assert restored['snapshot']['view']==authored['snapshot']['view'] and restored['context']==authored['context']
            page.locator('.direction[data-direction-id="custom-agent-group"]').click();page.wait_for_function("document.querySelector('#current-question').textContent==='KK towers as dark matter'")
            historical=page.locator('.miller-column[data-current="false"] .direction[data-direction-id="custom-agent-group"]');assert historical.count()==1
            previous_revision=page.evaluate('window.eigenquestionsNavigator.read().revision');historical.click()
            page.wait_for_function('revision=>window.eigenquestionsNavigator.read().revision>revision',arg=previous_revision)
            branched=page.evaluate('window.eigenquestionsNavigator.export()');branch_state=branched['snapshot']['session']['states'][-1]
            assert branch_state['query']=='KK towers as dark matter' and branch_state['focusIds']==sorted(set(group['seedIds']))
            passed('Back restores exact authored grouping and historical authored choice branches through its recorded action')
            unrelated=page.evaluate("async()=>await window.eigenquestionsNavigator.orient('black hole evaporation')")
            unrelated_session=unrelated['snapshot']['session'];session_file=temp/'unrelated-session.json'
            session_file.write_text(json.dumps({'schemaVersion':'1.0.0','kind':'eigenquestions-session','corpusId':unrelated_session['corpusId'],'computationId':unrelated_session['computationId'],'session':unrelated_session}))
            page.locator('#import-file').set_input_files(str(session_file));page.wait_for_function("document.querySelector('#current-question').textContent==='black hole evaporation'")
            assert page.evaluate('window.eigenquestionsNavigator.export().context.assumptions')==[]
            passed('independent legacy-session import does not inherit an earlier authored scientific assumption')
            page.locator('#question').fill('');page.locator('#reset').click();page.wait_for_function("document.querySelector('#question').value===''&&!document.body.classList.contains('busy')")
            reset=page.evaluate('window.eigenquestionsNavigator.export()');assert reset['context']['assumptions']==[]
            assert reset['snapshot']['session']['states'][0]['focusIds']==[]
            assert page.evaluate('location.hash')==''
            page.reload(wait_until='domcontentloaded');page.wait_for_function("document.documentElement.dataset.ready==='true'")
            assert page.evaluate('window.eigenquestionsNavigator.export()')==reset
            passed('New path clears inherited scientific context and canonical anchors')
            # Fresh boot starts empty and ready without corpus; a stored route wins
            # over prior local capsule, with no transient acceptance of that capsule.
            fresh=browser.new_context(viewport={'width':390,'height':844});cold=fresh.new_page();cold_requests=[];cold.on('request',lambda r:cold_requests.append(r.url));cold.on('pageerror',lambda e:errors.append(str(e)))
            cold.goto(origin,wait_until='domcontentloaded');cold.wait_for_function("document.documentElement.dataset.ready==='true'")
            assert cold.locator('#question').input_value()=='' and not any('/data/' in u for u in cold_requests)
            assert cold.locator('.reading-pane').is_hidden() and cold.locator('.column-navigation').is_hidden()
            cold.screenshot(path=str(output/'empty-mobile-viewport.png'),full_page=False)
            cold.evaluate('(value)=>localStorage.setItem("eigenquestions:view:v1",JSON.stringify(value))',b)
            cold.route('**/api/views/**',lambda route:route.fulfill(status=200,content_type='application/json',body=json.dumps(c)))
            cold.goto(origin+'/?startup-priority=1#view='+ids['c']);cold.wait_for_function("document.documentElement.dataset.stateId==='authored-c'")
            assert cold.locator('html').get_attribute('data-accepted-count')=='1'
            assert cold.evaluate('window.eigenquestionsNavigator.export()')==c
            assert not any('/data/' in u for u in cold_requests)
            cold.screenshot(path=str(output/'authored-mobile-viewport.png'),full_page=False)
            assert cold.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            passed('empty startup is cheap and neutral; explicit stored route wins over saved browser state with one accepted initial view')
            report['pageErrors']=errors;assert not errors;browser.close()
        report['passed']=True
    except Exception as error:
        report['passed']=False;report['failureType']=type(error).__name__;report['failure']=str(error)[:1000];raise
    finally:
        (output/'stored-views-browser-acceptance.json').write_text(json.dumps(report,indent=2)+'\n')
        if server:
            server.terminate()
            try:server.wait(timeout=10)
            except subprocess.TimeoutExpired:server.kill()
        shutil.rmtree(temp,ignore_errors=True)

if __name__=='__main__':main()
