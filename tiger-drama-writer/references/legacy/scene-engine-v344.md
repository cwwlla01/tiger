# V3.44 scene execution engine (pre-draft, not another post-hoc score)

Every new episode is drafted scene by scene. Before prose, privately specify for each scene these seven fields, with **different concrete values** in successive scenes:

1. **Pressure object and deadline:** an object, person or decision that may be lost now; do not merely announce a problem.
2. **Protagonist tactic 1:** an observable physical or interpersonal action (ask to inspect a copy, choose to surrender a token, stop a hand).
3. **Opponent's independent countermove:** a motivated move with a benefit to the opponent; no straw-person agreement.
4. **Tactic 2 with price:** a materially different action and the immediate sacrificed resource, trust, leverage, time, or safety.
5. **Relational collision:** at least one principal acts contrary to how another expected them to act; convey this in a choice, not the sentence 'she was moved'.
6. **State delta:** write a before -> after fact that later scenes must respect (who has the key, who knows the truth, who can enter, who is injured).
7. **Next-scene trigger:** a consequence of this scene rather than an unrelated knock at the door.

A private plan containing these fields does **not** pass. In the actual screenplay each named action, countermove, price and state change must be visible or spoken through a decision; action prose should be playable, not literary explanation. Draft one scene completely, then run `scene_checkpoint.py` if available; if it warns, rewrite the deficient scene before continuing, but **archive the untouched initial attempt** and do not call an internally revised scene a clean first-pass success. Review dramatic truth separately because static metrics cannot detect a false emotional turn.

## Before/after example (same beat)

**Reject as synopsis in dialogue:**

场：窗口。林舟要求查账，工作人员拒绝，姐姐劝她别闹。林舟坚持，终于拿到线索。

**Scene-level execution, shortened demonstration:**

窗口。林舟把父亲的最后一张缴款单压在玻璃下。窗口后的人用红章盖住收据的“退回”栏。

林舟：您可以不让我看原件，但请在这份复印件上写清楚是谁拒绝的。

窗口员：我写了，今天这个号就作废。你父亲的补贴得重新排。

姐姐伸手去抽单子。林舟按住，先把自己的手机和号码牌交给姐姐。

林舟：钱会晚来。我签字承担。姐，你别替我说原谅。

窗口员收起红章，递出拒绝登记簿。林舟没拿到原账，却亲手留下了可追踪的拒绝记录；姐姐转身离开，没再替她解释。

The demonstration is **not** a full scene length target. Its purpose is causal moves and changed relationship. Keep total episode duration claims explicitly unmeasured until read-through timing.

## Multi-episode anti-compression

Give the fifth episode the same full scene process as episode one. Do not reduce later scenes to summaries in order to finish the requested count. When output budget is low, write fewer **complete** episodes in files and clearly mark unfinished episodes; never hide truncation. Each batch logs: raw first-pass static result, editorial scene review, revised result, blind-voice test status, timed-runtime status, separate from each other.
