# Episode-by-episode first-pass checkpoint

1. Freeze the one-episode `raw/EPnn.md` and its hash. Avoid multi-episode combined files as the checkpoint input.
2. Run `python scripts/episode_stop_gate.py raw/EPnn.md --episode N --output checks/EPnn.json`; status 2 blocks further writing, status 0 means **static review ready only**.
3. If blocked, inspect specific episode/scene flags. Repair actual conflict, playable action or dialogue in separate `revised/EPnn.md`; preserve original for first-pass statistics. Do not game numerical warnings by filler.
4. If a revised episode passes, record state deltas, pending costs, and evidence boundary before continuing. Report raw and revised counts separately.
5. At end run `release_gate.py` and serial decay on all five; also independent voice, emotional-payoff, character continuity, and timed read-through reviews. No unperformed gate may be called passed.
