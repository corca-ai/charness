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

- **[Post-push goal (lane verification + settings scan + PR-mirror)](../charness-artifacts/goals/2026-06-10-postpush-verification-deleted-checkout-scan-pr-mirror.md) COMPLETE, awaiting push.**
  Slice 1: the 2026-06-10 push/release lane verified read-only —
  #342/#343/#344 CLOSED via carriers (`verify-closeout` status=verified),
  post-push quality-core green (27254637832), installed plugin 0.37.0 ==
  released tag v0.37.0. Slice 2: deleted-checkout settings scan — the #343
  blind spot closed; `session-capture status` gains a `settings_scan` section
  flagging host-settings entries whose known charness hook basename points at
  a missing path (commit 011a931f; basename set derived from owning modules'
  constants). Slice 3: **quality-core PR-mirror first real execution** — PR
  345 (F4 seeded-repo e2e + minimal pool-file docstring touch) ran the mirror
  job's full real path (run 27258023056, job 80496728903, success 9m51s,
  changed_pool_files non-empty) and merged green as 39ff5432. Bundle: broad
  73/0, locked producer PASS, consumer 0 uncovered; three fresh-eye reviews +
  disposition review; early-close report in the goal dir.
- Open issues (`gh`): **#184** (product metrics — operator `ideation`
  needed, fourth exclusion); **#346** (per-goal metric scoping for the
  host-log probe on Claude hosts — recurs-class, filed by this goal's retro).

## Next Session

- **Push the staged closeouts** (maintainer; `achieve` does not push):
  `origin/main..HEAD` carries the goal's three work/record commits + the
  closeout commit (local main is rebased onto the merged 39ff5432); pre-push
  gates green (broad 73/0; coverage produced + fingerprint-stamped at the
  locked closeout, consumer ok=true).
- **Deferred proof:** the next green scheduled `mutation-tests.yml` run on
  39ff5432 or later (the 07:17Z slot was cron-skipped; latest green is
  27253892006 on pre-push 58cc749a). One `gh run list` check.
- **#346** — recurs-class capability fix in retro/achieve helper scripts;
  candidate next goal slice.
- **#184** (product metrics) — product-level; needs `ideation`/`spec`, not a
  slice (fourth consecutive deliberate exclusion; should be its own goal).

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
