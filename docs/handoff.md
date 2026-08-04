# Charness Handoff

## Workflow Trigger

- **Next pickup:** first request the user's explicit confirmation of the broader proof-boundary umbrella: #491, #496, #502, #504, and #506. Until that confirmation is received, do not activate or implement. On confirmation, activate [the broader goal](../charness-artifacts/goals/2026-08-05-make-proof-claims-explicit-scoped-actionable.md) with `/goal @charness-artifacts/goals/2026-08-05-make-proof-claims-explicit-scoped-actionable.md`. It is one planning/evidence-coordination goal with independent track owners and independent issue dispositions, not a universal receipt protocol or an all-or-nothing release transaction. If the user wants one first-reader implementation goal instead, activate the existing [#502-focused draft](../charness-artifacts/goals/2026-08-05-make-proof-verdicts-contract-owned.md) and leave #491/#496/#504/#506 independent.

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
- Local branch is ahead of `origin/main` with unpushed documentation/artifact
  commits; read the live `git log` for the current HEAD. These commits contain
  only the unactivated broader umbrella goal, its pre-mortem/packet, the prior
  #502-focused fallback draft, and handoff evidence—not implementation.
- Live #491, #496, #502, #504, and #506 are OPEN. #502 is the only selected
  track with a new shared implementation: the 17 hand-written consumers of the
  `run-quality.sh` summary and the related slice-closeout verdict ownership
  decision. #496 and #504 have local repair evidence and need independent
  behavior/remote closeout handling; #491 and #506 retain separate reference
  and reviewer-boundary owners.

## Next Session

1. Request explicit confirmation of the five-issue umbrella and its independent
   track/closure boundary; do not activate or implement before that answer.
2. After confirmation, read the [broader goal draft](../charness-artifacts/goals/2026-08-05-make-proof-claims-explicit-scoped-actionable.md), its [pre-mortem](../charness-artifacts/critique/2026-08-05-broader-proof-claims-goal-pre-mortem.md), and live reads for all five issues, then activate with `/goal`.
3. Slice A must lock the per-track matrix (producer, first reader, owner,
   observable/falsifier, and closure dependency). Then implement only #502's
   shared receipt owner; keep #491/#506 separate and #496/#504 closeout-only
   unless fresh evidence changes their status.
4. Close or disposition each selected issue independently: its carrier,
   delegated critique, distinct behavior proof, and adapter readback must pass;
   one track's blocker must not be reported as another track's success.

## Discuss

- Confirm the five-issue umbrella is worth the coordination cost, while keeping
  each reader/owner/falsifier independent.
- Decide the structured receipt lifetime at activation: per-run contract/test
  seam with explicit machine-readable opt-in, not an unowned telemetry store.
- Decide #491's reviewer-owned versus narrow mechanical claim coupling only
  after its actual corpus inventory; do not preselect a new gate.
- Treat cross-surface parity as review-matrix facts, not identical prose,
  status vocabulary, or a shared closure transaction; keep `unproven` and
  `blocked` distinct.

Refresh kept: pushed SHA and independently observed green remote checks, the unactivated larger-goal pickup, and the owner/matrix decision required before implementation.

Refresh non-claims: the local #502 draft has not been pushed or remotely CI-verified; no implementation, issue close, release, or Cautilus evaluation was run for the new goal.

## References

- [broader goal](../charness-artifacts/goals/2026-08-05-make-proof-claims-explicit-scoped-actionable.md) · [goal pre-mortem](../charness-artifacts/critique/2026-08-05-broader-proof-claims-goal-pre-mortem.md) · [#502-focused fallback](../charness-artifacts/goals/2026-08-05-make-proof-verdicts-contract-owned.md)
- [North Star](./design-north-star.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [quality review](../charness-artifacts/quality/latest.md) · [remote check readback](../charness-artifacts/probe/2026-08-05-f29009bd-remote-check-readback.json) · [#502](https://github.com/corca-ai/charness/issues/502) · [#504 draft](../charness-artifacts/goals/2026-08-05-close-504-through-distinct-remote-proof.md)
