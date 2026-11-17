import {mkdir,writeFile} from 'node:fs/promises';
import {join} from 'node:path';
import {sha256} from './corpus.mjs';
import {validateAtlas,createAtlasNavigator} from '../../../lib/geometry/prepared-atlas.mjs';

export async function writePackage({directory,manifest,catalog,provenance,publicationStatus}) {
  await mkdir(directory,{recursive:true});
  const catalogText=JSON.stringify(catalog);
  if(Buffer.byteLength(catalogText)>64*1024*1024)throw new Error('Catalog exceeds prepared-reader 64MiB bound');
  manifest={...manifest,files:{...manifest.files,catalog:{path:'catalog.json',sha256:sha256(catalogText)}}};
  validateAtlas(manifest,catalog);
  const manifestText=JSON.stringify(manifest),manifestSha256=sha256(manifestText);
  const navigator=createAtlasNavigator({manifest,catalog,manifestSha256});navigator.computeView(navigator.createSession().states[0]);
  await writeFile(join(directory,'catalog.json'),catalogText);await writeFile(join(directory,'manifest.json'),manifestText);
  const handoff={schemaVersion:'q025-assembly-handoff/1',publicationStatus,notApprovedForSiteRelease:publicationStatus!=='accepted_for_installation',packageDirectory:directory,manifestSha256,catalogSha256:manifest.files.catalog.sha256,catalogBytes:Buffer.byteLength(catalogText),counts:{destinations:catalog.destinations.length,sources:catalog.sources.length,memberships:catalog.memberships.length,navigationRelations:catalog.relations.length,orientationNodes:catalog.orientation?.nodes.length||0,detailOverviewNodes:catalog.overview?.nodes.length||0},provenance};
  await writeFile(join(directory,'handoff.json'),JSON.stringify(handoff,null,2)+'\n');return handoff;
}
