# First-pass causal completeness contract (V3.8)

Before writing each autonomous five-episode batch, create a small private or project-file JSON manifest with exactly five sequential episodes. Include nonempty `objective`, `obstacle`, `choice`, `price`, `state_change`, `payoff`, `end_turn`, and at least three distinct scenes each with `location`, `action`, `reversal`. The sample schema follows:

```json
{"episodes":[{"episode":36,"objective":"...","obstacle":"...","choice":"...","price":"...","state_change":"...","payoff":"...","end_turn":"...","scenes":[{"location":"...","action":"...","reversal":"..."}]}]}
```

Run `python scripts/check_preflight.py contract.json` when code execution exists; the check tests **presence**, not depth. Do not ask the user to fill the template. If it fails, repair the **plan before drafting**, not by adding filler dialogue. After passing preflight, write all episode scripts in a single uninterrupted first-pass file, archive that file, and run `scripts/audit_script_batch.py`. Report separately: preflight pass, first-pass structural rate, repaired structural rate, causal blockers, runtime verification, and subjective drama shortcomings.

### Drafting depth calibration

For each proposed scene, write an actual turn that changes another character's next action; do not narrate the turn in summary. Avoid dialogue-only exchanges where the premise is restated. Let a protagonist earn gains via a known rule and specific source. A failed scene with no state delta must be replaced, not lengthened. For a 2–3 minute target, budget playable beats and spoken dialogue, but never guarantee actual duration without measured read-through. If an episode is unusually long or short, revise based on **performance**, not a simple character quota. Do not include this preflight contract as screenplay content.

### Important limitations

A manifest that passes does not prevent weak drama. A static checker that passes does not demonstrate human viewer engagement, actual timing, distinctive dialogue, accurate blocking or all continuity. Keep the three verdicts separate: planning coverage, text structural reviewability, and actual readiness.
