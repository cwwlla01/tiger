"""Conservative A/B evidence gate; no aesthetic scores are inferred."""
import hashlib
from pathlib import Path

REQUIRED = ('source_sha256','skill_version','run_id','output_sha256','output_path')

def sha256_file(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(65536),b''):h.update(block)
    return h.hexdigest()

def audit(baseline, candidate):
    if baseline is None or candidate is None:
        return {'status':'NOT_COMPARABLE','issues':['MISSING_INDEPENDENT_RUN'],'artistic_quality':'NOT_VERIFIED'}
    if not isinstance(baseline,dict) or not isinstance(candidate,dict):
        return {'status':'NOT_COMPARABLE','issues':['INVALID_RECORD'],'artistic_quality':'NOT_VERIFIED'}
    issues=[]
    for label,record in (('BASELINE',baseline),('CANDIDATE',candidate)):
        for field in REQUIRED:
            if not isinstance(record.get(field),str) or not record[field].strip():issues.append(f'{label}_MISSING_{field}')
        if record.get('evidence_level')=='SYNTHETIC_FIXTURE':issues.append(f'{label}_SYNTHETIC_FIXTURE')
        path=record.get('output_path')
        if isinstance(path,str) and path.strip():
            file=Path(path)
            if not file.is_file():issues.append(f'{label}_OUTPUT_NOT_FOUND')
            elif record.get('output_sha256')!=sha256_file(file):issues.append(f'{label}_HASH_MISMATCH')
    if baseline.get('source_sha256')!=candidate.get('source_sha256'):issues.append('DIFFERENT_SOURCE')
    if baseline.get('run_id')==candidate.get('run_id'):issues.append('NOT_INDEPENDENT_RUNS')
    if baseline.get('output_path')==candidate.get('output_path'):issues.append('SHARED_OUTPUT_PATH')
    if baseline.get('skill_version')==candidate.get('skill_version'):issues.append('SAME_SKILL_VERSION')
    if baseline.get('run_conditions')!=candidate.get('run_conditions'):issues.append('DIFFERENT_RUN_CONDITIONS')
    return {'status':'COMPARABLE_FOR_REVIEW' if not issues else 'NOT_COMPARABLE','issues':issues,'artistic_quality':'NOT_VERIFIED'}
