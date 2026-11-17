// Exact admitted scope records; this fixture grants no source membership.
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
const path='research/q025/assembly/organization-v4/candidate-v1/aggregate.local.json';
const bytes=await readFile(path),input=JSON.parse(bytes);
const ids=['q025-candidate-region:d5580f01c8ada8c471a82935','q025-candidate-region:839da90831bec9d6ef0a811b'];
const records=ids.map(id=>{const record=input.destinations.find(d=>d.id===id);if(!record)throw Error('Missing exact scope '+id);return record;});
const result={schemaVersion:'q025-scope-evidence-bound-fixture/1',origin:{path,sha256:createHash('sha256').update(bytes).digest('hex')},notice:'Exact scientific records for a runtime-bound regression. Test-only transport state and zero membership are added by the test; this fixture is not an atlas admission.',records};
await writeFile(new URL('scope-evidence-fixture.json',import.meta.url),JSON.stringify(result,null,2)+'\n');
