# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**. Bare
  `/handoff` runs chunked routing over handoff entries plus live open issues;
  `## Next Session` is sequencing judgment, not the full queue.
- Refresh: `git status --short --branch`,
  `git log --oneline origin/main..HEAD`, `gh issue list --state open --limit 50`.
- Before mutating code/exports/validation, read
  [implementation discipline](./conventions/implementation-discipline.md) and
  [operating contract](./conventions/operating-contract.md).

## Current State

- **[Next-queue goal (#342 + #343 + deferred proofs)](../charness-artifacts/goals/2026-06-10-342-343-adapter-schema-hook-lifecycle-deferred-proofs.md) COMPLETE, awaiting push.**
  Slice 1 (#342): integration-schema validation pulled into
  `validate_adapters.py` — `.agents/<name>-adapter.yaml` now jsonschema-validates
  against `integrations/<name>/manifest.schema.json` at every validate-adapters
  timing (commit 76909cc8). Slice 2 (#343): dangling-hook liveness in
  `session-capture status`, the multi-checkout posture decision documented,
  reconcile fan-out registry
  ([host_hook_registry.py](../scripts/host_hook_registry.py), commit 7f835610).
  Slice 3: deferred proofs consumed read-only — **quality-core first remote run
  GREEN** (run 27249353164), the edit-time #N-anchor guard observed BLOCKING a
  live scratch edit, **#335 confirmed bot-closed** (2026-06-08, workflow marker).
  Slice 4 (done-early continuation, #344): new-pool-module closeout advisory so
  the changed-line producer confirms instead of discovering (commit cd2618d1).
  Broad gate 73/0 on the final tree; producer/consumer 0 uncovered; four
  fresh-eye reviews; early-close report in the goal dir.
- Open issues (`gh`): **#184** (product metrics — operator `ideation` needed);
  #342/#343/#344 are open-but-carrier-staged (close on push).

## Next Session

- **Push the staged closeouts** (maintainer; `achieve` does not push):
  `origin/main..HEAD` carries the four work commits + the goal-closeout commit;
  `Closes #342/#343/#344` land on push. Pre-push gates are green (broad 73/0
  at 2026-06-10T13:11+09:00; changed-line coverage freshly produced +
  fingerprint-stamped post-cd2618d1, so the pre-push consumer trusts it).
- **quality-core PR-mirror job** has never run on a real PR (push/tag jobs are
  verified green) — its first PR-event execution is the remaining deferred
  proof; nothing to do until a PR exists.
- **#184** (product metrics) — product-level; needs `ideation`/`spec`, not a
  slice (third consecutive deliberate exclusion; should be its own goal).

## Discuss

- (Resolved 2026-06-10) **quality-core first remote run** — GREEN: run
  27249353164 (core job success, PR-mirror correctly skipped on push); the
  2026-06-10 next-queue goal consumed the deferred proof read-only. Only the
  PR-event mirror job remains unexecuted (needs a real PR).
- (Resolved 2026-06-10) **#335 auto-close** — closed by github-actions[bot]
  2026-06-08T17:23:42Z; the workflow marker owned it, no manual action.

## References

- [premerge-gate spec](../charness-artifacts/spec/mutation-changed-line-premerge-gate.md)
  (canonical; #335 Slice 3 surfacing entry),
  [preflight coverage spec](../charness-artifacts/spec/artifact-shape-preflight-coverage.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md),
  [quality latest](../charness-artifacts/quality/latest.md)
