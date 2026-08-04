# Charness Handoff

## Workflow Trigger

- **Next pickup:** first request the user's explicit confirmation of the #502 focus and two-surface scope. Until that confirmation is received, do not activate or implement. On confirmation, activate the draft [larger #502 goal](../charness-artifacts/goals/2026-08-05-make-proof-verdicts-contract-owned.md) with `/goal @charness-artifacts/goals/2026-08-05-make-proof-verdicts-contract-owned.md`; if declined, use `/handoff` to choose a different backlog item. Do not activate the smaller #504 closeout draft by default.

## Continuation Capability

- A terminal verdict is a proof surface: its last retained line must state the
  real outcome, actionable subject, and trustworthy recovery evidence. Keep
  semantic facts separate from the observed spelling or transport that exposed
  them. A false-positive control only controls the axis it varies; write the
  invariant and an axis-varying counterexample before adding a guard.
- Run the broad suite per meaningful slice, not only at closeout. Proof-surface
  repairs owe a second bounded fresh-eye round that reads the repaired surface.

## Current State

- Push `f29009bd` reached `origin/main`; the GitHub Checks API independently
  read both check-runs as successful: [core gates](https://github.com/corca-ai/charness/actions/runs/30950181120/job/92130004731) and [changed-line mutation coverage](https://github.com/corca-ai/charness/actions/runs/30950181120/job/92130004666). The durable [remote readback](../charness-artifacts/probe/2026-08-05-f29009bd-remote-check-readback.json) records this different observer/channel from the push exit code.
- Local `556dfee6` is one commit ahead of `origin/main`; it contains only the
  unactivated #502 goal draft and its critique evidence, not implementation.
- Live #502 is OPEN. Its problem is the 17 hand-written consumers of the
  `run-quality.sh` summary and the related slice-closeout verdict ownership
  decision. #504 is also OPEN but its local implementation is complete and its
  remote-only closeout is intentionally a smaller goal.

## Next Session

1. Request explicit confirmation that #502 and its two-surface scope are the
   next goal; do not activate or implement before that answer.
2. After confirmation, read the [goal draft](../charness-artifacts/goals/2026-08-05-make-proof-verdicts-contract-owned.md), [critique](../charness-artifacts/critique/2026-08-05-proof-verdict-contracts-goal-critique.md), and live [issue #502](https://github.com/corca-ai/charness/issues/502), then activate with `/goal`.
3. Slice A must lock the state/exit/recovery matrix and owner before
   implementation; then implement the thinnest shared receipt owner with producer-owned quality and
   closeout adapters; preserve domain-specific statuses and plugin parity.
4. Close #502 only after carrier validation, delegated resolution critique,
   distinct behavior proof, and adapter readback all pass.

## Discuss

- Confirm the larger #502 goal is preferred over #504 remote closeout, #496,
  or #491.
- Decide the structured receipt lifetime at activation: per-run contract/test
  seam with explicit machine-readable opt-in, not an unowned telemetry store.
- Treat cross-surface parity as shared semantic facts, not identical prose or
  status vocabulary; keep `unproven` and `blocked` distinct.

## References

- [larger goal](../charness-artifacts/goals/2026-08-05-make-proof-verdicts-contract-owned.md) · [goal critique](../charness-artifacts/critique/2026-08-05-proof-verdict-contracts-goal-critique.md)
- [North Star](./design-north-star.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [quality review](../charness-artifacts/quality/latest.md) · [remote check readback](../charness-artifacts/probe/2026-08-05-f29009bd-remote-check-readback.json) · [#502](https://github.com/corca-ai/charness/issues/502) · [#504 draft](../charness-artifacts/goals/2026-08-05-close-504-through-distinct-remote-proof.md)

Refresh kept: pushed SHA and independently observed green remote checks, the unactivated larger-goal pickup, and the owner/matrix decision required before implementation.

Refresh non-claims: the local #502 draft has not been pushed or remotely CI-verified; no implementation, issue close, release, or Cautilus evaluation was run for the new goal.
