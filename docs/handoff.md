# charness Handoff

## Workflow Trigger

- Start every task-oriented pickup with `charness:find-skills`, then read this file, [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md), and [charness-artifacts/retro/recent-lessons.md](../charness-artifacts/retro/recent-lessons.md).
- Refresh live state before acting: `git status --short --branch`, `git log --oneline origin/main..HEAD`, and `gh issue list --state open --limit 50 --json number,title,labels,createdAt,url`.
- Before mutating code, scripts, docs, skills, generated exports, or validation behavior, read [docs/conventions/implementation-discipline.md](./conventions/implementation-discipline.md). Before closeout, read [docs/conventions/operating-contract.md](./conventions/operating-contract.md).
- Route external URLs or source links that should become repo working context through `gather` before using them as durable input.

## Current State

- Local `main` includes `9175faa` plus the mutation semantics fix slice (not yet pushed at the time this handoff was edited). Prior session closed #180/#181/#182; #183 remains open until the pushed workflow run proves the new semantics.
- Public release `v0.7.6`. No version bump pending (release-adapter does not require bump per fix bundle).
- Latest inspected mutation runs:
  - `26137796207` (head_sha `594221a`, 2h 30m): `Run mutation` step success, summary `executed=1093/1821`, `killed=0`, `survived=872`, `status=FAIL-incomplete`; non-skipped completion is 54.6%, not the reported 60.0%, because skipped mutants are counted as executed.
  - `26141783678` (head_sha `594221a`, schedule, 2h 30m): `Run mutation` step success, summary `executed=938/1499`, `killed=91`, `survived=803`, `score=10.2%`, `status=FAIL-incomplete`; all killed mutants were in [scripts/repo_layout.py](../scripts/repo_layout.py), the only sampled module covered by `tests/control_plane` in the local coverage probe.
  These runs predate the fix. The current local fix makes [scripts/sample_mutation_files.py](../scripts/sample_mutation_files.py) collect coverage for the declared Cosmic Ray test command, samples only covered files, records changed files excluded by the coverage filter, filters uncovered mutation lines after `cosmic-ray init`, separates coverage scope gaps from native Cosmic Ray no-mutation-possible results, excludes skipped mutants from completion, requires per-file completion for `PASS-partial`, treats any non-timeout pending mutants as `FAIL-incomplete`, and lowers `mutation_testing.max_files` to 5.

## Next Session

1. Push the local fix commit, then dispatch with `gh workflow run mutation-tests.yml --ref main`.
2. Watch the next summary. It should show a sample drawn from the covered `tests/control_plane` mutation pool, changed files excluded by the coverage filter in `sample.md`, `Scope gaps (uncovered sampled mutants)` separated from score, `executed` over executable mutants only, and no `PASS-partial` unless each sampled file meets the per-file completion floor.
3. If the run still times out before the per-file floor with `max_files=5`, lower `mutation_testing.max_files` again or randomize/stratify Cosmic Ray work order before allowing `PASS-partial`.

## Discuss

- Six prior critique passes (premortem, code, release, broad, fifth deep, sixth claim-vs-behavior) all signed off without measuring the workflow end-to-end. The systemic test-command bug only surfaced on first real run. Lesson: infrastructure-shaped critique needs at least one measurement, not just reading.
- Watch list (deferred): Yarn Berry hook command idiom; pnpm+lefthook stale snippets in [docs/worktree-prepare.md](./worktree-prepare.md) and [skills/public/setup/references/bootstrap-seams.md](../skills/public/setup/references/bootstrap-seams.md); promote `filelock` + `pytest-xdist` into [pyproject.toml](../pyproject.toml); `sys.path.insert` sibling-import pattern routing through `runtime_bootstrap.import_repo_module`; seed-cache LRU eviction.

## References

- [charness-artifacts/debug/latest.md](../charness-artifacts/debug/latest.md): mutation execution and score semantics context, observed facts, implemented local remediation, verification plan.
- [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md): current quality posture.
- [charness-artifacts/release/latest.md](../charness-artifacts/release/latest.md): current release surface.
- [.github/workflows/mutation-tests.yml](../.github/workflows/mutation-tests.yml): the workflow whose `26137796207` run measured the mismatch.
