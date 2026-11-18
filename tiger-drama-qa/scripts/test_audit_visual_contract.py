import copy
import unittest
from audit_visual_contract import audit

BASE = {'take_id':'T-001','scene_id':'SC01','series_look_ref':'SERIES-A',
        'scene_look_ref':'SCENE-A','character_asset_ref':'CHAR-A-V1',
        'material_ref':'MAT-PBR-A','key_light_source':'WINDOW-1',
        'key_light_direction':'screen-left','weather':'dry',
        'palette':'cool-muted','screen_direction':'left-to-right',
        'composition':'thirds-right','focus_target':'face'}


def manifests():
    d={'takes':[copy.deepcopy(BASE)]}
    return d, copy.deepcopy(d), copy.deepcopy(d)

class VisualContractTests(unittest.TestCase):
    def test_valid(self): self.assertEqual(audit(*manifests()), [])
    def test_light_direction(self):
        d,s,v=manifests();v['takes'][0]['key_light_direction']='screen-right'
        self.assertTrue(any('key_light_direction' in e for e in audit(d,s,v)))
    def test_material_drift(self):
        d,s,v=manifests();s['takes'][0]['material_ref']='MAT-B'
        self.assertTrue(any('material_ref' in e for e in audit(d,s,v)))
    def test_character_drift(self):
        d,s,v=manifests();v['takes'][0]['character_asset_ref']='CHAR-B'
        self.assertTrue(any('character_asset_ref' in e for e in audit(d,s,v)))
    def test_composition_conflict(self):
        d,s,v=manifests();v['takes'][0]['composition_rules']=['center','thirds','symmetry']
        self.assertTrue(any('conflicting composition' in e for e in audit(d,s,v)))
    def test_weather_change(self):
        d,s,v=manifests()
        second=copy.deepcopy(BASE);second['take_id']='T-002';second['weather']='rain'
        for m in (d,s,v):m['takes'].append(copy.deepcopy(second))
        self.assertTrue(any('unexplained weather' in e for e in audit(d,s,v)))
    def test_weather_change_justified(self):
        d,s,v=manifests()
        second=copy.deepcopy(BASE);second['take_id']='T-002';second['weather']='rain';second['continuity_change_reason']='rain begins on screen'
        for m in (d,s,v):m['takes'].append(copy.deepcopy(second))
        self.assertEqual(audit(d,s,v), [])
    def test_unapproved_override(self):
        d,s,v=manifests();v['takes'][0]['unapproved_visual_change']=True
        self.assertTrue(any('unapproved' in e for e in audit(d,s,v)))
    def test_missing_still(self):
        d,s,v=manifests();s['takes']=[]
        self.assertTrue(any('missing 04' in e for e in audit(d,s,v)))

if __name__=='__main__':unittest.main()
