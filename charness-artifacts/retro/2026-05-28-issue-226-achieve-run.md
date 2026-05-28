# Retro

Mode: session

## Context

Reviewing the #226 `achieve` run (centralize a portable fresh-eye reviewer-tier
policy) — and specifically the user catching that the run's mandated Auto-Retro
and efficiency report were never actually produced.

## Evidence Summary

- Host-log probe (`probe_host_logs.py`) found the claude session JSONL
  (`caf42e53…`). Measured this session (achieve run + this retro):
  - output tokens ~377.8K; non-cache input ~14.3K; cache_read ~35.7M;
    cache_creation ~1.46M (prompt caching working hard — large always-on
    context re-read from cache each turn).
  - tool_use = 120: Bash 61, Edit 24, Read 14, Task* 12, Skill 3,
    AskUserQuestion 2, Agent 2, ToolSearch 1, Write 1.
  - wall clock ~2h52m (21:37Z → 00:30Z). Turn count is not cleanly separable
    from the JSONL (tool_result events share the user role); only ~5 real human
    prompts drove the run.

## Waste

1. **Auto-retro skipped; user had to ask (primary miss).** I wrote an inline
   `Auto-Retro` section in the goal artifact and flipped the goal to `complete`,
   but never ran the `retro` skill or `probe_host_logs.py`. I even wrote
   "Metrics: when available" while the metrics WERE available and unprobed. The
   achieve After-phase explicitly says "run `retro`"; I substituted a lighter
   from-memory paraphrase for the prescribed step.
2. **Pre-commit/pre-push markdown hook flooded context 3×.** Each commit/push
   printed the full 485-file `markdownlint` "Finding:" list as one multi-KB
   line; `tail` cannot trim a single line, so it landed in my context whole, 3
   times. Pure recurring noise on every commit in this repo.
3. **3 broad-gate runs across 3 pushes.** Two pushes were legitimately separate
   (completion record needs the issue closed; handoff was a separate user
   request), but the ~100–120s pre-push gate still ran 3× on near-identical
   trees. Minor.

Phase-aware note: the 61 Bash / investigation calls and the 2 read-only quality
runs were discovery + verification, not waste — the first quality run caught a
real ruff import-order failure. Genuine waste is items 1–2.

## Critical Decisions

- Corrected the policy to **host-plural** after the user's nudge (Codex-only →
  Codex + Claude Code) — changed deliverable correctness.
- Made `reviewer_tiers` a **validated adapter field** (user-chosen) rather than
  doc-only — durable, regression-guarded.
- **Confirmed the push** before landing (shared state) — correct discipline.
- **Filed #229** for the over-anchoring instead of only fixing it locally —
  turned a one-off into a guardrail.

## Expert Counterfactuals

- **Atul Gawande (checklist discipline):** the achieve After-phase is a
  checklist (run retro, report efficiency, honest non-claims). I executed a
  mental paraphrase and marked metrics "when available" without running the
  available probe. Changed action: treat each After-phase item as an executable
  step, and flip status to `complete` only after they are *run*, not summarized.
- **Gary Klein (pre-mortem):** a 10-second "if this goal is later judged
  incomplete, why?" at the complete-flip would have surfaced "the retro/metrics
  weren't actually produced" — exactly the gap the user caught.

Through-line: both of this session's misses are the same shape — **substituting
a lighter self-authored version for the prescribed/fuller thing** (Codex-only
vs the host-plural family; inline Auto-Retro vs running `retro`).

## Next Improvements

- **workflow:** when a skill phase says "run `<skill>`", invoke that skill; do
  not inline-substitute its output. Flip an achieve goal to `complete` only
  after the After-phase items (retro run, metrics reported) are executed.
- **capability:** quiet the pre-commit/pre-push markdown hook (print a file
  count, not the full 485-path list) so agent context is not flooded each
  commit; until then redirect that hook's stdout. Candidate issue.
- **memory:** this artifact + #229 capture the "lighter self-substitution"
  pattern for the next session.

## Sibling Search

Transferable pattern: "agent substitutes a lighter self-version for a
prescribed step." Four-axis quick scan:

- other skill After/closeout phases that rely on the agent invoking a sub-skill:
  `issue` closeout (resolution critique), `release` (standalone critique). These
  share the same prose-only reliance — the guard is convention, not a gate. The
  design-anchoring half is already filed as #229; the
  run-the-prescribed-skill half is this retro's lesson.
- hook/tool-output flooding: any per-file-printing hook (markdown lint here)
  shares the noise pattern; candidate capability fix above.

Not exhaustively scanned; recorded as the two follow-up directions above rather
than expanded into more issues now.

## Persisted
