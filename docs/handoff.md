# Charness Handoff

## Workflow Trigger

- **No shaped goal is waiting.** The 2026-08-02 goal is COMPLETE and pushed.
  Start with chunked routing over the backlog below, or take a task the user names.

## Continuation Capability

- **A remedy a durable record names is a hypothesis** — verify its premise before
  shaping a slice around it
  ([implementation-discipline](./conventions/implementation-discipline.md), Change
  Discipline). It paid this run: the completed goal's own worked example (#467 as
  "a self-authored critique") was FALSE, caught by reading the artifact before
  building on it.
- **A slice packet's NON-CLAIMS are claims.** New this run in
  [operating-contract.md](./conventions/operating-contract.md): the only blocker
  in one review was a packet sentence ("no `plugins/` mirror is involved") that
  was never checked. The whole `scripts/` tree is mirrored.
- **Verify the reviewer boundary fingerprint the moment the reviewer returns**,
  before any parent write — also new in the operating contract; verifying late
  downgrades the attestation from proof to testimony.
- **When a slice changes what a floor REFUSES, measure it against the real corpus
  and pin the number with its denominator.** Three successive over-blocks shipped
  into review this run (10, 6, then 11 honest artifacts); only the last was caught
  by measuring rather than by inspection.

## Current State

- `main` is at `24bf8c6b`, remote `Quality Core` **green**, local backlog empty.
  The 2026-08-02 goal is COMPLETE.
- **The changed-line gate now states its scope on every verdict path**
  (`changed_pool_file_counts`, analyzed/changed). Refusal behaviour deliberately
  unchanged — whether a partial denominator should refuse is still **D45**.
- **The issue-close floor now reads the cited critique's own
  `Fresh-eye satisfaction:`** and refuses a record stating no distinct observer
  read the resolution — gated on the `AGENTS.md` delegation contract and a
  2026-07-05 grandfather; it refuses 0 of 133 existing artifacts.
- **#471 is OPEN and is the cheapest real follow-up**:
  `validate_critique_artifacts.has_repo_delegation_contract` is INERT here (same
  bolded-marker defect), so whatever it gates has never fired. Repairing it makes a
  dormant gate live across 400+ artifacts — measure that before fixing.
- **#469 and #470 are still OPEN and are an operator decision**, recorded in the
  completed goal's `## Operator Decision Queue`. Neither lane resolves either
  issue's full requested outcome, and **#470's second follow-up is mis-stated** —
  fix its body or the next lane inherits the error.
- Still open and untouched: the **E-cluster** (most expensive lane), D45–D49, and
  `parse_created_date`'s five uncorroborated consumers.

## Next Session

1. **Pick from: #471 (measure first), the #469/#470 operator decision, or the
   E-cluster.** #471 is smallest and carries its own premise-check plan.
2. **Budget for the pre-push gate** (~70s here, but it refused this session's
   first push on nine real uncovered degrade branches). Walk the degrade branches
   of any NEW module into its tests before pushing, not after.
3. **A `completed` closeout gate is not broad proof.** This session's locked
   closeout reported `completed` without selecting broad pytest, because by then
   the changed set was markdown-only. Run
   `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only`
   explicitly and record the number.

## Discuss

- **Should `absent` refuse at the close boundary in every contract repo?** It does
  now, and the reasoning is that nothing orders the authoring validator before the
  GitHub mutation. That is a real teeth-increase on a self-reported field; the
  counterargument (teeth over a self-report land on honest authors, not liars) is
  written up in the Lane B critique's Counterweight Pass and is worth a second look.
- **A read-only check and an irreversible boundary deserve different teeth** — D48
  left `drift` alone and refused at publish; whether other gates adopt that split
  is still open.

## References

- [completed goal](../charness-artifacts/goals/2026-08-02-make-a-verdict-state-its-denominator-and-move-the-fresh-eye-round-before-the-boundary.md) · [retro](../charness-artifacts/retro/2026-08-02-make-a-verdict-state-its-denominator-and-move-the-fresh-eye-round-before-the-boundary.md)
- critiques: [Lane A](../charness-artifacts/critique/2026-08-02-lane-a-changed-line-denominator-critique.md) · [Lane B, both rounds](../charness-artifacts/critique/2026-08-02-lane-b-close-boundary-observer-critique.md) · [closeout claims](../charness-artifacts/critique/2026-08-02-make-a-verdict-state-its-denominator-and-move-the-fresh-eye-round-before-the-boundary-closeout-claims-review.md)
- [deferred decisions](./deferred-decisions.md) (D45–D49) · [the sweep](../charness-artifacts/audit/2026-07-28-evidence-surface-triage-sweep.md) · [north star](./design-north-star.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md) · [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md)
