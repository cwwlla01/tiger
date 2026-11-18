#!/usr/bin/env python3
"""Regression fixtures for structural and adversarial screening."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent))
from audit_script_batch import audit
from audit_adversarial import inspect

def run():
    root=Path(__file__).resolve().parents[1]/'tests'
    padded=root/'padded_fake.md'; thin=root/'thin_fake.md'
    assert audit(padded)['episodes'][0]['status']=='STRUCTURALLY_REVIEWABLE', 'Historical false positive fixture changed; review test'
    assert 'REPETITIVE_DIALOGUE_REVIEW' in inspect(padded)['episodes'][0]['adversarial_flags']
    assert 'THIN_SCENE_MAJORITY' in inspect(thin)['episodes'][0]['adversarial_flags']
    assert audit(thin)['episodes'][0]['status']=='REVIEW_REQUIRED'
    assert 'TEMPLATED_DIALOGUE_REVIEW' in inspect(root/'synonym_padding_fake.md')['episodes'][0]['adversarial_flags']
    assert 'STATIC_DEBATE_NO_STATE_CHANGE_REVIEW' in inspect(root/'static_debate_fake.md')['episodes'][0]['adversarial_flags']
    assert 'UNWRITTEN_PLACEHOLDER_BLOCKER' in inspect(root/'placeholder_fake.md')['episodes'][0]['adversarial_flags']
    assert 'UNWRITTEN_PLACEHOLDER_BLOCKER' not in inspect(root/'healthy_action_sample.md')['episodes'][0]['adversarial_flags']
    print('PASS: 8 deterministic fixture assertions')
if __name__=='__main__':run()

# Separate release-gate regression: exercise whole-batch status, not just individual flags.
