"""Delegate science to the explicitly corrected shared navigation validator."""
import importlib.util,json,sys
from pathlib import Path
B=Path(__file__).resolve().parent;spec=importlib.util.spec_from_file_location('navigation_v3',B.parent/'navigation-contract-v3/contract.py');shared=importlib.util.module_from_spec(spec);spec.loader.exec_module(shared);SCHEMA=shared.SCHEMA;evaluate=shared.evaluate
if __name__=='__main__':
 try:
  p=json.load(sys.stdin);print(json.dumps(evaluate(p['packet'],p['reply']),ensure_ascii=False,separators=(',',':')))
 except(AssertionError,KeyError,TypeError,ValueError)as e:print(json.dumps({'valid':False,'error':str(e)}));sys.exit(1)
