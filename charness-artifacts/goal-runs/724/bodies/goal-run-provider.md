<!-- charness-work-item-key: goal-run-provider -->
# Provide Exact Goal Run Graph Operations And Guarded Close

## Purpose

Own the adapter-resolved issue provider operations that let a Goal Run update a
parent body, create or reuse a managed child, add/remove real sub-issue
relationships, read exact graph state, and refuse unsafe close.

## Bounded contract

- Route every operation through the selected backend and complete preflight.
- Bind each mutation to an immutable started/terminal observation carrying the
  frozen draft and binding hashes.
- Verify repository, issue number, URL, body bytes, parent relationship, and
  post-mutation state through a distinct readback.
- Make retries idempotent, refuse unresolved prior creates and duplicate
  relationships, and preserve unverified outcomes instead of guessing.
- Guard immutable Goal Run metadata fields on parent-body updates.

## Acceptance and verification

Exercise fake backends plus the authenticated GitHub command surface for
preflight, read, update, create/reuse, list, add, remove, partial failure, and
retry behavior. Keep open-child close refusal explicit. The provider command
must not close issues as part of this child.

## Evidence boundary

This body records the provider capability contract; a successful local/fake
test is not live GitHub proof. Live proof requires the Goal Run observation and
exact external readback under the #724 bootstrap child.

## 2026-08-27 ownership cutover closeout

The provider boundary is implemented in commit
`35240a200ea77e82a64d9e719d9ae14f2f2e5518`.

- The canonical `skills/public/issue/scripts/` implementation and checked-in
  `plugins/charness/skills/issue/scripts/` export are byte-identical.
- The provider focused suite passed `8` tests through the standing pytest
  runner; the provider/runner/pickup/binding/lineage combined suite passed `65`.
- Provider `py_compile`, Ruff, skill-contract, evaluation, bootstrap-shim,
  standalone-import, and boundary-bypass checks passed before commit.
- Live `goal-run-preflight` against `corca-ai/charness#724` returned
  `status: ready`, `outcome: verified-read`, `mutation_invoked: false`, with
  all nine Goal Run operations and all ten backend operations available.
- Live graph reconciliation later returned `31` direct children, `14` CLOSED,
  and `17` OPEN after the representative #698 closeout. The earlier
  `3 completed / 28 open` bootstrap receipt was stale and is superseded by the
  current parent read and cursor update.

The guarded-close surface was verified narrowly: open-child refusal and the
generic-close Goal Run carrier refusal both pass without creating an observation
or invoking close. The general changed-line mutation runner was not promoted to
a blocking gate for the whole provider implementation under the current goal's
friction-reset policy. Its clean named-worktree attempt returned a blocked,
uncovered-provider-lines result; that result is retained as a non-claim, not as
a code-failure verdict. No broad mutation obligation is inferred from it.

This cutover does not invoke `goal-run-close`; #724 and #726 remain OPEN. No
issue closure, push, release, tag, remote-CI, installed-host, scheduler, or
consumer-repository enforcement is claimed. Forced fresh-eye, handoff, and
micro-slice rituals are intentionally omitted by operator direction.
