from pathlib import Path
import json, re
BASE=Path(__file__).resolve().parent/'fixtures/jinguang_ab_v252'
def audit():
 premise=json.loads((BASE/'frozen_premise.json').read_text())
 results={}
 for name in ('BASELINE_CINEMATIC','TACTICAL_JINGUANG_INSPIRED'):
  text=(BASE/(name+'.md')).read_text()
  ids=re.findall(r'^### (S\d+)｜(\d+)s｜(B\d+)',text,re.M)
  results[name]={'shots':len(ids),'seconds':sum(int(x[1]) for x in ids),'beats':[x[2] for x in ids],'no_claim_of_blind_test':'非独立盲测' in text}
  assert len(ids)==4 and [x[2] for x in ids]==[b['id'] for b in premise['beats']]
  assert results[name]['no_claim_of_blind_test']
 return {'status':'MANUAL_ILLUSTRATIVE_COMPARISON','plans':results,'visual_evidence':False,'independent_runs':False}
if __name__=='__main__':print(json.dumps(audit(),ensure_ascii=False,indent=2))
