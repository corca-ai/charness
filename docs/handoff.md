# Charness Handoff

## Workflow Trigger

- Continue the active `achieve` goal: `v5.1.0` is published and publicly
  verified, so the goal's publication boundary is now cleared. The remaining
  work is the 22-issue cohort disposition — each issue still holds an OPEN
  tracker carrier and none were closed by this release.

## Continuation Capability

- [Open-backlog goal](../charness-artifacts/goals/2026-08-12-resolve-open-quality-and-trust-backlog.md) — owns the fixed 22-issue cohort, active frame, publication boundary, and slice log.
- [Execution ledger](../charness-artifacts/goals/2026-08-12-open-backlog-execution-ledger.md) — owns per-issue premise, local proof, tracker carrier, and revisit state.

## Current State

- **Release `5.1.0` published** — tag `v5.1.0` at `1024e500`, branch `main` at
  `6bf2d545`, [release](https://github.com/corca-ai/charness/releases/tag/v5.1.0)
  verified through a credential-free API readback (`draft: false`). The release
  gate ran green (91 passed, 0 failed, `check-changed-line-mutation-coverage`
  UNPROVEN/partial), fresh-checkout probes passed, and `charness update`
  refreshed the installed plugin. It closed no issues.
- [Goal progress critique](../charness-artifacts/critique/2026-08-12-goal-progress-frame-and-ledger-critique.md) — binds the current ledger/frame to a fresh-eye review; local proof is not GitHub closure.
- [Issue #589 local proof](../charness-artifacts/critique/2026-08-13-issue-589-preset-reconciliation-resolution.md) — validator-accepted prescriptions now have reconciled, missing, unavailable, and advisory-metadata states; tracker carrier is [open](https://github.com/corca-ai/charness/issues/589#issuecomment-5268917088).
- [Issue #586 disposition](../charness-artifacts/debug/2026-08-13-debug-review.md) — no current inert production path was reproduced; its [OPEN tracker carrier](https://github.com/corca-ai/charness/issues/586#issuecomment-5268965258) names the concrete revisit trigger.
- [Issue #590 hosted proof](https://github.com/corca-ai/charness/issues/590#issuecomment-5268992650) — a scheduled CI descendant of its repair completed the mutation stages successfully; it remains OPEN pending cohort closeout.
- [Issue #606 local proof](../charness-artifacts/critique/2026-08-13-issue-606-boundary-baseline-resolution.md) — canonical baseline regeneration is guarded and all persisted verdict inputs are integrity-bound; its [OPEN tracker carrier](https://github.com/corca-ai/charness/issues/606#issuecomment-5269188496) awaits final direct-to-default readback.
- [Issue #582 local proof](../charness-artifacts/critique/2026-08-13-issue-582-readme-proof-evidence-binding-resolution.md) — the README Claim Ledger's Evidence cells are now path-bound at their Specdown reader; its [OPEN tracker carrier](https://github.com/corca-ai/charness/issues/582#issuecomment-5269364370) records that #524/#535 remain separate deliberate non-implementations.
- [Issue #583 re-read disposition](https://github.com/corca-ai/charness/issues/583#issuecomment-5269219339) — its cited pickup specs are deleted and #597 repaired the fixture fail-open; it remains OPEN with a bounded generic-gate deferral.
- [Issue #584 local proof](../charness-artifacts/critique/2026-08-13-issue-584-planner-read-cost-resolution.md) — representative quality/handoff planner reads disclose measured or typed-unavailable state across source/plugin layouts; its [OPEN tracker carrier](https://github.com/corca-ai/charness/issues/584#issuecomment-5269582606) defers broader planner rollout and cohort closeout.
- [Issue #539 local proof](../charness-artifacts/critique/2026-08-13-issue-539-create-url-shape-resolution.md) — create output now exposes only validated URL identity while retaining parsed alternate-backend numbers; its [OPEN tracker carrier](https://github.com/corca-ai/charness/issues/539#issuecomment-5269681471) awaits cohort closeout.
- [Issue #542 local proof](../charness-artifacts/critique/2026-08-13-issue-542-closeout-target-disagreement-resolution.md) — source-aware closeout authorization distinguishes manual declaration from CLI target before backend mutation; its [OPEN tracker carrier](https://github.com/corca-ai/charness/issues/542#issuecomment-5269820465) awaits cohort closeout.
- [Issue #602 local proof](../charness-artifacts/critique/2026-08-13-issue-602-create-verification-grammar-resolution.md) — deferred create readback is a typed, target-bound `verify-create` operation and body fidelity still requires the original body file; its [OPEN tracker carrier](https://github.com/corca-ai/charness/issues/602#issuecomment-5270132863) awaits cohort closeout.
- [Issue #588 local proof](../charness-artifacts/critique/2026-08-13-issue-588-policy-absent-dogfood-resolution.md) — policy-absent consumer repos receive typed applicability rather than a traceback while present invalid policy remains an error; its [OPEN tracker carrier](https://github.com/corca-ai/charness/issues/588#issuecomment-5270306863) awaits cohort closeout.
- [Issue #607 local proof](../charness-artifacts/critique/2026-08-13-issue-607-subprocess-settlement-inventory-resolution.md) — standing-test economics detail now exposes conservative, callsite-attributed settlement signals without claiming runtime child semantics; its [OPEN tracker carrier](https://github.com/corca-ai/charness/issues/607#issuecomment-5270588693) awaits cohort closeout.
- [Issue #527 decision brief](../charness-artifacts/issue/2026-08-13-issue-527-brief.md) — its documentation and invocation-policy choices remain operator-owned; its [OPEN tracker carrier](https://github.com/corca-ai/charness/issues/527#issuecomment-5270654051) records the bounded deferral rather than an assumed implementation.
- [Session retro](../charness-artifacts/retro/2026-08-13-session-retro.md) — records #607's conservative static-proof lessons, #527's decision boundary, the verified 22-row reconciliation, and #503's unchanged ownership of historical runtime telemetry; it makes no publication claim.
- [Issue #608 release-flow repair](../charness-artifacts/critique/2026-08-13-issue-608-claims-review-release-stage.md) — normal release preparation now stops at a marked local record and a separately committed, bound review record is required before publication; local focused tests passed, but no publication occurred.
- [Release-preflight retro](../charness-artifacts/retro/2026-08-13-release-preflight-retro.md) — records the 11-file coverage recovery and why the fresh locked full-range closeout, rather than focused tests, unlocked the release sequence.
- [Issue #528 split disposition](https://github.com/corca-ai/charness/issues/528#issuecomment-5269713927) — the core dotted-absence capability is already proven; consumer migration and hook discovery remain separately owned.
- [Issue #550](https://github.com/corca-ai/charness/issues/550), [#599](https://github.com/corca-ai/charness/issues/599), and [#601](https://github.com/corca-ai/charness/issues/601) — hold bounded OPEN deferrals for absent resolver-family, reader-taxonomy, and CLI-harness premises; the execution ledger owns their revisit triggers.
- [Issue #546](https://github.com/corca-ai/charness/issues/546), [#584](https://github.com/corca-ai/charness/issues/584), [#587](https://github.com/corca-ai/charness/issues/587), [#595](https://github.com/corca-ai/charness/issues/595), [#597](https://github.com/corca-ai/charness/issues/597), and [#605](https://github.com/corca-ai/charness/issues/605) — hold the remaining tracker-visible local-proof, split, or defer carriers recorded in the execution ledger.
Historical immutable publish-state claim — this captures the completed
2026-08-06 snapshot only; it does not describe this active backlog or authorize
issue closure, push, or release.

<!-- charness-publish-state-claim:post-push-operational-proof -->
```json
{"kind":"charness.publish-state-claim","schema_version":1,"block_id":"post-push-operational-proof","manifest_path":"charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json","manifest_sha256":"a31aab7aecfb00c9ef84b9c26c93dbe15d630e83416a6d5cf38c04b6367fea34","published_sha":"e7c3e1b3fd7ab64bd07e19a2adc8bf7cedf2bde5","claim_state":"reconciled_captured_snapshot","issue_scope":"repository_open_issues_empty","pending_publish":false,"captured_at":"2026-08-06T02:14:03Z"}
```

Refresh kept: the active-goal ledger and its complete disposition map because they still own the 22-issue cohort reconciliation that `5.1.0` deliberately did not close.

Refresh non-claims: the `v5.1.0` push, release, public-release readback, and
local installed-tool refresh have occurred. No issue closure, no
direct-to-default hosted CI result, and no post-publication fresh-eye closeout
review have occurred for this backlog goal; the session that published `5.1.0`
was barred from spawning subagents, so that review is unproven, not waived.

## Next Session

1. Run the post-publication fresh-eye closeout review for `v5.1.0` on a host that permits subagent spawning — scope and reviewer rules in [fresh-eye-subagent-review.md](../skills/shared/references/fresh-eye-subagent-review.md); it is the one release-floor step this publication could not prove.
2. Work the 22-issue cohort disposition against the [execution ledger](../charness-artifacts/goals/2026-08-12-open-backlog-execution-ledger.md). Publication cleared the release boundary but authorized no issue closure.
3. Close the release-resume ergonomics gap named by the [claims-review contract](../skills/public/release/references/critique-boundary.md): at a `prepared-awaiting-claims-review` stop, `python3 skills/public/release/scripts/plan_release_run.py --repo-root . --detail` reports `inspect_only` and emits no resume command, so the five-flag invocation (including the version-bound `--critique-artifact`) must be reconstructed by hand. A wrong critique path fails as "standalone critique not satisfied" without naming the artifact that would bind.
4. Revisit [#528](https://github.com/corca-ai/charness/issues/528) only with its two owners: cmanki consumer declaration migration and the Charness quality-policy hook-discovery decision.
5. Use the [release contract](../docs/conventions/operating-contract.md) — the next push/release remains conditional on cohort disposition, retro, frozen verification, release critique, and independent readbacks.

## Discuss

- #527's brief remains the owner of any future product decision; its current OPEN deferral does not authorize implementation.

## References

- [Recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [Current quality record](../charness-artifacts/quality/latest.md)
