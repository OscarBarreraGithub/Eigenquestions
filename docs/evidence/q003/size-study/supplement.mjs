import {readFile,writeFile} from 'node:fs/promises';
import {deflateRawSync,brotliCompressSync,constants} from 'node:zlib';
import {loadLocalNavigator} from '/Users/emmy/Documents/Eigenquestions/lib/protocol/runtime.mjs';
import {currentState,importSession} from '/Users/emmy/Documents/Eigenquestions/lib/protocol/session.mjs';
const directory='/private/tmp/eigenquestions-q003-size-study-20261106';
const report=JSON.parse(await readFile(`${directory}/report.json`,'utf8'));
const prefix='https://eigenquestions.com/#recipe=';
const budget=length=>[4096,8192,16384].find(limit=>length<=limit)??null;
function measure(value){
  const raw=Buffer.from(JSON.stringify(value));const deflate=deflateRawSync(raw,{level:9});const brotli=brotliCompressSync(raw,{params:{[constants.BROTLI_PARAM_QUALITY]:11}});const b64=n=>n.toString('base64url').length;
  return {jsonBytes:raw.length,rawBase64urlBytes:b64(raw),deflateBytes:deflate.length,deflateBase64urlBytes:b64(deflate),brotliBytes:brotli.length,brotliBase64urlBytes:b64(brotli),rawWholeUrlBytes:prefix.length+b64(raw),deflateWholeUrlBytes:prefix.length+b64(deflate),brotliWholeUrlBytes:prefix.length+b64(brotli),smallestBudgetBytes:{raw:budget(prefix.length+b64(raw)),deflate:budget(prefix.length+b64(deflate)),brotli:budget(prefix.length+b64(brotli))}};
}
const extras={};
for(const kind of ['kk','axion']){
  const snapshots=await Promise.all(report.results.filter(result=>result.name.startsWith(kind)).map(async result=>JSON.parse(await readFile(`${directory}/${result.name}-snapshot.json`,'utf8'))));
  const payload={session:snapshots.at(-1).session,visitedViews:snapshots.map(snapshot=>snapshot.view)};
  extras[`${kind}FourStepFullJourney`]={views:snapshots.length,sizes:measure(payload)};
}
const trial=JSON.parse(await readFile('/Users/emmy/Documents/Eigenquestions/docs/evidence/fresh-agent-session.json','utf8'));
const {navigator,corpus}=await loadLocalNavigator();
const session=importSession(trial,{corpusId:corpus.manifest.corpusId,computationId:navigator.computationId});
const current=currentState(session),view=navigator.computeView(current);
extras.retainedFreshAgentTrial={historyLength:session.states.length,stateId:current.id,sessionSizes:measure(trial),currentRecipeSizes:measure({recipeVersion:'1.0.0',kind:'eigenquestions-focus',state:current}),viewSizes:measure(view)};
const components=report.lastViewTopLevelBytes;
report.supplement=extras;
await writeFile(`${directory}/report.json`,JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({supplement:extras,lastViewTopLevelBytes:components,sameCurrentStateDifferentHistoryProducesSameView:report.sameCurrentStateDifferentHistoryProducesSameView},null,2));
