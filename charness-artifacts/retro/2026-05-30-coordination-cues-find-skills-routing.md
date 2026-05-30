# Retro — coordination-cues-find-skills-routing (session)

## Mode

session

## Context

Closeout of the achieve goal *Goal-doc coordination cues: route via find-skills +
gather/release floors* (commit `f55be70`). One session: find-skills routing →
read the achieve floor/closeout architecture → implement a new leaf module
`goal_artifact_coordination_floors.py` (gather + release presence-only closeout
floors mirroring the #253 disposition floor) + a `## Coordination Cues` template
carrier deferring to find-skills → reconcile 5 doc surfaces → 25 tests →
fresh-eye opus critique (found+fixed N1) → commit. What matters next: the goal is
complete; the deferred C9 bidirectional `/issue`–`/debug`-read-the-goal surface
is the natural follow-up.

## Evidence Summary

- Changed files + `git log` (commit `f55be70`); the goal artifact's Slice Log.
- Full suite run: `1893 passed / 4 skipped / 1 failed→0 after re-sync` (the
  failure was mirror drift, not logic).
- Host-log probe `charness-artifacts/probe/2026-05-30-coordination-cues-find-skills-routing.json`
  (claude host detected; token_count available, duration/turns/tool-calls
  derivable — point-in-time signals, not a waste conclusion).
- Fresh-eye implementation critique (opus subagent `a1052f6babb139f00`).

## Waste

- **Three serial pre-commit hook rejections *after* the full test suite was
  green.** `pytest tests/` passed (1893), so I treated the work as
  commit-ready and went straight to `git commit`. The commit was then rejected
  three times in a row — ruff (unused `Path` import), `validate-attention-state-visibility`
  (my length-neutral reword of the refusal note silently dropped the tracked
  `skipped: <enum>` term that a quality manifest pins to that file), and
  `check-markdown` (an inline code span wrapped across two physical lines in
  lifecycle.md). Each fix → re-sync mirror → retry → next rejection. None of
  these three gate families run under `pytest tests/`; they are pre-commit-only.
  Cost: ~3 extra commit cycles + 3 mirror re-syncs. The aggregate that surfaces
  all of them at once — `scripts/run_slice_closeout.py` — exists and the
  implementation-discipline doc explicitly says to run it before commit for a
  slice spanning multiple validator families. I skipped it.
- **One full-suite failure that was pure mirror drift.** I fixed N1 in the
  source *after* the last `sync_root_plugin_manifests.py`, so source≠mirror and
  `test_plugin_preamble`'s `root_install_surface.ok` went False. Re-sync cleared
  it. This is the known #257 "stage the regenerated mirror" trap recurring as
  "re-sync after *any* post-sync source edit". Low cost (one diagnosis), but a
  recurrence.

## Critical Decisions

- **Release-surface signal = artifact-text tokens, not git diff.** The goal left
  the signal open ("changed paths under the release manifest set, or a goal-shaped
  declaration"). Git-diff is *not clone-safe* (a fresh checkout has no diff), and
  the whole floor family is contracted as clone-safe (mirror the #233 binding
  rationale). So the release floor scans the goal's *recorded work* for precise
  path/action tokens (`bump_version` / `publish_release` / `marketplace.json` /
  `charness-artifacts/release/`) — never the bare word "release", which a goal
  that merely references the release skill (this one does) would trip on.
- **Grandfather cutoff 2026-05-31, not 2026-05-30.** The floors land 2026-05-30
  but several same-day goals (this one, #253, #255) predate them; a 2026-05-31
  cutoff grandfathers every in-flight same-day goal — zero retroactive friction
  on shipped work — while #253's own 2026-05-30 cutoff stays independent.
- **Scope reference/opt-out detection to `## Coordination Cues`.** A whole-body
  scan is poisoned because the goal body (this one included) *describes* the
  `Gather:`/`Release:` lines in prose — the exact #253 round-2 B-2 shape. Scoping
  + line-anchoring is the fix.
- **Fix N1 in-commit rather than defer.** The fresh-eye critique ranked the
  order-dependent false refusal a NIT, but it broke the "mirrors #253 exactly"
  claim and was a one-line fix + one test; fixing now beat a fast-follow.

## Expert Counterfactuals

- **A CI/release engineer (build-gate discipline):** would treat "the commit
  gate is a *different test surface* than the unit suite" as a first principle
  and run the pre-commit/aggregate gate *before* declaring done — not discover
  the gate families one rejection at a time. Changed action: run
  `run_slice_closeout.py` (the local pre-commit proxy) the moment the suite goes
  green, before the first `git commit`.
- **Michael Feathers (characterization / hidden coupling):** the
  `validate-attention-state-visibility` rejection is a *characterization*
  failure — a quality manifest pins specific literal terms inside a file as
  observable "attention state", an invariant invisible from the code itself. A
  length-neutral reword passed every test yet broke a declared contract.
  Changed question: "what *non-test* contracts pin literals in the file I'm
  about to edit?" — grep the file path against the attention-state manifest
  before rewording operator-facing strings.

## Next Improvements

- **workflow:** run `scripts/run_slice_closeout.py --repo-root .` (or the
  pre-commit hook set) the moment `pytest` is green and *before* the first
  commit on any slice that spans multiple validator families (ruff /
  attention-state-visibility / check-markdown / python-lengths / mirror drift
  are all pre-commit-only, not in `pytest tests/`). The teeth already exist and
  fired; the miss was sequencing.
- **memory:** fold "pre-commit gate family ≠ pytest; a length-neutral string
  reword can still break `validate-attention-state-visibility`; re-sync the
  mirror after *any* post-sync source edit" into `recent-lessons.md`.

## Sibling Search

The transferable pattern is "a non-test commit-time gate enforces an invariant
that `pytest tests/` does not surface, so a green suite reads as done when it is
not." Four-axis scan:

- **other validator families:** `check-markdown` (inline-span wrap),
  `check_skill_ownership_overlap` (cross-namespace mentions — also hit this
  session, caught pre-commit), `check_staged_mirror_drift`, `validate_packaging`,
  `validate-attention-state-visibility`, `check_python_lengths` — all
  commit-time, none in the unit suite. Confirmed siblings.
- **other skills editing .py/.md:** any skill whose closeout edits operator
  strings or references can drop an attention-state term or wrap a code span the
  same way; the gate is global, the habit is per-edit.
- **decision:** `existing tool, run it earlier` — the aggregate
  (`run_slice_closeout.py`) already unions these families; no new gate is
  warranted, only the sequencing habit + memory fold above. Not a new-issue
  candidate.

## Persisted

(to be set by persist_retro_artifact.py)
