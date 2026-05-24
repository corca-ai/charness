# charness Handoff

## Workflow Trigger

- Start every task-oriented pickup with `charness:find-skills`, then read this
  file, [quality latest](../charness-artifacts/quality/latest.md), and
  [recent lessons](../charness-artifacts/retro/recent-lessons.md).
- Refresh live state: `git status --short --branch`,
  `git log --oneline origin/main..HEAD`, and `gh issue list --state open --limit 50`.
- Before mutating code, generated exports, or validation behavior, read
  [implementation discipline](./conventions/implementation-discipline.md) and
  [operating contract](./conventions/operating-contract.md).
- Route external URLs through `gather`.

## Current State

- **Quality/critique sweep completed locally**: fresh-eye reviewers executed and
  fixes are committed for #211 plus sibling defects: RCA timestamp calendar
  validation, mutation-line continuation coverage without function-body
  overreach, current-pointer constant propagation with local-shadow guard, and
  `sync-support` exit-code alignment to `doctor_disposition`. A closeout-found
  standing-test economics race was also fixed so disappearing pytest temp paths
  do not crash inventory.
- **#211 Mutation test regression**: locally reproduced before fix; final
  committed mutation sampler `final5` reported 0 changed-line blockers and 0
  mutation-line coverage exclusions. GitHub currently reports #211 closed.
- **v0.7.12 release is published**: `main` and tag `v0.7.12` are on GitHub;
  release record is verified in [release latest](../charness-artifacts/release/latest.md).
- **Pytest temp blowup follow-up**: `run-quality.sh` now uses a repo-keyed
  pytest temp root under cache and [pyproject](../pyproject.toml) keeps only failed tmp-path
  sessions, so passed release runs should not retain 40GiB tmp trees.
- **Filed deferred issues from the sweep**: #212 RCA ledger `class_key`
  idempotency semantics; #213 `validate_packaging_install_surface.py` direct
  invocation needs repo import bootstrap; #214 structural CLI ergonomics
  registry/archetype inputs.
- **#184/#185 RCA ledger slices 1+2 landed earlier**. Open by design: numeric
  target is baseline-first, revisit after 2-4 weeks of live seed-excluded data;
  #185 LLM-as-judge and usage-episodes activation remain un-specced.

## Next Session

1. RCA ledger baseline observation: let live non-seed events accrue from
   `debug`/`issue`/`retro` closeouts. Revisit after 2-4 weeks with
   `python3 scripts/aggregate_rca_ledger.py`.
2. Deferred issue queue: #213 direct validator bootstrap first, then #212
   recorder idempotency contract, then #214 CLI ergonomics structural inventory.
3. If release-only tests fail after this change, inspect the repo-keyed cache
   temp root from `run-quality.sh` before widening the seed fixture budget.

## Discuss

- Changed-line and changed-path gates verified before commit are blind to the
  fix's own uncommitted files. Commit-then-verify is required for final mutation
  sample evidence.
- Current PR CI posture is intentional maintainer-local enforcement per
  [operating contract](./conventions/operating-contract.md); do not reopen unless outside PRs
  become recurring.
- Watch: Yarn Berry hooks; pnpm+lefthook stale snippets; `filelock`+`pytest-xdist`;
  seed-cache LRU eviction; release proof suppression; D21-D26 reopen watchlist;
  2 pre-existing ruff errors in vendored notion-to-md remain out of scope.

## References

- [quality posture](../charness-artifacts/quality/latest.md),
  [debug artifact](../charness-artifacts/debug/latest.md),
  [release surface](../charness-artifacts/release/latest.md),
  [usage-episodes spec](../charness-artifacts/spec/usage-episodes-h-lam-t-completion.md)
