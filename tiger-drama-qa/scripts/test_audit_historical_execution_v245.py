import hashlib,json,tempfile,unittest
from pathlib import Path
from audit_historical_execution_v245 import audit

class TestHistoricalExecutionV245(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory();self.root=Path(self.t.name)
        self.scene=self.root/'scene.json';self.scene.write_text('frozen')
        self.m={'scene_sha256':hashlib.sha256(b'frozen').hexdigest(),'arms':[{'arm':'V2.238','source_zip_sha256':'a'*64},{'arm':'V2.239','source_zip_sha256':'b'*64}]}
        self.man=self.root/'manifest.json';self.save()
    def tearDown(self):self.t.cleanup()
    def save(self):self.man.write_text(json.dumps(self.m))
    def result(self):return audit(self.man,self.scene,self.root)
    def add(self,arm='V2.238',**kw):
        d=self.root/arm.replace('.','').lower();d.mkdir(exist_ok=True)
        out=d/'03-专业导演分镜.md';out.write_text(kw.pop('output','shot 1'))
        record={'arm':arm,'source_zip_sha256':next(a['source_zip_sha256'] for a in self.m['arms'] if a['arm']==arm),'scene_sha256':self.m['scene_sha256'],'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'run_id':arm,'timestamp':'2026-11-16T00:00:00Z','model':'test-model','settings':{'temperature':0.7},'independence_attested':True}
        record.update(kw);(d/'run.json').write_text(json.dumps(record))
    def test_not_run(self):self.assertEqual(self.result()['status'],'NOT_RUN')
    def test_scene_tampered(self):self.scene.write_text('changed');self.assertIn('FROZEN_SCENE_HASH_MISMATCH',self.result()['errors'])
    def test_partial(self):self.add();self.assertEqual(self.result()['status'],'INCOMPARABLE')
    def test_complete(self):self.add();self.add('V2.239');self.assertEqual(self.result()['status'],'STRUCTURE_ONLY')
    def test_never_art_proven(self):self.add();self.add('V2.239');self.assertFalse(self.result()['artistic_superiority_proven'])
    def test_wrong_zip(self):self.add(source_zip_sha256='bad');self.add('V2.239');self.assertEqual(self.result()['status'],'INCOMPARABLE')
    def test_wrong_output_hash(self):self.add(output_sha256='bad');self.add('V2.239');self.assertEqual(self.result()['status'],'INCOMPARABLE')
    def test_duplicate_run(self):self.add();self.add('V2.239',run_id='V2.238');self.assertIn('DUPLICATE_RUN_ID',self.result()['errors'])
    def test_missing_independence(self):self.add(independence_attested=False);self.add('V2.239');self.assertEqual(self.result()['status'],'INCOMPARABLE')
    def test_empty_output(self):self.add(output='');self.add('V2.239');self.assertEqual(self.result()['status'],'INCOMPARABLE')
    def test_missing_model(self):self.add(model='');self.add('V2.239');self.assertEqual(self.result()['status'],'INCOMPARABLE')
    def test_invalid_log(self):self.add();self.add('V2.239');(self.root/'v2239'/'run.json').write_text('{');self.assertEqual(self.result()['status'],'INCOMPARABLE')
