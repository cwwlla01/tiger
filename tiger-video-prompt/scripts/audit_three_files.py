#!/usr/bin/env python3
"""Lightweight static audit for independent director/frame/video files."""
import argparse,re,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--director',required=True);p.add_argument('--frames',required=True);p.add_argument('--video',required=True);a=p.parse_args()
texts={k:Path(getattr(a,k)).read_text(encoding='utf-8') for k in ('director','frames','video')}
errors=[]
for k in ('director','frames','video'):
 if not texts[k].strip():errors.append(k+' empty')
for k in ('frames','video'):
 if not re.search(r'EP\d{3}',texts[k]):errors.append(k+' missing episode IDs')
 if not re.search(r'(?:SC\d{3}|场次)',texts[k]):errors.append(k+' missing scene IDs')
 if not re.search(r'(?:SH\d+|镜头)',texts[k]):errors.append(k+' missing shot IDs')
 if not re.search(r'T-\d+',texts[k]):errors.append(k+' missing take IDs')
if not re.search(r'(?:首帧|尾帧|关键帧|START|END|F-T)',texts['frames']):errors.append('frames missing frame roles')
if not re.search(r'(?:动作|过程|时序)',texts['video']):errors.append('video missing action/timing')
if errors:
 print('STATIC FAIL:', '; '.join(errors));sys.exit(1)
print('STATIC PASS: basic hierarchy present; does not verify prompt quality, references or video outputs')
