# charness Handoff

## Workflow Trigger

- Start every task-oriented pickup with `charness:find-skills`, then read this file,
  [quality latest](../charness-artifacts/quality/latest.md), and recent-lessons.md.
- Refresh live state: `git status --short --branch`,
  `git log --oneline origin/main..HEAD`, and `gh issue list --state open --limit 50`.
- Before mutating code, generated exports, or validation behavior, read
  [implementation discipline](./conventions/implementation-discipline.md) and
  [operating contract](./conventions/operating-contract.md).
- Route external URLs through `gather`.

## Current State

- `main` at `4bc44d3`. Closed this session: **#195** (`a37ab31` entry-guard
  mutation skip in `filter_cosmic_ray_mutants.py` + sampler mirror),
  **#197** (`3e59152` RCA — gate already at
  `validate_packaging_install_surface.py:130`; commit names the sync
  script in the drift message and locks the contract), **#196**
  (`4bc44d3` corpus normalization: 18 Repo-root + 6 Emit-JSON role-
  specific, 7 subparser helps added, Repository→Repo corpus-wide).
- Filed: **#198** (eval_registry sampler nodeid gap;
  `test_eval_registry_scenarios_are_immutable_contract_records` exists
  but sampler did not pick it for `eval_registry.py:6`).
- 1차 조사 메모 posted to **#185** and **#184**; full ideation deferred.

## Next Session

1. **Ideation for #185 + #184**: spawn `charness:ideation` against the
   1차 메모. Top-3 candidates: (a) 'symptom→root-cause shift' counter (#197
   is the exemplar), (b) LLM-as-judge via Cautilus `skill-experiment`,
   (c) usage-episodes adapter activation decision.
2. **Triage #198**: reproduce sampler attribution for `eval_registry.py:6`
   — budget vs coverage-context is the suspect. Do not lower threshold.
3. **Optional**: 14 pre-existing "used to resolve the X adapter" strings
   in `release/` + `issue_tool.py` understate their roles. Out of #196
   scope; only worth a sweep if budget allows.

## Discuss

- Sync gate already exists at `validate_packaging_install_surface.py:130`
  and runs before pytest. The diff-based design in #197 would have been
  weaker (false positives, misses unstaged); content-diff is correct.
- Entry-guard skip detector `is_trivial_entry_guard_mutation` lives in
  `filter_cosmic_ray_mutants.py` and is mirrored in
  `mutation_sampling_lib.py` so the sampler stops counting entry-guard
  lines as mutable. New stat: `skipped_entry_guard`.
- `add_argument` with `choices=` must have `help=` reflecting actual
  choice strings; argparse prints them, so paraphrase contradicts.
- Subprocess tests passing `--repo-root str(REPO_ROOT)` to a writing CLI
  must use the `fake_charness_repo` fixture in
  [tests/test_usage_episodes_host_hooks.py](../tests/test_usage_episodes_host_hooks.py);
  scrub `MUTATION_*` env keys before forwarding `os.environ`.
- Watch: Yarn Berry hooks; pnpm+lefthook stale snippets; `filelock` +
  `pytest-xdist`; seed-cache LRU eviction; release proof suppression;
  D21–D26 reopen-trigger watchlist.

## References

- [#193 help= sweep retro](../charness-artifacts/retro/2026-05-23-help-text-sweep-session.md)
- [quality posture](../charness-artifacts/quality/latest.md),
  [release surface](../charness-artifacts/release/latest.md)
- [usage-episodes spec](../charness-artifacts/spec/usage-episodes-h-lam-t-completion.md),
  [bug-pattern sibling scan](../charness-artifacts/debug/2026-05-21-bug-pattern-sibling-scan.md)
- Closed this session: [#195](https://github.com/corca-ai/charness/issues/195),
  [#196](https://github.com/corca-ai/charness/issues/196),
  [#197](https://github.com/corca-ai/charness/issues/197). Opened:
  [#198](https://github.com/corca-ai/charness/issues/198).
