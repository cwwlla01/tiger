import copy, json, unittest
from pathlib import Path
from audit_visual_preflight_v249 import audit
BASE=json.loads((Path(__file__).parent/'fixtures/visual_preflight_v249/manifest.json').read_text(encoding='utf-8'))
class VisualPreflightTests(unittest.TestCase):
    def fresh(self): return copy.deepcopy(BASE)
    def test_missing_studio_block(self): self.assertEqual(audit(self.fresh())['status'],'PRE_RENDER_BLOCKED')
    def test_no_visual_claim(self): self.assertFalse(audit(self.fresh())['visual_verified'])
    def test_four_shots(self): self.assertEqual(audit(self.fresh())['shot_count'],4)
    def test_duplicate_id(self):
        x=self.fresh();x['shots'][1]['shot_id']='S01';self.assertEqual(audit(x)['status'],'TEXT_PREFLIGHT_FAILED')
    def test_interior_reveal(self):
        x=self.fresh();x['shots'][0]['interior_visible']=True;self.assertIn('S01:premature_interior_reveal',audit(x)['errors'])
    def test_axis_drift(self):
        x=self.fresh();x['shots'][1]['screen_axis']='reverse';self.assertIn('S02:axis_not_preserved',audit(x)['errors'])
    def test_hand_mismatch(self):
        x=self.fresh();x['shots'][2]['end']='released';self.assertIn('S03_to_S04_hand_state_mismatch',audit(x)['errors'])
    def test_premature_release(self):
        x=self.fresh();x['shots'][3]['start']='released';self.assertIn('S04_first_frame_premature_release',audit(x)['errors'])
    def test_sound_order(self):
        x=self.fresh();x['shots'][3]['sound_stops_before_release']=False;self.assertIn('S04_sound_action_order',audit(x)['errors'])
    def test_missing_beat(self):
        x=self.fresh();x['shots'][0]['beat_id']='';self.assertIn('S01:missing_beat',audit(x)['errors'])
    def test_complete_metadata_still_requires_visual_review(self):
        x=self.fresh();x['studio_project_id']='test';x['approved_identity_version']='test';x['approved_scene_slot_ids']={s['shot_id']:'test' for s in x['shots']}
        for s in x['shots']:s['image_sha256']='a'*64
        self.assertEqual(audit(x)['status'],'VISUAL_REVIEW_REQUIRED')
        self.assertFalse(audit(x)['visual_verified'])
if __name__=='__main__':unittest.main()
