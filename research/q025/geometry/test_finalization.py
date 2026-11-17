#!/usr/bin/env python3
"""Regression for the observed duplicate elapsed keyword completion failure."""
import ast, json, tempfile, time
from pathlib import Path
from types import SimpleNamespace

root=Path(__file__).parent
for filename in ['run_round1.py','run_round2.py','run_round3.py']:
 tree=ast.parse((root/filename).read_text())
 mark=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='mark')
 complete=next(n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='mark' and n.args and isinstance(n.args[0],ast.Constant) and n.args[0].value=='complete')
 with tempfile.TemporaryDirectory() as temporary:
  def dump(path,data):Path(path).write_text(json.dumps(data))
  namespace={'Path':Path,'time':time,'json':json,'dump':dump,'progress':[],'start':time.time(),'started':time.time(),'a':SimpleNamespace(out=Path(temporary))}
  module=ast.Module(body=[mark,ast.Expr(value=complete)],type_ignores=[]);ast.fix_missing_locations(module)
  exec(compile(module,filename,'exec'),namespace)
  saved=json.loads((Path(temporary)/'progress.json').read_text())
  assert saved[-1]['stage']=='complete' and saved[-1]['elapsed']>=0
 print(filename,'completion serialization passed')
