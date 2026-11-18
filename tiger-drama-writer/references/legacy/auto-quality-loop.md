# Automated quality loop (V1.3)

Use after each outlined arc and each completed screenplay batch. Distinguish objective failure gates from subjective editorial ratings. A high self-assigned score is not proof of quality.

## Gate order

**Gate 0: Delivery completeness.** Count expected and actually scripted episodes. A list of episode summaries never passes as a screenplay. Report missing scenes/episodes accurately. For each episode, require a scene heading, character action, and speakable dialogue unless the user asked for silent storytelling.

**Gate 1: Continuity and causality (blocking).** Fail if a key actor knows an unlearned secret; a reveal is unsupported by existing setup; one prop is in two places at once; a conflict resolves by impossible authority, unexplained coincidence or unsupported technology; or the climax requires a decision absent from the script. List exact scene and reason. Revise those scenes plus affected later beats before grading polish.

**Gate 2: Dramatic change (blocking).** Every episode needs at least one consequential active choice and a measurable before/after state (power, relationship, risk, information, commitment). The same status quo at end as start is a fail even if people argue loudly. For a run of three, reject all three sharing the same central device (e.g. another document proves guilt, another meeting rebuffs the villain). Differentiate emotional outcome and tactic, not merely prop labels.

**Gate 3: Viewer experience (editorial).** Score 0-5 each: opening hook, active agency, payoff originality and earnedness, emotional clarity, escalating stakes, dialogue/subtext, cliffhanger, visual storytelling, and screenplay practicality. Write one sentence of *evidence* for each low score (0-2) and for all major 4-5 scores. Scores are internal heuristic, not external metrics. Target each dimension >=3 and median >=4 for deliverable; do not claim this proves audience retention.

**Gate 4: Screenplay completeness.** Reject placeholder scenes, missing dialogue, unplayable abstract action, or unresolved causality. Verify consistent scene identifiers and state updates.

## Repair policy

1. Enumerate defects with identifiers: `C` continuity, `D` drama, `E` editorial, `V` video, `O` output-completeness. Include exact episode/scene, observed evidence, harm, and severity (`blocker`, `major`, `minor`).
2. Fix blockers first, then majors; prioritize minimum scene-level change over whole-story regeneration. For each fix, state the intended new decision / consequence. Preserve locked canon and update downstream scene conditions.
3. Re-score only after an actual revised passage exists. Use a maximum of two automatic rewrite passes per batch; if remaining blockers are not resolved, mark as unresolved and never call the batch production-ready.
4. Log before/after evidence using the same rubric. Keep original defect trace and explain tradeoffs (e.g. faster pace but weaker relationship development).
5. Deliver finished screenplay as primary output. Attach concise audit log; keep auto-analysis short unless asked.

## Beat ledger schema

One row per episode with fields `episode`, `hook`, `pressure`, `protagonist_choice`, `earned_payoff`, `payoff_type`, `cost`, `state_before`, `state_after`, `end_hook`, `visual_anchor`, `location_count`, `cast_count`, `unresolved_clues`. Values must be materially distinct; phrases like 'conflict intensifies' do not qualify as concrete changed state. `payoff_type` examples: strategic, relational, emotional, revelation, physical, moral, status, sacrifice.

## Measuring watchability honestly

Separate three labels: **text-level editorial check** (possible in ChatGPT), **generated-video feasibility** (requires rendering the shots), **viewer retention** (requires actual audience data). Never merge these labels or report an untested target as an observed result.
