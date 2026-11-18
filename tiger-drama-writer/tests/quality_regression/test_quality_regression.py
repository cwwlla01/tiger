import copy, json, pathlib, unittest
ROOT=pathlib.Path(__file__).parent


def writer(d):
    errors=[]; beats=d.get('beats',[])
    ids=[b.get('id') for b in beats]
    if not ids or any(type(x) is not int for x in ids) or ids!=sorted(set(ids)):
        errors.append('beat_ids_not_strictly_increasing')
    events={}
    for b in beats:events.setdefault(b.get('event'),[]).append(b)
    for e in ('visible_rule','visible_clue','vote','withdraw','formal_count','reveal'):
        if len(events.get(e,[]))!=1:errors.append('event_count_'+e)
    if errors:return errors
    at=lambda e:events[e][0]['id']
    if not at('visible_rule')<at('vote')<at('withdraw')<at('formal_count'):
        errors.append('illegal_vote_withdraw_count_sequence')
    if not at('visible_clue')<at('reveal'):errors.append('unfair_clue_sequence')
    if not {'valid_until':'formal_count','first_visible_beat':at('visible_rule')}.items()<=d['rules'][0].items():
        errors.append('rule_metadata_mismatch')
    vote=events['vote'][0].get('text','')
    if not ('实时预览' in vote and '尚未计票' in vote):errors.append('vote_preview_not_explicit')
    if '正式计票前' not in events['visible_rule'][0].get('text',''):errors.append('rule_not_explicit')
    count=events['formal_count'][0].get('text','')
    if '尚未开始' in count or '未开始' in count:errors.append('formal_count_not_performed')
    return errors

def director(d):
    errors=[]; shots=d.get('shots',[]); takes=d.get('takes',{})
    if len(shots)!=4:errors.append('edit_shot_count')
    if not shots:return errors
    if shots[0].get('key_before')!=d['source'].get('key_initial'):
        errors.append('initial_key_state_mismatch')
    used=[]; last=None
    for i,s in enumerate(shots):
        if i and last!=s.get('key_before'):errors.append('key_teleport_'+str(i))
        last=s.get('key_after')
        if not s.get('takes'):errors.append('shot_missing_takes_'+str(i))
        used+=s.get('takes',[])
    if len(used)!=len(set(used)):errors.append('take_reused')
    if set(used)!=set(takes):errors.append('take_coverage_mismatch')
    for t,info in takes.items():
        if not isinstance(info.get('generation_seconds'),(int,float)) or info['generation_seconds']<=0:
            errors.append('invalid_generation_duration_'+t)
    if d['source'].get('key_winner')=='UNSPECIFIED':
        for s in shots:
            if s.get('key_after','').startswith(('held_by_','hand_')):
                errors.append('winner_not_authorized')
    for p in d.get('proposals',[]):
        if p.get('approval')!='WRITER_APPROVAL_REQUIRED' or p.get('used_in_authoritative_shots') is not False:
            errors.append('proposal_promoted')
    return errors

class Regression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.w=json.loads((ROOT/'W03-retest-v7.json').read_text())
        cls.d=json.loads((ROOT/'D01-retest-v7.json').read_text())
    def test_writer_positive(self):self.assertEqual(writer(self.w),[])
    def test_writer_bad_order(self):
        x=copy.deepcopy(self.w);x['beats'][3]['id']=8;self.assertIn('beat_ids_not_strictly_increasing',writer(x))
    def test_writer_late_rule(self):
        x=copy.deepcopy(self.w);x['beats'][0]['id']=3;self.assertTrue(writer(x))
    def test_writer_count_is_not_count(self):
        x=copy.deepcopy(self.w);x['beats'][-1]['text']='计票尚未开始';self.assertIn('formal_count_not_performed',writer(x))
    def test_writer_missing_rule_words(self):
        x=copy.deepcopy(self.w);x['beats'][0]['text']='请按按钮';self.assertIn('rule_not_explicit',writer(x))
    def test_director_positive(self):self.assertEqual(director(self.d),[])
    def test_director_initial_state(self):
        x=copy.deepcopy(self.d);x['shots'][0]['key_before']='under_table_front_left_leg';self.assertIn('initial_key_state_mismatch',director(x))
    def test_director_teleport(self):
        x=copy.deepcopy(self.d);x['shots'][2]['key_before']='door';self.assertTrue(any('key_teleport' in e for e in director(x)))
    def test_director_take_reuse(self):
        x=copy.deepcopy(self.d);x['shots'][2]['takes']=['T02a'];self.assertIn('take_reused',director(x))
    def test_director_take_missing(self):
        x=copy.deepcopy(self.d);x['shots'][1]['takes']+=['T99'];self.assertIn('take_coverage_mismatch',director(x))
    def test_director_promotion(self):
        x=copy.deepcopy(self.d);x['proposals'][0]['used_in_authoritative_shots']=True;self.assertIn('proposal_promoted',director(x))
    def test_director_winner(self):
        x=copy.deepcopy(self.d);x['shots'][-1]['key_after']='held_by_A';self.assertIn('winner_not_authorized',director(x))
if __name__=='__main__':unittest.main(verbosity=2)
