# Recent Retro Lessons

## Current Focus

- Goal run implementing the A4-lite contract that turns retro waste findings into **structural, destination-routed** issue proposals instead of incident-coupled ones (shared reference + retro/achieve/issue wiring + issue-adapter `harness_upstream` + presence-only `validate_proposal_fields.py` + tests). (source: `charness-artifacts/retro/2026-06-03-retro-issue-destination-split.md`)
- Reviewing the just-completed `/charness:quality` slice that closed the #283 mutation regression in the Codex session/token reporter (new unit tests + `main` routing/non-ASCII tests, verified by targeted local cosmic-ray, committed as `9fb08f6f`). (source: `charness-artifacts/retro/2026-06-03-quality-283-waste-retro.md`)

## Repeat Traps

- `check_auto_trigger.py` is state-sensitive: once a helper commits and pushes the release, the current diff is empty and the trigger cannot reconstruct the just-finished slice. (source: `charness-artifacts/retro/2026-06-03-auto-retro-trigger-miss.md`)
- Handoff edit cascade: editing `docs/handoff.md` broke `check-doc-links` (backticked file paths instead of markdown links) and `test_handoff_chunker_parse.py` (it pins the live Next-Session issue refs at `[184, 261]`, now stale because #261 is closed). That forced one extra full `run-quality` (~51s) plus investigation. Root cause: edited a coupled surface without checking its two known couplings first. (source: `charness-artifacts/retro/2026-06-03-quality-283-waste-retro.md`)
- I accidentally ran `upsert_goal.py` without `--date` when activating the existing 2026-06-02 goal. That created a duplicate 2026-06-03 goal artifact, which I had to delete before continuing. (source: `charness-artifacts/retro/2026-06-03-184-usage-episode-product-success-consume-policy.md`)
- I initially treated `first_value_ref` too much like user-value evidence. The user correctly pushed back that Charness almost always leaves artifacts, so artifact existence cannot stand in for satisfaction. The resulting design is better: first-value is only an evidence floor; satisfaction and friction are separate signals. (source: `charness-artifacts/retro/2026-06-03-184-usage-episode-product-success-consume-policy.md`)

## Next-Time Checklist

- a `--report-all` (collect-all) mode for `validate_quality_artifact.py` and peers would surface every violation in one pass; 21 `validate_*.py` raise on the first error today vs 10 that already collect failures. Optional candidate, not committed here. (source: `charness-artifacts/retro/2026-06-03-quality-283-waste-retro.md`)
- Add an explicit release-helper handoff field such as `retro_trigger_evaluation` that records `triggered`, `paths`, and whether a bounded session retro was written or intentionally skipped. (source: `charness-artifacts/retro/2026-06-03-auto-retro-trigger-miss.md`)
- applied: Declare the new skipped attention state for release-retro closeout so skipped trigger status cannot masquerade as a clean closeout proof. (source: `charness-artifacts/retro/2026-06-03-281-automatic-waste-retro-closeout.md`)
- applied: Freeze the release-retro trigger behavior with tests that cover commit-range detection, pre-release delta hits, helper-generated packaging path hits, and persisted retro closeout artifacts. (source: `charness-artifacts/retro/2026-06-03-281-automatic-waste-retro-closeout.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-06-03-184-usage-episode-product-success-consume-policy.md`
- `charness-artifacts/retro/2026-06-03-281-automatic-waste-retro-closeout.md`
- `charness-artifacts/retro/2026-06-03-auto-retro-trigger-miss.md`
- `charness-artifacts/retro/2026-06-03-quality-283-waste-retro.md`
- `charness-artifacts/retro/2026-06-03-retro-issue-destination-split.md`
