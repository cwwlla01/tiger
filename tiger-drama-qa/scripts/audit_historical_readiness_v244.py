"""Inspect original historical director archives without pretending to execute them."""
import argparse, hashlib, json, zipfile, difflib
from pathlib import Path

def sha(data): return hashlib.sha256(data).hexdigest()

def inspect(left,right):
    with zipfile.ZipFile(left) as a, zipfile.ZipFile(right) as b:
        if a.testzip() or b.testzip(): raise ValueError("archive corrupt")
        na=set(a.namelist()); nb=set(b.namelist())
        sk="tiger-drama-director/SKILL.md"
        if sk not in na or sk not in nb: raise ValueError("missing director entrypoint")
        aa=a.read(sk).decode("utf-8"); bb=b.read(sk).decode("utf-8")
        added=sorted(nb-na);removed=sorted(na-nb)
        changed=sorted(k for k in na&nb if a.read(k)!=b.read(k))
        diff=list(difflib.unified_diff(aa.splitlines(),bb.splitlines(),fromfile="V2.38/SKILL.md",tofile="V2.39/SKILL.md",lineterm=""))
        return {"status":"SOURCE_DIFF_ONLY","archives":{"v238_sha256":sha(Path(left).read_bytes()),"v239_sha256":sha(Path(right).read_bytes())},"files_added":added,"files_removed":removed,"files_changed":changed,"skill_diff_lines":diff[:400],"historical_runs_executed":False,"blind_review_performed":False}

def main():
    p=argparse.ArgumentParser();p.add_argument("--v238",required=True);p.add_argument("--v239",required=True);p.add_argument("--out")
    args=p.parse_args(); result=inspect(args.v238,args.v239);out=json.dumps(result,ensure_ascii=False,indent=2)
    if args.out:Path(args.out).write_text(out+"\n",encoding="utf-8")
    else:print(out)
if __name__=="__main__":main()
