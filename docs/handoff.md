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

- **Quality/critique sweep completed locally**: #211 and sibling fixes landed
  for RCA timestamp validation, mutation-line continuation coverage,
  current-pointer constants, `sync-support` exit codes, and disappearing pytest
  temp paths. GitHub reports #211 closed.
- **v0.7.12 release is published**: `main` and tag `v0.7.12` are on GitHub;
  release record is verified in [release latest](../charness-artifacts/release/latest.md).
- **Pytest temp blowup follow-up**: `run-quality.sh` now uses a repo-keyed
  pytest temp root under cache and [pyproject](../pyproject.toml) keeps only failed tmp-path
  sessions, so passed release runs should not retain 40GiB tmp trees.
- **Deferred sweep issues are closed on GitHub**: #212 RCA ledger recorder
  now treats duplicate `source` + `event_kind` + `class_key` appends as success
  no-ops; #213 `validate_packaging_install_surface.py` bootstraps repo imports
  without `PYTHONPATH`; #214 adds advisory CLI ergonomics registry/archetype
  inputs and a standing `run-quality` advisory inventory phase.
- **#215 Mutation test regression is closed on GitHub**: mutation coverage
  sampling now scopes generated coverage rcfiles to the repo root, and
  survivor-adjacent tests pin runtime profile, setup parent creation, and
  GitHub Actions JSON formatting contracts.
- **#184/#185 RCA ledger slices 1+2 landed earlier**. Open by design: numeric
  target is baseline-first, revisit after 2-4 weeks of live seed-excluded data;
  #185 LLM-as-judge and usage-episodes activation remain un-specced.

## Next Session

1. Publish the next patch release after the #215 closeout if not already done.
2. RCA ledger baseline observation: let live non-seed events accrue from
   `debug`/`issue`/`retro` closeouts. Revisit after 2-4 weeks with
   `python3 scripts/aggregate_rca_ledger.py`.
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
  seed-cache LRU eviction; release proof suppression; D21-D26 reopen watchlist.

## References

- [quality posture](../charness-artifacts/quality/latest.md), [debug artifact](../charness-artifacts/debug/latest.md), [release surface](../charness-artifacts/release/latest.md)
