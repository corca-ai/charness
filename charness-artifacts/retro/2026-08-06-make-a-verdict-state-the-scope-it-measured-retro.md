# Session Retro
Date: 2026-08-06

Goal: [2026-08-06-make-a-verdict-state-the-scope-it-measured.md](../goals/2026-08-06-make-a-verdict-state-the-scope-it-measured.md)

## Context

One goal, five slices, seven commits, four issues repaired (#487, #488, #489,
and #490 which the goal's own activation produced). The goal was shaped around
three surfaces that returned a success their own evidence contradicts; activating
it produced a fourth before any planned slice ran.

## Evidence Summary

- 7 commits: `a5b5d0e8`, `8573f862`, `3f7e0d04`, `c09c7f4a`, `736e99a0`,
  `817af71e`, `94d2b74b`. HEAD green on both CI check-runs via the check-runs API.
- 9 bounded review rounds. Blockers: round 1 of A (1), round 1 of B (1),
  round 1 of C (2), round 2 of C (2). ~25 non-blocking findings.
- **Every round that read REPAIRS on a verdict surface found something**, and 3
  of 4 found the class being repaired.
- 2 pre-push refusals, both naming real uncovered changed lines, both fixed by
  covering. 0 gates weakened, 0 `--no-verify`.
- 4 dup-ratchet hard blocks; 3 classified `intentional`, 1 (`_resolve_goal_path`)
  genuinely extractable and extracted.
- 3 forced length-cap extractions; 2 introduced a defect the suite could not see.

## Waste

- **The unplanned artifact repair came first.** ~1 slice of budget reconstructing
  a goal artifact rather than pursuing the goal. Cost created by the previous
  session's write, not avoidable in-session.
- **Three length-cap extractions, all forced mid-slice** because the slice added
  reasoning comments. Each then needed its own dup classification or repair.
- **Four dup-ratchet hard blocks, none of them new duplication** — every one a
  span shift bringing a pre-existing boilerplate parallel over the threshold.

## Critical Decisions

- **Asking the operator about #488 rather than picking.** The fix collided with a
  policy the lane records in its own comments; both readings were defensible and
  led to materially different work. The operator chose a third option neither the
  issue nor D40 had considered, and it cost no toll.
- **Extracting `goal_cli_args.py` instead of classifying its dup families
  `intentional`.** An `intentional` label on extractable code is a false record
  on a proof surface — the same class as everything else here.
- **Keeping the #487 reproduction test that still loses the prose.** It asserts
  the truncation still happens, so the new channel can never be mistaken for a
  fix to the shell.

## North Star Alignment

Read `docs/design-north-star.md` for this work.

**Held.** P4 governed the whole goal and was applied as written: at every
irreversible boundary the success was treated as provisional and confirmed by a
different observer AND a different channel. Remote CI was read through the
check-runs API rather than inferred from a push exit code — and that mattered,
because two intermediate SHAs show a `cancelled` mutation mirror that a push exit
code would have hidden. The four issue closes each carry a `Behavior #N:` verdict
naming a channel distinct from the one that produced the fix.

**Mis-applied, once.** "Confirm with a different observer" was weakened in slice
B's round 2: the reviewer-boundary fingerprint was verified AFTER the parent's
repairs instead of the moment the reviewer returned, so that window has no
integrity proof. Recorded as a non-claim rather than papered over, but the facet
was not honoured.

**Failure signature walked into: "a green is not a verdict", from the inside.**
Three times a repair shipped carrying the class it repaired — an ordering that
disarmed a push refusal, a detector recognising only the spelling copied from the
issue, and three silent-loss paths inside the channel built to remove silent
loss. The north star says teeth belong where a wrong answer escapes; the wrong
answers here escaped into the *repairs*, which is the place the standard's own
"round that reads the repairs" rule exists for, and it caught all three.

## Expert Counterfactuals

**Direct lens, no name needed: "where else is this fact computed and dropped?"**

Round 1 of slice B found an ordering error that disarmed a push refusal; round 2
found the identical defect in the sibling branch ten lines away, and I had
written a comment asserting the ordering did not matter. The same shape recurred
in slice C (fixed "the status lies about a deletion", shipped a detector that
recognised only deletions) and slice D (three silent-loss paths inside the
loss-removing channel).

Applying that question at design time, not review time, would have collapsed
three review rounds into zero findings.

## Sibling Search

- axis: a shipped reference describing the old behaviour | decision: valid
  follow-up outside the slice | proof: three instances in one goal —
  `lifecycle-before.md` (slice A), `bootstrap-posture.md` (slice C),
  `goal-artifact.md` (slice D, the file carrying the copy-paste command); all
  three caught by a bounded reviewer and by no gate | follow-up: issue #491
- axis: a module that cannot be imported standalone | decision: valid follow-up
  outside the slice | proof: `quality_policy_merge` raised
  `ImportError: partially initialized module` in a fresh process while 4979 tests
  passed, because every existing importer reached the other module first |
  follow-up: issue #492
- axis: a refill report stopping one level above the next instance | decision:
  valid follow-up outside the slice | proof: `_mark_subkey_refills` compares
  top-level keys, so a nested `mutation_testing` block under-reports |
  follow-up: issue #493
- axis: the sibling helper named in scope and not swept | decision: valid
  follow-up outside the slice | proof: `upsert_goal.py --goal-body` still takes
  prose through argv; the delegated close critique refused a wider #487 close |
  follow-up: issue #494

## Next Improvements

- workflow: verify the reviewer boundary the MOMENT the reviewer returns, before
  any parent write. Missed once this run, costing that window its proof.
- capability: a gate refusing a change whose owning reference still describes the
  old behaviour — issue #491.
- memory: a standalone-import check for every module in a package, generalizing
  the one-pair guard already committed — issue #492.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-06-make-a-verdict-state-the-scope-it-measured-retro.md
