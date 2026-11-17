/** Recheck only the already-inspected cross-leaf locators; export no raw text. */
import {writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {loadFrozenCorpus,readPinnedJson} from '../corpus.mjs';
import {verifyPrimaryEvidence} from '../primary-evidence.mjs';
const root=fileURLToPath(new URL('../../../../',import.meta.url)),archiveRoot=resolve(process.argv[2]||'/Users/emmy/Developer/physics-atlas-swampland');
const corpus=await loadFrozenCorpus(resolve(root,'data/navigation')),audit=await readPinnedJson(resolve(root,'research/q025/assembly/cross-leaf-semantics-audit-v1.json'),'9c5f19dfc2b3fc80a20665a49d28e9850a3534e944dd925a14507ea6969a2489'),contextRoot=resolve(root,'research/q025/geometry/source-context-v3-compact/pack'),manifest=await readPinnedJson(resolve(contextRoot,'manifest.json'),'c86bc90966007c28ce40523348e51e4ace4d20d62354f79928133d371f77c6f5');
const verified=await verifyPrimaryEvidence({references:audit.value.inspectedPrimaryLocators,corpus,archiveRoot,contextRoot,contextManifest:manifest.value});
const report={...verified.report,testedImplementation:'research/q025/assembly/primary-evidence.mjs',sourceAuditSha256:audit.sha256,contextManifestSha256:manifest.sha256,meaning:'Re-resolved only13 already-inspected primary locators from cross-leaf audit. No new scientific reading or admission.'};
await writeFile(new URL('real-primary-resolution.json',import.meta.url),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({references:report.referenceCount,distinctLocators:report.distinctLocators,files:report.files.length}));
