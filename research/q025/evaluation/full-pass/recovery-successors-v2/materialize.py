"""Immutable successor inputs, reusing completed reviews and existing compilers."""
import copy,importlib.util,json,sys
from pathlib import Path
import contract
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent
sys.path.insert(0,str(F/'compact-v1'));from compact_pipeline import dump,hfile,model_view
from production_pipeline import compile_production
sys.path.insert(0,str(F/'parents-v1'));from parent_pipeline import make_parent_packet
spec=importlib.util.spec_from_file_location('q025_successor_child',F/'parents-wave-v1/build_child_artifact.py');child=importlib.util.module_from_spec(spec);spec.loader.exec_module(child)

def successor_model_view(packet):
 view=model_view(packet)
 if packet.get('preservedComponents'):
  p=packet['preservedComponents'];partial=[]
  for lock in p['lockedValues']:
   path=lock['path'];covered=path and path[0] in p['completeFields']
   if len(path)>1 and path[0] in p['completeArrayPrefixes'] and isinstance(path[1],int):covered=path[1]<len(p['completeArrayPrefixes'][path[0]])
   if not covered:partial.append({'path':path,'value':lock['value']})
  # Full bytes/ranges remain in the hashed packet and prefix artifact. The model
  # sees each selected value once, plus every earlier differing scientific value
  # in the top-level streamVariants array, without repeated archival wrappers.
  view['preservedComponents']={'schemaVersion':p['schemaVersion'],'selectedAttempt':p['selectedAttempt'],'completeFields':p['completeFields'],'completeArrayPrefixes':p['completeArrayPrefixes'],'partialValueLocks':partial,'selectionBasis':p['selectionBasis'],'representationNotice':'Lossless content view: complete selected values appear once; all earlier differing complete components are in streamVariants. Exact ranges and redundant copies remain in the pinned private prefix artifact.'}
 return view

def verified_review(job,expected_receipt=None):
 job=Path(job);receipt=json.loads((job/'receipt.json').read_text());assert receipt['status']=='complete' and not receipt.get('toolUseAttempted'),'Prior review not complete'
 assert receipt.get('model')=='gpt-6-astra' and receipt.get('effort')=='xhigh' and receipt.get('sourceOnly') is True and receipt.get('sandbox')=='read-only','Prior review execution limits changed'
 if expected_receipt:assert hfile(job/'receipt.json')==expected_receipt,'Pinned prior receipt changed'
 packet=job/('packet.actual.json' if (job/'packet.actual.json').exists() else 'packet.json')
 for name,key in [('reply.raw.txt','replySha256'),('reply.json','normalizedReplySha256'),('normalization.json','normalizationReceiptSha256')]:assert hfile(job/name)==receipt[key],'Prior artifact changed: '+name
 assert hfile(packet)==receipt['inputPins']['packetSha256'],'Prior packet changed'
 return json.loads((job/'reply.json').read_text()),json.loads((job/'normalization.json').read_text()),receipt

def parent_children(req,runtime):
 plan=json.loads((F/'coverage-plan.json').read_text());regions={r['reviewKey']:r for r in plan['regions']};members=json.loads((F/'coverage-memberships.local.json').read_text());children=[];pins=[]
 for dep in req.get('childDependencies',[]):
  job=E/dep['jobPath'];
  if dep.get('externalRequestSha256'):assert hfile(job/'request.json')==dep['externalRequestSha256'],'External dependency request changed'
  reply,normal,receipt=verified_review(job,dep.get('receiptSha256'));artifact=child.build(job,regions[dep['reviewKey']],members[dep['reviewKey']])
  if normal.get('priorAnnotationContext'):artifact['priorAnnotationContext']=copy.deepcopy(normal['priorAnnotationContext'])
  if normal.get('structuralVariantEvidence'):artifact['structuralVariantEvidence']=copy.deepcopy(normal['structuralVariantEvidence'])
  if normal.get('streamVariantAssessments'):artifact['streamVariantAssessments']=copy.deepcopy(normal['streamVariantAssessments']);artifact['variantAdmissionNotice']='Material conflicts or unresolved earlier alternatives need adjudication; this child input does not admit them.'
  target=runtime/'child-artifacts'/f'{dep["reviewKey"]}.json'
  if target.exists():assert json.loads(target.read_text())==artifact,'Frozen child artifact changed'
  else:dump(target,artifact)
  artifact['artifactSha256']=hfile(target);children.append(artifact);pins.append({'reviewKey':dep['reviewKey'],'kind':dep['kind'],'path':str(target.relative_to(E)),'sha256':hfile(target),'childReceiptSha256':hfile(job/'receipt.json'),'childReplySha256':hfile(job/'reply.json')})
 return children,pins

