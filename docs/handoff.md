# Charness Handoff

## Workflow Trigger

- An active goal governs: read [recent lessons](../charness-artifacts/retro/recent-lessons.md), then resume [operator-rulings goal](../charness-artifacts/goals/2026-08-12-execute-operator-rulings-2-3-5-6.md) at its `## Active Operating Frame`.
- State the unpushed count with `git log --oneline origin/main..HEAD | wc -l` in the first reply. No push grant carries forward.

## Continuation Capability

- [Operating contract](./conventions/operating-contract.md) — proof-surface verdict changes require a second bounded review of repairs.
- [Implementation discipline](./conventions/implementation-discipline.md#declared-where-derivable) — derive facts before pinning them; form validators remain separate.
- [Cautilus on demand](../skills/public/quality/references/cautilus-on-demand.md) — plan first and ask before every evaluation run.

## Current State

- The [harness-improvement thesis](../charness-artifacts/spec/2026-08-11-harness-improvement-thesis.md) led to completed local ledger/session evidence; [comparative policy](../charness-artifacts/goals/2026-08-12-compare-score-policy-evidence.md) remains dormant pending naturally varied sessions.
- The active [operator-rulings goal](../charness-artifacts/goals/2026-08-12-execute-operator-rulings-2-3-5-6.md) completed rulings 2 and 3 locally. Ruling 5's `judge-intent` scenario is ready, but remains not executed: Cautilus requires both a qualifying log-backed behavior source and an explicit one-run grant before evaluation. Ruling 6 waits for that boundary.
- [Remote CI reconciliation](../charness-artifacts/spec/2026-08-09-remote-ci-changed-line-reconciliation-contract.md) remains locally resolved; hosted readback is not claimed.
Refresh kept: [the active goal](../charness-artifacts/goals/2026-08-12-execute-operator-rulings-2-3-5-6.md), its ordered first slice, the Cautilus approval boundary, and the remote-proof non-claim because each changes the next action.

Refresh non-claims: prior handoff backlog history, issue snapshots, quality numbers, and ownership-gate chronology now live in their owning artifacts.

<!-- charness-publish-state-claim:post-push-operational-proof -->
```json
{"kind":"charness.publish-state-claim","schema_version":1,"block_id":"post-push-operational-proof","manifest_path":"charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json","manifest_sha256":"a31aab7aecfb00c9ef84b9c26c93dbe15d630e83416a6d5cf38c04b6367fea34","published_sha":"e7c3e1b3fd7ab64bd07e19a2adc8bf7cedf2bde5","claim_state":"reconciled_captured_snapshot","issue_scope":"repository_open_issues_empty","pending_publish":false,"captured_at":"2026-08-06T02:14:03Z"}
```

## Next Session

1. Ask the operator to name a qualifying failing-prompt, transcript, operator-log, issue-log, or regression-log file and to grant one Cautilus evaluation for [the active goal](../charness-artifacts/goals/2026-08-12-execute-operator-rulings-2-3-5-6.md)'s ready `handoff/judge-intent` scenario; without both, the planner returns `next_action: none` and no invocation is permitted.
2. Continue [the active goal](../charness-artifacts/goals/2026-08-12-execute-operator-rulings-2-3-5-6.md) with ruling 6 only after the ruling-5 boundary is recorded.
3. Keep all running context in [the goal](../charness-artifacts/goals/2026-08-12-execute-operator-rulings-2-3-5-6.md); refresh this handoff only for a real interruption or user-requested baton pass.

## Discuss

- Cautilus evaluation requires a later, scenario-specific approval and qualifying behavior-source log. Push, release, issue close, and hosted readback also require new phase-scoped grants.

## References

- [Active operator-rulings goal](../charness-artifacts/goals/2026-08-12-execute-operator-rulings-2-3-5-6.md)
- [Six operator rulings](../charness-artifacts/spec/2026-08-11-six-operator-rulings.md)
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [Current quality posture](../charness-artifacts/quality/latest.md)
