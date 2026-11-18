#!/usr/bin/env python3
from pathlib import Path
import tempfile
from check_serial_decay import assess

def make(counts):
    s=''
    for i,n in enumerate(counts,1):
        s+=f'## EP{i:02d}《测试》\n### SC1 房间\n### SC2 室外\n### SC3 门口\n'+('甲'*n)+'\n'
    return s
with tempfile.TemporaryDirectory() as td:
    p=Path(td)/'fixture.md'
    p.write_text(make([930,700,680,710,690]),encoding='utf8')
    a=assess(p)
    assert 'LATE_BATCH_COMPRESSION' in a['issues'],a
    assert 'EP02_THIN' in a['issues'],a
    p.write_text(make([930,960,950,950,960]),encoding='utf8')
    b=assess(p)
    assert b['issues']==[],b
print('serial decay tests: 3 assertions passed')
