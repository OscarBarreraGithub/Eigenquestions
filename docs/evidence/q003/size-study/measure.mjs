import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {deflateRawSync,inflateRawSync,brotliCompressSync,brotliDecompressSync,constants} from 'node:zlib';
import {loadLocalNavigator} from '/Users/emmy/Documents/Eigenquestions/lib/protocol/runtime.mjs';
import {createNavigator} from '/Users/emmy/Documents/Eigenquestions/lib/geometry/index.mjs';
import {createSession,currentState,applyAction,exportSession,importSession} from '/Users/emmy/Documents/Eigenquestions/lib/protocol/session.mjs';

const directory='/private/tmp/eigenquestions-q003-size-study-20261106';
const {corpus,navigator}=await loadLocalNavigator();
const independentNavigator=createNavigator(corpus);
const base={corpusId:corpus.manifest.corpusId,computationId:navigator.computationId};
const prefix='https://eigenquestions.com/#recipe=';
const hash=value=>createHash('sha256').update(value).digest('hex');
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const budget=length=>[4096,8192,16384].find(limit=>length<=limit)??null;
function measure(value){
  const raw=Buffer.from(JSON.stringify(value));
  const deflate=deflateRawSync(raw,{level:9});
  const brotli=brotliCompressSync(raw,{params:{[constants.BROTLI_PARAM_QUALITY]:11}});
  if(!inflateRawSync(deflate).equals(raw)||!brotliDecompressSync(brotli).equals(raw))throw Error('Compression round trip failed');
  const b64=n=>n.toString('base64url').length;
  return {jsonBytes:raw.length,rawBase64urlBytes:b64(raw),deflateBytes:deflate.length,deflateBase64urlBytes:b64(deflate),brotliBytes:brotli.length,brotliBase64urlBytes:b64(brotli),rawWholeUrlBytes:prefix.length+b64(raw),deflateWholeUrlBytes:prefix.length+b64(deflate),brotliWholeUrlBytes:prefix.length+b64(brotli),smallestBudgetBytes:{raw:budget(prefix.length+b64(raw)),deflate:budget(prefix.length+b64(deflate)),brotli:budget(prefix.length+b64(brotli))}};
}
const results=[];
async function capture(name,session,view=navigator.computeView(currentState(session))){
  const state=currentState(session);
  // This envelope is only a measurement specimen, not an implemented API.
  const recipe={recipeVersion:'1.0.0',kind:'eigenquestions-focus',state};
  const roundTrip=JSON.parse(Buffer.from(Buffer.from(JSON.stringify(recipe)).toString('base64url'),'base64url').toString('utf8'));
  const reconstructedSession=createSession(roundTrip.state);
  const reconstructed=independentNavigator.computeView(currentState(reconstructedSession));
  const imported=importSession(JSON.parse(JSON.stringify(exportSession(session))),base);
  const replayed=independentNavigator.computeView(currentState(imported));
  const check={stateIdEqual:currentState(reconstructedSession).id===state.id,fullViewJsonExactlyEqual:same(view,reconstructed),fullSessionReplayExactlyEqual:same(view,replayed),sourceOrderEqual:same(view.nodes.map(n=>n.id),reconstructed.nodes.map(n=>n.id)),groupsNamesMembershipEqual:same(view.directions,reconstructed.directions),chartCenterBasisDiagnosticsEqual:same(view.chart,reconstructed.chart),viewSha256:hash(JSON.stringify(view))};
  if(!Object.values(check).filter(v=>typeof v==='boolean').every(Boolean))throw Error(`Reconstruction mismatch: ${name}`);
  const result={name,query:state.query,stateId:state.id,historyLength:session.states.length,focusCount:state.focusIds.length,nodeCount:view.nodes.length,directionCount:view.directions.length,edgeCount:view.edges.length,groupMemberCounts:view.directions.map(d=>d.memberIds.length),reconstruction:check,sizes:{currentState:measure(state),recipe:measure(recipe),session:measure(exportSession(session)),view:measure(view),snapshot:measure({session,view,revision:0})}};
  results.push(result);
  await writeFile(`${directory}/${name}-snapshot.json`,JSON.stringify({session,view,revision:0}));
  console.log(JSON.stringify({name,history:session.states.length,recipe:result.sizes.recipe,session:result.sizes.session,view:result.sizes.view}));
}
let kk=createSession({...base,query:'KK towers'});
await capture('kk-broad',kk);
for(const [name,query] of [['kk-dark-matter','KK towers as dark matter'],['kk-decays','How do Kaluza-Klein dark matter gravitons decay?'],['kk-lifetime','What observational constraints bound the lifetime of Kaluza-Klein graviton dark matter?']]){
  const output=applyAction(kk,{type:'refine',query,intent:'phenomenology'},navigator);kk=output.session;await capture(name,kk,output.view);
}
let axion=createSession({...base,query:'axions quantum gravity constraints'});
await capture('axion-broad',axion);
let output=applyAction(axion,{type:'refine',query:'How does the axion weak gravity conjecture constrain axion decay constants through instanton actions?',intent:'derive',lens:'method'},navigator);axion=output.session;
await capture('axion-derive',axion,output.view);
const unitsById=new Map(corpus.units.map(unit=>[unit.id,unit]));
const direction=output.view.directions.find(d=>d.seedIds.some(id=>unitsById.get(id)?.paperId==='2203.05575'));
if(!direction)throw Error('Expected existing EDE direction absent; do not invent a substitute');
output=applyAction(axion,{type:'select',directionId:direction.id},navigator);axion=output.session;
await capture('axion-selected-method',axion,output.view);
output=applyAction(axion,{type:'refine',query:'What phenomenological constraints does the axion weak gravity conjecture impose on early dark energy and its energy fraction?',intent:'phenomenology',lens:'combined'},navigator);axion=output.session;
await capture('axion-ede',axion,output.view);
const last=JSON.parse(await readFile(`${directory}/axion-ede-snapshot.json`,'utf8'));
const alternateHistory={...last.session,states:[kk.states[0],currentState(last.session)],cursor:1};
const historyIgnored=same(last.view,independentNavigator.computeView(currentState(alternateHistory)));
const viewParts={};
for(const key of Object.keys(last.view))viewParts[key]=Buffer.byteLength(JSON.stringify(last.view[key]));
const report={study:'Q003 URL artifact size and v1 reconstruction, read-only architecture experiment',timestamp:new Date().toISOString(),node:process.version,computationId:navigator.computationId,corpusId:corpus.manifest.corpusId,compression:{deflate:'raw DEFLATE level 9',brotli:'Brotli quality 11',text:'compact JSON UTF-8, unpadded base64url'},urlAccounting:{prefix,limits:[4096,8192,16384],notice:'Engineering budgets only, not universal browser or messaging limits; compressed recipe loading is not implemented.'},equalityScope:'Exact JSON in two independently created navigators in the same Node process, using a verified corpus; no cross-browser or scientific semantic-equivalence claim.',sameCurrentStateDifferentHistoryProducesSameView:historyIgnored,lastViewTopLevelBytes:viewParts,results};
await writeFile(`${directory}/report.json`,JSON.stringify(report,null,2)+'\n');
console.log(`REPORT ${directory}/report.json`);
