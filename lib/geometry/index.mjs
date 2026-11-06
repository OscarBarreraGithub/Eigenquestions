import {ENGINE_SOURCE_SHA256,PARAMETERS_SHA256} from './identity.mjs';
/** Frozen-data, deterministic question-conditioned navigation. No model or network
 * calls occur during computeView. Works unchanged in browsers and Node. */
export const ENGINE_VERSION = '1.0.0';
export const DEFAULT_PARAMETERS = Object.freeze({nodeLimit:64,anchorLimit:18,directionCount:5,graphSteps:3,restart:0.65,lexicalWeight:0.44,vectorWeight:0.40,graphWeight:0.16,focusWeight:0.55,chartMethod:'weighted-pca',chartFitScope:'direction-centroids',grouping:'mmr',pcaIterations:64,slabQuantile:0.8,seed:17,contextConsensus:0.6,contextTermLimit:6,contextLexicalWeight:0.55,contextVectorWeight:0.45,contextFloor:0.28,contextStrength:0.72,contextAnchorFloor:0.25,contextAnchorStrength:0.75,contextAnchorLexical:0.6,contextAnchorVector:0.4});
const EPS=1e-12;
const dot=(a,b)=>{let s=0;for(let i=0;i<a.length;i++)s+=a[i]*b[i];return s;};
const norm=a=>Math.sqrt(dot(a,a));
const unit=a=>{const n=norm(a);return Array.from(a,v=>n>EPS?v/n:0);};
const sub=(a,b)=>Array.from(a,(v,i)=>v-b[i]);
const quantile=(a,q)=>{const s=[...a].sort((x,y)=>x-y);return s[Math.min(s.length-1,Math.floor(q*(s.length-1)))]??0;};
const hash=text=>{let h=2166136261;for(const c of text)h=Math.imul(h^c.charCodeAt(0),16777619);return (h>>>0).toString(16).padStart(8,'0');};
const stableSort=(a)=>a.sort((x,y)=>y.score-x.score||x.index-y.index);
const STOP=new Set('a an the of on in at to for and or is are was were be been with from by as it its this that these those can could would should how what why which when where do does did let lets want see work works recent recently about using use uses used study studies studied derive derived derivation derive implications phenomenology explore paper papers we our their they if into under between through show shown have has more most also new result results based theory theoretical model models proposed proposal question investigate investigating discuss consider'.split(' '));
export function tokenize(text){
  const normalized=String(text??'').toLowerCase().normalize('NFKD').replace(/[–—−]/g,'-').replace(/\bkk\b/g,'kaluza klein').replace(/kaluza[- ]klein/g,'kaluza klein').replace(/\badc\b/g,'anti de sitter distance conjecture').replace(/\bwgc\b/g,'weak gravity conjecture');
  return normalized.match(/[a-z][a-z0-9]+/g)?.filter(x=>!STOP.has(x)).map(x=>x.length>4&&x.endsWith('s')&&!x.endsWith('ss')?x.slice(0,-1):x)??[];
}
function checkedBuffer(value){if(value instanceof ArrayBuffer)return value;if(ArrayBuffer.isView(value))return value.buffer.slice(value.byteOffset,value.byteOffset+value.byteLength);throw new Error('Binary reader must return ArrayBuffer or typed array');}
export async function loadCorpus(base,options={}){
  const url=p=>`${String(base).replace(/\/$/,'')}/${p}`;
  const readJson=options.readJson??(async path=>{const r=await fetch(path);if(!r.ok)throw new Error(`Corpus HTTP ${r.status}: ${path}`);return r.json();});
  const readBinary=options.readBinary??(async path=>{const r=await fetch(path);if(!r.ok)throw new Error(`Corpus HTTP ${r.status}: ${path}`);return r.arrayBuffer();});
  const manifestBuffer=checkedBuffer(await readBinary(url('manifest.json'))),manifest=JSON.parse(new TextDecoder().decode(manifestBuffer));if(manifest.schemaVersion!=='1.0.0')throw new Error('Unsupported corpus schemaVersion');
  const digestHex=async buffer=>{if(!globalThis.crypto?.subtle)throw new Error('SHA-256 verification needs Web Crypto (HTTPS or localhost)');const digest=await crypto.subtle.digest('SHA-256',buffer);return [...new Uint8Array(digest)].map(x=>x.toString(16).padStart(2,'0')).join('');};
  const verifiedBinary=async file=>{const buffer=checkedBuffer(await readBinary(url(file.path)));if(buffer.byteLength!==file.bytes)throw new Error(`Shard byte length mismatch: ${file.path}`);if(options.verifyHashes!==false&&(await digestHex(buffer))!==file.sha256)throw new Error(`Shard hash mismatch: ${file.path}`);return buffer;};
  const verifiedJson=async file=>JSON.parse(new TextDecoder().decode(await verifiedBinary(file)));
  const manifestSha256=await digestHex(manifestBuffer);
  const count=manifest.scope.unitCount,dim=manifest.encoder.dimensions;
  const units=new Array(count),adjacency=new Array(count),vectors=new Float32Array(count*dim);
  const tasks=[async()=>verifiedJson(manifest.files.papers),async()=>manifest.files.scopes?verifiedJson(manifest.files.scopes):{},...manifest.files.units.map(f=>async()=>{const x=await verifiedJson(f);if(x.length!==f.count)throw new Error('Unit shard size mismatch');for(let i=0;i<x.length;i++)units[f.start+i]=x[i];}),...manifest.files.graph.map(f=>async()=>{const x=await verifiedJson(f);if(x.length!==f.count)throw new Error('Graph shard size mismatch');for(let i=0;i<x.length;i++)adjacency[f.start+i]=x[i];}),...manifest.files.vectors.map(f=>async()=>{const buffer=await verifiedBinary(f);if(buffer.byteLength!==f.count*dim*4)throw new Error('Vector shard size mismatch');vectors.set(new Float32Array(buffer),f.start*dim);})];
  const results=new Array(tasks.length);let next=0,completed=0;
  await Promise.all(Array.from({length:Math.min(6,tasks.length)},async()=>{while(next<tasks.length){const i=next++;results[i]=await tasks[i]();options.onProgress?.({completed:++completed,total:tasks.length});}}));
  return {manifest,manifestSha256,papers:results[0],scopes:results[1],units,vectors,adjacency};
}
function weightedMean(rows,weights,dimension){const out=Array(dimension).fill(0);let sum=0;rows.forEach((row,i)=>{const w=weights[i];sum+=w;for(let d=0;d<dimension;d++)out[d]+=w*row[d];});return out.map(x=>x/(sum||1));}
function orthogonal(v,bases){let out=Array.from(v);for(const b of bases){const s=dot(out,b);out=out.map((x,i)=>x-s*b[i]);}return out;}
function signFix(v,reference){if(reference&&Math.abs(dot(v,reference))>EPS)return dot(v,reference)<0?v.map(x=>-x):v;let k=0;for(let i=1;i<v.length;i++)if(Math.abs(v[i])>Math.abs(v[k]))k=i;return v[k]<0?v.map(x=>-x):v;}
/** An affine plane in the SAME ambient Euclidean metric as unit source vectors.
 * Points are projections; inSlab separately reports finite residual thickness. */
