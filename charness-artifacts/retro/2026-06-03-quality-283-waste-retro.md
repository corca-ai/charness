# Retro — /charness:quality #283 waste/efficiency

Mode: session (waste-focused)

## Context

Reviewing the just-completed `/charness:quality` slice that closed the #283
mutation regression in the Codex session/token reporter (new unit tests +
`main` routing/non-ASCII tests, verified by targeted local cosmic-ray, committed
as `9fb08f6f`). The unit of work is done and green; this retro asks where time
and trust were lost while doing it, so the next gated-artifact slice is cheaper.

## Evidence Summary

- `probe_host_logs.py` detected the live Claude Code session JSONL
  (`~/.claude/projects/.../8ca9722a-....jsonl`); token counts available, tool
  calls/turns derivable.
- Parsed that JSONL directly: 299 assistant messages; tool_use = Bash 78, Edit
  25, Read 16, Skill 3, Write 3, Agent 1; cumulative output ≈ 375.9k tokens,
  cache_read ≈ 40.4M, cache_create ≈ 1.2M.
- Bash pattern tally: `validate_quality_artifact` 15, artifact line-count checks
  11, `pytest` 11, `git status` 10, full `run-quality.sh` 6, `git diff` 6,
  cosmic-ray subcommands 8 (3 logical runs), poll/sleep loops 4.

## Waste

Phase-aware first: the 3 cosmic-ray runs, the bounded fresh-eye review, and the
baseline/post-change/final gate runs were the *verification* the "빡세게"
(rigorous) ask demanded — turning "I think these tests kill the mutants" into
proof. Those are investment, not waste. The avoidable waste was:

- Quality-artifact validator ping-pong (largest): ~15 `validate_quality_artifact`
  runs + 11 `wc -l` checks. I wrote a 204-line artifact, then discovered the
  140-line cap and fixed six distinct rules one failure at a time (max-lines,
  `prose review result:` line position, advisory `none` wording, advisory
  evidence on the first physical line, slow-gate lens naming, `passive ... because`).
  Root cause: I did not read the validator's full enforced ruleset before writing.
- Handoff edit cascade: editing `docs/handoff.md` broke `check-doc-links`
  (backticked file paths instead of markdown links) and
  `test_handoff_chunker_parse.py` (it pins the live Next-Session issue refs at
  `[184, 261]`, now stale because #261 is closed). That forced one extra full
  `run-quality` (~51s) plus investigation. Root cause: edited a coupled surface
  without checking its two known couplings first.
- Minor: 4 manual poll/sleep loops waiting on background cosmic-ray, partly
  redundant with the harness's background-completion notifications.

## Critical Decisions

- Verify the fix with local cosmic-ray rather than trust reasoning — caught that
  loose end-to-end coverage was the root cause and proved survivors dropped
  (23→12 / 6→4). Outcome-changing; without it the "fix" would have been a guess.
- Classify equivalent mutants (annotation unions, regex-domain `GtE`, cosmetic
  `indent`/`sort_keys`) instead of chasing them — avoided brittle byte-exact
  output guards the quality contract discourages.
- Apply the reviewer's `ensure_ascii` finding — closed a genuinely-killable mutant
  I had deferred; the fresh-eye pass paid for itself.

## Expert Counterfactuals

- Gary Klein (pre-mortem / recognition-primed): would have recognized
  "gate-validated artifact" as a known hazard surface up front and run one
  contract-read step before writing, collapsing the 15-run fix loop into 1–2.
- Bertrand Meyer (Design by Contract): treat the validator as the artifact's
  contract and satisfy the whole contract in the draft, not by trial-and-error;
  the same lens says a coupled doc (handoff) has a contract too — its doc-link
  rule and the chunker anchor test — that should be read before editing.

## Next Improvements

- workflow: Before producing any gate-validated artifact (quality / retro /
  handoff), read the owning validator's enforced rules once (required sections,
  max-lines, wording and evidence rules, `passive ... because`, slow-gate lenses)
  and write a compliant first draft instead of discovering rules one failure at
  a time.
- workflow: When editing `docs/handoff.md`, pre-check its two known couplings —
  `check-doc-links` wants markdown links not backticked paths, and
  `test_handoff_chunker_parse.py` pins the live Next-Session issue refs — before
  spending a full `run-quality`.
- capability: a `--report-all` (collect-all) mode for `validate_quality_artifact.py`
  and peers would surface every violation in one pass; 21 `validate_*.py` raise on
  the first error today vs 10 that already collect failures. Optional candidate,
  not committed here.
- memory: persist this retro so the contract-first lesson rides the recent-lessons
  digest into the next session.

## Sibling Search

- workflow axis: gate-validated artifacts (quality/retro/handoff) | decision:
  durable fix is the contract-first workflow habit above (repo-agnostic, recorded
  in memory), no code patch needed | proof: the six serial failures were all
  rules already declared in `scripts/validate_quality_artifact.py`.
- capability axis: `scripts/validate_*.py` first-error-vs-collect-all | decision:
  no in-slice follow-up — mass-converting 21 raise-first validators is a separate
  capability call, lower leverage than the workflow habit | proof: scan found 21
  raise-first vs 10 collect-failure validators; converting all is churn the
  contract-first habit already neutralizes.

## Persisted

- yes — `charness-artifacts/retro/2026-06-03-quality-283-waste-retro.md`
  (via `persist_retro_artifact.py`; recent-lessons digest + lesson-selection-index
  refreshed).
