import tempfile, unittest, json
from pathlib import Path
from audit_package import audit

class Tests(unittest.TestCase):
    def test_missing_inputs_are_not_accepted(self):
        with tempfile.TemporaryDirectory() as d:
            x=audit(d)
            self.assertEqual(x['production_acceptance'],'NOT_VERIFIED')
            self.assertEqual(len(x['flags']),5)
    def test_present_tasks_not_automatically_accepted(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d,'02-资产生成任务清单.json').write_text(json.dumps({'tasks':[{'prompt':'测试','image_status':'IMAGE_MISSING'}]}),encoding='utf-8')
            x=audit(d)
            self.assertEqual(x['tasks']['count'],1)
            self.assertTrue(any(y['code']=='IMAGE_MISSING' for y in x['flags']))
            self.assertEqual(x['gate_decisions']['G2'],'NOT_VERIFIED')
    def test_invalid_json_is_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d,'02-资产生成任务清单.json').write_text('{',encoding='utf-8')
            self.assertTrue(any(y['code']=='TASK_JSON_INVALID' for y in audit(d)['flags']))

if __name__=='__main__':unittest.main()
