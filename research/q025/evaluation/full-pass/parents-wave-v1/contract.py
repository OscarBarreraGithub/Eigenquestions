"""Same evidence/coverage contract; bound total reply, never cut scientific clauses."""
import importlib.util,json,sys
from pathlib import Path
B=Path(__file__).resolve().parent;path=B.parent/'production-v3/contract.py';spec=importlib.util.spec_from_file_location('q025_parent_base_contract',path);base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
from compact_contract import SCHEMA

def without_string_caps(schema):
 if isinstance(schema,dict):
  schema.pop('maxLength',None)
  for v in schema.values():without_string_caps(v)
 elif isinstance(schema,list):
  for v in schema:without_string_caps(v)
without_string_caps(SCHEMA)
def evaluate(packet,reply):
 out=base.evaluate(packet,reply);out['contractAmendment']='No individual string maximum; complete qualifications required. Native runner enforces120000 total output characters. Evidence, coverage, types and normalization unchanged.';return out
if __name__=='__main__':
 if '--schema' in sys.argv:print(json.dumps(SCHEMA,indent=2));sys.exit(0)
 data=json.load(sys.stdin)
 try:print(json.dumps(evaluate(data['packet'],data['reply']),ensure_ascii=False,separators=(',',':')))
 except (AssertionError,KeyError,TypeError,ValueError) as e:print(json.dumps({'valid':False,'error':str(e)}));sys.exit(1)