export function computeChart(rows,weights,anchor,parameters={}){
  const p={...DEFAULT_PARAMETERS,...parameters},d=rows[0]?.length??anchor.length;
  const center=weightedMean(rows,weights,d),centered=rows.map(r=>sub(r,center)),sum=weights.reduce((a,b)=>a+b,0)||1;
  const variance=Array(d).fill(0);centered.forEach((r,i)=>r.forEach((x,j)=>variance[j]+=weights[i]*x*x/sum));
  const totalVariance=variance.reduce((a,b)=>a+b,0);
  const cov=v=>{const out=Array(d).fill(0);centered.forEach((r,i)=>{const a=weights[i]*dot(r,v)/sum;for(let j=0;j<d;j++)out[j]+=a*r[j];});return out;};
  const principal=(bases,offset)=>{let v=unit(orthogonal(Array.from({length:d},(_,j)=>Math.sin((j+1)*(p.seed+offset+1)*0.731)),bases));for(let k=0;k<p.pcaIterations;k++){const raw=orthogonal(cov(v),bases);if(norm(raw)<EPS)break;v=unit(raw);}if(dot(v,cov(v))<EPS){const j=variance.indexOf(Math.max(...variance));v=unit(orthogonal(Array.from({length:d},(_,i)=>i===j?1:0),bases));}return signFix(v);};
  let first=p.chartMethod==='anchor-pca'?unit(sub(anchor,center)):principal([],0);let anchorFallback=false;
  if(norm(first)<EPS||dot(first,cov(first))<EPS){first=principal([],0);anchorFallback=true;}
  first=signFix(first,sub(anchor,center));let second=principal([first],1);const eigenvalues=[dot(first,cov(first)),dot(second,cov(second))];
  if(eigenvalues[1]<EPS)second=Array(d).fill(0);
  const projected=centered.map(r=>[dot(r,first),dot(r,second)]),residuals=centered.map((r,i)=>Math.sqrt(Math.max(0,dot(r,r)-projected[i][0]**2-projected[i][1]**2)));
  const scale=Math.sqrt(projected.reduce((s,r,i)=>s+weights[i]*(r[0]**2+r[1]**2),0)/sum)||1;
  const third=principal([first,second],2),omittedVariance=dot(third,cov(third)),relativeCutoffGap=(eigenvalues[1]-omittedVariance)/Math.max(EPS,eigenvalues[1]);
  const thickness=quantile(residuals,p.slabQuantile),captured=eigenvalues.reduce((a,b)=>a+b,0);
  let loss=0,den=0;for(let i=0;i<rows.length;i++)for(let j=0;j<i;j++){const hd=Math.sqrt(Math.max(0,dot(sub(rows[i],rows[j]),sub(rows[i],rows[j]))));const ld=Math.hypot(projected[i][0]-projected[j][0],projected[i][1]-projected[j][1]);loss+=(hd-ld)**2;den+=hd**2;}
  const knnRecall=()=>{if(rows.length<3)return 1;let hits=0,total=0;const k=Math.min(5,rows.length-1);for(let i=0;i<rows.length;i++){const h=[],l=[];for(let j=0;j<rows.length;j++)if(i!==j){h.push([j,-dot(sub(rows[i],rows[j]),sub(rows[i],rows[j]))]);l.push([j,-Math.hypot(projected[i][0]-projected[j][0],projected[i][1]-projected[j][1])]);}h.sort((a,b)=>b[1]-a[1]||a[0]-b[0]);l.sort((a,b)=>b[1]-a[1]||a[0]-b[0]);const ids=new Set(h.slice(0,k).map(x=>x[0]));hits+=l.slice(0,k).filter(x=>ids.has(x[0])).length;total+=k;}return hits/total;};
  return {method:p.chartMethod,center,basis:[first,second],dimension:d,metric:'Euclidean chord distance on L2-normalized frozen embeddings',scale,thickness,slabQuantile:p.slabQuantile,projectionMeaning:'All selected points are orthogonally projected; inSlab is a separate residual test, not a claim of exact plane intersection.',explainedVariance:totalVariance>EPS?captured/totalVariance:0,axisVariances:eigenvalues,omittedAxisVariance:omittedVariance,relativeCutoffGap,nearDegenerate:totalVariance>EPS&&relativeCutoffGap<.05,totalVariance,degenerate:totalVariance<EPS||eigenvalues[1]<EPS,anchorFallback,orthogonalityError:Math.abs(dot(first,second)),basisNorms:[norm(first),norm(second)],stress:Math.sqrt(loss/(den||1)),neighborRecallAt5:knnRecall(),points:projected.map((r,i)=>({x:r[0]/scale,y:r[1]/scale,residual:residuals[i],inSlab:residuals[i]<=thickness+EPS})),residualSummary:{median:quantile(residuals,.5),p90:quantile(residuals,.9),max:Math.max(0,...residuals)}};
}
/** Project observations into an already fitted plane, without changing it. */
export function projectToChart(rows,weights,chart){
  const centered=rows.map(r=>sub(r,chart.center)),coordinates=centered.map(r=>chart.basis.map(b=>dot(r,b))),sum=weights.reduce((a,b)=>a+b,0)||1;
  const residuals=centered.map((r,i)=>Math.sqrt(Math.max(0,dot(r,r)-coordinates[i][0]**2-coordinates[i][1]**2)));
  const totalVariance=centered.reduce((s,r,i)=>s+weights[i]*dot(r,r)/sum,0),captured=coordinates.reduce((s,r,i)=>s+weights[i]*dot(r,r)/sum,0);
  const distances=rows.map(()=>[]),projected=rows.map(()=>[]);let loss=0,den=0;
  for(let i=0;i<rows.length;i++)for(let j=0;j<i;j++){const difference=sub(rows[i],rows[j]),hd=Math.sqrt(dot(difference,difference)),ld=Math.hypot(coordinates[i][0]-coordinates[j][0],coordinates[i][1]-coordinates[j][1]);loss+=(hd-ld)**2;den+=hd**2;distances[i].push([j,hd]);distances[j].push([i,hd]);projected[i].push([j,ld]);projected[j].push([i,ld]);}
  const recall=k=>{if(rows.length<2)return 1;k=Math.min(k,rows.length-1);let hits=0;for(let i=0;i<rows.length;i++){const order=a=>[...a].sort((x,y)=>x[1]-y[1]||x[0]-y[0]);const actual=new Set(order(distances[i]).slice(0,k).map(x=>x[0]));hits+=order(projected[i]).slice(0,k).filter(x=>actual.has(x[0])).length;}return hits/(rows.length*k);};
  return {points:coordinates.map((r,i)=>({x:r[0]/chart.scale,y:r[1]/chart.scale,residual:residuals[i],inSlab:residuals[i]<=chart.thickness+EPS})),explainedVariance:totalVariance>EPS?captured/totalVariance:0,totalVariance,stress:Math.sqrt(loss/(den||1)),neighborRecallAt1:recall(1),neighborRecallAt5:recall(5),residualSummary:{median:quantile(residuals,.5),p90:quantile(residuals,.9),max:Math.max(0,...residuals)},sourceSlabThickness80:quantile(residuals,.8)};
}
export function createNavigator(corpus){
  const {manifest,units,vectors,adjacency}=corpus,d=manifest.encoder.dimensions,n=units.length;
  if(!Number.isInteger(d)||d<1||vectors.length!==n*d||adjacency.length!==n)throw new Error('Corpus vector/graph alignment mismatch');
  const computationId=`${ENGINE_VERSION}:${ENGINE_SOURCE_SHA256}:${PARAMETERS_SHA256}:${corpus.manifestSha256??`fixture-${hash(JSON.stringify(manifest))}`}`;
  const paperById=new Map(corpus.papers.map(p=>[p.id,p])),idToIndex=new Map(),paperUnits=new Map();
  const tokens=[],titleTokens=[],documentFrequency=new Map();
  units.forEach((u,i)=>{if(u.vectorRow!==i)throw new Error('Corpus row mismatch');if(idToIndex.has(u.id))throw new Error('Duplicate corpus ID');idToIndex.set(u.id,i);const p=paperById.get(u.paperId);if(!p)throw new Error('Missing paper record');const ts=tokenize(u.text);tokens.push(ts);titleTokens.push(tokenize(p.title));for(const t of new Set(ts))documentFrequency.set(t,(documentFrequency.get(t)??0)+1);if(!paperUnits.has(u.paperId))paperUnits.set(u.paperId,[]);paperUnits.get(u.paperId).push(i);for(let j=0;j<d;j++)if(!Number.isFinite(vectors[i*d+j]))throw new Error('Nonfinite embedding');for(const[j,w]of adjacency[i]??[])if(!Number.isInteger(j)||j<0||j>=n||!Number.isFinite(w)||w<0)throw new Error('Invalid graph edge');});
  const row=i=>vectors.subarray(i*d,(i+1)*d),idf=t=>Math.log(1+(n-(documentFrequency.get(t)??0)+.5)/((documentFrequency.get(t)??0)+.5));
  const lex=(query,ts)=>{if(!query.length)return 0;const counts=new Map();for(const t of ts)counts.set(t,(counts.get(t)??0)+1);let s=0,matched=0;for(const t of query){const tf=counts.get(t)??0;if(tf){matched++;s+=idf(t)*tf*2.2/(tf+1.2*(.25+.75*ts.length/45));}}return s*(.35+.65*(matched/query.length)**2);};
  const relation=(i,qt)=>{const u=units[i],matchedTerms=qt.filter(t=>tokens[i].includes(t)),coverage=matchedTerms.length/(qt.length||1),qMatch=u.lens==='physical_question'&&coverage>=.5,mMatch=u.lens==='method'&&coverage>=.5;return {matchedTerms,termCoverage:coverage,kind:qMatch?'on':mMatch?'using':'ambiguous',basis:qMatch?'question facet mentions query terms':mMatch?'method facet mentions query terms':'semantic neighbor; role not established',evidenceIds:[u.id]};};
  function retrieve(state,overrides={}){
    const p={...DEFAULT_PARAMETERS,...state.parameters,...overrides};if(state.computationId&&state.computationId!==computationId)throw new Error('Computation identity mismatch: engine, parameters, or corpus changed');if(state.corpusId&&state.corpusId!==manifest.corpusId)throw new Error(`Corpus mismatch: expected ${manifest.corpusId}`);
    const query=String(state.query??'').trim(),qt=[...new Set(tokenize(query))],focus=(state.focusIds??[]).map(id=>idToIndex.get(id)).filter(i=>i!==undefined),constraints=state.constraints??{},excluded=new Set(constraints.excludeIds??[]),intent=state.intent??'explore',workRelation=state.workRelation??(intent==='using'?'using':'either'),lens=state.lens??'combined';
    const legal=i=>{const u=units[i],year=paperById.get(u.paperId).year;return !excluded.has(u.id)&&!excluded.has(u.paperId)&&(!constraints.yearMin||year>=constraints.yearMin)&&(!constraints.yearMax||year<=constraints.yearMax);};
    const intentTerms=intent==='derive'?tokenize('calculation equations action analytic proof derivation formalism expansion approximation mathematical construction'):intent==='phenomenology'?tokenize('observable measurement constraints experiment prediction signal detection observation data exclusion bound'):[];
    const focusFrequency=new Map();for(const i of focus)for(const t of new Set([...tokens[i],...titleTokens[i]]))focusFrequency.set(t,(focusFrequency.get(t)??0)+1);
    const focusTerms=[...focusFrequency].filter(([t,count])=>count>=Math.max(1,Math.ceil(focus.length*p.contextConsensus))&&!qt.includes(t)).sort((a,b)=>b[1]*idf(b[0])-a[1]*idf(a[0])||a[0].localeCompare(b[0])).slice(0,p.contextTermLimit).map(x=>x[0]);
    const contextLexical=units.map((u,i)=>focusTerms.length?lex(focusTerms,[...tokens[i],...titleTokens[i]]):0),maxContext=Math.max(EPS,...contextLexical),focusCenter=focus.length?unit(weightedMean(focus.map(row),focus.map(()=>1),d)):null;
    const lexical=units.map((u,i)=>{if(!legal(i))return 0;const direct=lex(qt,tokens[i]),title=lex(qt,titleTokens[i]);return direct+(workRelation==='using'?0:0.24*title);});
    const maxLex=Math.max(EPS,...lexical),lexicalNorm=lexical.map(x=>x/maxLex);
    const preference=i=>{const u=units[i];let w=1;if(lens!=='combined'&&u.lens!==lens)w*=.5;if((intent==='derive'||workRelation==='using')&&u.lens!=='method')w*=.42;if(workRelation==='on'&&u.lens!=='physical_question')w*=.45;if(intentTerms.length)w*=1+.30*Math.min(1,lex(intentTerms,tokens[i])/7);return w;};
    const anchorCandidates=stableSort(units.map((_,i)=>({index:i,score:lexicalNorm[i]*preference(i)*(focus.length?p.contextAnchorFloor+p.contextAnchorStrength*(p.contextAnchorLexical*contextLexical[i]/maxContext+p.contextAnchorVector*Math.max(0,dot(row(i),focusCenter))):1)})).filter(x=>x.score>0));
    const anchors=[],anchorPapers=new Set();for(const c of anchorCandidates){const paper=units[c.index].paperId;if(!anchorPapers.has(paper)){anchors.push(c);anchorPapers.add(paper);}if(anchors.length>=p.anchorLimit)break;}
    const warnings=[];if(focus.length!==(state.focusIds??[]).length)warnings.push('Some focus IDs were not found in this corpus and were ignored.');if(!qt.length&&!focus.length)warnings.push('Enter a physics question or choose a source-linked focus; an empty query has no supported semantic anchor.');else if(!anchors.length&&!focus.length)warnings.push('No query terms matched the frozen source descriptions. Supply a source ID or more specific terminology; no question embedding was invented.');
    if(!anchors.length&&!focus.length)return {p,query,qt,focus,candidates:[],anchors:[],anchor:Array(d).fill(0),warnings,lexicalNorm,graph:[],workRelation};
    const ar=anchors.map(x=>row(x.index)),aw=anchors.map(x=>x.score*x.score);for(const i of focus){ar.push(row(i));aw.push(p.focusWeight*(aw.reduce((a,b)=>a+b,0)||1)/Math.max(1,focus.length));}
    const anchor=unit(weightedMean(ar,aw,d));
    // Personalized diffusion restarts at source anchors; every query also scans ALL
    // vectors, so no inherited cluster, path, or previous chart can trap retrieval.
    let restart=new Float64Array(n);anchors.forEach(x=>restart[x.index]+=x.score);focus.forEach(i=>restart[i]+=.4);let rs=restart.reduce((a,b)=>a+b,0)||1;restart=restart.map(x=>x/rs);let graph=restart.slice();
    for(let step=0;step<p.graphSteps;step++){const next=restart.map(x=>p.restart*x);for(let i=0;i<n;i++){if(!graph[i])continue;const edges=adjacency[i]??[],sum=edges.reduce((s,e)=>s+e[1],0);if(sum)for(const [j,w]of edges)next[j]+=(1-p.restart)*.85*graph[i]*w/sum;else next[i]+=(1-p.restart)*.85*graph[i];const same=paperUnits.get(units[i].paperId);for(const j of same)next[j]+=(1-p.restart)*.15*graph[i]/same.length;}graph=next;}
    const maxGraph=Math.max(EPS,...graph),focusSet=new Set(focus),candidates=[];
    for(let i=0;i<n;i++)if(legal(i)){
      const vector=Math.max(0,dot(anchor,row(i))),graphScore=Math.sqrt(graph[i]/maxGraph),lexical=lexicalNorm[i],pref=preference(i),role=relation(i,qt);
      let score=(p.lexicalWeight*lexical+p.vectorWeight*vector*vector+p.graphWeight*graphScore)*pref;
      const contextScore=focus.length?p.contextLexicalWeight*contextLexical[i]/maxContext+p.contextVectorWeight*Math.max(0,dot(row(i),focusCenter)):1;
      if(focus.length)score*=p.contextFloor+p.contextStrength*contextScore;
      if(workRelation!=='either'&&role.kind!==workRelation)score*=.62;
      if(intent==='recent'){const year=paperById.get(units[i].paperId).year;const age=Math.max(0,manifest.scope.latestYear-year);score*=.72+.28*Math.exp(-age/4);}
      if(focusSet.has(i))score+=.08;
      if(score>.025)candidates.push({index:i,score,lexical,vector,graph:graphScore,role,contextScore,preference:pref});
    }
    stableSort(candidates);
    // At most two facets/paper in chart, one per direction anchor.
    const counts=new Map(),selected=[];for(const c of candidates){const id=units[c.index].paperId;if((counts.get(id)??0)<2){selected.push(c);counts.set(id,(counts.get(id)??0)+1);}if(selected.length>=p.nodeLimit)break;}
    return {p,query,qt,focus,candidates:selected,ranked:candidates,anchors,anchor,warnings,lexicalNorm,graph,workRelation,focusTerms};
  }
  function evidence(i){const u=units[i],paper=paperById.get(u.paperId);return {id:u.id,paperId:u.paperId,title:paper.title,text:u.text,lens:u.lens,url:paper.url,year:paper.year,date:paper.date,datePrecision:paper.datePrecision,...u.evidence,readingScope:u.evidence.readingScope??corpus.scopes?.[u.evidence.readingScopeId]??null};}
  function directions(result,state){
    const {p,candidates}=result;if(!candidates.length)return [];
    const unique=[],seen=new Set();for(const c of candidates){if((state.focusIds??[]).includes(units[c.index].id)&&state.query===units[c.index].text.slice(0,3900))continue;const id=units[c.index].paperId;if(!seen.has(id)){unique.push(c);seen.add(id);}}
    if(!unique.length)return [];const k=Math.min(p.directionCount,unique.length),seeds=[unique[0]];
    for(let j=1;j<k;j++){let best=null,bestScore=-Infinity;for(const c of unique){if(seeds.includes(c))continue;const similarity=Math.max(...seeds.map(s=>dot(row(c.index),row(s.index))));const value=.56*c.score/unique[0].score+.44*(1-similarity);if(value>bestScore){best=c;bestScore=value;}}if(best)seeds.push(best);}
    if(p.grouping==='medoids')for(let iteration=0;iteration<3;iteration++){const groups=seeds.map(()=>[]);for(const c of unique){const distances=seeds.map(s=>dot(row(c.index),row(s.index)));groups[distances.indexOf(Math.max(...distances))].push(c);}groups.forEach((group,j)=>{if(!group.length)return;let best=seeds[j],bestValue=-Infinity;for(const c of group){const value=group.reduce((sum,x)=>sum+x.score*dot(row(c.index),row(x.index)),0);if(value>bestValue){best=c;bestValue=value;}}seeds[j]=best;});}
    const groups=seeds.map(()=>[]);for(const c of candidates){const ds=seeds.map(s=>dot(row(c.index),row(s.index)));groups[ds.indexOf(Math.max(...ds))].push(c);}
    return seeds.map((s,j)=>{const u=units[s.index],members=groups[j],paper=paperById.get(u.paperId);const first=u.text.split(/(?<=[?.!])\s/)[0];const label=first.length>125?`${first.slice(0,122).replace(/\s+\S*$/,'')}…`:first;return {id:`direction:${hash(`${state.id??''}:${u.id}:${p.grouping}`)}`,label,summary:`${members.length} nearby source descriptions; representative: ${paper.title}. Similarity suggests a question, not a physical conclusion.`,seedIds:[u.id],query:u.text.slice(0,3900),intent:state.intent??'explore',lens:state.lens??'combined',workRelation:state.workRelation??'either',evidenceIds:members.slice(0,3).map(x=>units[x.index].id),memberIds:members.map(x=>units[x.index].id),x:0,y:0};});
  }
  function computeView(state){
    const r=retrieve(state),{p}=r,rows=r.candidates.map(c=>row(c.index)),weights=r.candidates.map(c=>Math.max(c.score,EPS));
    const ds=directions(r,state),candidateById=new Map(r.candidates.map(c=>[units[c.index].id,c])),totalMass=weights.reduce((a,b)=>a+b,0)||1;
    const groups=ds.map(direction=>{const members=direction.memberIds.map(id=>candidateById.get(id)),mass=members.reduce((s,c)=>s+c.score,0),centroid=weightedMean(members.map(c=>row(c.index)),members.map(c=>c.score),d);const withinGroupVariance=members.reduce((s,c)=>{const dx=sub(row(c.index),centroid);return s+c.score*dot(dx,dx)/mass;},0);return {centroid,mass,withinGroupVariance,sourceCount:members.length};});
    const fitGroups=p.chartFitScope==='direction-centroids'&&groups.length>1;
    const chart=computeChart(fitGroups?groups.map(g=>g.centroid):rows,fitGroups?groups.map(g=>g.mass):weights,r.anchor,p);
    chart.fitScope=fitGroups?'direction-centroids':'source-vectors';chart.metric=fitGroups?`Euclidean distance between weighted source-vector means in the original ${d}-dimensional normalized-embedding ambient space; means are not renormalized`:chart.metric;
    chart.fitWeightsMeaning=fitGroups?'Each group mass is the sum of selected source retrieval scores; this is display importance, not a scientific probability.':'Selected source retrieval scores';
    const sourceProjection=projectToChart(rows,weights,chart),groupProjection=projectToChart(groups.map(g=>g.centroid),groups.map(g=>g.mass),chart);
    chart.sourceDiagnostics={...sourceProjection};delete chart.sourceDiagnostics.points;
    chart.groupDiagnostics={...groupProjection};delete chart.groupDiagnostics.points;
    chart.neighborRecallAt1=fitGroups?groupProjection.neighborRecallAt1:sourceProjection.neighborRecallAt1;
    chart.groupCentroids=groups.map((g,i)=>({directionId:ds[i].id,centroid:g.centroid,mass:g.mass,sourceCount:g.sourceCount,withinGroupVariance:g.withinGroupVariance}));
    chart.points=sourceProjection.points;
    const nodes=r.candidates.map((c,k)=>{const u=units[c.index],paper=paperById.get(u.paperId);return {id:u.id,paperId:u.paperId,title:paper.title,label:u.text,...chart.points[k],score:c.score,sourceUrl:paper.url,year:paper.year,date:paper.date,lens:u.lens,evidence:evidence(c.index),retrieval:{lexical:c.lexical,cosine:c.vector,graph:c.graph,context:c.contextScore,workRelation:c.role},directionId:ds.find(dir=>dir.memberIds.includes(u.id))?.id};});
    for(let i=0;i<ds.length;i++){const g=groups[i];Object.assign(ds[i],groupProjection.points[i],{mass:g.mass,massFraction:g.mass/totalMass,sourceCount:g.sourceCount,withinGroupRms:Math.sqrt(g.withinGroupVariance)});} 
    const included=new Set(r.candidates.map(c=>c.index)),edges=[];for(const c of r.candidates){for(const[j,w]of adjacency[c.index]??[])if(included.has(j)&&c.index<j)edges.push({source:units[c.index].id,target:units[j].id,type:'retrieval_affinity',weight:w,evidence:'text-derived source affinity; no physical implication'});for(const j of paperUnits.get(units[c.index].paperId)??[])if(included.has(j)&&c.index<j)edges.push({source:units[c.index].id,target:units[j].id,type:'same_paper',weight:1,evidence:paperById.get(units[c.index].paperId).url});}
    delete chart.points;
    const warnings=[...r.warnings];if(nodes.length&&chart.sourceDiagnostics.explainedVariance<.4)warnings.push('The source overlay omits substantial variation. Direction-level fidelity describes group means only; consult within-group spread and source residuals. Proximity is not a physics claim.');if(fitGroups&&chart.neighborRecallAt1<.8)warnings.push('The 2D direction map changes some nearest-direction relationships. Its layout is an overview, not a reliable nearest-neighbor ordering.');if(chart.nearDegenerate)warnings.push('Nearby variance directions have a small gap: small data changes can rotate the chart. Fixed-state replay remains deterministic.');if(chart.degenerate)warnings.push('The selected neighborhood has fewer than two supported geometric directions.');if(r.workRelation!=='either')warnings.push('ON/USING is inferred from matched question/method facets. Semantic-only neighbors are marked ambiguous.');if(state.intent==='recent')warnings.push(manifest.scope.recentMeaning);
    return {schemaVersion:'1.0.0',computationId,engineVersion:ENGINE_VERSION,corpusId:manifest.corpusId,stateId:state.id??`state:${hash(JSON.stringify(state))}`,query:r.query,nodes,edges,directions:ds,chart,diagnostics:{parameters:p,globalCandidateCount:r.ranked?.length??0,corpusUnitCount:n,distinctPapers:new Set(nodes.map(x=>x.paperId)).size,anchorIds:r.anchors.map(x=>units[x.index].id),focusIds:r.focus.map(i=>units[i].id),contextTerms:r.focusTerms??[],queryAnchorMethod:'paper-balanced lexical source-facet anchors blended with selected real vectors; no fabricated query embedding',scope:manifest.scope,snapshotDate:manifest.snapshotDate,sourceRoleCounts:nodes.reduce((a,x)=>{const role=x.retrieval.workRelation.kind;a[role]=(a[role]??0)+1;return a;},{}),retrievalKnobsPinned:true,globalReentry:true},warnings};
  }
  return {computationId,computeView,search(query,options={}){const r=retrieve({query,corpusId:manifest.corpusId,...options},{nodeLimit:options.limit??20});return r.candidates.map(c=>({...evidence(c.index),score:c.score,retrieval:{lexical:c.lexical,cosine:c.vector,graph:c.graph,context:c.contextScore,workRelation:c.role}}));},getEvidence(ids){return ids.map(id=>{const i=idToIndex.get(id);return i===undefined?{id,error:'unknown source ID'}:evidence(i);});},corpus:manifest};
}
