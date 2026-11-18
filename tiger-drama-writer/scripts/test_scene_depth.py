from pathlib import Path
import tempfile
from audit_scene_depth import audit

def script(size):
    return '## EP01《样本》\n'+''.join(f'### 1-{i} 夜 内 测试室\n'+'【人物试图开门，门被锁住。】'*size+'\n'+''.join(f'甲：我想试第{j}次，门锁还在。\n乙：你必须承担后果。\n' for j in range(5)) for i in range(1,4))
with tempfile.TemporaryDirectory() as td:
    p=Path(td)/'x.md';p.write_text(script(0));res=audit(p)
    assert res['episodes'][0]['weak_scenes']==3
    p.write_text(script(14));res=audit(p)
    assert res['episodes'][0]['weak_scenes']==0
print('scene depth tests: 2/2 passed')
