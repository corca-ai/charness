# Final Release Boundary Retro — R2 Resume
Date: 2026-08-21
Goal: charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md

## Context

This retro closes the first receipted R2 resume session against the published
6.2.1 boundary. It records how the repair train moved from semantic candidate
proof to an externally verified release, while keeping fresh-eye approval,
Cautilus evaluation, and host-side #687 resolution as explicit non-claims.

## Window

The window spans the candidate-bound release work through the post-publish
managed-checkout repair. Evidence includes the exact release record, claims
review, public GitHub release readback, installed version/doctor readback, and
the command-boundary failures retained during the run.

## Evidence Summary

- Release tag `v6.2.1` points to `46169b7ad7491e1d4b1a50b5411ebf5a08f03a68`.
- `origin/main` and the managed install were reconciled to
  `d0df6dc7ac9c761b14bd1d5c5ef8b95bd1f2ec9d`.
- `gh release view v6.2.1` confirmed a non-draft, non-prerelease GitHub
  release; `charness version` reported `6.2.1`; `charness doctor --detail`
  reported valid cache manifest and no source/cache drift.
- The independent claims review passed as a release-record review only; it did
  not grant fresh-eye semantic approval.

## Waste

- recurrence-class: proof-surface-message-drift — intentionally wrong release
  command examples were initially rendered as runnable command evidence, so the
  quality gate treated the documentation as executable. The structural repair
  is to keep rejected calls non-executable and validate the owning command
  surface before recording them.
- recurrence-class: changed-line-proof-before-broad-quality — the final repair
  sequence used changed-line proof before the broad release gate; this remains a
  required ordering invariant because a passing broad suite cannot prove
  changed-line ownership.
- The first post-publish install observation was at an older artifact commit;
  the supported default `charness update --detail` was then run to reconcile
  the managed checkout. The first observation remains a drift smell, not a
  release pass.

## Critical Decisions

- Preserve the two-round fresh-eye cap and record round-2 repairs as
  accepted-unreviewed rather than inventing a third approval.
- Publish only after the claims review and exact release-candidate gates, then
  repair the post-publish managed-install skew through the supported command.
- Leave issue tracker closeout unrequested. The release carries Charness-side
  prevention and per-row evidence, but does not claim host-side #687 resolution
  or silently close #681–#687.

## North Star Alignment

The north star requires a capable judge and a different observer/channel at
irreversible boundaries. Public GitHub readback, `gh release view`, and the
separate installed `version`/`doctor` readback were kept distinct from the
publisher's exit status. The mis-application was treating stale routing prose
and an older managed checkout as if they were current proof; both were repaired
by binding exact identities and rereading the supported surface.

## Expert Counterfactuals

- Engelbart's system-improving lens would model release helper, claims record,
  managed install, and handoff as one H+LAM+T loop. It would require the helper
  to emit a post-publish commit identity and reconcile that identity before
  declaring install readback complete.
- A fail-closed evidence reviewer would ask “what does this observer not see?”
  before accepting each green signal: HTTP reachability does not prove a GitHub
  Release, a tag does not prove installed behavior, and a claims review does not
  prove semantic fresh-eye approval.

## Sibling Search

- same layer: release helper and handoff routing | decision: same waste, fix now | proof: exact post-publish commit and current handoff reconciliation
- abstraction up: release-record/public/install status axes | decision: same waste, fix now | proof: typed release record and separate readback fields
- specialization down: Codex cache manifest and doctor renderer | decision: same waste, fix now | proof: valid manifest, matching hashes, `source_cache_drift: false`
- mental-model siblings: wrong paths, stale refs, unsupported flags, and old checkout pointers | decision: valid follow-up outside the slice | proof: rejected calls retained as non-pass evidence and current supported command readback | follow-up: deferred docs/handoff.md#current-state

## Next Improvements

- workflow: make the release closeout planner require the post-publish artifact
  commit identity before its install-refresh step can be described as current.
- capability: expose a single typed “observer scope / does-not-establish” field
  for public, installed, host, and semantic verdict consumers.
- memory: keep “wrong call is a smell, never a pass” next to the release
  boundary and retain the current #681–#687 disposition packet as the tracker
  source of truth.

## Lesson Evaluation

Lesson evaluation: {"score_event_count":3,"session_id":"2026-08-21-goal-r2-resume","status":"effect-recorded"}

## Packet Consumed

Packet Consumed: charness-artifacts/retro/2026-08-21-123706-packet.md

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-21-goal-r2-resume-final.md
