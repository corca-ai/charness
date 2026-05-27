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

- **v0.9.0 is published and verified** on `main` + tag; no version drift. It
  shipped the public `achieve` skill, the #223 duplicate-test-pressure contract,
  and a `local-linux-aarch64-4cpu` runtime budget profile.
- **#225 RESOLVED** (closed): pre-push gate is deterministic again; honest pushes
  from this host no longer need `--no-verify`. `run-quality.sh` now hard-fails if
  the pytest basetemp ever resolves inside the repo. See
  [debug artifact](../charness-artifacts/debug/2026-05-27-issue-225-prepush-nondeterminism.md).
- **#224/#219 RESOLVED pending scheduled auto-close**: the Cosmic Ray mutant
  filter recognized PEP 604 annotation-union `|` equivalents only on single-line
  `def` lines, so 212 equivalent mutants across 81 files leaked into the score.
  Fix rewrote `filter_cosmic_ray_mutants.py` to detect them by AST position; the
  mutation workflow auto-closes both on the next green scheduled run (do not
  hand-close). See
  [debug artifact](../charness-artifacts/debug/2026-05-27-issue-224-219-mutation-annotation-filter.md).

## Next Session

1. **#226** (Codex fresh-eye reviewer model policy) and **#227** (default
   survey/turn-policy reliability) are the newest open issues, filed after the
   prior handoff; #227 is a user-requested retro whose scope is partly in ceal.
2. **#184/#185** remain deferred product/AI-ML direction work.
3. **Mutation-gate residuals** (deferred from the #224/#219 fix; pick up if the
   scheduled gate goes red, not yet filed as issues):
   - Real test-strength survivors #224 named (`build_payload` comparisons,
     worktree `timeout` numbers) the filter fix does not touch — re-confirm
     against current HEAD before investing; they may be stale.
   - `Annotated[...]` metadata over-skip: the AST detector skips any `|` in an
     annotation subtree, including `Annotated` metadata (runtime-observable, so
     not equivalent). Latent — zero `Annotated` usage today; a pin test
     documents it. Exclude `Annotated` metadata before adopting that pattern.

## Discuss

- Current PR CI posture is intentional maintainer-local enforcement per
  [operating contract](./conventions/operating-contract.md); do not reopen unless
  outside PRs become recurring.
- Watch: Yarn Berry hooks; pnpm+lefthook stale snippets; `filelock`+`pytest-xdist`;
  seed-cache LRU eviction; release proof suppression.

## References

- [quality posture](../charness-artifacts/quality/latest.md), [debug artifact](../charness-artifacts/debug/latest.md), [release surface](../charness-artifacts/release/latest.md)
