import unittest
from audit_camera_contract import audit


class CameraContractTests(unittest.TestCase):
    def make(self, technique, extras):
        shot = {'take_id': 'T-005', 'camera_primary_id': 'CAM-01',
                'camera_modifier_ids': [technique], 'start_state': 'staring',
                'end_state': 'shocked', 'screen_axis': 'A', **extras}
        return {'takes': [shot]}, {'takes': [shot.copy()]}

    def test_dolly_zoom_pass(self):
        d, v = self.make('CAM-22', {'dolly_direction': 'backward',
                                   'zoom_direction': 'in', 'subject_size_lock': 'head'})
        self.assertEqual([], audit(d, v))

    def test_dolly_zoom_missing_zoom_fails(self):
        d, v = self.make('CAM-22', {'dolly_direction': 'backward',
                                   'zoom_direction': 'in', 'subject_size_lock': 'head'})
        v['takes'][0]['zoom_direction'] = 'out'
        self.assertTrue(any('zoom_direction' in e for e in audit(d, v)))

    def test_orbit_missing_height_fails(self):
        d, v = self.make('CAM-12', {'orbit_direction': 'clockwise',
                                   'height_change': 'low to high', 'subject_anchor': 'center'})
        v['takes'][0].pop('height_change')
        self.assertTrue(any('height_change' in e for e in audit(d, v)))

    def test_bullet_time_not_slow_motion(self):
        d, v = self.make('CAM-31', {'freeze_behavior': 'freeze',
                                   'viewpoint_motion': 'orbit', 'implementation_route': '3D'})
        v['takes'][0]['camera_modifier_ids'] = ['CAM-29']
        self.assertTrue(any('CAM-31' in e for e in audit(d, v)))

    def test_whip_pan_endpoint(self):
        d, v = self.make('CAM-21', {'whip_direction': 'right',
                                   'start_target': 'actor', 'end_target': 'monster'})
        v['takes'][0]['end_target'] = 'door'
        self.assertTrue(any('end_target' in e for e in audit(d, v)))

    def test_missing_take(self):
        d, v = self.make('CAM-29', {})
        v['takes'] = []
        self.assertTrue(any('missing 05 take' in e for e in audit(d, v)))


if __name__ == '__main__':
    unittest.main()
