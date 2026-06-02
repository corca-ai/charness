# Recent Retro Lessons

## Current Focus

- Closeout retro for `charness-artifacts/goals/2026-06-02-workflow-review-efficiency-and-generalization.md`. (source: `charness-artifacts/retro/2026-06-02-workflow-review-efficiency-closeout.md`)
- Goal: `charness-artifacts/goals/2026-06-02-279-achieve-activation-discussion-closeout.md` This goal resolved #279 by separating "activation discussion was surfaced" from "activation discussion was resolved" in `achieve` helper output, public skill guidance, lifecycle guidance, CLI wrapper coverage, and checked-in dogfood evidence. (source: `charness-artifacts/retro/2026-06-02-279-achieve-activation-discussion-closeout.md`)

## Repeat Traps

- **Broad pytest ran before the slice was stable.** The worst instance was closeout: full gate passed, then a fresh-eye review exposed a real `find-skills` output-volume gap, which required code/docs/tests/plugin changes and made the earlier broad run stale. That earlier broad run became mostly diagnostic theater. (source: `charness-artifacts/retro/2026-06-02-hard-waste-full-pytest-reruns.md`)
- **Closeout proof and mutation were interleaved.** After the goal was almost complete, I still mutated `find-skills --summary`, dogfood evidence, handoff, critique artifacts, retro artifacts, and goal evidence. That kept invalidating previous verification results. (source: `charness-artifacts/retro/2026-06-02-hard-waste-full-pytest-reruns.md`)
- **Full pytest was used as readiness discovery.** A later aggregate run found a handoff invariant failure caused by a non-issue `Next Session` entry. That was a real catch, but it was an expensive way to discover a markdown shape issue that a focused handoff parser test found in 3 seconds after the failure. (source: `charness-artifacts/retro/2026-06-02-hard-waste-full-pytest-reruns.md`)
- One full quality run was invoked incorrectly as `python3 scripts/run-quality.sh --read-only`; it failed immediately with a syntax error before running gates. This was command-form waste, not validation feedback. (source: `charness-artifacts/retro/2026-06-02-279-achieve-activation-discussion-closeout.md`)

## Next-Time Checklist

- add a lightweight `--no-broad` or `--skip-broad-pytest` mode to `run_slice_closeout.py` for pre-lock closeout rehearsal, so agents can prove sync/docs/artifact surfaces without paying the full suite before the slice is stable. (source: `charness-artifacts/retro/2026-06-02-hard-waste-full-pytest-reruns.md`)
- add or document a release preflight that maps changed adapter fields to focused tests, so update-instruction, fresh-checkout-probe, and real-host-checklist edits do not wait for full release quality to find local mismatches. (source: `charness-artifacts/retro/2026-06-02-release-helper-waste.md`)
- after editing a release adapter, run adapter-specific focused tests before invoking `publish_release.py --execute`. For this repo that includes `pytest tests/quality_gates/test_release_real_host.py -q` when real-host trigger/checklist fields change. (source: `charness-artifacts/retro/2026-06-02-release-helper-waste.md`)
- applied: Bind `Retro:`, `Host log probe:`, and `Disposition review:` evidence before marking active achieve goals `complete`. (source: `charness-artifacts/retro/2026-06-02-274-261-mutation-regression-and-standard-decision.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-06-02-274-261-mutation-regression-and-standard-decision.md`
- `charness-artifacts/retro/2026-06-02-279-achieve-activation-discussion-closeout.md`
- `charness-artifacts/retro/2026-06-02-hard-waste-full-pytest-reruns.md`
- `charness-artifacts/retro/2026-06-02-release-helper-waste.md`
- `charness-artifacts/retro/2026-06-02-workflow-review-efficiency-closeout.md`
