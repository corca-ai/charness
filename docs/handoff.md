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

- **#184/#185 RCA ledger slices 1+2 landed** (this session = slice 2 + fixture
  fix). Substrate (schema, `record_rca_event.py`, `validate_rca_ledger.py`,
  `aggregate_rca_ledger.py`, seeded
  [ledger](../charness-artifacts/metrics/rca-ledger.jsonl)) plus auto-append wired
  into `debug`/`issue`/`retro` closeouts via presence-gated
  [rca-ledger-append.md](../skills/shared/references/rca-ledger-append.md) (no-op
  for consumers); `AUTO_APPEND_WIRED=True`, banner `ON` with the
  prompt-enforced/self-reported honesty qualifier. A retro caught the committed
  ledger doubling as the AC4/AC7 fixture (first live append would break them) —
  fixed via synthetic seed-only fixtures. First live event dogfood-appended;
  seed-excluded baseline now `0/1 (0.0%)`, window open and accruing. Contract:
  [spec](../charness-artifacts/spec/rca-conversion-ledger.md),
  [metrics doc](./product-success-metrics.md).
- Prior: fixed **#209**/**#208** (mutation changed-scope gate self-recurrence,
  [RCA](../charness-artifacts/debug/2026-05-24-mutation-changed-line-uncovered-guard-recurrence.md));
  bug-sweep `4e69881` (v0.7.11); closed #198, #202–#206.
- Open: **#184** + **#185** stay OPEN — numeric target is baseline-first (revisit
  after 2–4 weeks of live seed-excluded data); #185 improvements #2 (LLM-as-judge)
  and #3 (usage-episodes activation) are un-specced.

## Next Session

1. **RCA ledger baseline observation** (DONE: slices 1+2 + fixture decoupling;
   first live event landed). Let live (non-seed) events keep accruing from
   `debug`/`issue`/`retro` closeouts. Revisit the numeric target after 2–4 weeks
   of seed-excluded data (`python3 scripts/aggregate_rca_ledger.py`). Optional
   follow-ups (spec slice-2 residual risk; each needs spec + critique first): an
   advisory closeout nudge when a `debug`/`issue`/`retro` slice commits with no
   matching ledger append; `class_key` dedup so a re-run cannot double-append.
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
