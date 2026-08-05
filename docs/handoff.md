# Charness Handoff

## Workflow Trigger

- **Next pickup:** do not activate the completed five-issue umbrella or the
  existing #502 draft unchanged. Ask one explicit operator question: should the
  existing [#502 implementation-and-proof draft](../charness-artifacts/goals/2026-08-05-make-proof-verdicts-contract-owned.md)
  be reshaped first, then adopted as the next standalone goal? If yes, live-read #502 and
  reconcile the local implementation/proof already recorded by the completed
  [umbrella goal](../charness-artifacts/goals/2026-08-05-make-proof-claims-explicit-scoped-actionable.md)
  before activation. If no, stop without activation, implementation, push,
  issue closure, or action on #491/#496/#504/#506. All five GitHub issues remain
  OPEN; the completed umbrella is background coordination evidence, not an
  activation target.

## Continuation Capability

- A terminal verdict is a proof surface: its last retained line must state the
  real outcome, actionable subject, and trustworthy recovery evidence. Keep
  semantic facts separate from the observed spelling or transport that exposed
  them. A false-positive control only controls the axis it varies; write the
  invariant and an axis-varying counterexample before adding a guard.
- Run the broad suite per meaningful slice, not only at closeout. Proof-surface
  repairs owe a second bounded fresh-eye round that reads the repaired surface.

## Current State

- Local branch is ahead of `origin/main` with unpushed documentation, artifact,
  and proof-receipt implementation commits; read the live `git log` for the
  current HEAD. The completed umbrella records the local implementation and
  proof, but no remote CI, issue closure, release, or installed-host claim.
- Live #491, #496, #502, #504, and #506 are OPEN. #502 is the only selected
  track with a new shared implementation: the 17 hand-written consumers of the
  `run-quality.sh` summary and the related slice-closeout verdict ownership
  decision. #496 and #504 have local repair evidence and need independent
  behavior/remote closeout handling; #491 and #506 retain separate reference and reviewer-boundary owners.

## Next Session

1. Ask whether to reshape #502 first and then adopt it as a standalone
   implementation-and-proof goal. Do not use the old five-issue umbrella as an
   activation target.
2. If yes, re-read the completed umbrella, the #502 draft, the current HEAD,
   and live #502 state. Confirm which local implementation/proof is historical
   versus intended to be carried by the next goal.
3. If yes, make Slice A an identity/carrier triage: bind the producer,
   first reader, owner, falsifier, current tests, source/plugin mirrors, and
   issue carrier to one revision before deciding whether any implementation
   remains. This does not authorize push or issue closure. Keep
   #491/#496/#504/#506 independently OPEN and unselected. If no, stop; a future
   successor artifact may be authored only in a separately authorized
   follow-up.
4. Any later issue close requires that issue's carrier, delegated critique,
   distinct behavior proof, and adapter readback; local green proof never
   stands in for remote CI or issue closure.

## Discuss

- Decide whether to reshape #502 first and then adopt it as a standalone
  implementation-and-proof goal. If no, leave this queue blocked; do not author
  a successor artifact in this pickup. The existing draft cannot be described as
  closeout-only without changing its contract.
- Confirm that the completed five-track umbrella remains background evidence
  only; it must not be reactivated and must not imply closure of any issue.
- Decide the structured receipt lifetime at activation: per-run contract/test
  seam with explicit machine-readable opt-in, not an unowned telemetry store.
- Treat cross-surface parity as review-matrix facts, not identical prose,
  status vocabulary, or a shared closure transaction; keep `unproven` and
  `blocked` distinct.

Refresh non-claims: no successor goal has been activated. The local proof does
not establish remote CI or issue closure for any successor goal. No push, issue
close, release, Cautilus evaluation, or installed-host proof was run for the
next goal. All five GitHub issues remain OPEN.

## References

- [broader goal](../charness-artifacts/goals/2026-08-05-make-proof-claims-explicit-scoped-actionable.md) · [goal pre-mortem](../charness-artifacts/critique/2026-08-05-broader-proof-claims-goal-pre-mortem.md) · [#502-focused fallback](../charness-artifacts/goals/2026-08-05-make-proof-verdicts-contract-owned.md)
- [North Star](./design-north-star.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [quality review](../charness-artifacts/quality/latest.md) · [remote check readback](../charness-artifacts/probe/2026-08-05-f29009bd-remote-check-readback.json) · [#502](https://github.com/corca-ai/charness/issues/502) · [#504 draft](../charness-artifacts/goals/2026-08-05-close-504-through-distinct-remote-proof.md)
