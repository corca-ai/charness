# Retro — Workflow-ergonomics bundle goal (#336 goal-slot + critique-enum + update_instructions)

Mode: session

Goal: `charness-artifacts/goals/2026-06-08-workflow-ergonomics-goal-slot-and-authoring-friction.md`

## Context

The `achieve` workflow-ergonomics bundle goal: three small structural fixes to
surfaces where the achieve/release workflow trips the operator/agent — (1) #336
achieve draft must not consume the host active-goal slot, (2) critique-scaffold
enum validity by-construction, (3) publish_release `--prep-update-instructions`
pre-publish stub. Activated via `/goal`, ran 4 slices (3 impl + bundle closeout),
each with a fresh-eye critique. Broad gate passed 73/73 phases. Next: the #336
direct-commit closeout carrier + verify-closeout, then complete.

## Evidence Summary

- 6 commits over merge-base origin/main..HEAD; goal artifact Slice Log; the three
  fresh-eye subagent critiques (all SHIP); the changed-line mutation coverage
  producer (ok:true after covering 6 lines); broad gate `run-quality.sh
  --read-only` (73 passed, 0 failed); host log probe
  (`charness-artifacts/probe/2026-06-08-workflow-ergonomics-goal-slot.json`).

## Waste

- **Changed-line coverage round-trip (anticipated, partly avoidable).** The
  Slice-3 prep affordance added input-normalization branches (list/string/None)
  and three defensive `SystemExit` guards, plus a refactor that relocated the
  clean-worktree check. Slice-3 tests covered the happy path but not those
  branches, so the bundle-boundary producer flagged 6 uncovered changed lines,
  costing a cover-then-re-run-producer cycle (each producer run is multi-minute
  mutation coverage). Running the producer FIRST (per the carried guardrail)
  worked — it surfaced the gap at the boundary, not post-merge — but covering the
  branches IN Slice 3 would have made the producer a confirmation, not a
  discovery.
- **SKILL.md core buffer block (minor, anticipated).** Slice 1's first edit added
  +2 achieve core lines and tripped the core-headroom buffer (4-line floor); one
  re-tighten to +1 line + re-sync. The carried "anticipate the no-increase
  ratchets / compress-to-offset" lesson applied; the cost was one edit cycle.
- **Invalid-adapter test first miss (trivial).** The first invalid-adapter test
  wrote an adapter that was valid-with-defaults (hit the version guard instead);
  one fix to a non-integer version. Trivial.

## Critical Decisions

- **#336 portable-vs-host determination (Slice 1, early).** Determined the host
  active-goal slot is host-owned but slot *consumption* is agent/operator-driven
  (`upsert_goal.py` is pure file I/O), so the achieve contract IS the real
  portable fix, not a partial — and the host-auto-activation residual is a
  documented non-claim, not a speculative host-gap issue. This avoided both
  faking a fix and over-filing.
- **Drift-test single-source-of-truth for the critique enum legend (Slice 2).**
  Chose hardcoded scaffold constants pinned to the validator's frozensets by a
  bidirectional drift test, over a runtime validator import — keeping the scaffold
  portable to exported/consumer layouts. Paid off immediately: the #336 resolution
  critique authored this session validated on the FIRST try (zero validate->fix
  round-trips — the exact trap Slice 2 fixes), dogfooding the fix in-session.
- **Extract `execute_publish_plan` to free main()'s 100-line cap (Slice 3).**
  A behavior-preserving extraction (empty byte-level diff of the moved body,
  independently confirmed by the fresh-eye reviewer) that also dropped main()
  from 100 to ~25 function lines.

## Expert Counterfactuals

- **Kent Beck (test-the-branches-you-write lens).** When introducing the prep
  affordance's input normalization (list/str/None) and defensive guards, Beck's
  habit would be to write the branch-covering test the moment each branch is
  added — not defer to a happy-path test. Changed action: in Slice 3, enumerate
  the new branches/guards and cover each in-slice, so the bundle-boundary mutation
  producer confirms rather than discovers, removing the cover-then-re-run cycle.
- **W. Edwards Deming (study-before-claim lens, applied positively).** The
  producer-first discipline is exactly the "inspect at the source, not after the
  fact" move — running coverage at the bundle boundary BEFORE the broad gate
  caught the gap when it was cheap to fix. Keep this; the only refinement is
  pushing the same inspection one step earlier (into the introducing slice).

## Next Improvements

- **workflow/memory:** When a slice adds a helper with input-normalization
  branches (list/str/None/empty) or defensive `SystemExit`/raise guards, cover
  each branch IN that slice — the changed-line mutation gate will flag them at the
  bundle boundary regardless. Treat "new normalization branch or new guard line"
  as a same-slice test obligation, not a happy-path-only one.
  Disposition: applied — durably recorded in this checked-in retro's Next Improvements and ingested as a recent-lessons candidate; the auto-selected digest surfaced it this refresh as a backward Repeat-Trap waste record (not yet a forward Next-Time Checklist line — the selector promotes on recurrence).
- **memory (positive, keep):** The producer-first guardrail and the critique enum
  legend both worked as designed this session (producer surfaced the gap early;
  the legend gave a first-try critique). No change needed; recorded so the next
  session keeps both habits.
  Disposition: applied — both are already Next-Time Checklist lines in recent-lessons (from the prior retro), confirmed effective.

## Sibling Search

The transferable pattern is "newly-added input-normalization branches and
defensive guard lines ship uncovered and surface only at the bundle-boundary
mutation gate." Four-axis scan:

- **other scripts:** the same prep-affordance pattern (normalize input, guard,
  emit) recurs in other release/achieve helpers, but those are pre-existing
  (not changed this run) so the changed-line gate does not flag them; no fresh
  sibling to fix now.
- **other workflows:** this is a testing-habit lesson, not a code-site defect,
  so the durable fix is the recent-lessons signal above, not a code change.
- **docs/contracts:** the lesson is *adjacent to* the existing "anticipate the
  no-increase ratchets on additive work" recent-lessons line but names a distinct
  trigger (mutation-coverage of normalization/guard branches, not core-headroom).
  It was NOT folded into that ratchet line — that line is a different subject and
  stays unedited; this lesson lives in this retro's Next Improvements + the
  candidate pool.
- **decision:** `n/a — habit lesson, no code sibling to fix this run`; the
  improvement is the durable retro record + pooled candidate, not a sibling code
  change.

## Persisted

Persisted: yes (path set by persist_retro_artifact.py).
