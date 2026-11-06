import fs from 'node:fs/promises';
import {createNavigator,loadCorpus} from '../../lib/geometry/index.mjs';
const corpus=await loadCorpus(new URL('../../data/navigation/',import.meta.url).pathname,{readJson:async p=>JSON.parse(await fs.readFile(p,'utf8')),readBinary:p=>fs.readFile(p)});
const nav=createNavigator(corpus);
let prior;
for(const [query,intent,workRelation,refine]of [
 ['KK towers','explore','either',false],['what if they are dark matter?','explore','either',true],['how do they decay?','derive','either',true],['KK towers','derive','either',false],['KK towers','phenomenology','either',false],['KK towers','recent','on',false],['KK towers','recent','using',false],['black hole entropy','explore','either',false],['higher derivative corrections','derive','either',true]]){
 const start=performance.now();const state={schemaVersion:'1.0.0',corpusId:corpus.manifest.corpusId,id:`test-${query}-${intent}`,query,intent,workRelation,lens:'combined',focusIds:refine?prior.nodes.slice(0,5).map(x=>x.id):[]};
 const view=nav.computeView(state);console.log(JSON.stringify({query,intent,workRelation,refine,ms:performance.now()-start,explained:view.chart.explainedVariance,stress:view.chart.stress,recall:view.chart.neighborRecallAt5,top:view.nodes.slice(0,10).map(x=>({id:x.id,paper:x.paperId,title:x.title,text:x.evidence.text,score:x.score,cosine:x.retrieval.cosine,role:x.retrieval.workRelation.kind})),directions:view.directions.map(x=>x.label)},null,2));prior=view;
}
