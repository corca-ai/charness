# charness Handoff

## Workflow Trigger

- Start every task-oriented pickup with `charness:find-skills`, then read this file, [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md), and [charness-artifacts/retro/recent-lessons.md](../charness-artifacts/retro/recent-lessons.md).
- Refresh live state before acting: `git status --short --branch`, `git log --oneline origin/main..HEAD`, and `gh issue list --state open --limit 50 --json number,title,labels,createdAt,url`.
- Before mutating code, scripts, docs, skills, generated exports, or validation behavior, read [docs/conventions/implementation-discipline.md](./conventions/implementation-discipline.md). Before closeout, read [docs/conventions/operating-contract.md](./conventions/operating-contract.md).
- Route external URLs or source links that should become repo working context through `gather` before using them as durable input.

## Current State

- `main` at `594221a` (2026-05-20). Prior session closed #180/#181/#182 across six commits (`9e0ac1c`, `0c7cb1a`, `232a998`, `4f629b7`, `e385254`, `594221a`); #183 **still OPEN** because the mutation workflow now runs end-to-end but reports `score=0%` due to a separate systemic bug — see [charness-artifacts/debug/latest.md](../charness-artifacts/debug/latest.md).
- Public release `v0.7.6`. No version bump pending (release-adapter does not require bump per fix bundle).
- Latest mutation run `26137796207` (head_sha `594221a`, 2h 30m): `Run mutation` step success, `executed=1093/1821`, `killed=0`, `survived=872`, `status=FAIL-incomplete`. All four #183 fix layers (filelock install, exec timeout `check=False`, dump atomic rename, partial-run scoring) verified by this run; the remaining blocker is the test-command vs sample-module mismatch described in the debug artifact.

## Next Session

1. Read [charness-artifacts/debug/latest.md](../charness-artifacts/debug/latest.md) (mutation test-command mismatch, two remediation paths).
2. Pick Option A (recommended): edit [cosmic-ray.toml](../cosmic-ray.toml) test-command to full pytest suite, lower `mutation_testing.max_files` in [.agents/quality-adapter.yaml](../.agents/quality-adapter.yaml) from 10 to 5. Premortem critique via subagent before push (changes mutation-testing semantics).
3. Push, dispatch with `gh workflow run mutation-tests.yml --ref main`, watch for a non-zero score on the next run; #183 auto-closes when status is PASS or PASS-partial.
4. If `executed_ratio < 0.75` on the full-suite path, tune `PARTIAL_RUN_COMPLETION_FLOOR` in [scripts/check_mutation_score.py](../scripts/check_mutation_score.py) to the measured value and update the partial-run boundary tests.

## Discuss

- Six prior critique passes (premortem, code, release, broad, fifth deep, sixth claim-vs-behavior) all signed off without measuring the workflow end-to-end. The systemic test-command bug only surfaced on first real run. Lesson: infrastructure-shaped critique needs at least one measurement, not just reading.
- Watch list (deferred): Yarn Berry hook command idiom; pnpm+lefthook stale snippets in [docs/worktree-prepare.md](./worktree-prepare.md) and [skills/public/setup/references/bootstrap-seams.md](../skills/public/setup/references/bootstrap-seams.md); promote `filelock` + `pytest-xdist` into [pyproject.toml](../pyproject.toml); `sys.path.insert` sibling-import pattern routing through `runtime_bootstrap.import_repo_module`; seed-cache LRU eviction.

## References

- [charness-artifacts/debug/latest.md](../charness-artifacts/debug/latest.md): full mutation test-command mismatch context, observed facts, two-path remediation, verification plan.
- [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md): current quality posture.
- [charness-artifacts/release/latest.md](../charness-artifacts/release/latest.md): current release surface.
- [.github/workflows/mutation-tests.yml](../.github/workflows/mutation-tests.yml): the workflow whose `26137796207` run measured the mismatch.
