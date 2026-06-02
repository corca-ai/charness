# Recent Retro Lessons

## Current Focus

- This retro covers the #184 usage-episode consume-policy goal. (source: `charness-artifacts/retro/2026-06-03-184-usage-episode-product-success-consume-policy.md`)
- Closeout retro for `charness-artifacts/goals/2026-06-02-workflow-review-efficiency-and-generalization.md`. (source: `charness-artifacts/retro/2026-06-02-workflow-review-efficiency-closeout.md`)

## Repeat Traps

- I accidentally ran `upsert_goal.py` without `--date` when activating the existing 2026-06-02 goal. That created a duplicate 2026-06-03 goal artifact, which I had to delete before continuing. (source: `charness-artifacts/retro/2026-06-03-184-usage-episode-product-success-consume-policy.md`)
- I initially treated `first_value_ref` too much like user-value evidence. The user correctly pushed back that Charness almost always leaves artifacts, so artifact existence cannot stand in for satisfaction. The resulting design is better: first-value is only an evidence floor; satisfaction and friction are separate signals. (source: `charness-artifacts/retro/2026-06-03-184-usage-episode-product-success-consume-policy.md`)
- The first implementation copied the policy phrase "one emitter" into prose but only checked trigger and entry point in code. Fresh-eye review caught the gap; the final helper now checks `single_emitter`. (source: `charness-artifacts/retro/2026-06-03-184-usage-episode-product-success-consume-policy.md`)
- **Broad pytest ran before the slice was stable.** The worst instance was closeout: full gate passed, then a fresh-eye review exposed a real `find-skills` output-volume gap, which required code/docs/tests/plugin changes and made the earlier broad run stale. That earlier broad run became mostly diagnostic theater. (source: `charness-artifacts/retro/2026-06-02-hard-waste-full-pytest-reruns.md`)

## Next-Time Checklist

- keep product-evidence logic out of the main report script once it grows beyond a simple summary. Disposition: applied by extracting `scripts/usage_episode_product_evidence.py`. (source: `charness-artifacts/retro/2026-06-03-184-usage-episode-product-success-consume-policy.md`)
- product: do not close #184 until maintainer/source-thread synthesis and feedback/baseline evidence exist. Disposition: applied by leaving #184 open and recording non-claims in the goal artifact. (source: `charness-artifacts/retro/2026-06-03-184-usage-episode-product-success-consume-policy.md`)
- when using `upsert_goal.py` on an existing dated artifact, pass the explicit `--date` from the artifact path. Disposition: applied in this run by deleting the accidental duplicate and continuing on the user-provided goal artifact; no code change needed unless this recurs. (source: `charness-artifacts/retro/2026-06-03-184-usage-episode-product-success-consume-policy.md`)
- add a lightweight `--no-broad` or `--skip-broad-pytest` mode to `run_slice_closeout.py` for pre-lock closeout rehearsal, so agents can prove sync/docs/artifact surfaces without paying the full suite before the slice is stable. (source: `charness-artifacts/retro/2026-06-02-hard-waste-full-pytest-reruns.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-06-02-hard-waste-full-pytest-reruns.md`
- `charness-artifacts/retro/2026-06-02-workflow-review-efficiency-closeout.md`
- `charness-artifacts/retro/2026-06-03-184-usage-episode-product-success-consume-policy.md`
