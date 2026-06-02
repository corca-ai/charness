# Hard Waste Retro: Full Pytest Reruns
Date: 2026-06-02

## Context

Session retro after the workflow-review efficiency goal was completed and the
user called out that full pytest was being run too often. This retro reviews
verification waste, not product correctness.

## Evidence Summary

- Host probe from the completed goal:
  `charness-artifacts/probe/2026-06-02-workflow-review-efficiency-and-generalization-host-log-probe.json`.
- Codex session audit over
  `/home/hwidong/.codex/sessions/2026/06/02/rollout-2026-06-02T06-03-47-019e84ff-f5f5-7101-8853-400b521b0a80.jsonl`.
- Prior recurrence:
  `charness-artifacts/retro/2026-06-01-reviewer-tier-sibling-scan-waste.md`.
- Final closeout aggregate:
  `python3 scripts/run_slice_closeout.py --repo-root . --ack-cautilus-skill-review`.

Observed session-wide signals:

- `pytest`: 31 repeated broad-gate invocations.
- `./scripts/check-markdown.sh`: 23 invocations.
- `git status`: 57, `git diff`: 52.
- 10 context compactions, 968 function calls, 125 custom tool calls, 22
  subagent spawns.

These counts are session-wide proxy pressure, not a clean per-goal cost
denominator. The waste classification below relies on command sequence and
phase, not raw counts alone.

## Waste

- **Broad pytest ran before the slice was stable.** The worst instance was
  closeout: full gate passed, then a fresh-eye review exposed a real
  `find-skills` output-volume gap, which required code/docs/tests/plugin
  changes and made the earlier broad run stale. That earlier broad run became
  mostly diagnostic theater.
- **Full pytest was used as readiness discovery.** A later aggregate run found a
  handoff invariant failure caused by a non-issue `Next Session` entry. That was
  a real catch, but it was an expensive way to discover a markdown shape issue
  that a focused handoff parser test found in 3 seconds after the failure.
- **Closeout proof and mutation were interleaved.** After the goal was almost
  complete, I still mutated `find-skills --summary`, dogfood evidence, handoff,
  critique artifacts, retro artifacts, and goal evidence. That kept invalidating
  previous verification results.
- **The existing lesson was not honored.** The 2026-06-01 retro already said
  broad pytest should wait until after fresh-eye disposition and triage lock.
  This run repeated the same class of waste, so the failure is not lack of
  memory; it is failure to obey the memory under closeout pressure.
- **`run_slice_closeout.py` made the right call, but I invoked it too early.**
  The script is appropriate after code/plugin/test changes. The waste was using
  it while the evidence bundle and handoff were still moving.

## Critical Decisions

- Good: after the user challenged "expression difference", I stopped treating
  prose-shape coupling as harmless and corrected the audit before final closeout.
- Good: after fresh-eye challenged `find-skills` output volume, I added
  `--summary` instead of narrowing the acceptance claim.
- Bad: I let those late improvements enter `fix now` after broad verification
  had already started, rather than reopening the triage lock explicitly and
  delaying full pytest until the new fix set was stable.
- Bad: I used broad pytest as a safety net for handoff and artifact wording
  instead of running focused artifact/parser checks first.

## Expert Counterfactuals

- **Eliyahu Goldratt / Theory of Constraints:** the bottleneck was broad
  verification time. A constraint-aware run would protect that resource by
  requiring a "no more mutation except commit metadata" declaration before
  running full pytest.
- **W. Edwards Deming:** the process had no stable "study" point. I measured
  before the system stopped changing, then changed the system again. The
  counterfactual is to study with focused checks until variance is gone, then
  run the expensive gate once.
- **Michael Feathers:** characterize the changed boundary first. Handoff prose
  changes should run handoff parser tests; `find-skills` output projection
  should run `find-skills` tests; only after those are green should the broad
  regression suite run.

## Next Improvements

- workflow: before any full pytest or `run_slice_closeout.py` that includes
  broad pytest, write a one-line **verification lock** in the working notes or
  goal artifact: "mutation set locked; only fixes for failing gates may change
  files." If a fresh-eye finding or user correction adds scope after that, the
  lock is broken and focused tests must run again before the next broad gate.
- workflow: require a **focused-failure replay** after broad pytest finds a
  localized issue. Do not immediately rerun the broad gate; first add or run the
  smallest target that reproduces the failure, as happened with
  `test_current_handoff_pipeline_has_only_actionable_candidates`.
- capability: add a lightweight `--no-broad` or `--skip-broad-pytest` mode to
  `run_slice_closeout.py` for pre-lock closeout rehearsal, so agents can prove
  sync/docs/artifact surfaces without paying the full suite before the slice is
  stable.
- memory: carry forward that the 2026-06-01 broad-pytest-before-triage-lock
  lesson recurred on 2026-06-02; future retros should treat another recurrence
  as process noncompliance, not a new discovery.

## Sibling Search

- same layer: `run_slice_closeout.py` closeout rehearsal | decision: valid follow-up outside the slice | proof: current script runs broad pytest for repo-python surfaces; a pre-lock mode would reduce waste before mutation lock
  follow-up: deferred docs/handoff.md Next Session #261/#184 queue context
- abstraction up: achieve goal lifecycle | decision: diagnostic-only | proof: lifecycle already says focused checks first and broad gates near final, but it lacks an explicit verification-lock phrase
- specialization down: handoff markdown edits | decision: same waste, fix now | proof: after broad failure, focused handoff parser test reproduced and verified the issue quickly
- mental-model siblings: "broad pytest means I am close to done" | decision: same waste, fix now | proof: this run showed broad pytest before lock can become stale within minutes

## Persisted

Persisted: yes `charness-artifacts/retro/2026-06-02-hard-waste-full-pytest-reruns.md`
