import {decodeCapsuleBytes, MAX_COMPRESSED_BYTES} from '../lib/protocol/capsule.mjs';
import {BUDGET_NAME, VIEW_ID} from './budget.mjs';

const cors = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, HEAD, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, If-None-Match',
  'Access-Control-Expose-Headers': 'ETag, X-Content-SHA256, Location, Retry-After',
  'Access-Control-Max-Age': '86400',
  'X-Content-Type-Options': 'nosniff',
  'Content-Security-Policy': "default-src 'none'; sandbox",
};
const messages = {
  daily_attempt_limit: 'Today’s upload attempt budget is exhausted. Keep the file and retry tomorrow.',
  daily_save_limit: 'Today’s new-view budget is exhausted. Existing links still work; keep the file and retry tomorrow.',
  storage_capacity: 'Stored-view capacity is full. Existing links still work; keep the file for manual import.',
};

class HttpError extends Error {
  constructor(status, code, message) { super(message); this.status = status; this.code = code; }
}
function json(value, status = 200, headers = {}) {
  return Response.json(value, {status, headers: {...cors, 'Cache-Control': 'no-store', ...headers}});
}
function failure(status, code, message, headers) { return json({error: {code, message}}, status, headers); }

async function readUpload(request) {
  const contentType = request.headers.get('Content-Type')?.split(';')[0].trim().toLowerCase();
  if (!['application/gzip', 'application/json', 'application/octet-stream'].includes(contentType)) throw new HttpError(415, 'unsupported_media_type', 'Send a contextual-view JSON or gzip file as the request body.');
  if (request.headers.has('Content-Encoding')) throw new HttpError(415, 'unsupported_content_encoding', 'Send raw gzip bytes with Content-Type: application/gzip and no Content-Encoding header.');
  const length = request.headers.get('Content-Length');
  if (length && (!/^\d+$/.test(length) || Number(length) > MAX_COMPRESSED_BYTES)) throw new HttpError(413, 'view_too_large', 'Stored files must be at most 512 KiB; gzip the JSON locally first.');
  if (!request.body) throw new HttpError(400, 'invalid_capsule', 'The request body is empty.');
  const reader = request.body.getReader(), chunks = []; let size = 0;
  try {
    while (true) {
      const {done, value} = await reader.read(); if (done) break;
      size += value.byteLength;
      if (size > MAX_COMPRESSED_BYTES) {
        await reader.cancel();
        throw new HttpError(413, 'view_too_large', 'Stored files must be at most 512 KiB; gzip the JSON locally first.');
      }
      chunks.push(value);
    }
  } finally { reader.releaseLock(); }
  const bytes = new Uint8Array(size); let offset = 0;
  for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.byteLength; }
  try { await decodeCapsuleBytes(bytes, {encoding: contentType === 'application/gzip' ? 'gzip' : 'auto'}); }
  catch (error) {
    const tooLarge = /exceeds .*size limit|exceeds .*limit/.test(error.message);
    throw new HttpError(tooLarge ? 413 : 400, tooLarge ? 'view_too_large' : 'invalid_capsule', tooLarge ? 'The contextual view exceeds the 2 MiB decoded or 512 KiB stored limit.' : 'The file is not a supported contextual view. Check its format and source/group references.');
  }
  return {bytes, contentType: bytes[0] === 0x1f && bytes[1] === 0x8b ? 'application/gzip' : 'application/json'};
}

function receipt(request, env, object, id, sha256, status) {
  const origin = env.VIEW_SITE_ORIGIN || new URL(request.url).origin;
  return json({id, url: `${origin}/#view=${id}`, readUrl: `${origin}/api/views/${id}`,
    sha256, bytes: object.size, createdAt: object.customMetadata.createdAt}, status,
  {Location: `/api/views/${id}`});
}

