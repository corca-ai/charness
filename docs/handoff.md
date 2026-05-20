# charness Handoff

## Workflow Trigger

- Start every task-oriented pickup with `charness:find-skills`, then read this file, [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md), and [charness-artifacts/retro/recent-lessons.md](../charness-artifacts/retro/recent-lessons.md).
- Refresh live state before acting: `git status --short --branch`, `git log --oneline origin/main..HEAD`, and `gh issue list --state open --limit 50 --json number,title,labels,createdAt,url`.
- Before mutating code, scripts, docs, skills, generated exports, or validation behavior, read [docs/conventions/implementation-discipline.md](./conventions/implementation-discipline.md). Before closeout, read [docs/conventions/operating-contract.md](./conventions/operating-contract.md).
- Route external URLs or source links that should become repo working context through `gather` before using them as durable input.

## Current State

- `main` at `594221a` (2026-05-20). Prior session closed #180/#181/#182 across six commits (`9e0ac1c`, `0c7cb1a`, `232a998`, `4f629b7`, `e385254`, `594221a`); #183 **still OPEN** because the mutation workflow now runs end-to-end but its execution scope and score semantics are invalid — see [charness-artifacts/debug/latest.md](../charness-artifacts/debug/latest.md).
- Public release `v0.7.6`. No version bump pending (release-adapter does not require bump per fix bundle).
- Latest inspected mutation runs:
  - `26137796207` (head_sha `594221a`, 2h 30m): `Run mutation` step success, summary `executed=1093/1821`, `killed=0`, `survived=872`, `status=FAIL-incomplete`; non-skipped completion is 54.6%, not the reported 60.0%, because skipped mutants are counted as executed.
  - `26141783678` (head_sha `594221a`, schedule, 2h 30m): `Run mutation` step success, summary `executed=938/1499`, `killed=91`, `survived=803`, `score=10.2%`, `status=FAIL-incomplete`; all killed mutants were in [scripts/repo_layout.py](../scripts/repo_layout.py), the only sampled module covered by `tests/control_plane` in the local coverage probe.
  All four #183 resilience layers (filelock install, exec timeout `check=False`, dump atomic rename, partial-run scoring) let the workflow produce artifacts, but the remaining blocker is broader than a 0% score: the sampler mutates `scripts/*.py` while [cosmic-ray.toml](../cosmic-ray.toml) runs only `tests/control_plane`, and the summary treats unexercised sampled modules as ordinary survived mutants.

## Next Session

1. Read [charness-artifacts/debug/latest.md](../charness-artifacts/debug/latest.md) (mutation execution/test-scope mismatch, misleading `no_tests`, skipped-mutant completion inflation, and partial-run representativeness).
2. Do **not** land the prior Option A as written. Local measurements on 2026-05-20: `python3 -m pytest -q tests/control_plane` took 14.27s, while `python3 -m pytest -q` took 344.22s; Cosmic Ray repeats the command per mutant and [cosmic-ray.toml](../cosmic-ray.toml) sets per-mutant `timeout = 300.0`, so full pytest is not viable under the current runner/sample size.
3. Implement a scope-owned strategy instead: either filter by per-line/per-mutant coverage for the declared test command, or make [scripts/sample_mutation_files.py](../scripts/sample_mutation_files.py) rewrite both `module-path` and a measured per-sample test command mapping. Update [scripts/check_mutation_score.py](../scripts/check_mutation_score.py) so `No tests (scope gap)` is based on sampled mutation coverage, not only Cosmic Ray `WorkerOutcome.NO_TEST`.
4. Fix partial-run evaluation: exclude `skipped` mutants from completion numerator/denominator, and do not allow `PASS-partial` unless every sampled file has attempted non-skipped mutants plus a per-sampled-file completion floor, or the workflow randomizes/stratifies work order with a declared floor.
5. Push, dispatch with `gh workflow run mutation-tests.yml --ref main`, and require the next summary to show matching sample/test scope plus a non-misleading completion ratio before treating #183 as recoverable.

## Discuss

- Six prior critique passes (premortem, code, release, broad, fifth deep, sixth claim-vs-behavior) all signed off without measuring the workflow end-to-end. The systemic test-command bug only surfaced on first real run. Lesson: infrastructure-shaped critique needs at least one measurement, not just reading.
- Watch list (deferred): Yarn Berry hook command idiom; pnpm+lefthook stale snippets in [docs/worktree-prepare.md](./worktree-prepare.md) and [skills/public/setup/references/bootstrap-seams.md](../skills/public/setup/references/bootstrap-seams.md); promote `filelock` + `pytest-xdist` into [pyproject.toml](../pyproject.toml); `sys.path.insert` sibling-import pattern routing through `runtime_bootstrap.import_repo_module`; seed-cache LRU eviction.

## References

- [charness-artifacts/debug/latest.md](../charness-artifacts/debug/latest.md): full mutation test-command mismatch context, observed facts, two-path remediation, verification plan.
- [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md): current quality posture.
- [charness-artifacts/release/latest.md](../charness-artifacts/release/latest.md): current release surface.
- [.github/workflows/mutation-tests.yml](../.github/workflows/mutation-tests.yml): the workflow whose `26137796207` run measured the mismatch.
