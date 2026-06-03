# Recent Retro Lessons

## Current Focus

- The user pointed out that waste retros still appear not to happen automatically. (source: `charness-artifacts/retro/2026-06-03-auto-retro-trigger-miss.md`)
- This retro covers the #184 usage-episode consume-policy goal. (source: `charness-artifacts/retro/2026-06-03-184-usage-episode-product-success-consume-policy.md`)

## Repeat Traps

- `check_auto_trigger.py` is state-sensitive: once a helper commits and pushes the release, the current diff is empty and the trigger cannot reconstruct the just-finished slice. (source: `charness-artifacts/retro/2026-06-03-auto-retro-trigger-miss.md`)
- I accidentally ran `upsert_goal.py` without `--date` when activating the existing 2026-06-02 goal. That created a duplicate 2026-06-03 goal artifact, which I had to delete before continuing. (source: `charness-artifacts/retro/2026-06-03-184-usage-episode-product-success-consume-policy.md`)
- I initially treated `first_value_ref` too much like user-value evidence. The user correctly pushed back that Charness almost always leaves artifacts, so artifact existence cannot stand in for satisfaction. The resulting design is better: first-value is only an evidence floor; satisfaction and friction are separate signals. (source: `charness-artifacts/retro/2026-06-03-184-usage-episode-product-success-consume-policy.md`)
- Release publishing performs critique, quality, public verification, and issue closeout, but it does not run a post-publish waste retro or preserve the changed-path set for `retro` to evaluate afterward. (source: `charness-artifacts/retro/2026-06-03-auto-retro-trigger-miss.md`)

## Next-Time Checklist

- Add an explicit release-helper handoff field such as `retro_trigger_evaluation` that records `triggered`, `paths`, and whether a bounded session retro was written or intentionally skipped. (source: `charness-artifacts/retro/2026-06-03-auto-retro-trigger-miss.md`)
- Filed issue #281 so this does not remain a prose-only retro lesson. (source: `charness-artifacts/retro/2026-06-03-auto-retro-trigger-miss.md`)
- for reporter scripts that can mutate external state, write edge fixtures before broad happy-path tests: empty window/no data, missing binary, partial/multi-action failure, and privacy redaction. Disposition: applied in `tests/test_usage_episodes_report.py` for this reporter. (source: `charness-artifacts/retro/2026-06-03-280-corca-internal-usage-last-seen-product-review.md`)
- In release/goal closeout, run `check_auto_trigger.py --paths <release-delta-paths>` before the tree is cleaned, or persist the changed-path list from the helper so post-publish retro can evaluate the same slice. (source: `charness-artifacts/retro/2026-06-03-auto-retro-trigger-miss.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-06-03-184-usage-episode-product-success-consume-policy.md`
- `charness-artifacts/retro/2026-06-03-280-corca-internal-usage-last-seen-product-review.md`
- `charness-artifacts/retro/2026-06-03-auto-retro-trigger-miss.md`
