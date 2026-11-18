from pathlib import Path
from tempfile import TemporaryDirectory
from scene_checkpoint import checkpoint

def test():
    p=Path(__file__).resolve().parents[1]
    raw=p/'tests/fixtures/bridge_letters_raw.md'
    if True:
        report=checkpoint(raw)
        assert len(report['scenes'])==9
        assert not report['all_static_ready']
        assert any(s['warnings'] for s in report['scenes'])
        assert checkpoint(raw,episode=1,scene=1)['scenes'][0]['scene_index']==1
    with TemporaryDirectory() as d:
        path=Path(d)/'x.md'
        path.write_text('## EP01｜测例\n### 1-1 内 日 屋内\n【门打开。】\n甲：走。\n乙：不行。\n',encoding='utf8')
        r=checkpoint(path)
        assert r['scenes'][0]['checkpoint']=='NEEDS_REALIZATION'
        try:checkpoint(path,episode=9)
        except ValueError:pass
        else:raise AssertionError('missing episode should fail')
    print('4 scene checkpoint assertions PASSED')
if __name__=='__main__':test()
