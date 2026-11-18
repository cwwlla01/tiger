# V3.34 Five-episode fresh-first-draft verification

This regression preserves `/mnt/data/v78/trials/saltline_five_raw.md` as a separate test artifact; a package should not ship the entire trials directory. It was written sequentially as five playable episodes, then screened without rewriting the five episodes. The screenplay includes three scenes per episode, with two-sided agency, tactical costs and status handoffs. Not a controlled A/B against previous versions.

**Generator practice:** Privately write one finished scene with playable resistance and a costly adapted choice, then continue; if continuity is fragile, append the *observed* inventory/injury/knowledge state before the next scene. Never treat prompt checklists as scene content or repeat dialogue merely to reach a floor. When the batch is long, use a persistent file, not simultaneous short episode sketches.

**Audit integrity:** Accepted headings include `## EP01《标题》`, `## EP01｜标题`, `## EP01：标题`; scenes include `### SC1`, `### 场1｜地点`, `### 场景1｜地点`. Run `test_heading_notation.py` alongside existing regressions; an unparsed heading is a tooling issue, not evidence of absent episodes. Report immutable first-pass numerator separate from revised outputs. Static passing is only a reviewable draft, not measured performance or artistic acceptance.

**Manual outstanding risks:** A short drama must still verify genre-specific reward cadence, emotionally compelling protagonist choices, character voice distinctions, credible technology and injury/medical causality, and read-through timing. The V3.34 fresh five-episode static result is not proof of reliability across different genres or 60 episodes.
