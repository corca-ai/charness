# Slice 3 — goal-activation preflight surface (Activation preamble)
Date: 2026-06-08

## Decision Under Review

Add a `goal-activation` surface to `scripts/check_artifact_surface_preflight.py`
that surfaces the goal `Activation:` preamble line shape at author time. It uses a
new `template_preamble` shape source + `_extract_preamble` (pre-first-`## ` lines),
because the `Activation:` line is a preamble line, not a `## Heading` section.
Author-time-only (`validator=None`, `commit_boundary=False`) with an `owner`
override naming the real enforcement path.

## Failure Angles

- The `owner` message could misattribute enforcement to the wrong CLI surface,
  sending an author to a command that false-PASSes a missing `Activation:` line.
- Adding optional `Surface` fields could break positional instantiations or
  `dataclasses.replace`-based tests.
- The owner-line / emit_stub generalization could change output for existing
  surfaces (verdict-equality risk).
- The new surface could leak into the commit-boundary sweep and add a new gate.
- `_extract_preamble` could mis-handle a `## ` inside a fenced preamble block.

## Counterweight Pass

- Misattribution: REAL — found and fixed (see F1). `--pursue-ready` skips the
  Activation check; the default `check_goal_artifact.py` (`goal_lib.check_goal`)
  is the enforcer.
- Field addition: safe — new fields are keyword-defaulted AFTER `paths_arg`, so
  positional `Surface(...)` calls and `replace(...)` tests are unaffected
  (verified: `test_shape_text_handles_each_missing_shape_source` still reaches
  the "(no shape source registered)" fallback).
- Existing-surface output: unchanged — owner=None surfaces keep the default
  "achieve closeout (...)" line; emit_stub for goal-closeout still says "no
  scaffold script". The 29 baseline tests pass.
- Commit-boundary leak: not possible — `changed_artifacts` only processes
  `commit_boundary` surfaces; `surface_for_path` returns None for goal files
  (prefix=None). No new blocking behavior.
- Fenced `## `: not exercised (the live template preamble has no fence/`## `),
  and `check_goal`'s own check is the cruder `"Activation:" not in text`, so the
  surfacer is already more faithful than the validator needs — non-blocking.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/check_artifact_surface_preflight.py:goal-activation owner | action: fix | note: owner message originally claimed `check_goal_artifact.py --pursue-ready` enforces the Activation line; empirically --pursue-ready SKIPS it (pursue_readiness) and the DEFAULT check_goal is the enforcer — FIXED to name the default check; note string + spec + test assertion corrected; re-review SHIP
- F2 | bin: over-worry | evidence: weak | ref: scripts/check_artifact_surface_preflight.py:_extract_preamble | action: defer | note: naive line scan would truncate at a `## ` inside a fenced preamble block; not present in the live template and the owning validator is cruder still, so no action

## Reviewer Tier Evidence

- Requested tier: bounded fresh-eye subagent reviewer (separate agent context), per the goal verification plan's Slice-3 preflight boundary.
- Requested spawn fields: read-only critique reviewer with the bounded slice packet (intent, changed files + mirror, expected invariants, non-claims, out-of-scope, reviewer questions); inspect via git diff/show + read-only test runs only.
- Host exposure state: applied
- Application state: host-confirmed: bounded fresh-eye subagent (general-purpose agent a9dc870c3281165bd) returned VERDICT HOLD on round 1 with a real blocker (owner-message enforcer misattribution, empirically proven by running --pursue-ready vs default on a goal missing the Activation line); after the fix, round 2 returned VERDICT SHIP, no blockers, confirming the owner message is accurate down to the `charness goal check --goal-path <goal>` example command and 33/33 tests green.

## Fresh-Eye Satisfaction

SHIP (round 2). The fresh-eye reviewer's round-1 HOLD caught a genuine
operator-facing accuracy defect — the original owner message would have pointed an
author at `--pursue-ready`, which returns PASS even when the `Activation:` line is
missing. The fix names the real enforcer (the default `check_goal_artifact.py`
check), and the reviewer independently re-verified accuracy (including that the
cited `charness goal check` example runs the default `check_goal` path) and
behavior-preservation (no logic change; 33/33 tests green; mirror byte-identical).
