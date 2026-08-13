# Charness Handoff

## Workflow Trigger

- Continue the active [open-backlog `achieve` goal](../charness-artifacts/goals/2026-08-12-resolve-open-quality-and-trust-backlog.md). #615 has a verified local carrier but remains OPEN; without a new push grant, continue with #614.

## Continuation Capability

- [Open-backlog goal](../charness-artifacts/goals/2026-08-12-resolve-open-quality-and-trust-backlog.md) — owns the fixed 22-issue cohort, active frame, publication boundary, and slice log.
- [Execution ledger](../charness-artifacts/goals/2026-08-12-open-backlog-execution-ledger.md) — owns per-issue premise, local proof, tracker carrier, revisit state, and Late Arrivals. **Read it for any per-row question.**

## Current State

- [#615 debug](../charness-artifacts/debug/2026-08-13-issue-615-focused-changed-line-false-clean.md) and [critique](../charness-artifacts/critique/2026-08-13-issue-615-focused-marker-parity.md) — hold the marker-population root cause, exact historical block, export repair, and two-round review.
- [#615 carrier](../charness-artifacts/issue/2026-08-13-issue-615-closeout-commit-message.md) — holds the verified local direct-commit closeout claim and its publication non-claims.
- [Current session retro](../charness-artifacts/retro/2026-08-13-session-retro.md) — holds #615 waste, the lesson-evaluation audit, and the handoff link assessment.
- [Handoff/retro skill critique](../charness-artifacts/critique/2026-08-13-handoff-retro-skill-feedback-loop.md) — owns the repaired feedback-loop contract, review dispositions, and deferred typed-adapter boundary.
- [Lesson-ledger contract](../charness-artifacts/spec/2026-08-12-lesson-ledger-and-contract-register.md) — owns score rules and the boundary between ledger-backed preview selection and the generated digest.
- [Lesson-ledger state](../charness-artifacts/retro/lesson-ledger.json) — records declared preview-session snapshots and sparse score events; a snapshot proves containment, not exposure.
- [Lesson-evaluation continuity contract](../charness-artifacts/spec/2026-08-13-lesson-evaluation-observability-contract.md) — owns the eligible-retro denominator, exact disposition grammar, bounded receipt claim, and reconciliation violations.
- [#614](https://github.com/corca-ai/charness/issues/614) — holds the remaining unbounded `pytest-tmp` and `reports/mutation` cache class.

Historical immutable publish-state claim — this captures the completed
2026-08-06 snapshot only; it does not describe this active backlog or authorize
issue closure, push, or release.

<!-- charness-publish-state-claim:post-push-operational-proof -->
```json
{"kind":"charness.publish-state-claim","schema_version":1,"block_id":"post-push-operational-proof","manifest_path":"charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json","manifest_sha256":"a31aab7aecfb00c9ef84b9c26c93dbe15d630e83416a6d5cf38c04b6367fea34","published_sha":"e7c3e1b3fd7ab64bd07e19a2adc8bf7cedf2bde5","claim_state":"reconciled_captured_snapshot","issue_scope":"repository_open_issues_empty","pending_publish":false,"captured_at":"2026-08-06T02:14:03Z"}
```

Refresh kept: the goal and execution ledger remain the cohort owners; #615 stays visible until publication/readback, #614 remains the next locally decidable issue, and the lesson-ledger start/retro boundary is now workflow-wired but still needs honest operation next session.

Refresh non-claims: no #615 push, hosted CI, GitHub closure, or installed-consumer readback occurred. Lesson scores do not yet control the [recent-lessons digest](../charness-artifacts/retro/recent-lessons.md), prove human usefulness, or justify score-policy changes.

## Next Session

1. Do not report [#615](https://github.com/corca-ai/charness/issues/615) closed from its local carrier. Under a new phase-scoped grant, push it, observe hosted CI through a distinct channel, and run `verify-closeout --expect-state CLOSED`; without that grant, leave it OPEN.
2. Before #614, run the start command in [Local Lesson-Ledger Authoring](./development.md#local-lesson-ledger-authoring), actually present its deterministic list, and retain the same session ID through the retro disposition. At retro, record only sparse anchored effects, persist exactly one [Lesson Evaluation Disposition](./development.md#lesson-evaluation-disposition) line, then run the continuity report. The declaration and receipt do not prove presentation.
3. Resolve [#614](https://github.com/corca-ai/charness/issues/614)'s remaining members: `pytest-tmp` keeps the most recent N failed basetemps rather than cleaning up on failure (the retention is deliberate), and `reports/mutation` has no policy at all.
4. Keep the [score-policy evidence goal](../charness-artifacts/goals/2026-08-12-compare-score-policy-evidence.md) dormant until multiple declared sessions contain naturally varied scores; do not tune from the current positive-only cohort.
5. [#584](https://github.com/corca-ai/charness/issues/584) stays held on the ledger's Umbrella Closure Contract.
6. The other cohort rows retain their tracker-visible non-closures and revisit triggers in the [execution ledger](../charness-artifacts/goals/2026-08-12-open-backlog-execution-ledger.md).
7. The next release remains conditional on the [operating contract](./conventions/operating-contract.md)'s frozen verification, critique, and independent readbacks.

## Discuss

- #527's brief remains the owner of any future product decision; its current OPEN deferral does not authorize implementation.
- Whether a machine-local observer can count meaningful work that never produces
  a durable retro without writing noisy per-chat repository state; until then,
  the [continuity contract](../charness-artifacts/spec/2026-08-13-lesson-evaluation-observability-contract.md)
  claims durable-retro continuity only.
- Whether a typed public evaluator-adapter schema is warranted after more than one repo-local evaluator demonstrates that generic evidence discovery is insufficient.

## References

- [Recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [Current quality record](../charness-artifacts/quality/latest.md)
