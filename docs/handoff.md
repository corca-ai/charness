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

- **Quality/critique sweep in progress**: fresh-eye reviewers executed. Self-fixes
  are staged for #211 plus sibling defects: RCA timestamp calendar validation,
  mutation-line continuation coverage without function-body overreach,
  current-pointer constant propagation with local-shadow guard, and
  `sync-support` exit-code alignment to `doctor_disposition`. A closeout-found
  standing-test economics race was also fixed so disappearing pytest temp paths
  do not crash inventory.
- **#211 Mutation test regression**: locally reproduced before fix; current fix
  has targeted tests green. Important closeout step: after committing, rerun the
  mutation sampler against a window that includes the committed fix because
  `MUTATION_HEAD_SHA=HEAD` ignores uncommitted work.
- **Filed deferred issues from the sweep**: #212 RCA ledger `class_key`
  idempotency semantics; #213 `validate_packaging_install_surface.py` direct
  invocation needs repo import bootstrap; #214 structural CLI ergonomics
  registry/archetype inputs.
- **#184/#185 RCA ledger slices 1+2 landed earlier**. Open by design: numeric
  target is baseline-first, revisit after 2-4 weeks of live seed-excluded data;
  #185 LLM-as-judge and usage-episodes activation remain un-specced.

## Next Session

1. Finish this sweep closeout if not already committed:
   - validate debug/quality artifacts and seam index;
   - run `python3 scripts/run_slice_closeout.py --repo-root .` if changed
     surfaces require it;
   - commit, then rerun the #211 mutation sample with committed HEAD;
   - run `./scripts/run-quality.sh --read-only`;
   - close or comment #211 only after pushed/verified if remote closeout is in
     scope.
2. RCA ledger baseline observation: let live non-seed events accrue from
   `debug`/`issue`/`retro` closeouts. Revisit after 2-4 weeks with
   `python3 scripts/aggregate_rca_ledger.py`.
3. Deferred issue queue: #212 before changing recorder idempotency; #213 direct
   validator bootstrap; #214 CLI ergonomics structural inventory.

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
