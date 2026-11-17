#!/usr/bin/env python3
"""Small scope and output-finalization checks before a full export."""
import tempfile
from pathlib import Path
from context_override import POLICY, resolve_override
from export_index import write, desc

def node(i,paper,record,window):
    return {'id':i,'paperId':paper,'provenance':{'record':{'record_id':record,'source_unit_id':window}}}
p={'sourceObjects':[node('method','p','r','w1'),node('same-window','p','r','w1'),node('whole-paper','p','whole','whole_paper_first_pass'),node('external','other','e','w1')],
   'sourceRelations':[{'id':'reviewed','source':'method','target':'external','semanticStatus':'reviewed_scoped'}]}
d={'shardId':'p','attachmentOverride':{'policy':POLICY,'anchorObjectIds':['method'],'sourceRecordIds':['r']}}
x=resolve_override('u',d,p);sc={a['scope']:a for a in x['sourceAttachments']}
assert sc['direct_record_relation']['relationIds']==['reviewed']
assert sc['direct_record_relation']['objectIds']==['external','method']
assert sc['shared_extraction_window_context']['objectIds']==['same-window']
assert sc['same_paper_context']['objectIds']==['whole-paper']
d['attachmentOverride']['anchorObjectIds']=['missing'];d['attachmentOverride']['sourceRecordIds']=['whole']
x=resolve_override('u',d,p)
assert x['missingAnchorIds']==['missing']
assert x['coverage']['windowRecordCount']==0 and x['coverage']['directExportedRelationCount']==0
assert not any(a['scope']=='direct_record_relation' for a in x['sourceAttachments'])
with tempfile.TemporaryDirectory() as t:
    f=Path(t)/'out.json';write(f,x);metadata=desc(f);assert metadata['bytes']>0 and len(metadata['sha256'])==64
print('scope and output-finalization smoke checks passed')
