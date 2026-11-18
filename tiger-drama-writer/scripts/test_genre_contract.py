#!/usr/bin/env python3
import json
import tempfile
from pathlib import Path
from check_genre_contract import check

with tempfile.TemporaryDirectory() as d:
    d=Path(d)
    script=d/'script.md'; manifest=d/'manifest.json'
    words={
        'ability_setup':'她曾靠共振听见松动的钢丝。',
        'ability_use':'许峥屏息听出闸门间隙，抢在落闸前抽走手臂。',
        'obstacle_changed':'闸板卡住，下面的病人终于能撤出。',
        'cost_or_limit':'她的左手再次流血，耳鸣持续了整整半分钟。',
        'end_state':'闸板停住，但唯一的扳手已经弯曲报废。'
    }
    script.write_text('## EP01 测试\n'+'\n'.join(words.values()),encoding='utf-8')
    good={'genre':'power_progression','episodes':[{'episode':1,**words,'power_gain':{'new_points':0}}]}
    manifest.write_text(json.dumps(good,ensure_ascii=False),encoding='utf-8')
    assert check(script,manifest)['evidence_ready']
    bad=dict(good); bad['episodes']=[dict(good['episodes'][0],ability_use='这是脚本中根本没有出现的万能技能描述。')]
    manifest.write_text(json.dumps(bad,ensure_ascii=False),encoding='utf-8')
    assert not check(script,manifest)['evidence_ready']
    bad2=dict(good); bad2['episodes']=[dict(good['episodes'][0],power_gain={'new_points':10})]
    manifest.write_text(json.dumps(bad2,ensure_ascii=False),encoding='utf-8')
    assert 'UNVERIFIED_POWER_GAIN' in check(script,manifest)['episodes'][0]['issues']
    bad3=dict(good); bad3['episodes']=[dict(good['episodes'][0],cost_or_limit='')]
    manifest.write_text(json.dumps(bad3,ensure_ascii=False),encoding='utf-8')
    assert 'COST_OR_LIMIT_MISSING' in check(script,manifest)['episodes'][0]['issues']
print('genre-contract regression: 4/4 passed')

# A later episode may owe an explicit payoff without fabricating ability use.
with tempfile.TemporaryDirectory() as td:
    td=Path(td); script=td/'ep.md'; manifest=td/'m.json'
    script.write_text('## EP02 测试\n工具折断，主角被迫撤离。\n他们只拿到未确认的证据。',encoding='utf-8')
    deferred={'episode':2,'payoff_deferred':True,'payoff_debt_due':3,'defer_reason':'下一集将验证能力能否解开新的障碍','cost_or_limit':'工具折断，主角被迫撤离。','end_state':'他们只拿到未确认的证据。','power_gain':{'new_points':0}}
    manifest.write_text(json.dumps({'genre':'power_progression','episodes':[deferred]},ensure_ascii=False))
    assert not check(script,manifest)['evidence_ready'] # no real payoff in the window
print('genre-contract serial deferral regression: 1/1 passed')

# Cross-episode borrowing must be rejected even when every quoted string is in the combined file.
with tempfile.TemporaryDirectory() as td:
    td=Path(td); script=td/'batch.md'; manifest=td/'manifest.json'
    content='## EP01 测试\n'+'\n'.join(words.values())+'\n## EP02 测试\n主角只是查阅了旧账，没有使用特殊能力。'
    script.write_text(content, encoding='utf-8')
    forged={'genre':'power_progression','episodes':[{'episode':2,**words,'power_gain':{'new_points':0}}]}
    manifest.write_text(json.dumps(forged,ensure_ascii=False),encoding='utf-8')
    result=check(script,manifest)
    assert not result['evidence_ready']
    assert 'ABILITY_USE_NOT_IN_CLAIMED_EPISODE' in result['episodes'][0]['issues']
    valid={'genre':'power_progression','episodes':[{'episode':1,**words,'power_gain':{'new_points':0}}]}
    manifest.write_text(json.dumps(valid,ensure_ascii=False),encoding='utf-8')
    assert check(script,manifest)['evidence_ready']
print('cross-episode evidence scope: 2/2 passed')
