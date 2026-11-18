"""Check evidence completeness, never artistic quality."""
import json,sys
REQUIRED=('source_anchor','shot_id','observed_issue','audience_impact','minimal_fix','confidence')
def audit(report):
    errors=[]
    for i,item in enumerate(report.get('findings',[])):
        for field in REQUIRED:
            if not isinstance(item.get(field),str) or not item[field].strip(): errors.append(f'finding[{i}].{field}: missing')
        if item.get('severity') not in ('P0','P1','P2'): errors.append(f'finding[{i}].severity: invalid')
    status=report.get('status')
    if status in ('TEXT_REVIEW_PASS','VIDEO_QA_PASSED'):
        if not report.get('independent_reviewer_evidence'): errors.append('independent review evidence missing')
        if status=='VIDEO_QA_PASSED' and not report.get('footage_evidence'): errors.append('footage evidence missing')
        if any(x.get('severity') in ('P0','P1') for x in report.get('findings',[])): errors.append('blocking findings unresolved')
    return errors
if __name__=='__main__':
    data=json.load(open(sys.argv[1],encoding='utf-8'));errors=audit(data);print(json.dumps({'ok':not errors,'errors':errors},ensure_ascii=False,indent=2));sys.exit(bool(errors))
