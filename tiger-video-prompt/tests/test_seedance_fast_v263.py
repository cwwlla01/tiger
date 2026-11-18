from __future__ import annotations
import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_seedance_fast_v263 import audit


def description():
    return {'intent':'description','delivery_type':'description',
            'source_text':'Describe a frightened person collapsing, then blue eyes and blue hair.',
            'duration_policy':{'selected_seconds':None},'takes':[]}


def single():
    return {'intent':'seedance_prompt','delivery_type':'seedance_prompt',
            'delivery_status':'CANDIDATE','fixture_id':None,
            'channel':{'platform':'jimeng_web','model_display_name':'Seedance 2 Fast',
                       'proof_scope':'unknown','multishot_proof':'unverified',
                       'supported_durations_s':[]},
            'duration_policy':{'user_requested_seconds':None,'selected_seconds':6,
                               'origin':'dramatic_pacing',
                               'reason':'One continuous emotional shift and hair-eye change plus a reaction hold.'},
            'editorial_shots':[{'id':'SH01','dramatic_event':'panic turns into transformed state'}],
            'takes':[{'id':'T01','shot_ids':['SH01'],'grouping':'SINGLE',
                      'generated_seconds':6,
                      'prompt':'A person trembles in fear and collapses emotionally, then the eyes and hair turn bright blue in a single restrained push-in shot.'}]}


def merged():
    x=single()
    x['duration_policy']['selected_seconds']=8
    x['editorial_shots']=[{'id':'SH01'},{'id':'SH02'}]
    x['takes']=[{'id':'T01','shot_ids':['SH01','SH02'],'grouping':'MERGE',
                 'generated_seconds':8,
                 'prompt':'[00:00-00:03|SH01] A wide establishing mountain view. [00:03|HARD_CUT] [00:03-00:08|SH02] A long-lens moving-cliff shot under the same sunset.',
                 'merge_decision':{
                     'benefit':'matched_visual_reveal',
                     'specific_gain':'The mountain silhouette becomes an evidence-bearing visual motif for the later identity reveal.',
                     'boundaries':[{'from':'SH01','to':'SH02',
                                  'dramatic_reason':'The rising threat should transfer attention from the witness to the distant slope without a reset.',
                                  'continuity_evidence':'Same mountain silhouette, west sunset direction and cloud layer across both compositions.',
                                  'risk_mitigation':'Keep terrain shape locked and split to two independent takes if the hard cut changes geology.',
                                  'transition':'HARD_CUT','risk_level':'LOW','pilot_observed':False}]},
                 'shot_timeline':[{'shot_id':'SH01','start':0,'end':3},
                                  {'shot_id':'SH02','start':3,'end':8}]}]
    return x


