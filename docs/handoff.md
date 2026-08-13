# Charness Handoff

## Workflow Trigger

- Continue the active [open-backlog `achieve` goal](../charness-artifacts/goals/2026-08-12-resolve-open-quality-and-trust-backlog.md): read back live tracker state into the [execution ledger](../charness-artifacts/goals/2026-08-12-open-backlog-execution-ledger.md), reconcile the goal with the [latest release record](../charness-artifacts/release/latest.md), then decide goal closeout before selecting another issue.

## Continuation Capability

- [Open-backlog goal](../charness-artifacts/goals/2026-08-12-resolve-open-quality-and-trust-backlog.md) — owns the fixed cohort, acceptance contract, boundaries, and slice plan.
- [Execution ledger](../charness-artifacts/goals/2026-08-12-open-backlog-execution-ledger.md) — owns per-issue premise, carrier, evidence, tracker disposition, and Late Arrivals.
- [Latest release record](../charness-artifacts/release/latest.md) — owns publication, distinct-channel, installed-version, doctor, observer, and baton-reconcile observations.

## Current State

- [Release notes](../charness-artifacts/release/2026-08-13-v5.2.0-notes.md) — hold the published value, update path, migration and rollback boundaries, proof limits, and issue boundary.
- [Claims review](../charness-artifacts/release-review/2026-08-13-v5.2.0-claims-review.md) — holds the independent prepared-record audit and the repaired update-surface claim.
- [#614](https://github.com/corca-ai/charness/issues/614), [#615](https://github.com/corca-ai/charness/issues/615), and [#616](https://github.com/corca-ai/charness/issues/616) — own their tracker `CLOSED` state after the direct carriers reached hosted `main`.
- [Session retro](../charness-artifacts/retro/2026-08-13-session-retro.md) — holds pre-release waste, proof-population lessons, and the lesson-evaluation disposition.
- [Release auto-retro](../charness-artifacts/retro/2026-08-13-v5-2-0-release-auto-retro.md) — holds release-triggered lessons and its explicit session-coverage limits.
- [#616 quality review](../charness-artifacts/quality/2026-08-13-issue-616-applied-lifecycle.md) — owns the production-only PLR2004/no-magic-numbers baseline recommendation.
- [Lesson and contract register](../charness-artifacts/spec/2026-08-12-lesson-ledger-and-contract-register.md) — owns lifecycle, proposal, transition, retention, and non-authorization semantics.

Refresh kept: publication truth stays in the [latest release record](../charness-artifacts/release/latest.md); the active [goal](../charness-artifacts/goals/2026-08-12-resolve-open-quality-and-trust-backlog.md) and [ledger](../charness-artifacts/goals/2026-08-12-open-backlog-execution-ledger.md) remain because their stale routing now changes the first action.

Refresh non-claims: the configured real-host trigger did not match; this machine observed update, version, and doctor readback, not a restarted host session or provider behavior. No live lesson lifecycle or contract-membership transition was applied.

## Next Session

1. Run `gh issue list --repo corca-ai/charness --state all --limit 100` to regenerate the live tracker set, then reconcile the [execution ledger](../charness-artifacts/goals/2026-08-12-open-backlog-execution-ledger.md)'s stale issue states.
2. [Open-backlog goal](../charness-artifacts/goals/2026-08-12-resolve-open-quality-and-trust-backlog.md) — reconcile its Active Operating Frame, final slice, verification, and status with the tracker-aligned ledger and latest release record, then decide goal closeout.
3. Only after that goal decision, run `gh issue list --repo corca-ai/charness --state open --limit 100` if another issue is to be selected.
4. [#616 quality review](../charness-artifacts/quality/2026-08-13-issue-616-applied-lifecycle.md) — production-only PLR2004 baseline/no-increase move, separate from lifecycle semantics.
5. [Score-policy evidence goal](../charness-artifacts/goals/2026-08-12-compare-score-policy-evidence.md) — remains dormant until declared sessions contain naturally varied scores.
6. [#584](https://github.com/corca-ai/charness/issues/584) — remains held by the [execution ledger's Umbrella Closure Contract](../charness-artifacts/goals/2026-08-12-open-backlog-execution-ledger.md#umbrella-closure-contract).
7. [Operating contract](./conventions/operating-contract.md) — owns critique, frozen verification, and independent readbacks for any later publication boundary.

## Discuss

- [#527](https://github.com/corca-ai/charness/issues/527) remains the owner of any destructive-skill selection product decision; its deferral does not authorize implementation.
- Whether machine-local observation should cover meaningful work that produces no durable retro without creating noisy per-chat repository state; the [continuity contract](../charness-artifacts/spec/2026-08-13-lesson-evaluation-observability-contract.md) currently claims durable-retro continuity only.
- Whether a typed public evaluator-adapter schema is warranted after more than one repo-local evaluator shows generic evidence discovery is insufficient.

## References

- [Recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [Current quality record](../charness-artifacts/quality/latest.md)
- [Latest release record](../charness-artifacts/release/latest.md)
