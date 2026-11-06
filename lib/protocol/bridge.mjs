import http from 'node:http';
import {randomBytes, timingSafeEqual} from 'node:crypto';
import {readFile, realpath, stat} from 'node:fs/promises';
import path from 'node:path';

const MIME = {'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.mjs':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json; charset=utf-8','.f32':'application/octet-stream','.svg':'image/svg+xml','.png':'image/png','.ico':'image/x-icon','.md':'text/plain; charset=utf-8'};
const MAX_BODY = 2 * 1024 * 1024;
function json(response, status, value) { response.writeHead(status, {'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'}); response.end(JSON.stringify(value)); }
async function body(request) {
  if (!(request.headers['content-type'] ?? '').startsWith('application/json')) throw new Error('Content-Type must be application/json');
  const chunks = []; let size = 0;
  for await (const chunk of request) { size += chunk.length; if (size > MAX_BODY) throw new Error('Request body exceeds 2 MiB'); chunks.push(chunk); }
  return JSON.parse(Buffer.concat(chunks).toString('utf8'));
}
export async function startBridge({runtime, staticDir, port = 4317, allowedOrigins = ['https://eigenquestions.com'], token = randomBytes(32).toString('hex')}) {
  const staticRoot = await realpath(staticDir);
  const publicOrigins = new Set(allowedOrigins.map(origin => { const url = new URL(origin); if (url.origin !== origin || !['https:','http:'].includes(url.protocol)) throw new Error('Allowed origin must be an exact HTTP(S) origin'); return origin; }));
  let address;
  const clients = new Set();
  const server = http.createServer(async (request, response) => {
    try {
      const host = `127.0.0.1:${address.port}`;
      if (request.headers.host !== host) return json(response, 403, {error:'Unexpected Host; use the 127.0.0.1 bridge URL'});
      const origin = request.headers.origin;
      if (origin && origin !== `http://${host}` && !publicOrigins.has(origin)) return json(response, 403, {error:'Origin is not allowed'});
      if (origin) {
        response.setHeader('Access-Control-Allow-Origin', origin);
        response.setHeader('Vary', 'Origin');
        response.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
        response.setHeader('Access-Control-Allow-Headers', 'Authorization, Content-Type');
        response.setHeader('Access-Control-Allow-Private-Network', 'true');
      }
      const url = new URL(request.url, `http://${host}`);
      if (request.method === 'OPTIONS') { response.writeHead(204); return response.end(); }
      if (url.pathname.startsWith('/api/')) {
        const supplied = request.headers.authorization?.replace(/^Bearer /, '') ?? url.searchParams.get('token') ?? '';
        const a = Buffer.from(supplied), b = Buffer.from(token);
        if (a.length !== b.length || !timingSafeEqual(a,b)) return json(response,401,{error:'Missing or invalid bridge session token'});
        if (request.method === 'GET' && url.pathname === '/api/session') return json(response,200,runtime.snapshot());
        if (request.method === 'GET' && url.pathname === '/api/export') return json(response,200,runtime.export());
        if (request.method === 'GET' && url.pathname === '/api/events') {
          response.writeHead(200, {'Content-Type':'text/event-stream','Cache-Control':'no-cache, no-transform','Connection':'keep-alive','X-Accel-Buffering':'no'});
          response.write(`data: ${JSON.stringify(runtime.snapshot())}\n\n`);
          const send = snapshot => response.write(`data: ${JSON.stringify(snapshot)}\n\n`);
          const unsubscribe = runtime.subscribe(send); clients.add(response);
          const heartbeat = setInterval(() => response.write(': heartbeat\n\n'),15000);
          request.on('close', () => { clearInterval(heartbeat); unsubscribe(); clients.delete(response); });
          return;
        }
        if (request.method === 'POST' && url.pathname === '/api/action') return json(response,200,runtime.action(await body(request)));
        if (request.method === 'POST' && url.pathname === '/api/import') return json(response,200,runtime.import(await body(request)));
        if (request.method === 'POST' && url.pathname === '/api/viewer') return json(response,200,runtime.acknowledge(await body(request)));
        if (request.method === 'POST' && url.pathname === '/api/search') { const data = await body(request); return json(response,200,runtime.search(data.query, data.options)); }
        if (request.method === 'POST' && url.pathname === '/api/evidence') { const data = await body(request); return json(response,200,runtime.evidence(data.ids)); }
        return json(response,404,{error:'Unknown bridge endpoint or method'});
      }
      if (!['GET','HEAD'].includes(request.method)) return json(response,405,{error:'Method not allowed'});
      const decoded = decodeURIComponent(url.pathname);
      const filename = path.resolve(staticRoot, `.${decoded === '/' ? '/index.html' : decoded}`);
      if (filename !== staticRoot && !filename.startsWith(staticRoot + path.sep)) return json(response,403,{error:'Path outside static root'});
      let target;
      try { target = await realpath(filename); } catch { return json(response,404,{error:'Static file not found'}); }
      if (!target.startsWith(staticRoot + path.sep) || !(await stat(target)).isFile()) return json(response,403,{error:'Not a static file'});
      response.writeHead(200, {'Content-Type':MIME[path.extname(target)] ?? 'application/octet-stream','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer','Cache-Control':'no-cache'});
      response.end(request.method === 'HEAD' ? undefined : await readFile(target));
    } catch (error) { if (!response.headersSent) json(response,400,{error:error.message}); else response.end(); }
  });
  server.requestTimeout = 30000;
  await new Promise((resolve,reject) => { server.once('error',reject); server.listen(port,'127.0.0.1',resolve); });
  address = server.address();
  return {
    server, token, url:`http://127.0.0.1:${address.port}/`,
    async close() { for (const client of clients) client.end(); server.closeIdleConnections(); await new Promise(resolve => server.close(resolve)); },
  };
}
