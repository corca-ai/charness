# Charness Handoff

> Status: live session state
> Source of truth: current repository, release, and proof readbacks
> Last verified: 2026-08-25

## Workflow Trigger

- Run `python3 scripts/open_lesson_session.py --repo-root . --session-id <date-slug> --seed <date-slug>`
  BEFORE any brief or reviewer spawn — the REPO'S OWN copy, never the installed one:
  the installed-copy declare wrote a receipt without a ledger event, the half-written
  state the continuity gate then refuses (`unknown session` on every score).
- Then run `## Next Session` item 1.

## Continuation Capability

- The [tracker requalification packet](../charness-artifacts/issues/2026-08-22-tracker-requalification.md)
  holds the per-issue probe commands, the controls that prove each defect path was
  entered, and the stated evidence gap per issue.
- The [closeout critique](../charness-artifacts/critique/2026-08-22-issue-closeout-critique.md)
  holds both review rounds, the mutant that survived three tests, and the rung-2
  judgment on the typed probe-record dispositions.
- The [recent-lessons digest](../charness-artifacts/retro/recent-lessons.md) holds
  the session-start recurrence traps and parallel/timeout discipline.

## Current State

- Published release: `6.4.1` (`v6.4.1`) — verify locally with
  `git describe --tags --abbrev=0`; the [release record](../charness-artifacts/release/latest.md)
  and <https://github.com/corca-ai/charness/releases/tag/v6.4.1> are the sources
  for the public claim.
- The [quality receipt](../.charness/release-quality-receipt.json) is typed
  `pass` with no unproven subjects; its measured counts and the fresh-checkout
  plus installed `version`/`doctor` readbacks are the evidence source.
- The claims review is recorded in the
  [claims review artifact](../charness-artifacts/release-review/2026-08-25-v6.4.1-claims-review.md).
  Its only finding is advisory: the dated critique narrative becomes stale when
  revalidated against the final release delta.
- `charness update` refreshed the installed surface. Restart Codex/Claude
  sessions before relying on newly rotated absolute skill paths; the update
  receipt reports one potentially stale active-session path.
- Open tracker issues, including **#689**, **#690**, **#691**, and **#713**,
  remain tracker facts and were not closed by this release. Do not infer issue
  resolution from the shipped code or release tag.

## Next Session

1. Restart the Codex/Claude sessions after the `charness update` cache rotation,
   then run the repo-owned opener before any new brief or reviewer spawn:
   `python3 scripts/open_lesson_session.py --repo-root . --session-id <slug> --seed <slug>`.
2. Requalify the open consumer-friction issues from GitHub, starting with #713
   and checking whether #689/#690/#691 have durable shipped evidence. Keep issue
   status as the source of truth; this release did not close them.
3. Treat the advisory claims finding and the unauthored generated release body
   in the [release record](../charness-artifacts/release/latest.md) as follow-up
   work. Do not rewrite the published release record in place without a new
   proof packet and public readback.
4. Preserve the release proof floor documented in the
   [operating contract](./conventions/operating-contract.md): typed quality
   receipt, fresh-checkout probes, distinct observer, and distinct-channel
   public verification. A zero exit code or reachable tag alone is not a
   release verdict.

## Discuss

- **This bullet IS an SC14 anchor — do not tidy it away.** The
  [dominance test](../tests/quality_gates/test_command_dominance.py) substitutes into the
  real handoff and needs the bare backticked `python3 scripts/run_standing_pytest.py`, with no flags inside
  the backticks, present here.

## References

- The [design north star](./design-north-star.md) holds the different-observer rule and
  the proof-surface reading of the irreversible boundary.
- The [operating contract](./conventions/operating-contract.md) holds the two-round
  critique floor and the write-capable isolation rule.
- [Implementation discipline](./conventions/implementation-discipline.md) holds the
  `mutate -> sync -> verify -> publish` order and the generated-surface rule.
- [Validator timing layers](./conventions/validator-timing-layers.md) holds which gate runs
  at which boundary and why.
