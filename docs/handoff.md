# Charness Handoff

## Workflow Trigger

- Continue the active `achieve` goal. **Ten cohort issues are now CLOSED and
  independently read back** — the earlier seven plus #597, #607, and #590, each
  repaired under two bounded review rounds and closed through the `issue` floor
  with a per-issue behavioral verdict. #609 is closed the same way. Twelve cohort
  rows remain OPEN; #584 is unchanged, still held on the ledger's Umbrella
  Closure Contract. `gh issue list --state open` returns 17 including the
  late arrivals.

## Continuation Capability

- [Open-backlog goal](../charness-artifacts/goals/2026-08-12-resolve-open-quality-and-trust-backlog.md) — owns the fixed 22-issue cohort, active frame, publication boundary, and slice log.
- [Execution ledger](../charness-artifacts/goals/2026-08-12-open-backlog-execution-ledger.md) — owns per-issue premise, local proof, tracker carrier, revisit state, and the Late Arrivals section. **Read it for any per-row question**; this file no longer restates it.

## Current State

- **Release `5.1.0` published** — tag `v5.1.0` at `1024e500`; existence and
  `draft: false` rest on the credential-free REST readback in
  [the observables probe](../charness-artifacts/probe/2026-08-13-v5.1.0-post-publication-observables.md),
  not the unauthenticated HTML fetch. It closed no issues.
- **Post-publication closeout review is done** —
  [review](../charness-artifacts/critique/2026-08-13-v5.1.0-post-publication-closeout-review.md).
  Both of its residues are now discharged: #609 is repaired and CLOSED, and the
  owed retro is
  [written](../charness-artifacts/retro/2026-08-13-proof-surface-repair-retro.md).
- **Four proof surfaces repaired this session**, two bounded review rounds each —
  [two-round critique](../charness-artifacts/critique/2026-08-13-four-proof-surface-repairs-two-round-critique.md).
  Commits `dd473642` (repairs) and `dfb29e0e` (coverage for the refusal branches
  subprocess tests cannot reach). Round 2 found a defect inside a round-1 repair
  on **every** surface reviewed — including one repair that silently disabled a
  sibling repair, and one that reopened the exact class the sibling fold closed.
  Both reviewer-boundary windows verified clean before any fold.
- Tracker carriers for the repaired rows, each naming what was proven and what was
  not: [#597](https://github.com/corca-ai/charness/issues/597#issuecomment-5275158380),
  [#607](https://github.com/corca-ai/charness/issues/607#issuecomment-5275160359),
  [#590](https://github.com/corca-ai/charness/issues/590#issuecomment-5275163833),
  [#609](https://github.com/corca-ai/charness/issues/609#issuecomment-5275163978).
- [Goal progress critique](../charness-artifacts/critique/2026-08-12-goal-progress-frame-and-ledger-critique.md) — local proof is not GitHub closure. The [prior session retro](../charness-artifacts/retro/2026-08-13-session-retro.md) does not cover this session.

Historical immutable publish-state claim — this captures the completed
2026-08-06 snapshot only; it does not describe this active backlog or authorize
issue closure, push, or release.

<!-- charness-publish-state-claim:post-push-operational-proof -->
```json
{"kind":"charness.publish-state-claim","schema_version":1,"block_id":"post-push-operational-proof","manifest_path":"charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json","manifest_sha256":"a31aab7aecfb00c9ef84b9c26c93dbe15d630e83416a6d5cf38c04b6367fea34","published_sha":"e7c3e1b3fd7ab64bd07e19a2adc8bf7cedf2bde5","claim_state":"reconciled_captured_snapshot","issue_scope":"repository_open_issues_empty","pending_publish":false,"captured_at":"2026-08-06T02:14:03Z"}
```

Refresh kept: the execution ledger and its per-row disposition map, because they
still own the 22-issue cohort reconciliation `5.1.0` deliberately did not close.

Refresh non-claims. #597, #607, #590, and #609 are CLOSED and read back; nothing
else was closed. **CI on `b0eb51d5` FAILED** its changed-line mutation-coverage
job on three lines; repaired in `ae118905`/`23f0735f`, and Quality Core on the
current head `d316bca2` is `success` (both jobs). The JS settlement repairs are
fixture-proven and consumer-facing (this repo's test tree contains no JS/TS
seams), and #590's log-tail and clamp branches remain unconfirmed because the
reporting step only runs when the pipeline is already red.

## Next Session

1. Decide [#613](https://github.com/corca-ai/charness/issues/613) first among the
   three filed residues — its mitigation is a loud refusal, so any consumer with a
   non-default adapter `output_dir` cannot publish at all until the record path is
   threaded through. Then
   [#610](https://github.com/corca-ai/charness/issues/610) (the claims verdict
   never reaches the published release record) and
   [#611](https://github.com/corca-ai/charness/issues/611) (the claims resume lane
   never runs the notes-file preflight).
2. [#584](https://github.com/corca-ai/charness/issues/584) stays held on the
   ledger's Umbrella Closure Contract, untouched this session. The nine deliberate
   non-closures (#527, #546, #550, #583, #586, #587, #599, #601, #605) were
   re-verified on 2026-08-13; #528 and #582 stay split.
3. Act on the retro's
   [skipped-is-not-passed](../charness-artifacts/retro/2026-08-13-proof-surface-repair-retro.md)
   lesson: this session pushed on a local green that had SKIPPED the
   changed-line mutation gate CI then blocked on.
4. The next push/release stays conditional on cohort disposition, retro, frozen
   verification, release critique, and independent readbacks per the
   [operating contract](./conventions/operating-contract.md). Nothing is pushed.

## Discuss

- #527's brief remains the owner of any future product decision; its current OPEN deferral does not authorize implementation.

## References

- [Recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [Current quality record](../charness-artifacts/quality/latest.md)
