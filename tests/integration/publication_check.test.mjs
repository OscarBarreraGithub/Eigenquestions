import test from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';
import {readFile} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {checkPublication} from './publication_check.mjs';

const dist=fileURLToPath(new URL('../../dist/',import.meta.url));
test('publication helper detects exact release and rejects stale module or surviving old API',async()=>{
  assert.deepEqual(await readFile(path.join(dist,'lib/protocol/presentation.mjs')),await readFile(new URL('../../lib/protocol/presentation.mjs',import.meta.url)),'The build must ship the current shared presentation helper');
  let stale=false,stalePresentation=false;
  const server=http.createServer(async(request,response)=>{
    const pathname=new URL(request.url,'http://127.0.0.1').pathname;
    if(stale&&pathname==='/app.js'){response.writeHead(200);response.end('old application');return;}
    if(stalePresentation&&pathname==='/lib/protocol/presentation.mjs'){response.writeHead(200);response.end('old presentation helper');return;}
    if(stale&&pathname==='/api/vote'){response.writeHead(400,{'Content-Type':'application/json'});response.end('{"error":"old API validation"}');return;}
    try{const data=await readFile(path.join(dist,pathname==='/'?'index.html':pathname.slice(1)));response.writeHead(200);response.end(data);}
    catch{response.writeHead(request.method==='POST'?405:404);response.end('retired');}
  });
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  try{
    const origin=`http://127.0.0.1:${server.address().port}`;
    const good=await checkPublication({origin,dist});assert.equal(good.passed,true);assert.equal(good.summary.assetChecks,17);assert.equal(good.summary.retiredRouteChecks,32);
    assert.equal(good.assets.find(item=>item.path==='/lib/protocol/presentation.mjs').passed,true);
    assert.ok(good.expected.computationId.startsWith('1.0.0:'));
    assert.equal(JSON.stringify(good).includes(dist),false);
    stale=true;const bad=await checkPublication({origin,dist});assert.equal(bad.passed,false);
    assert.equal(bad.assets.find(item=>item.path==='/app.js').passed,false);
    assert.equal(bad.retiredRoutes.find(item=>item.path==='/api/vote'&&item.method==='POST').passed,false);
    stale=false;stalePresentation=true;
    const staleHelper=await checkPublication({origin,dist});assert.equal(staleHelper.passed,false);
    assert.equal(staleHelper.assets.find(item=>item.path==='/lib/protocol/presentation.mjs').passed,false);
    assert.equal(staleHelper.summary.matchedAssets,16);
    assert.equal(staleHelper.summary.retiredRoutePasses,32);
  }finally{server.closeIdleConnections();await new Promise(resolve=>server.close(resolve));}
});
