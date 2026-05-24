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

- **#184 ideation → spec (this session)**: locked product north-star =
  operator/agent task success (named, not yet measurable); first *instrumented*
  objective = RCA-to-learning conversion rate. Wrote
  [rca-conversion-ledger spec](../charness-artifacts/spec/rca-conversion-ledger.md)
  (spec critique + 3-angle decision-premortem applied), doc
  [product-success-metrics.md](./product-success-metrics.md). Commits `bc78db5`,
  `201dacb`. #184 stays OPEN (numeric target is baseline-first).
- Fixed **#209** then **#208** (mutation changed-scope gate self-recurrence); RCA
  in [debug](../charness-artifacts/debug/2026-05-24-mutation-changed-line-uncovered-guard-recurrence.md).
- Prior: bug-sweep `4e69881` (v0.7.11); closed #198, #202–#206.
- Open: **#184** (ledger specced; impl pending), **#185** (RCA ledger =
  improvement #1; #2 LLM-as-judge / #3 usage-episodes activation un-specced).

## Next Session

1. **Impl the RCA conversion ledger** (slice 1) per
   [the spec](../charness-artifacts/spec/rca-conversion-ledger.md): schema +
   `record_rca_event.py` + `validate_rca_ledger.py` + `aggregate_rca_ledger.py` +
   seed (both outcomes) + rubric into the doc + tests AC1–AC8. Reuse the
   jsonschema/portable-path helpers from `slice_closeout_usage_episode.py`; do
   NOT couple to the usage-episodes adapter. Slice 2 (auto-append into
   debug/issue/retro prompts) is a hard prereq before any numeric target.
2. **Mutation blocker follow-up** (#208/#207): if changed-line *statement*
   coverage proves too weak, consider mutation-line coverage of changed lines
   (needs Cosmic Ray init on all changed files) — spec + critique first.

## Discuss

- **Deferred (#209 critique)**: a changed-line gate verified pre-commit against
  `git diff base..HEAD` is blind to a fix's own *new* uncommitted file → false
  green. Discipline: commit-then-verify, or 100% coverage on new sampler modules.
- Advisory-by-design: `validate_skill_output_schemas.py` (un-wired); new opt-in
  artifact validators are section-gated + changed-paths-default.
- Watch: Yarn Berry hooks; pnpm+lefthook stale snippets; `filelock`+`pytest-xdist`;
  seed-cache LRU eviction; release proof suppression; D21–D26 reopen watchlist;
  2 pre-existing ruff errors in vendored notion-to-md (out of scope).

## References

- [quality posture](../charness-artifacts/quality/latest.md),
  [release surface](../charness-artifacts/release/latest.md),
  [usage-episodes spec](../charness-artifacts/spec/usage-episodes-h-lam-t-completion.md)
- Recently closed: #198, #202–#209 (#207 by-design).