def materialize(request_path,runtime):
 request_path=Path(request_path).resolve();d=request_path.parent;req=json.loads(request_path.read_text());runtime=Path(runtime).resolve();assert not (d/'dispatch-request.json').exists(),'Already materialized; no retry'
 source=E/req['originalPacketPath'];assert hfile(source)==req['originalPacketSha256'];original=json.loads(source.read_text());prior=None;normal=None;pins={};children=[]
 if req.get('priorJobPath') or req.get('dependsOn'):
  old=E/req['priorJobPath'] if req.get('priorJobPath') else d.parent/req['dependsOn'];prior,normal,receipt=verified_review(old,req.get('priorReceiptSha256'));pins.update(priorReplySha256=hfile(old/'reply.json'),priorRawReplySha256=receipt['replySha256'],priorReceiptSha256=hfile(old/'receipt.json'),priorNormalizationSha256=hfile(old/'normalization.json'))
 if req.get('completion'):
  preserved=E/req['preservedPacketPath'];assert hfile(preserved)==req['preservedPacketSha256'];packet=json.loads(preserved.read_text());prefix=E/req['prefixPath'];assert hfile(prefix)==req['prefixSha256'];packet['preservedComponents']=json.loads(prefix.read_text());packet['prefixArtifactSha256']=hfile(prefix);packet['streamVariants']=packet['preservedComponents']['streamVariants'];view=model_view(packet)
 elif req['kind']=='leaf':packet,view=compile_production(original,req['stage'],prior,normal)
 else:
  original['fullMemberCount']=req['fullMemberCount'];children,childpins=parent_children(req,runtime);packet,view=make_parent_packet(original,children,req['stage'],prior);pins['childArtifacts']=childpins
  contexts=[{'childRef':f'c{i}','citationRef':f'c{i}','childRegionId':c['candidateRegionId'],'scope':'attributed_prior_annotation_context','primaryReadingClaim':False,'referenceNamespaceNotice':'Nested pf/e references belong to the original child review. Cite the current c* child reference for this attributed context, never reuse its internal references as current primary evidence.','records':c['priorAnnotationContext']} for i,c in enumerate(children) if c.get('priorAnnotationContext')]
  if contexts:packet['inheritedPriorAnnotationContext']=contexts
  variants=[{'childRef':f'c{i}','citationRef':f'c{i}','childRegionId':c['candidateRegionId'],'assessments':c['streamVariantAssessments'],'structuralVariantEvidence':c.get('structuralVariantEvidence',[]),'admissionNotice':c['variantAdmissionNotice']} for i,c in enumerate(children) if c.get('streamVariantAssessments')]
  if variants:packet['inheritedStreamVariantAssessments']=variants
 if req.get('prefixPath') and not req.get('completion'):
  prefix=E/req['prefixPath'];assert hfile(prefix)==req['prefixSha256'];packet['streamVariants']=json.loads(prefix.read_text())['streamVariants'];packet['priorStreamVariantAssessments']=normal.get('streamVariantAssessments',[]);packet['structuralVariantEvidence']=normal.get('structuralVariantEvidence',[]);packet['prefixArtifactSha256']=hfile(prefix)
 view=successor_model_view(packet);base_instructions=F/('parents-wave-v1/INSTRUCTIONS.md' if req['kind']=='parent' else 'production-v3/INSTRUCTIONS.md');instructions=base_instructions.read_text()+'\n\n'+(B/'INSTRUCTIONS.md').read_text()
 dump(d/'packet.actual.json',packet);(d/'prompt-base.actual.txt').write_text(instructions+'\n\nEXACT SUCCESSOR SOURCE PACKET\n'+json.dumps(view,ensure_ascii=False,separators=(',',':'))+'\n');actual={**req,**pins,'baseRequestSha256':hfile(request_path),'packetSha256':hfile(d/'packet.actual.json'),'promptBaseSha256':hfile(d/'prompt-base.actual.txt')};dump(d/'dispatch-request.json',actual);return actual
if __name__=='__main__':print(json.dumps({'materialized':materialize(sys.argv[1],sys.argv[2])['jobId']}))
