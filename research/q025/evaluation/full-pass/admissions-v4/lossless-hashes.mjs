// Future hash compilers must decode UTF-8 once, after joining raw byte chunks.
import {scopeContentHash,sourceContributionContentHash} from '../../../assembly/accepted.mjs';
import {pathToFileURL} from 'node:url';
export async function readJsonBytes(stream){const chunks=[];for await(const chunk of stream)chunks.push(Buffer.isBuffer(chunk)?chunk:Buffer.from(chunk));return JSON.parse(Buffer.concat(chunks).toString('utf8'));}
export function hashesFor(x){const destinations=new Map(x.destinations.map(d=>[d.id,d]));return{scopes:x.destinations.map(scopeContentHash),rows:(x.rows||[]).map(r=>sourceContributionContentHash(r,scopeContentHash(destinations.get(r.destinationId))))};}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href)console.log(JSON.stringify(hashesFor(await readJsonBytes(process.stdin))));
