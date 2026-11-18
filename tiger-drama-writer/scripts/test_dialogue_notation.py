#!/usr/bin/env python3
"""Plain and Markdown-bold dialogue notation must be equivalent for both audits."""
import tempfile
from pathlib import Path
from audit_script_batch import audit
from audit_adversarial import inspect
lines=[]
for scene in range(1,4):
    lines.append(f'### {scene}-{scene} 夜 内 门厅\n'+('【甲拿出证物，乙提出反对，甲改变决定。】'*15))
    for i in range(8):
        who='甲' if i%2 else '乙'
        lines.append(f'{who}：这份证物需要登记，不能随便毁弃，我们先查明来历。')
with tempfile.TemporaryDirectory() as td:
    content='## EP01《标注兼容》\n'+'\n'.join(lines)
    plain=Path(td)/'plain.md';plain.write_text(content,encoding='utf8')
    bold=Path(td)/'bold.md';bold.write_text(content.replace('甲：','**甲**：').replace('乙：','**乙**：'),encoding='utf8')
    a=audit(plain)['episodes'][0];b=audit(bold)['episodes'][0]
    assert a['dialogue_turns']==b['dialogue_turns']==24,(a,b)
    assert a['speakers']==b['speakers']==2
    assert a['dialogue_han']==b['dialogue_han']
    x=inspect(plain)['episodes'][0];y=inspect(bold)['episodes'][0]
    assert x['dialogue_average_han']==y['dialogue_average_han']
    assert x['repeat_count']==y['repeat_count']
print('PASS: dialogue notation equivalence: 5 assertions')