class ChannelIntentMergeV263(unittest.TestCase):
    def assert_failure(self,case,code):
        r=audit(case)
        self.assertEqual(r['status'],'FAIL',r)
        self.assertIn(code,repr(r['errors']))

    def test_description_no_video_no_duration(self):
        self.assertEqual(audit(description())['status'],'TEXT_ROUTE_PASS')

    def test_description_does_not_inherit_fifteen_seconds(self):
        x=description();x['duration_policy']['selected_seconds']=15
        self.assert_failure(x,'E-DESCRIPTION-LEAK')

    def test_description_does_not_trigger_seedance(self):
        x=description();x['delivery_type']='seedance_prompt';x['takes']=[{'id':'T01'}]
        self.assert_failure(x,'E-OUTPUT-TYPE')

    def test_single_transformation_without_unnecessary_merge(self):
        self.assertEqual(audit(single())['status'],'TEXT_ROUTE_PASS')

    def test_no_global_default_15_seconds(self):
        x=single();x['duration_policy']['origin']='legacy_fixture_default'
        self.assert_failure(x,'E-DURATION-ORIGIN')

    def test_six_case_fixture_not_global(self):
        x=single();x['duration_policy']['origin']='fixture_15s'
        self.assert_failure(x,'E-FIXTURE-LEAK')

    def test_user_duration_never_overridden(self):
        x=single();x['duration_policy'].update({'origin':'user_requested','user_requested_seconds':5,'selected_seconds':15})
        self.assert_failure(x,'E-USER-DURATION')

    def test_correct_channel_not_api_identifier(self):
        x=single();x['channel']['model_id']='doubao-seedance-2-0-fast-260128'
        self.assert_failure(x,'E-CHANNEL-MIX')

    def test_null_prompt_does_not_crash(self):
        x=single();x['takes'][0]['prompt']=None
        self.assert_failure(x,'E-PROMPT-MISSING')

    def test_merge_claimed_exact_channel_requires_evidence(self):
        x=merged();x['channel']['multishot_proof']='same_channel_verified'
        self.assert_failure(x,'E-MULTISHOT-EVIDENCE')

    def test_wrong_model_rejected(self):
        x=single();x['channel']['model_display_name']='Seedance 2.0'
        self.assert_failure(x,'E-MODEL')

    def test_merge_with_specific_reason_is_candidate_only(self):
        x=merged();r=audit(x)
        self.assertEqual(r['status'],'TEXT_ROUTE_PASS',r)
        self.assertTrue(any('MULTISHOT-PILOT' in n for n in r['notices']))

    def test_merge_for_lower_cost_fails(self):
        x=merged();x['takes'][0]['merge_decision']['benefit']='reduce_generation_count'
        self.assert_failure(x,'E-MERGE-BENEFIT')

    def test_merge_without_boundary_fails(self):
        x=merged();x['takes'][0]['merge_decision']['boundaries']=[]
        self.assert_failure(x,'E-MERGE-BOUNDARY-COUNT')

    def test_merge_boundary_without_risk_mitigation_fails(self):
        x=merged();x['takes'][0]['merge_decision']['boundaries'][0]['risk_mitigation']='none'
        self.assert_failure(x,'E-MERGE-RISK')

    def test_high_risk_requires_actual_pilot(self):
        x=merged();x['takes'][0]['merge_decision']['boundaries'][0]['risk_level']='HIGH'
        self.assert_failure(x,'E-MERGE-HIGH-RISK')

    def test_no_submit_ready_claim_without_channel_evidence(self):
        x=merged();x['delivery_status']='SUBMIT_READY'
        self.assert_failure(x,'E-SUBMIT-READY')

    def test_no_multi_shot_submit_ready_based_on_series(self):
        x=merged();x['delivery_status']='SUBMIT_READY'
        x['channel']['proof_scope']='user_interface_verified'
        x['channel']['evidence']='Screenshot of same Seedance 2 Fast selection in exact Jimeng interface.'
        self.assert_failure(x,'E-CHANNEL-SUBMIT-MERGE')

    def test_merged_copy_block_cannot_omit_shot(self):
        x=merged();x['takes'][0]['prompt']=x['takes'][0]['prompt'].replace('SH02','MISS')
        self.assert_failure(x,'E-MERGED-PROMPT-SHOT')

    def test_merged_copy_block_needs_cut_instruction(self):
        x=merged();x['takes'][0]['prompt']=x['takes'][0]['prompt'].replace('HARD_CUT','MISSING')
        self.assert_failure(x,'E-MERGED-PROMPT-CUT')

    def test_missing_internal_timeline_fails(self):
        x=merged();x['takes'][0]['shot_timeline']=[]
        self.assert_failure(x,'E-MULTISHOT-TIMELINE')

    def test_shot_order_mismatch_fails(self):
        x=merged();x['editorial_shots']=[{'id':'SH02'},{'id':'SH01'}]
        self.assert_failure(x,'E-SHOT-COVERAGE')

    def test_reference_token_without_upload_fails(self):
        x=single();x['takes'][0]['prompt']+=' @image1'
        self.assert_failure(x,'E-UNVERIFIED-ASSET-TOKEN')

    def test_verified_duration_choices_enforced_for_submit(self):
        x=single();x['channel'].update({'proof_scope':'user_interface_verified',
                                        'evidence':'Image showing same channel and selected model with 4 and 8 second durations.',
                                        'supported_durations_s':[4,8]})
        x['delivery_status']='SUBMIT_READY'
        self.assert_failure(x,'E-CHANNEL-DURATION')

    def test_generation_padding_above_retained_scene_is_allowed(self):
        x=single();x['takes'][0]['generated_seconds']=8
        x['takes'][0]['edit_in_seconds']=0
        x['takes'][0]['edit_out_seconds']=6
        self.assertEqual(audit(x)['status'],'TEXT_ROUTE_PASS')

    def test_invalid_trim_bounds_rejected(self):
        x=single();x['takes'][0]['generated_seconds']=8
        x['takes'][0]['edit_in_seconds']=0
        x['takes'][0]['edit_out_seconds']=9
        self.assert_failure(x,'E-EDIT-TRIM')

    def test_valid_api_model_distinct_from_jimeng(self):
        x=single();x['channel'].update({'platform':'volc_ark_api','model_id':'doubao-seedance-2-0-fast-260128',
                                        'proof_scope':'official_exact_channel',
                                        'evidence':'Official Volc Ark Seedance 2.0 family reference for Fast model ID.'})
        self.assertEqual(audit(x)['status'],'TEXT_ROUTE_PASS')

if __name__=='__main__':unittest.main()
