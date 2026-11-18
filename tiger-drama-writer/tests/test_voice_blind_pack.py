import sys, unittest, tempfile, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from voice_blind_pack import make_pack

class TestBlind(unittest.TestCase):
    def make(self, directory):
        p = Path(directory) / 't.md'
        a = [f'这个结果完全超出我的预计，现在必须重新核对第{i}份资料。' for i in range(12)]
        b = [f'我已经承担第{i}次风险，你不能再让我替你签下保证。' for i in range(12)]
        p.write_text('## EP01｜测试\n' + ''.join(f'甲：{a[i]}\n乙：{b[i]}\n' for i in range(12)), encoding='utf-8')
        return p
    def test_anonymized_ids_do_not_encode_role_cycle(self):
        with tempfile.TemporaryDirectory() as d:
            p = self.make(d)
            r = make_pack(p, samples=8)
            self.assertEqual(len(r['cards']), 16)
            self.assertEqual(len(r['answer_key']), 16)
            self.assertEqual(r['cards'], make_pack(p, samples=8)['cards'])
            # No alternating A/B by ID (the prior implementation leaked roles).
            roles = [r['answer_key'][c['id']]['role'] for c in r['cards']]
            self.assertTrue(any(roles[i] == roles[i+1] for i in range(len(roles)-1)))
            self.assertTrue(all(set(card) == {'id', 'line'} for card in r['cards']))
            self.assertTrue(all('source_episode' in k for k in r['answer_key'].values()))
    def test_exclude_name_leak_and_ambiguous_repetitions(self):
        with tempfile.TemporaryDirectory() as d:
            p = self.make(d)
            with p.open('a', encoding='utf-8') as f:
                f.write('甲：乙已经说过这张票据不能撤回。\n乙：这句话完全一样不应成为盲测。\n甲：这句话完全一样不应成为盲测。\n')
            r = make_pack(p, samples=12)
            self.assertGreaterEqual(r['excluded']['explicit_name'], 1)
            self.assertGreaterEqual(r['excluded']['repeated_line'], 2)
            self.assertFalse(any('甲' in x['line'] or '乙' in x['line'] for x in r['cards']))
    def test_empty(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 't.md'
            p.write_text('## EP01｜测试\n甲：好。\n', encoding='utf-8')
            self.assertEqual(make_pack(p)['cards'], [])

if __name__ == '__main__': unittest.main()
