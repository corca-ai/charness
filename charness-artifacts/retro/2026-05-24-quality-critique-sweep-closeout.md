# Quality Critique Sweep Closeout Retro
Date: 2026-05-24

## Context

This session continued the user-requested full-codebase `quality` and
`critique` sweep with subagents. It fixed #211-class mutation proof failures and
four sibling defects, filed #212-#214 for non-autonomous follow-ups, and updated
debug/quality/handoff artifacts.

## Evidence Summary

- `charness-artifacts/debug/latest.md`
- `charness-artifacts/quality/latest.md`
- #211 reproduction via mutation sample before the fix
- Fresh-eye reviewers: quality posture, bug/RCA scan, architecture/code critique,
  and counterweight
- Targeted tests, packaging validators, doc/link/markdown validators, and RCA
  ledger validation
- Full `run-quality --read-only` exposed and then covered a volatile pytest temp
  scan race in standing-test economics.

## Waste

- The first mutation-line continuation fix over-propagated coverage across
  enclosing `FunctionDef` bodies. Counterweight caught it, but only after a
  full sample probe had already been run.
- A pre-commit mutation sample using `MUTATION_HEAD_SHA=HEAD` proved only the
  previous committed window, not the current uncommitted patch. This repeated
  the same verification-window trap already documented in the mutation debug
  artifacts.
- The first post-commit sampler still found changed-line coverage gaps in new
  helper branches. The fix was straightforward, but it shows targeted tests
  should be checked against the committed sampler's actual selection signal.
- The final committed sampler cleared the sweep-specific blockers: 0
  changed-line blockers and 0 mutation-line coverage exclusions.
- Directly editing `recent-lessons.md` was waste because the file is generated
  from the retro lesson index.
- The first full quality rerun found an inventory race that targeted tests had
  not exercised; closeout gates need to run before treating the patch as ready
  to commit.

## Critical Decisions

- Treated #211 as blocking because the scheduled deeper-check had already filed
  it and local reproduction confirmed the same changed-line/mutation-line
  signals.
- Bundled sibling fixes that had clear deterministic tests: timestamp calendar
  validation, current-pointer constant detection, sync-support disposition exit
  semantics, and volatile pytest-temp inventory traversal.
- Filed #212-#214 instead of implementing them because they require spec,
  policy, or structural design decisions.

## Expert Counterfactuals

- Gary Klein: run the counterfactual failure story before the first full sample
  probe. That would have asked, "What if statement coverage propagates too far?"
  and forced the negative function-body test earlier.
- Daniel Kahneman: treat the passing pre-commit sampler as a substitution error.
  It answered "is the previous committed window green?" while the real question
  was "will the next committed window include this fix cleanly?"

## Next Improvements

- workflow: after any changed-line or changed-path gate fix, commit first, then
  rerun the sampler against the committed `base..HEAD` window before claiming
  the scheduled gate is repaired.
- workflow: when that committed sampler names residual changed-line gaps, add
  branch-level tests immediately and rerun before updating issue status.
- workflow: for mutation-line coverage heuristics, write the negative
  overreach test before the expensive end-to-end sample probe.
- workflow: for filesystem inventories over runtime temp trees, include a
  disappearing-path regression before relying on read-only quality closeout.
- capability: do not hand-edit `charness-artifacts/retro/recent-lessons.md`;
  persist a retro artifact and refresh through
  `persist_retro_artifact.py` / `refresh_recent_lessons.py`.
- memory: keep #212 as the owner for RCA ledger idempotency semantics so future
  closeout retries do not silently double-append metric events.

## Persisted

yes `charness-artifacts/retro/2026-05-24-quality-critique-sweep-closeout.md`
