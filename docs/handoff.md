# Charness Handoff

## Workflow Trigger

- **A shaped goal is READY TO RUN, led by an OPERATOR-REPORTED defect (#475).**
  All activation items are settled, so activate it directly:
  `/goal @charness-artifacts/goals/2026-08-03-fix-the-rule-that-cannot-fire-where-it-was-written-to-then-count-the-rest.md`

## Continuation Capability

- **A remedy a durable record names is a hypothesis, and so is a previous
  reviewer's finding list** — verify the premise first
  ([implementation-discipline](./conventions/implementation-discipline.md), Change
  Discipline). #475 was found by ASKING the operator what they observed, after a
  lane had already been spent on a surface that was not the symptom.
- **A slice packet's NON-CLAIMS are claims**, and **verify the reviewer boundary
  the moment the reviewer returns** — both in
  [operating-contract.md](./conventions/operating-contract.md).
- **The second bounded round earns its cost on verdict surfaces.** Round 2 —
  reading only the repairs — found a case-sensitive filter silently dropping a
  completed goal out of every reported bucket, plus two overstated claims of the
  parent's. None of it was visible to round 1.
- **A count is not a finding until you know what could have made it different.**
  Two numbers this run were 0 for structural reasons, not corpus reasons.

## Current State

- `main` is at the commit below, local backlog empty. Re-check remote CI state
  rather than trusting this line: `gh run list --limit 3`.
- **The delegation-contract guard is LIVE** (#471 closed).
  `has_repo_delegation_contract` flattens inline markup before matching, so
  `_check_forbidden_blocker_phrases` finally runs; measured before and after, it
  refuses nothing. Pinned by a test reading the REAL `AGENTS.md` — a synthetic
  fixture spells the marker the way the code does, which is why this hid.
- **`audit_disposition_corpus.py` states its denominator**: `in_scope` splits into
  `in_scope_dated` + `in_scope_undatable`, each undatable goal named, intake split
  three ways. Recount with
  `python3 skills/public/achieve/scripts/audit_disposition_corpus.py --repo-root .`
- **The changed-line gate states its scope on every verdict path**; refusal is
  still **D40**'s toll. Still open and untouched: the **E-cluster** (most
  expensive lane), D41–D49, `parse_created_date`'s uncorroborated consumers.

## Next Session

1. **Lane A is #475.** Bounded review is MANDATED by several skills and is inert
   in any repo that never ran `setup`, because the authorization rule names only
   `AGENTS.md`. Build the settled three-rung ladder. The agent proves the
   MECHANISM only; the behavioural proof is the operator re-running in the repo
   that refused — this session cannot produce it, and must not claim it.
2. **Lane B counts the rest of the class** (#471/#473/#475 are one shape: a rule
   that cannot fire where it was written to). #475 widens the population the
   earlier sweep draft had wrong — it enumerated only code, and #475 lives in a
   contract surface. **Lane C is #474.** Cut order: C, then B's repairs, never A.
3. **#472 stays filed unless the operator pulls it in.** Widening the phrase list
   refuses checked-in artifacts — arming teeth on a corpus that cannot object.
   Measured: widening to the `delegation policy` stem refuses exactly 2, both
   dated 2026-05-21, so an enforce-from-date floor would refuse 0 today.
4. **A `completed` closeout gate is not broad proof.** Run
   `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only`
   explicitly and record the number.

## Discuss

- **Should the phrase-list widening (#472) be dated or retroactive?** The
  near-miss artifacts are from May 2026, so an enforce-from-date floor mirroring
  `FRESH_EYE_PRESENCE_RULE_DATE` is the cheap answer — but that is arming teeth on
  a corpus that cannot object, which this repo has got wrong twice (D49).
- **Settled (#475): who grants the standing delegation request.** A three-rung
  ladder — `AGENTS.md`, else a structured repo-owned opt-in, else ask once and
  persist. The plugin never self-grants. Reopen only if the per-repo question
  proves more friction than the never-ran-`setup` refusal it replaces.
- **A read-only check and an irreversible boundary deserve different teeth** — D48
  left `drift` alone and refused at publish; still open for other gates.

## References

- [waiting goal](../charness-artifacts/goals/2026-08-03-fix-the-rule-that-cannot-fire-where-it-was-written-to-then-count-the-rest.md) · [completed goal](../charness-artifacts/goals/2026-08-03-close-the-guard-that-never-fires-and-the-measurement-that-never-states-its-denominator.md) · [retro](../charness-artifacts/retro/2026-08-02-close-the-guard-that-never-fires-and-the-measurement-that-never-states-its-denominator.md) · [prior goal](../charness-artifacts/goals/2026-08-02-make-a-verdict-state-its-denominator-and-move-the-fresh-eye-round-before-the-boundary.md)
- critiques: [#471 resolution](../charness-artifacts/critique/2026-08-02-issue-471-resolution-critique.md) · [closeout claims](../charness-artifacts/critique/2026-08-02-close-the-guard-that-never-fires-and-the-measurement-that-never-states-its-denominator-closeout-claims-review.md)
- [deferred decisions](./deferred-decisions.md) (D45–D49) · [the sweep](../charness-artifacts/audit/2026-07-28-evidence-surface-triage-sweep.md) · [north star](./design-north-star.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md) · [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md)
