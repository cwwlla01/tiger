import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from audit_emotion_arc import audit

SCRIPT='''## EP01｜试验
### SC01｜走廊｜夜｜内
△甲握着离职信却一直不敢递出去，她知道签字就再也回不来。
甲：我怕失去这里的工资，连下个月房租都交不起。
### SC02｜办公室｜夜｜内
△甲把离职信放在桌上，亲手按下印泥留下指印。
甲：我决定签字，责任我自己承担，别再让乙替我背锅。
△经理当场收走她的工作证，告诉她今晚就不能回宿舍。
### SC03｜楼梯｜夜｜内
△乙把自己的备用钥匙递给甲，第一次不再躲着她的眼睛。
乙：以前我觉得你会逃，今天我愿意陪你去找新住处。
'''
QUOTES=[ '△甲握着离职信却一直不敢递出去，她知道签字就再也回不来。','△甲把离职信放在桌上，亲手按下印泥留下指印。','△经理当场收走她的工作证，告诉她今晚就不能回宿舍。','△乙把自己的备用钥匙递给甲，第一次不再躲着她的眼睛。']
FIELDS=('pressure','costly_choice','visible_cost','relationship_shift')
class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.script=Path(self.tmp.name)/'EP01.md'; self.script.write_text(SCRIPT,encoding='utf-8')
        self.ledger=Path(self.tmp.name)/'ledger.json'
        self.obj={'script_sha256':hashlib.sha256(self.script.read_bytes()).hexdigest(),'character':'甲','evidence':{k:{'quote':v,'scene':(1 if i==0 else 2 if i<3 else 3),'interpretation':'这段行动对人物后续关系形成了可观察到的影响。'} for i,(k,v) in enumerate(zip(FIELDS,QUOTES))}}
    def run_audit(self):
        self.ledger.write_text(json.dumps(self.obj,ensure_ascii=False),encoding='utf-8')
        return audit(self.script,self.ledger)
    def test_good(self): self.assertTrue(self.run_audit()['accepted_for_human_review'])
    def test_hash(self):
        self.obj['script_sha256']='x'; self.assertIn('SCRIPT_SHA256_MISMATCH',self.run_audit()['errors'])
    def test_cross_script_quote(self):
        self.obj['evidence']['pressure']['quote']='△一段另一部剧本才有的非常长的对白。';self.assertIn('QUOTE_NOT_UNIQUE_PRESSURE',self.run_audit()['errors'])
    def test_scene(self):
        self.obj['evidence']['visible_cost']['scene']=3;self.assertIn('SCENE_MISMATCH_VISIBLE_COST',self.run_audit()['errors'])
    def test_order(self):
        a=self.obj['evidence'];a['pressure']['quote'],a['relationship_shift']['quote']=a['relationship_shift']['quote'],a['pressure']['quote'];a['pressure']['scene']=3;a['relationship_shift']['scene']=1
        self.assertIn('NONCHRONOLOGICAL_ARC',self.run_audit()['errors'])
    def test_missing(self):
        self.obj['evidence'].pop('visible_cost');self.assertIn('MISSING_VISIBLE_COST',self.run_audit()['errors'])
    def test_duplicate(self):
        self.script.write_text(SCRIPT+'\n'+QUOTES[0],encoding='utf-8');self.obj['script_sha256']=hashlib.sha256(self.script.read_bytes()).hexdigest();self.assertIn('QUOTE_NOT_UNIQUE_PRESSURE',self.run_audit()['errors'])
if __name__=='__main__':unittest.main()