async function saveView(request, env) {
  if (!env.VIEWS || !env.VIEW_BUDGET || env.VIEW_UPLOADS_ENABLED !== 'true') throw new HttpError(503, 'storage_unavailable', 'Saving links is not configured. Download this view and use file import.');
  const {bytes, contentType} = await readUpload(request);
  const sha256 = Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', bytes)), value => value.toString(16).padStart(2, '0')).join('');
  const reservation = await env.VIEW_BUDGET.getByName(BUDGET_NAME).reserve(sha256, bytes.byteLength);
  if (!reservation.ok) return failure(reservation.code === 'storage_capacity' ? 507 : 429, reservation.code, messages[reservation.code], reservation.retryAfter ? {'Retry-After': String(reservation.retryAfter)} : {});
  const {id, createdAt} = reservation, key = `views/${id}`;
  // This preflight avoids charged PUTs on ordinary retries. Conditional creation
  // still protects against concurrent retries or any unexpected key collision.
  let object = await env.VIEWS.head(key);
  if (object) {
    if (object.customMetadata?.sha256 !== sha256) throw new Error('Immutable view key collision');
    return receipt(request, env, object, id, sha256, 200);
  }
  object = await env.VIEWS.put(key, bytes, {
    onlyIf: new Headers({'If-None-Match': '*'}), sha256,
    httpMetadata: {contentType, cacheControl: 'public, max-age=31536000, immutable'},
    customMetadata: {sha256, createdAt},
  });
  if (object) return receipt(request, env, object, id, sha256, 201);
  object = await env.VIEWS.head(key);
  if (!object || object.customMetadata?.sha256 !== sha256) throw new Error('Immutable view write conflict');
  return receipt(request, env, object, id, sha256, 200);
}

async function readView(request, env, id) {
  if (!VIEW_ID.test(id)) throw new HttpError(404, 'view_not_found', 'This stored view was not found.');
  if (!env.VIEWS) throw new HttpError(503, 'storage_unavailable', 'Stored-view retrieval is not configured. You can still import a view file.');
  const object = request.method === 'HEAD' ? await env.VIEWS.head(`views/${id}`) : await env.VIEWS.get(`views/${id}`);
  if (!object) throw new HttpError(404, 'view_not_found', 'This stored view was not found.');
  const headers = {...cors,
    'Content-Type': object.httpMetadata.contentType,
    'Content-Length': String(object.size),
    'Content-Disposition': `attachment; filename="eigenquestions-${id}.${object.httpMetadata.contentType === 'application/gzip' ? 'json.gz' : 'json'}"`,
    'Cache-Control': 'public, max-age=31536000, immutable',
    ETag: object.httpEtag,
    'X-Content-SHA256': object.customMetadata.sha256,
  };
  const tags = request.headers.get('If-None-Match')?.split(',').map(tag => tag.trim().replace(/^W\//, '')) ?? [];
  if (tags.includes('*') || tags.includes(object.httpEtag)) {
    if (object.body) await object.body.cancel();
    delete headers['Content-Length'];
    return new Response(null, {status: 304, headers});
  }
  return new Response(request.method === 'HEAD' ? null : object.body, {headers});
}

export default {
  async fetch(request, env) {
    const path = new URL(request.url).pathname;
    const read = path.match(/^\/api\/views\/([^/]+)$/);
    if (path !== '/api/views' && !read) {
      if (path.startsWith('/api/')) return failure(404, 'not_found', 'This API route does not exist.');
      return env.ASSETS ? env.ASSETS.fetch(request) : new Response('Not found', {status: 404});
    }
    if (request.method === 'OPTIONS') return new Response(null, {status: 204, headers: cors});
    const methods = read ? ['GET', 'HEAD'] : ['POST'];
    if (!methods.includes(request.method)) return failure(405, 'method_not_allowed', 'This method is not supported.', {Allow: [...methods, 'OPTIONS'].join(', ')});
    try { return read ? await readView(request, env, read[1]) : await saveView(request, env); }
    catch (error) {
      if (error instanceof HttpError) return failure(error.status, error.code, error.message);
      // Never log scientific content, public identifiers or request bodies.
      console.error(JSON.stringify({event: 'stored_view_failure', operation: read ? 'read' : 'save'}));
      return failure(503, 'storage_unavailable', 'Storage did not confirm this operation. Keep the file and retry with exactly the same bytes.');
    }
  },
};
