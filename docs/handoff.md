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

- **#184/#185 ledger slice 1 impl (this session)**: shipped the RCA conversion
  ledger substrate per
  [the spec](../charness-artifacts/spec/rca-conversion-ledger.md) —
  [rca_event.schema.json](../scripts/rca_event.schema.json), `record_rca_event.py`,
  `validate_rca_ledger.py`, `aggregate_rca_ledger.py`, seeded
  [rca-ledger.jsonl](../charness-artifacts/metrics/rca-ledger.jsonl) (3 converted
  / 2 unconverted, all `seed=true`; 60% seed-included, seed-excluded `n/a`),
  rubric into [product-success-metrics.md](./product-success-metrics.md), AC1–AC8
  tests. Learned fact: the usage-episodes adapter is now `enabled`, so ledger
  independence is proven structurally (scripts reference no adapter machinery).
  Slice 2 (auto-append wiring) is still the hard prereq for any numeric target.
- **#184 ideation → spec (prior session)**: locked product north-star =
  operator/agent task success (named, not yet measurable); first *instrumented*
  objective = RCA-to-learning conversion rate. Wrote the
  [rca-conversion-ledger spec](../charness-artifacts/spec/rca-conversion-ledger.md)
  (spec critique + 3-angle decision-premortem applied), doc
  [product-success-metrics.md](./product-success-metrics.md). Commits `bc78db5`,
  `201dacb`. #184 stays OPEN (numeric target is baseline-first).
- Fixed **#209** then **#208** (mutation changed-scope gate self-recurrence); RCA
  in [debug](../charness-artifacts/debug/2026-05-24-mutation-changed-line-uncovered-guard-recurrence.md).
- Prior: bug-sweep `4e69881` (v0.7.11); closed #198, #202–#206.
- Open: **#184** (ledger slice 1 landed; stays OPEN for baseline-first numeric
  target after slice 2), **#185** (RCA ledger = improvement #1, slice 1 done /
  slice 2 pending; #2 LLM-as-judge / #3 usage-episodes activation un-specced).

## Next Session

1. **RCA ledger slice 2 — auto-append wiring** (DONE: slice 1 substrate). Wire
   `record_rca_event.py` into the `debug`, `issue`, and `retro` closeout prompts
   so events accrue without manual discipline. This is a behavior-steering prompt
   change: give it its own preserve/improve claim + critique + proof path, and
   flip `AUTO_APPEND_WIRED` in [rca_ledger_lib.py](../scripts/rca_ledger_lib.py)
   only when wiring lands.
   The baseline window (and any numeric target) does not open until this is live.
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
- [recent-lessons](../charness-artifacts/retro/recent-lessons.md): recently
  closed #198, #202–#209 (#207 by-design).
