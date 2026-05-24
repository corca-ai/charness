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

- **#184/#185 ledger slice 2 — auto-append wiring (this session)**: wired the
  recorder into the `debug`/`issue`/`retro` closeout prompts via a presence-gated
  shared reference
  [rca-ledger-append.md](../skills/shared/references/rca-ledger-append.md) (no-op
  in consumer repos), flipped `AUTO_APPEND_WIRED=True` so the aggregator banner
  reads `ON`, and kept the baseline guards (n/a + no non-seed number until live
  events accrue). Spec [slice-2 section](../charness-artifacts/spec/rca-conversion-ledger.md)
  records the preserve/improve claim + residual risk (append is prompt-enforced,
  not gate-enforced). The baseline window is now **open but empty**.
- **#184/#185 ledger slice 1 impl (prior session)**: shipped the RCA conversion
  ledger substrate —
  [rca_event.schema.json](../scripts/rca_event.schema.json), `record_rca_event.py`,
  `validate_rca_ledger.py`, `aggregate_rca_ledger.py`, seeded
  [rca-ledger.jsonl](../charness-artifacts/metrics/rca-ledger.jsonl) (3 converted
  / 2 unconverted, all `seed=true`; 60% seed-included, seed-excluded `n/a`),
  rubric into [product-success-metrics.md](./product-success-metrics.md), AC1–AC8
  tests. usage-episodes adapter is `enabled`, so ledger independence is proven
  structurally (scripts reference no adapter machinery).
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
- Open: **#184** (ledger slices 1+2 landed; stays OPEN for baseline-first numeric
  target after 2–4 weeks of live data), **#185** (RCA ledger = improvement #1,
  slices 1+2 done; #2 LLM-as-judge / #3 usage-episodes activation un-specced).

## Next Session

1. **RCA ledger baseline observation** (DONE: slices 1+2). The auto-append window
   is open; let live (non-seed) events accrue from `debug`/`issue`/`retro`
   closeouts. Revisit the numeric target after 2–4 weeks of seed-excluded data
   (`python3 scripts/aggregate_rca_ledger.py`). Optional follow-up: an advisory
   closeout nudge when a `debug`/`issue`/`retro` slice commits with no matching
   ledger append (spec slice-2 residual risk) — spec + critique first.
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
