# Recent Retro Lessons

## Current Focus

- This retro reviews the goal that resolved #291, #292, and #284 in one bundle: activation readiness, staged-index test isolation, and skill-surface preflight. (source: `charness-artifacts/retro/2026-06-04-291-292-284-activation-index-and-skill-preflight.md`)
- Goal run implementing the A4-lite contract that turns retro waste findings into **structural, destination-routed** issue proposals instead of incident-coupled ones (shared reference + retro/achieve/issue wiring + issue-adapter `harness_upstream` + presence-only `validate_proposal_fields.py` + tests). (source: `charness-artifacts/retro/2026-06-03-retro-issue-destination-split.md`)

## Repeat Traps

- The first final broad gate failed on two test-structure issues that focused tests did not reveal: the isolated repo-copy e2e test needed `pytest.mark.release_only`, and #284 tests introduced a boundary-bypass candidate by spawning an import-safe script. (source: `charness-artifacts/retro/2026-06-04-291-292-284-activation-index-and-skill-preflight.md`)
- The first push attempt hit a live usage-episode snapshot flake in one host hook test. A focused rerun passed, and the second pre-push broad gate passed. (source: `charness-artifacts/retro/2026-06-04-291-292-284-activation-index-and-skill-preflight.md`)
- The goal artifact needed one more closeout repair pass because the After-phase evidence floors require explicit bound `Retro:`, `Host log probe:`, `Disposition review:`, `Gather:`, and `Issue closeout:` lines. (source: `charness-artifacts/retro/2026-06-04-291-292-284-activation-index-and-skill-preflight.md`)
- `check_auto_trigger.py` is state-sensitive: once a helper commits and pushes the release, the current diff is empty and the trigger cannot reconstruct the just-finished slice. (source: `charness-artifacts/retro/2026-06-03-auto-retro-trigger-miss.md`)

## Next-Time Checklist

- applied: `3b7ed973` marked the copy-heavy isolated repo test release-only and converted #284 tests to the in-process preflight API. (source: `charness-artifacts/retro/2026-06-04-291-292-284-activation-index-and-skill-preflight.md`)
- applied: the new preflight helper and implementation-discipline guidance make skill-surface headroom/coupling checks executable before broad quality. (source: `charness-artifacts/retro/2026-06-04-291-292-284-activation-index-and-skill-preflight.md`)
- no new issue: broader index-sensitive test inventory and installed-host proof are valid future work, but they are outside this bounded issue bundle and are recorded as non-claims. (source: `charness-artifacts/retro/2026-06-04-291-292-284-activation-index-and-skill-preflight.md`)
- a `--report-all` (collect-all) mode for `validate_quality_artifact.py` and peers would surface every violation in one pass; 21 `validate_*.py` raise on the first error today vs 10 that already collect failures. Optional candidate, not committed here. (source: `charness-artifacts/retro/2026-06-03-quality-283-waste-retro.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-06-03-auto-retro-trigger-miss.md`
- `charness-artifacts/retro/2026-06-03-quality-283-waste-retro.md`
- `charness-artifacts/retro/2026-06-03-retro-issue-destination-split.md`
- `charness-artifacts/retro/2026-06-04-291-292-284-activation-index-and-skill-preflight.md`
