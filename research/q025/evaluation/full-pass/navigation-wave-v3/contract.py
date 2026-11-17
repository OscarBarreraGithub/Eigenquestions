import importlib.util,json,sys
from pathlib import Path
path=Path(__file__).resolve().parent.parent/'navigation-contract-v3/contract.py';s=importlib.util.spec_from_file_location('navigation_v3',path);base=importlib.util.module_from_spec(s);s.loader.exec_module(base);SCHEMA=base.SCHEMA;evaluate=base.evaluate
if __name__=='__main__':
 if '--schema'in sys.argv:print(json.dumps(SCHEMA,indent=2));sys.exit()
 x=json.load(sys.stdin)
 try:print(json.dumps(evaluate(x['packet'],x['reply']),ensure_ascii=False,separators=(',',':')))
 except(AssertionError,KeyError,TypeError,ValueError)as e:print(json.dumps({'valid':False,'error':str(e)}));sys.exit(1)
