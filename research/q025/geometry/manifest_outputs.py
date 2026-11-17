#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('root',type=Path);a=p.parse_args()
files={}
for f in sorted(a.root.rglob('*')):
 if f.is_file() and f.name!='output-manifest.json':
  h=hashlib.sha256()
  with f.open('rb') as stream:
   for b in iter(lambda:stream.read(1048576),b''):h.update(b)
  files[str(f.relative_to(a.root))]={'sha256':h.hexdigest(),'bytes':f.stat().st_size}
(a.root/'output-manifest.json').write_text(json.dumps({'schemaVersion':'q025-geometry-output-files/1','files':files},indent=2)+'\n')
print(json.dumps({'files':len(files),'bytes':sum(f['bytes'] for f in files.values())}))
