# Project-level version management (mandatory for serial works)

When an existing story has multiple drafts, **never assume latest file is authoritative**. Maintain a durable project folder with:

- `project.json`: project ID, current edition, approved episode revision IDs, and last change timestamp (not a claim of publication).
- `canon.json`: entries with stable IDs, values, source (`USER_LOCKED`, `APPROVED_DRAFT`, `DERIVED`, `PROPOSED`), evidence references, and status. User-locked entries cannot be silently replaced. Proposals cannot become approved on their own.
- `episodes.json`: each episode ID, revision ID, status (`OUTLINE`, `SCENE_DRAFT`, `FULL_SCRIPT`, `TIMED`), file path, parent revision, and dependencies. An alternate test is `CANDIDATE`, not the approved version.
- `progression.json`: append-only transactions with scene ID, source item/event, earned amount, allocations, and arithmetic status. Maintain original stat versus effective stat, and known status effects separately.
- `open_threads.json`: planted clue, known-to-characters, due range, payoff proof, resolved/unresolved status.
- `changes.json`: append-only change log: what changed, why, impacted episodes and downstream status.

Workflow:
1. **Discover sources** and inventory old drafts with paths and provenance. Preserve all drafts; never silently merge incompatible manuscripts.
2. **Establish authority**: explicit user statements override model proposals; for scripts with no approval record, mark them CANDIDATE. If two sources disagree, record `CONFLICT` and withhold a canonical assertion. Do not invent a single authoritative EP01–20 from disconnected tests.
3. **Build a baseline** with `scripts/check_project.py` validation. Never silently promote suggestions to USER_LOCKED.
4. **Perform edits on a copy**: generate a new revision, list the episode IDs touched, and trace all downstream dependent events, attributes, knowledge and foreshadowing. Keep old revision accessible.
5. **Check and commit**: run validator, and only mark approved if a user explicitly approves or the project has an explicit approval policy. An internally authored rewrite is always candidate absent such authority.
6. **Export resume packet**: project ID, authoritative baseline, unresolved conflicts, next unwritten episode, stat balance caveats, required references and current candidate revisions. Cross-chat continuation needs the files, not implied model memory.

Completeness rules: if earlier point sources are unverified, note `unreconciled`, never claim the entire balance is 0. A balanced transaction proves only itself. Story planning is not a completed screenplay. Keep script production separate from shots/video.
