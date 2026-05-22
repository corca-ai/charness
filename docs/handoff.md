# charness Handoff

## Workflow Trigger

- Start every task-oriented pickup with `charness:find-skills`, then read this file,
  [quality latest](../charness-artifacts/quality/latest.md), and recent-lessons.md.
- Refresh live state before acting: `git status --short --branch`,
  `git log --oneline origin/main..HEAD`, and `gh issue list --state open --limit 50`.
- Before mutating code, generated exports, or validation behavior, read
  [implementation discipline](./conventions/implementation-discipline.md) and
  [operating contract](./conventions/operating-contract.md).
- Route external URLs or source links that should become repo working context through `gather`.

## Current State

- Current shipped release is `v0.7.10`; local `main` is in sync with origin.
- Bug-pattern sibling scan complete: `check-current-pointer-writes` scanner,
  symlink-safe helper, gitignore-aware standing Python scans, and the
  adapter-resolved hitl writer migration are all in place.
- Issue #190 (mutation regression on main) resolved: the sampler-spawned
  pytest probe was inheriting `MUTATION_BASE_SHA`/`MUTATION_HEAD_SHA` from the
  parent step env. The vulnerable test now scrubs both keys before subprocess.
- Mutation sampling/score, critique artifact, read-only quality, and shell
  markdown/link/secret/shell gates fail closed on discovery, manifest, or
  scan-staging failures.
- Release publishing fails closed when unreleased-path diff, real-host proof
  config, previous-tag base-ref lookup/fetch, or post-create verification fails.
- Usage episodes are configured but disabled; validation reports `disabled`.

## Next Session

1. Static `check-current-pointer-writes` scanner only catches string-literal
   `latest.md`/`latest.json` writes; future adapter-resolved writers must adopt
   the helper by convention. Scanner generalization stays deferred until a
   second adapter-resolved sibling appears.
2. PR CI mirroring of `./scripts/run-quality.sh --read-only` stays paused under
   the single-maintainer push model; document the absence as intended.
3. Keep usage episodes disabled until maintainers intentionally opt into local
   runtime capture.
4. Generated reference docs (cli-reference) move to `docs/generated/` with an
   enforced "GENERATED" header.

## Discuss

- Mutation selection lessons: sampler predicates must be at least as strict as
  fatal downstream closeout predicates, and runtime is executable mutants times
  selected test command cost, not just file count.
- Step-env leakage into nested test-command coverage probes is a class of bug;
  subprocess tests that build `env={**os.environ, ...}` must scrub
  workflow-controlled `MUTATION_*` keys before invoking the script under test.
- Watch list: Yarn Berry hook idiom; pnpm+lefthook stale snippets; `filelock`
  plus `pytest-xdist`; seed-cache LRU eviction; CLI docs ownership;
  release proof suppression.

## References

- [bug-pattern sibling scan](../charness-artifacts/debug/2026-05-21-bug-pattern-sibling-scan.md):
  current-pointer and gitignore sibling scan RCA and prevention.
- [mutation subprocess coverage](../charness-artifacts/debug/2026-05-21-mutation-subprocess-coverage.md):
  mutation #189 survivor and subprocess coverage RCA.
- [quality posture](../charness-artifacts/quality/latest.md) and
  [release surface](../charness-artifacts/release/latest.md): current state pointers.
