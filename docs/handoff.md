# Charness Handoff

## Workflow Trigger

- Continue the active `achieve` goal. **Three release residues are repaired and
  committed locally but NOT closed**: #613, #610, and #611 each took two bounded
  review rounds, carry `draft_verified` carriers with per-issue behavioral
  verdicts, and are committed as `503545d7`, `2eaa887b`, `e455c338`. Their
  `Closes #N` keywords take effect only on a push, and no push grant exists, so
  GitHub state is unchanged. Ten cohort issues remain CLOSED and read back; #584
  is unchanged on the Umbrella Closure Contract.

## Continuation Capability

- [Open-backlog goal](../charness-artifacts/goals/2026-08-12-resolve-open-quality-and-trust-backlog.md) — owns the fixed 22-issue cohort, active frame, publication boundary, and slice log.
- [Execution ledger](../charness-artifacts/goals/2026-08-12-open-backlog-execution-ledger.md) — owns per-issue premise, local proof, tracker carrier, revisit state, and Late Arrivals. **Read it for any per-row question.**

## Current State

- [Two-round critique](../charness-artifacts/critique/2026-08-13-release-claims-path-record-and-notes-two-round-critique.md) — holds what both rounds found on #613/#610/#611, the three counterweight declines, and the reviewer/boundary evidence.
- [Proof-surface repair retro](../charness-artifacts/retro/2026-08-13-proof-surface-repair-retro.md) — holds the `skipped-is-not-passed` lesson, now promoted to the [operating contract](./conventions/operating-contract.md#external-side-effect-discipline) because the rolling digest ranked it out of its slots.
- Local verification on `e455c338`: `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --include-release-only` (8959 passed) and `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root .` (clean).
- [Release `5.1.0` observables probe](../charness-artifacts/probe/2026-08-13-v5.1.0-post-publication-observables.md) — holds the credential-free REST readback behind the published-release claim; it closed no issues.
- [Goal progress critique](../charness-artifacts/critique/2026-08-12-goal-progress-frame-and-ledger-critique.md) — holds why local proof is not GitHub closure.

Historical immutable publish-state claim — this captures the completed
2026-08-06 snapshot only; it does not describe this active backlog or authorize
issue closure, push, or release.

<!-- charness-publish-state-claim:post-push-operational-proof -->
```json
{"kind":"charness.publish-state-claim","schema_version":1,"block_id":"post-push-operational-proof","manifest_path":"charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json","manifest_sha256":"a31aab7aecfb00c9ef84b9c26c93dbe15d630e83416a6d5cf38c04b6367fea34","published_sha":"e7c3e1b3fd7ab64bd07e19a2adc8bf7cedf2bde5","claim_state":"reconciled_captured_snapshot","issue_scope":"repository_open_issues_empty","pending_publish":false,"captured_at":"2026-08-06T02:14:03Z"}
```

Refresh kept: the unpushed-carrier state, because it is the only thing standing
between three finished repairs and their tracker closure, and the execution
ledger, because it still owns the 22-issue cohort reconciliation.

Refresh non-claims. Nothing is pushed and no issue changed state on GitHub, so all
three of #613, #610, and #611 are repaired and committed, not closed. No release
was cut. No
consumer repo with a non-default adapter `output_dir` was exercised — the claims
path behaviour is proven against the exported plugin copy and repo fixtures only.
The `--close-issue` half of #611 stays unenforced on the prepared-claims-review
lane, and the notes preflight keys on a filename convention its helper cannot see
through; both are recorded in the critique's Counterweight Pass.

## Next Session

1. Ask the maintainer for a phase-scoped push grant, then push and run
   `python3 "$SKILL_DIR/scripts/issue_tool.py" verify-closeout --repo corca-ai/charness --number 613 --carrier direct-commit --expect-state CLOSED` for each of [#613](https://github.com/corca-ai/charness/issues/613), [#610](https://github.com/corca-ai/charness/issues/610), and [#611](https://github.com/corca-ai/charness/issues/611); confirm remote CI through a channel distinct from the push.
2. [#584](https://github.com/corca-ai/charness/issues/584) stays held on the ledger's Umbrella Closure Contract, untouched this session.
3. The eleven other open cohort rows hold tracker-visible non-closures with owners and revisit triggers in the [execution ledger](../charness-artifacts/goals/2026-08-12-open-backlog-execution-ledger.md).
4. The next release stays conditional on cohort disposition, retro, frozen verification, release critique, and independent readbacks per the [operating contract](./conventions/operating-contract.md).

## Discuss

- #527's brief remains the owner of any future product decision; its current OPEN deferral does not authorize implementation.
- Whether the three counterweight declines in this session's critique deserve their own tracker rows or stay recorded-only.

## References

- [Recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [Current quality record](../charness-artifacts/quality/latest.md)
