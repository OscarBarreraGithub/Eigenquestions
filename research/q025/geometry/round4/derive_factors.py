#!/usr/bin/env python3
"""Transparent exact-span factor draft, preserving uncertainty and polarity."""
import argparse, hashlib, json, re
from pathlib import Path

def factors(unit,rules):
 text=unit['text'];out=[]
 for rule in rules['rules']:
  matches=[]
  for pattern in rule['patterns']:
   for m in re.finditer(pattern,text,re.I):
    if rule.get('respectInflationPolarity'):
     prefix=text[max(0,m.start()-25):m.start()].lower()
     if re.search(r'(without|post-|pre-|post|pre)\s*$',prefix):continue
    matches.append({'start':m.start(),'end':m.end(),'text':m.group(0),'evidenceKind':'exact_question_description_span'})
  if matches:
   seen=set();matches=[m for m in matches if not ((m['start'],m['end']) in seen or seen.add((m['start'],m['end'])))]
   out.append({'role':rule['role'],'value':rule['value'],'specific':rule['specific'],'spans':matches,'status':'automatic_source_span_nomination','scientificRelation':False})
 return {'unitId':unit['unitId'],'paperId':unit['paperId'],'sourceRow':unit['sourceRow'],'textSha256':unit['textSha256'],'factors':out,'unknownRoles':[r for r in ['system','framework','target','regime','assumption_mentioned'] if not any(x['role']==r for x in out)],'qualification':'Factors identify wording-supported scope candidates, not certified scientific claims or complete physical scope. No same-paper assumptions inherited.'}

def main():
 p=argparse.ArgumentParser();p.add_argument('--cohort',type=Path,required=True);p.add_argument('--rules',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 cohort=json.loads(a.cohort.read_text());rules=json.loads(a.rules.read_text());rows=[factors(u,rules) for u in cohort['units']]
 for u,r in zip(cohort['units'],rows):
  assert hashlib.sha256(u['text'].encode()).hexdigest()==r['textSha256']
  for factor in r['factors']:
   for span in factor['spans']:assert u['text'][span['start']:span['end']]==span['text']
 result={'schemaVersion':'q025-source-scope-factors/1','cohortSha256':hashlib.sha256(a.cohort.read_bytes()).hexdigest(),'rulesSha256':hashlib.sha256(a.rules.read_bytes()).hexdigest(),'unitCount':len(rows),'scientificAcceptance':False,'factors':rows}
 a.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n');print(json.dumps({'units':len(rows),'factors':sum(len(x['factors']) for x in rows),'sha256':hashlib.sha256(a.out.read_bytes()).hexdigest()}))

if __name__=='__main__':main()
