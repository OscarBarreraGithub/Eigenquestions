"""Size/chance and omitted-flow diagnostics from the frozen job output only."""
import array,ast,collections,json,math,statistics,struct,sys,zipfile
from pathlib import Path
B=Path(__file__).resolve().parent;R=B/'results'
local=json.loads((R/'local-chart-diagnostics.json').read_text());charts={x['entryDestinationId']:x for x in json.loads((R/'local-charts.json').read_text())};ids=json.loads((R/'atom-ids.json').read_text());lookup={id:i for i,id in enumerate(ids)}
with zipfile.ZipFile(R/'complete-flows.npz')as z:b=z.read('baseline.npy')
assert b[:6]==b'\x93NUMPY';offset=10 if b[6]==1 else 12;nheader=struct.unpack('<H'if b[6]==1 else'<I',b[8:offset])[0];header=ast.literal_eval(b[offset:offset+nheader].decode());assert header['descr']=='<f8'and header['shape']==(len(ids),len(ids));a=array.array('d');a.frombytes(b[offset+nheader:]);
if sys.byteorder!='little':a.byteswap()
# C is symmetric, so row/column-major storage yields the same flat lookup.
assert all(abs(a[i*len(ids)+j]-a[j*len(ids)+i])<1e-10 for i in range(0,len(ids),100)for j in range(0,len(ids),100))
n=len(ids);degree=[sum(a[i*n:(i+1)*n])for i in range(n)];rows=[]
for r in local:
 chart=charts[r['entryDestinationId']];ix={lookup[x['destinationId']]for x in chart['nodes']if x['destinationId']in lookup};off=sum(degree[i]-a[i*n+i]for i in ix);inside=sum(a[i*n+j]for i in ix for j in ix if i!=j);rec=[]
 for i in ix:
  ranking=sorted((j for j in range(n)if j!=i),key=lambda j:a[i*n+j]/math.sqrt(degree[i]*degree[j]),reverse=True)[:5];rec.append(len(set(ranking)&ix)/5)
 rows.append({**r,'randomTop5ExpectedRecall':min(1,5/(r['represented']-1)),'directHomeAtoms':len(ix),'supportCentroidPoints':len(chart['nodes'])-len(ix),'omittedDirectAtomOffDiagonalFlowFraction':1-inside/off if off else None,'allAtomAffinityTop5RetainedByChart':statistics.mean(rec)if rec else None})
strata=[]
for lo,hi in [(2,6),(7,10),(11,15)]:
 xs=[r for r in rows if lo<=r['represented']<=hi];strata.append({'sizeRange':[lo,hi],'charts':len(xs),'meanLocalTop5Recall':statistics.mean(x['topFiveNeighborRecall']for x in xs),'meanChanceRecall':statistics.mean(x['randomTop5ExpectedRecall']for x in xs),'medianStress':statistics.median(x['distanceStress']for x in xs),'medianOmittedOffDiagonalFlow':statistics.median(x['omittedDirectAtomOffDiagonalFlowFraction']for x in xs if x['omittedDirectAtomOffDiagonalFlowFraction']is not None),'meanGlobalAffinityTop5Retained':statistics.mean(x['allAtomAffinityTop5RetainedByChart']for x in xs if x['allAtomAffinityTop5RetainedByChart']is not None)})
out={'schemaVersion':'q025-existing-layout-boundary-analysis/1','sizeHistogram':dict(sorted(collections.Counter(x['represented']for x in rows).items())),'strata':strata,'evaluationUniverse':'Reported local geometric recall compares high-dimensional distances ONLY among the selected chart points. It is not full eligible-neighborhood recall.','boundaryMetric':'Full baseline C is retained. Boundary flow uses direct-home atoms in each chart, excluding massless support-centroid points; global affinity neighbors use Cij/sqrt(di*dj), not high-dimensional diffusion distances.','rows':rows};(B/'size-boundary-analysis.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k!='rows'},indent=2))
