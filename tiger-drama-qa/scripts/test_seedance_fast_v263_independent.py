from __future__ import annotations
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_seedance_fast_v263_independent import audit


def new_merged():
    return {'intent':'seedance_prompt','delivery_type':'seedance_prompt','delivery_status':'CANDIDATE',
            'channel':{'platform':'jimeng_web','model_display_name':'Seedance 2 Fast',
                       'proof_scope':'unknown','multishot_proof':'series_only'},
            'duration_policy':{'origin':'dramatic_pacing','selected_seconds':8},
            'editorial_shots':[{'id':'SH01'},{'id':'SH02'}],
            'takes':[{'id':'T01','grouping':'MERGE','shot_ids':['SH01','SH02'],
                      'merge_decision':{'benefit':'motivated_viewpoint_change','boundaries':[
                          {'from':'SH01','to':'SH02','dramatic_reason':'The witness gaze motivates closer inspection of the same distant subject.',
                           'continuity_evidence':'The mountain silhouette and light direction remain the same across the jump cut.',
                           'risk_mitigation':'Split locally into two takes if the change corrupts the shared geography.',
                           'risk_level':'LOW'}]},
                      'shot_timeline':[{'shot_id':'SH01','start':0,'end':4},
                                       {'shot_id':'SH02','start':4,'end':8}]}]}


class V263IndependentQA(unittest.TestCase):
    def test_valid_candidate_with_evidence(self):
        self.assertEqual(audit(new_merged())['status'],'TEXT_STRUCTURE_PASS')

    def test_missing_boundary_evidence(self):
        x=new_merged();x['takes'][0]['merge_decision']['boundaries'][0]['dramatic_reason']=''
        self.assertEqual(audit(x)['status'],'FAIL')

    def test_unmotivated_merge_rejected(self):
        x=new_merged();x['takes'][0]['merge_decision']['benefit']='save_cost'
        self.assertEqual(audit(x)['status'],'FAIL')

    def test_high_risk_without_pilot(self):
        x=new_merged();x['takes'][0]['merge_decision']['boundaries'][0]['risk_level']='HIGH'
        self.assertEqual(audit(x)['status'],'FAIL')

    def test_candidate_never_claimed_ready_on_series_docs(self):
        x=new_merged();x['delivery_status']='SUBMIT_READY'
        self.assertEqual(audit(x)['status'],'FAIL')

    def test_description_no_fifteen_second_template(self):
        x={'intent':'description','delivery_type':'description','duration_policy':{'selected_seconds':None},'takes':[]}
        self.assertEqual(audit(x)['status'],'TEXT_STRUCTURE_PASS')
        x['duration_policy']['selected_seconds']=15
        self.assertEqual(audit(x)['status'],'FAIL')

    def test_wrong_shot_order(self):
        x=new_merged();x['editorial_shots'][0]['id']='SH09'
        self.assertEqual(audit(x)['status'],'FAIL')

    def test_api_id_attached_to_jimeng(self):
        x=new_merged();x['channel']['model_id']='doubao-seedance-2-0-fast-260128'
        self.assertEqual(audit(x)['status'],'FAIL')

if __name__=='__main__':unittest.main()
