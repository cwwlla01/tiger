from pathlib import Path
from release_gate import evaluate
root=Path(__file__).resolve().parents[1]/'tests'
bad=evaluate([root/'healthy_action_sample.md',root/'placeholder_fake.md'])
assert not bad['batch_screening_ready'],bad
assert any('UNWRITTEN_BLOCKER' in i for i in bad['files'][1]['issues'])
normal=evaluate([root/'healthy_action_sample.md'])
assert not any('UNWRITTEN_BLOCKER' in i for i in normal['files'][0]['issues'])
assert len(bad['files'])==2
print('PASS: 4 release-gate assertions')

# Regression from V3.40 real five-episode screenplays: raw EP04 scene 3 must block.
fixture=root/'fixtures/lockbox_five_raw.md'
fixed=root/'fixtures/lockbox_five_revised.md'
if True:
    raw=evaluate([fixture]); revised=evaluate([fixed])
    assert not raw['batch_screening_ready'], raw
    assert any('SCENE' in issue and 'EP04' in issue for issue in raw['files'][0]['issues']),raw
    assert not any('SCENE' in issue for issue in revised['files'][0]['issues']),revised
    print('PASS: 3 real-script scene-gate assertions')

# A batch with a sharp series-length drop must not receive a clean screening label.
legacy=root/'fixtures/five_first_draft.md'
if True:
    result=evaluate([legacy])
    assert 'SERIAL_EP04_SHRINKS_OVER_20_PERCENT' in result['files'][0]['issues'], result
    assert not result['batch_screening_ready']
    print('PASS: real five-episode serial-decay integration')
