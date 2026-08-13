# Charness Handoff

## Workflow Trigger

- Continue the active `achieve` goal. **#613, #610, and #611 are CLOSED and read
  back** — each took two bounded review rounds, closed through the `issue` floor
  with a behavioral verdict via the exported plugin copy, and `verify-closeout`
  returned `verified` for all three, reconciled against an independent
  `gh issue list` (16 open, none of the three). `e7d87764` is pushed with remote
  CI green on BOTH jobs. #584 is unchanged on the Umbrella Closure Contract;
  #614 remains unresolved. #615 is locally repaired with a direct-commit
  carrier, but remains OPEN until an explicitly authorized push and readback.

## Continuation Capability

- [Open-backlog goal](../charness-artifacts/goals/2026-08-12-resolve-open-quality-and-trust-backlog.md) — owns the fixed 22-issue cohort, active frame, publication boundary, and slice log.
- [Execution ledger](../charness-artifacts/goals/2026-08-12-open-backlog-execution-ledger.md) — owns per-issue premise, local proof, tracker carrier, revisit state, and Late Arrivals. **Read it for any per-row question.**

## Current State

- [Two-round critique](../charness-artifacts/critique/2026-08-13-release-claims-path-record-and-notes-two-round-critique.md) — holds what both rounds found on #613/#610/#611, the three counterweight declines, and the reviewer/boundary evidence.
- [Session retro](../charness-artifacts/retro/2026-08-13-release-residues-and-unbounded-caches-retro.md) — holds why the push took five attempts, and the environment-not-test lesson behind it.
- [#614](https://github.com/corca-ai/charness/issues/614) — holds the unbounded-cache class: the seed cache is fixed and pruned, `pytest-tmp` and `reports/mutation` are recorded and unfixed.
- [#615 debug](../charness-artifacts/debug/2026-08-13-issue-615-focused-changed-line-false-clean.md) and [two-round critique](../charness-artifacts/critique/2026-08-13-issue-615-focused-marker-parity.md) — the focused lane widened broad marker policy with `release_only`; the repair removes that widening, and the historical range blocks on the exact reported lines.
- [Proof-surface repair retro](../charness-artifacts/retro/2026-08-13-proof-surface-repair-retro.md) — holds the `skipped-is-not-passed` lesson, now in the [operating contract](./conventions/operating-contract.md#external-side-effect-discipline) because the rolling digest ranked it out of its slots.
- Verification on `e7d87764`: pre-push gate `91 passed, 0 failed` and remote CI green on both jobs; re-run with `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --include-release-only` (8959 passed). The current open set is `gh issue list --repo corca-ai/charness --state open`.
- [Release `5.1.0` observables probe](../charness-artifacts/probe/2026-08-13-v5.1.0-post-publication-observables.md) — holds the credential-free REST readback behind the published-release claim; it closed no issues.

Historical immutable publish-state claim — this captures the completed
2026-08-06 snapshot only; it does not describe this active backlog or authorize
issue closure, push, or release.

<!-- charness-publish-state-claim:post-push-operational-proof -->
```json
{"kind":"charness.publish-state-claim","schema_version":1,"block_id":"post-push-operational-proof","manifest_path":"charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json","manifest_sha256":"a31aab7aecfb00c9ef84b9c26c93dbe15d630e83416a6d5cf38c04b6367fea34","published_sha":"e7c3e1b3fd7ab64bd07e19a2adc8bf7cedf2bde5","claim_state":"reconciled_captured_snapshot","issue_scope":"repository_open_issues_empty","pending_publish":false,"captured_at":"2026-08-06T02:14:03Z"}
```

Refresh kept: the execution ledger, because it still owns the 22-issue cohort
and late-arrival reconciliation, and #614, because two of its named caches are
still unbounded. #615 stays visible until its local carrier is pushed and its
GitHub state is read back.

Refresh non-claims. No release was cut and no tag moved. No consumer repo with a
non-default adapter `output_dir` was exercised — the claims-path behaviour is
proven against the exported plugin copy and repo fixtures only. The
`--close-issue` half of #611 stays unenforced on the prepared-claims-review lane,
and the notes preflight keys on a filename convention its helper cannot see
through; both are in the critique's Counterweight Pass. #614 is filed and
unresolved: only the seed cache is bounded, while `pytest-tmp` (5.5 GB, leaks a
basetemp per failing run by design) and `reports/mutation` (2.2 GB) are recorded
and untouched. #615 has local runtime and review proof only: no hosted CI,
push, GitHub closure, or installed-consumer readback is claimed.

## Next Session

1. Do not report [#615](https://github.com/corca-ai/charness/issues/615) closed from its local carrier. Under a new phase-scoped grant, push it, observe hosted CI through a distinct channel, and run `verify-closeout --expect-state CLOSED`; without that grant, leave it OPEN.
2. Resolve [#614](https://github.com/corca-ai/charness/issues/614)'s remaining members: `pytest-tmp` keeps the most recent N failed basetemps rather than cleaning up on failure (the retention is deliberate), and `reports/mutation` has no policy at all.
3. [#584](https://github.com/corca-ai/charness/issues/584) stays held on the ledger's Umbrella Closure Contract, untouched this session.
4. The eleven other open cohort rows hold tracker-visible non-closures with owners and revisit triggers in the [execution ledger](../charness-artifacts/goals/2026-08-12-open-backlog-execution-ledger.md).
5. The next release stays conditional on cohort disposition, retro, frozen verification, release critique, and independent readbacks per the [operating contract](./conventions/operating-contract.md).

## Discuss

- #527's brief remains the owner of any future product decision; its current OPEN deferral does not authorize implementation.
- Whether the three counterweight declines in this session's critique deserve their own tracker rows or stay recorded-only.

## References

- [Recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [Current quality record](../charness-artifacts/quality/latest.md)
