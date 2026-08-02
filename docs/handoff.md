# Charness Handoff

## Workflow Trigger

- **A shaped goal is waiting and needs THREE approvals before `/goal`.** Run
  `/achieve @charness-artifacts/goals/2026-08-03-count-the-rest-of-the-class-this-run-kept-finding-by-accident.md`
  to review its `## Discuss Before Activation`, settle it, then activate. It is
  deliberately NOT `pursue_ready`: item (2) is a toll only the operator can pay.

## Continuation Capability

- **A remedy a durable record names is a hypothesis** — verify its premise first
  ([implementation-discipline](./conventions/implementation-discipline.md), Change
  Discipline). Both lanes this run were reviewer-named; re-reading each surface
  first is what turned "fix a typo" into the measurement that was the deliverable.
- **A slice packet's NON-CLAIMS are claims**, and **verify the reviewer boundary
  the moment the reviewer returns** — both in
  [operating-contract.md](./conventions/operating-contract.md).
- **The second bounded round earns its cost on verdict surfaces.** Round 1 here
  found the phrase list under-fires; round 2 — reading only the repairs — found a
  case-sensitive status filter silently dropping a completed goal out of every
  reported bucket, and two sentences of mine that claimed more than was
  established. Neither was visible to round 1.
- **A count is not a finding until you know what could have made it different.**
  Two numbers this run were 0 for structural reasons, not corpus reasons.

## Current State

- `main` is at the commit below, local backlog empty. Re-check remote CI state
  rather than trusting this line: `gh run list --limit 3`.
- **The delegation-contract guard is LIVE** (#471 closed).
  `has_repo_delegation_contract` flattens inline markup before matching, so
  `_check_forbidden_blocker_phrases` finally runs. Measured before and after the
  repair against the real corpus: it refuses nothing, so no grandfather was taken.
  Pinned by a test that reads the REAL `AGENTS.md` — a synthetic fixture spells
  the marker the way the code does, which is why this stayed invisible.
- **`audit_disposition_corpus.py` states its denominator**: `in_scope` splits into
  `in_scope_dated` + `in_scope_undatable`, each undatable goal is named, and
  intake splits exactly three ways. Recount any figure with
  `python3 skills/public/achieve/scripts/audit_disposition_corpus.py --repo-root .`
- **The changed-line gate states its scope on every verdict path**; refusal is
  still **D40**'s toll. **The issue-close floor reads the cited critique's own
  `Fresh-eye satisfaction:`**, gated on the `AGENTS.md` contract.
- Still open and untouched: the **E-cluster** (most expensive lane), D41–D49, and
  `parse_created_date`'s uncorroborated consumers.

## Next Session

1. **Settle the waiting goal's three activation items, then run it.** Lane A
   sweeps the class this run found three times by accident and states its size;
   the population is already counted (19 `*_RULE_DATE` floors, 93 `validate_*` /
   `check_*` scripts). #473 is resolved inside it as the worked example.
2. **Lane B is #474** — surface dup-ratchet pressure at the first edit. Three
   consecutive runs wrote "run it early" into a plan and hit it at the closeout
   aggregate anyway; a prose checklist fires when nobody is reading the prose.
3. **#472 stays filed unless the operator pulls it in.** Widening the phrase list
   refuses checked-in artifacts — arming teeth on a corpus that cannot object.
4. **A `completed` closeout gate is not broad proof.** Run
   `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only`
   explicitly and record the number.

## Discuss

- **Should the phrase-list widening (#472) be dated or retroactive?** The
  near-miss artifacts are from May 2026, so an enforce-from-date floor mirroring
  `FRESH_EYE_PRESENCE_RULE_DATE` is the cheap answer — but that is arming teeth on
  a corpus that cannot object, which this repo has got wrong twice (D49).
- **How hard should the sweep look?** Its population is counted but its predicate
  is unwritten, so the reading cost is unknown until Lane A defines it. The goal
  stops and re-scopes rather than silently sampling; confirm that is wanted.
- **A read-only check and an irreversible boundary deserve different teeth** — D48
  left `drift` alone and refused at publish; whether other gates adopt that split
  is still open.

## References

- [waiting goal](../charness-artifacts/goals/2026-08-03-count-the-rest-of-the-class-this-run-kept-finding-by-accident.md) · [completed goal](../charness-artifacts/goals/2026-08-03-close-the-guard-that-never-fires-and-the-measurement-that-never-states-its-denominator.md) · [retro](../charness-artifacts/retro/2026-08-02-close-the-guard-that-never-fires-and-the-measurement-that-never-states-its-denominator.md) · [prior goal](../charness-artifacts/goals/2026-08-02-make-a-verdict-state-its-denominator-and-move-the-fresh-eye-round-before-the-boundary.md)
- critiques: [#471 resolution](../charness-artifacts/critique/2026-08-02-issue-471-resolution-critique.md) · [closeout claims](../charness-artifacts/critique/2026-08-02-close-the-guard-that-never-fires-and-the-measurement-that-never-states-its-denominator-closeout-claims-review.md)
- [deferred decisions](./deferred-decisions.md) (D45–D49) · [the sweep](../charness-artifacts/audit/2026-07-28-evidence-surface-triage-sweep.md) · [north star](./design-north-star.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md) · [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md)
