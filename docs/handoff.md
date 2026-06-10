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

- **[Post-push verification + #349 goal](../charness-artifacts/goals/2026-06-10-postpush-verify-346-348-closed-349-hitl-boundary.md) COMPLETE, awaiting push.**
  Slice 1: third 2026-06-10 push + v0.39.0 release lane verified read-only
  (quality-core 27275145498 green on pushed HEAD 768ded84; #346/#348
  `verify-closeout` verified CLOSED via carriers 84dc1db3/a65a232c;
  installed plugin 0.39.0 == tag and installed SHA == pushed HEAD via live
  probe). Slice 2 (#349): hitl's reviewed core now names the reciprocal
  `hotl` boundary (intro line; Bootstrap defaults compressed 7->2 under
  the 200-line ceiling — 196/200, preserve claim, mirrors byte-synced;
  carrier 763653c7 `Closes #349` staged, `draft_verified`). Bundle: broad
  73/0, changed-line consumer "no eligible files", two slice-level
  fresh-eye reviews + recurrence resolution critique + disposition review
  ACCEPT-WITH-CORRECTIONS (all corrections were closeout bookkeeping).
- Open issues (`gh`): **#184** (product metrics — operator `ideation`
  needed, SIXTH exclusion); **#350** (NEW, from #349's resolution
  critique: create-skill propagation step silent on the at-cap
  adjacent-skill outcome; five skills sit at exactly 200/200 — proposes a
  checklist line + near-cap `>=195/200` preflight warning).

## Next Session

- **Push the staged closeouts** (maintainer; `achieve` does not push):
  `origin/main..HEAD` carries 763653c7 (`Closes #349`, `draft_verified`)
  plus the goal closeout commit; verify #349 flips CLOSED after the push
  (`issue_tool.py verify-closeout`).
- **Deferred proof to consume:** the first scheduled `mutation-tests.yml`
  run whose headSha is 768ded84 or later (none had fired by goal
  closeout; latest green 27270609532 covers pre-push fd3c2c6c) — plus the
  post-push quality-core run on the new HEAD.
- **#350** — small bounded slice: create-skill at-cap checklist line +
  optional near-cap preflight warning (recurrence guards for the #349
  class).
- **ceal-side consumption of `hotl`** — named in #348 as the consuming
  repo's follow-up; not charness work, but worth surfacing to the
  operator.
- **#184** (product metrics) — product-level; needs `ideation`/`spec`,
  not a slice (sixth consecutive deliberate exclusion; should be its own
  goal).

## Discuss

## References

- [premerge-gate spec](../charness-artifacts/spec/mutation-changed-line-premerge-gate.md)
  (canonical), [preflight coverage spec](../charness-artifacts/spec/artifact-shape-preflight-coverage.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md),
  [quality latest](../charness-artifacts/quality/latest.md)
