#!/usr/bin/env python3
import tempfile
from pathlib import Path
from audit_script_batch import audit
from audit_scene_depth import audit as scene_audit
for title in ["## EP01｜测试", "## EP01《测试》", "## EP01：测试"]:
    for scene in ["### 场1｜内景｜屋内｜夜", "### 场景1｜内景｜屋内｜夜", "### SC1 内景"]:
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"x.md"
            p.write_text(title+"\n"+scene+"\n许澄：现在关阀。\n"+scene.replace('1','2')+"\n周岳：我来。\n"+scene.replace('1','3')+"\n许澄：确认。\n",encoding="utf8")
            r=audit(p)
            assert len(r['episodes'])==1,(title,r)
            assert r['episodes'][0]['scenes']==3,(scene,r)
            assert len(scene_audit(p)['episodes'][0]['scenes'])==3,scene
print('heading notation: 9/9 passed')
