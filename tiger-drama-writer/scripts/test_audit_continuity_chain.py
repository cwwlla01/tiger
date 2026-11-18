import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from audit_continuity_chain import check_chain

class ChainTest(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.root=Path(t.name)
        self.scripts=[]
        texts=['△阿遥把钥匙放在桌上。','△阿遥把桌上的钥匙交给阿帆。','△阿帆把钥匙锁进自己的柜子。']
        for i,body in enumerate(texts):
            p=self.root/f'EP{i+1}.md';p.write_text('### SC01\n'+body,encoding='utf-8');self.scripts.append(p)
        states=['桌上','阿帆手里','阿帆柜内']
        self.entries=[]
        for i in range(2):
            before=self.scripts[i];after=self.scripts[i+1]
            data={'previous_sha256':hashlib.sha256(before.read_bytes()).hexdigest(), 'current_sha256':hashlib.sha256(after.read_bytes()).hexdigest(),
                  'previous_state':{'钥匙.位置':states[i]}, 'current_state':{'钥匙.位置':states[i+1]},
                  'previous_anchors':{'钥匙.位置':texts[i][1:]},
                  'changes':[{'key':'钥匙.位置','from':states[i],'to':states[i+1], 'current_quote':texts[i+1][1:],'interpretation':'本集明确把钥匙移到了新的位置并展示动作'}]}
            ledger=self.root/f'l{i+1}.json';ledger.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
            self.entries.append({'previous_script':str(before),'current_script':str(after),'ledger':str(ledger)})
    def test_valid_chain(self):self.assertTrue(check_chain(self.entries)['mechanically_valid'])
    def test_changed_handoff_without_script_modification(self):
        p=Path(self.entries[1]['ledger']);d=json.loads(p.read_text());d['previous_state']['钥匙.位置']='陌生人手里';d['changes'][0]['from']='陌生人手里';p.write_text(json.dumps(d,ensure_ascii=False))
        self.assertIn('STATE_HANDOFF_MISMATCH_1',check_chain(self.entries)['errors'])
    def test_different_middle_script_content(self):
        other=self.root/'fake_middle.md';other.write_text('### SC01\n△阿遥把桌上的钥匙交给阿帆。\n\n',encoding='utf-8')
        self.entries[1]['previous_script']=str(other)
        self.assertIn('SCRIPT_HANDOFF_MISMATCH_1',check_chain(self.entries)['errors'])
    def test_missing_transition(self):
        self.assertIn('AT_LEAST_TWO_TRANSITIONS_REQUIRED',check_chain(self.entries[:1])['errors'])
    def test_invalid_second_transition_stops(self):
        p=Path(self.entries[1]['ledger']);d=json.loads(p.read_text());d['changes']=[];p.write_text(json.dumps(d,ensure_ascii=False))
        self.assertIn('TRANSITION_INVALID_1',check_chain(self.entries)['errors'])

    def test_reused_ledger_is_blocked(self):
        entries=self.entries + [dict(self.entries[0])]
        outcome=check_chain(entries)
        self.assertIn('DUPLICATE_LEDGER_2',outcome['errors'])
        self.assertIn('DUPLICATE_TRANSITION_2',outcome['errors'])
    def test_identical_episode_bytes_blocked(self):
        p=self.scripts[1]
        p.write_bytes(self.scripts[0].read_bytes())
        self.assertIn('IDENTICAL_EPISODE_BYTES_0',check_chain(self.entries)['errors'])
    def test_copied_ledger_at_new_path_is_rejected(self):
        duplicate=self.root/'copy_l1.json'
        duplicate.write_bytes(Path(self.entries[0]['ledger']).read_bytes())
        entries=self.entries+[dict(self.entries[0],ledger=str(duplicate))]
        self.assertIn('DUPLICATE_LEDGER_CONTENT_2',check_chain(entries)['errors'])

    def test_reused_episode_under_new_path_is_rejected(self):
        # Build a third independently valid transition back to EP01 content.
        fourth=self.root/'EP04_copy.md'
        fourth.write_bytes(self.scripts[0].read_bytes())
        before=self.scripts[2]
        body='△阿遥把钥匙放在桌上。'
        ledger=self.root/'l3.json'
        ledger.write_text(json.dumps({
            'previous_sha256':hashlib.sha256(before.read_bytes()).hexdigest(),
            'current_sha256':hashlib.sha256(fourth.read_bytes()).hexdigest(),
            'previous_state':{'钥匙.位置':'阿帆柜内'},
            'current_state':{'钥匙.位置':'桌上'},
            'previous_anchors':{'钥匙.位置':'阿帆把钥匙锁进自己的柜子。'},
            'changes':[{'key':'钥匙.位置','from':'阿帆柜内','to':'桌上',
                        'current_quote':body[1:],'interpretation':'当前集重新把钥匙移动回桌面并展示完整操作'}]
        },ensure_ascii=False),encoding='utf-8')
        entries=self.entries+[{'previous_script':str(before),'current_script':str(fourth),'ledger':str(ledger)}]
        self.assertIn('REPEATED_EPISODE_CONTENT_2',check_chain(entries)['errors'])

    def test_missing_handoff_file_reports_failure(self):
        # Malformed/missing files should return audit errors, not crash.
        self.scripts[1].unlink()
        report=check_chain(self.entries)
        self.assertFalse(report['mechanically_valid'])
        self.assertTrue(report['errors'])

if __name__=='__main__':unittest.main()
