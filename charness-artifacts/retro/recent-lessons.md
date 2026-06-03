# Recent Retro Lessons

## Current Focus

- The user pointed out that waste retros still appear not to happen automatically. (source: `charness-artifacts/retro/2026-06-03-auto-retro-trigger-miss.md`)
- This retro covers the #184 usage-episode consume-policy goal. (source: `charness-artifacts/retro/2026-06-03-184-usage-episode-product-success-consume-policy.md`)

## Repeat Traps

- `check_auto_trigger.py` is state-sensitive: once a helper commits and pushes the release, the current diff is empty and the trigger cannot reconstruct the just-finished slice. (source: `charness-artifacts/retro/2026-06-03-auto-retro-trigger-miss.md`)
- I accidentally ran `upsert_goal.py` without `--date` when activating the existing 2026-06-02 goal. That created a duplicate 2026-06-03 goal artifact, which I had to delete before continuing. (source: `charness-artifacts/retro/2026-06-03-184-usage-episode-product-success-consume-policy.md`)
- I initially treated `first_value_ref` too much like user-value evidence. The user correctly pushed back that Charness almost always leaves artifacts, so artifact existence cannot stand in for satisfaction. The resulting design is better: first-value is only an evidence floor; satisfaction and friction are separate signals. (source: `charness-artifacts/retro/2026-06-03-184-usage-episode-product-success-consume-policy.md`)
- `publish_release_cli.py` briefly exceeded the file/function length limits after the new logic was added. Extracting `publish_release_plan.py` and `publish_release_retro.py` fixed the immediate gate and left a better module boundary. (source: `charness-artifacts/retro/2026-06-03-281-automatic-waste-retro-closeout.md`)

## Next-Time Checklist

- Add an explicit release-helper handoff field such as `retro_trigger_evaluation` that records `triggered`, `paths`, and whether a bounded session retro was written or intentionally skipped. (source: `charness-artifacts/retro/2026-06-03-auto-retro-trigger-miss.md`)
- applied: Declare the new skipped attention state for release-retro closeout so skipped trigger status cannot masquerade as a clean closeout proof. (source: `charness-artifacts/retro/2026-06-03-281-automatic-waste-retro-closeout.md`)
- applied: Freeze the release-retro trigger behavior with tests that cover commit-range detection, pre-release delta hits, helper-generated packaging path hits, and persisted retro closeout artifacts. (source: `charness-artifacts/retro/2026-06-03-281-automatic-waste-retro-closeout.md`)
- applied: Keep new release-helper behavior in helper modules instead of growing `publish_release_cli.py`; this run added `publish_release_plan.py` and `publish_release_retro.py`. (source: `charness-artifacts/retro/2026-06-03-281-automatic-waste-retro-closeout.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-06-03-184-usage-episode-product-success-consume-policy.md`
- `charness-artifacts/retro/2026-06-03-281-automatic-waste-retro-closeout.md`
- `charness-artifacts/retro/2026-06-03-auto-retro-trigger-miss.md`
