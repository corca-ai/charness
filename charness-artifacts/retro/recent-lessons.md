# Recent Retro Lessons

## Current Focus

- Closeout retro for `charness-artifacts/goals/2026-06-02-workflow-review-efficiency-and-generalization.md`. (source: `charness-artifacts/retro/2026-06-02-workflow-review-efficiency-closeout.md`)
- Session retro after the workflow-review efficiency goal was completed and the user called out that full pytest was being run too often. (source: `charness-artifacts/retro/2026-06-02-hard-waste-full-pytest-reruns.md`)

## Repeat Traps

- **Broad pytest ran before the slice was stable.** The worst instance was closeout: full gate passed, then a fresh-eye review exposed a real `find-skills` output-volume gap, which required code/docs/tests/plugin changes and made the earlier broad run stale. That earlier broad run became mostly diagnostic theater. (source: `charness-artifacts/retro/2026-06-02-hard-waste-full-pytest-reruns.md`)
- **Closeout proof and mutation were interleaved.** After the goal was almost complete, I still mutated `find-skills --summary`, dogfood evidence, handoff, critique artifacts, retro artifacts, and goal evidence. That kept invalidating previous verification results. (source: `charness-artifacts/retro/2026-06-02-hard-waste-full-pytest-reruns.md`)
- **Full pytest was used as readiness discovery.** A later aggregate run found a handoff invariant failure caused by a non-issue `Next Session` entry. That was a real catch, but it was an expensive way to discover a markdown shape issue that a focused handoff parser test found in 3 seconds after the failure. (source: `charness-artifacts/retro/2026-06-02-hard-waste-full-pytest-reruns.md`)
- **`run_slice_closeout.py` made the right call, but I invoked it too early.** The script is appropriate after code/plugin/test changes. The waste was using it while the evidence bundle and handoff were still moving. (source: `charness-artifacts/retro/2026-06-02-hard-waste-full-pytest-reruns.md`)

## Next-Time Checklist

- add a lightweight `--no-broad` or `--skip-broad-pytest` mode to `run_slice_closeout.py` for pre-lock closeout rehearsal, so agents can prove sync/docs/artifact surfaces without paying the full suite before the slice is stable. (source: `charness-artifacts/retro/2026-06-02-hard-waste-full-pytest-reruns.md`)
- add or document a release preflight that maps changed adapter fields to focused tests, so update-instruction, fresh-checkout-probe, and real-host-checklist edits do not wait for full release quality to find local mismatches. (source: `charness-artifacts/retro/2026-06-02-release-helper-waste.md`)
- after editing a release adapter, run adapter-specific focused tests before invoking `publish_release.py --execute`. For this repo that includes `pytest tests/quality_gates/test_release_real_host.py -q` when real-host trigger/checklist fields change. (source: `charness-artifacts/retro/2026-06-02-release-helper-waste.md`)
- applied: Efficiency retros should separate measured host signals from proxy pressure and unavailable goal-window signals. This retro and the host probe use that split instead of treating cached input or session-wide counts as direct waste. (source: `charness-artifacts/retro/2026-06-02-workflow-review-efficiency-closeout.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-06-02-hard-waste-full-pytest-reruns.md`
- `charness-artifacts/retro/2026-06-02-release-helper-waste.md`
- `charness-artifacts/retro/2026-06-02-workflow-review-efficiency-closeout.md`
