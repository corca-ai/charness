# Recent Retro Lessons

## Current Focus

- This retro covers the #184 usage-episode consume-policy goal. (source: `charness-artifacts/retro/2026-06-03-184-usage-episode-product-success-consume-policy.md`)
- This retro covers the #280 goal slice that added a Corca-internal last-seen product-review reporter for usage episodes. (source: `charness-artifacts/retro/2026-06-03-280-corca-internal-usage-last-seen-product-review.md`)

## Repeat Traps

- I accidentally ran `upsert_goal.py` without `--date` when activating the existing 2026-06-02 goal. That created a duplicate 2026-06-03 goal artifact, which I had to delete before continuing. (source: `charness-artifacts/retro/2026-06-03-184-usage-episode-product-success-consume-policy.md`)
- I initially treated `first_value_ref` too much like user-value evidence. The user correctly pushed back that Charness almost always leaves artifacts, so artifact existence cannot stand in for satisfaction. The resulting design is better: first-value is only an evidence floor; satisfaction and friction are separate signals. (source: `charness-artifacts/retro/2026-06-03-184-usage-episode-product-success-consume-policy.md`)
- The first implementation copied the policy phrase "one emitter" into prose but only checked trigger and entry point in code. Fresh-eye review caught the gap; the final helper now checks `single_emitter`. (source: `charness-artifacts/retro/2026-06-03-184-usage-episode-product-success-consume-policy.md`)
- The first reporter version reached fresh-eye review with several privacy and execution edge cases still open: empty windows read as `usage_observed`, `classification_skipped` alone could become actionable, target refs could be posted into mutating comments, and `gh`/window errors were not structured. The critique caught these before commit, so this was not shipped waste, but it did push the slice through another implementation/test/sync loop. (source: `charness-artifacts/retro/2026-06-03-280-corca-internal-usage-last-seen-product-review.md`)

## Next-Time Checklist

- for reporter scripts that can mutate external state, write edge fixtures before broad happy-path tests: empty window/no data, missing binary, partial/multi-action failure, and privacy redaction. Disposition: applied in `tests/test_usage_episodes_report.py` for this reporter. (source: `charness-artifacts/retro/2026-06-03-280-corca-internal-usage-last-seen-product-review.md`)
- keep product-evidence logic out of the main report script once it grows beyond a simple summary. Disposition: applied by extracting `scripts/usage_episode_product_evidence.py`. (source: `charness-artifacts/retro/2026-06-03-184-usage-episode-product-success-consume-policy.md`)
- no new gate needed. Existing fresh-eye critique plus `run_slice_closeout` caught the issue before commit; the right improvement was targeted tests and the dogfood registry note, both committed in this slice. (source: `charness-artifacts/retro/2026-06-03-280-corca-internal-usage-last-seen-product-review.md`)
- product: do not close #184 until maintainer/source-thread synthesis and feedback/baseline evidence exist. Disposition: applied by leaving #184 open and recording non-claims in the goal artifact. (source: `charness-artifacts/retro/2026-06-03-184-usage-episode-product-success-consume-policy.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-06-03-184-usage-episode-product-success-consume-policy.md`
- `charness-artifacts/retro/2026-06-03-280-corca-internal-usage-last-seen-product-review.md`
