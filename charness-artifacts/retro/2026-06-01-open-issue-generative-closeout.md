# Retro: Open issue generative closeout

Mode: session

## Context

This retro covers the 2026-06-01 goal that turned the active handoff plus all 12 open issues into a sequenced closeout run. The run closed the implementation-backed issue set through a final direct-commit carrier and intentionally left #261 and #184 open with carry-forward comments.

## Evidence Summary

Evidence used: the goal artifact `charness-artifacts/goals/2026-06-01-handoff-open-issue-generative-closeout.md`, final carrier `charness-artifacts/issue/2026-06-01-open-issue-final-carrier.md`, final broad `./scripts/run-quality.sh --read-only` pass, `issue_tool.py verify-closeout --expect-state CLOSED`, live `gh issue` state for #261/#184, final fresh-eye review by Ptolemy, goal DB lifecycle counters, and Codex session audit `charness-artifacts/probe/2026-06-01-open-issue-generative-closeout-codex-audit.json`.

## Measured Cost

- Goal lifecycle counter: 2,203,327 tokens over 8,058 seconds, about 2h14m.
- Codex session audit: 4,316 events, 625 token-count snapshots, 8 context compactions, 942 function calls, 109 custom tool calls, and 104 patch applications.
- Tool pressure: 747 `exec_command` calls, 142 `write_stdin` polls, 109 `apply_patch` calls, 9 subagent spawns, 16 subagent waits, and 4 subagent closes.
- Repetition pressure proxies: `git status` 61, `git diff` 40, `./scripts/check-markdown.sh` 23, `pytest` 26, and `ruff` 25. These are proxy counts, not all waste; some are expected across a seven-slice goal.

## Waste

The main cost was coordination cost from carrying many issue dispositions until the final carrier. That cost is visible in 8 context compactions, 1,051 total tool calls, repeated VCS checks, and repeated broad-gate probes. The most expensive risk was ambiguity around when engineering success could close #185 while product success #184 stayed open. Resolving that before the final carrier prevented a broad, misleading closeout, but it also consumed a large share of the run's 2.2M goal-token budget.

## Critical Decisions

- Product success (#184) stayed open because the maintainer's newer framing and source-thread refresh remain necessary.
- AI/ML engineering success (#185) closed only as necessary engineering conditions, not as sufficient product success.
- Final live mutation waited until local broad quality, carrier validation, and fresh-eye review were complete.
- #261 stayed open because mutation-standard policy was not decided by the mechanical survivor closeout.

## Expert Counterfactuals

A Gary Klein premortem lens would have asked earlier, "Which issue would we regret closing accidentally?" That points directly to #184/#261 and validates the explicit leave-open comments.

A Daniel Kahneman base-rate lens would have treated closeout-keyword mistakes and stale handoff state as likely recurrence risks. The final verifier and handoff refresh addressed those risks before completion.

## Next Improvements

- workflow: applied — use `issue_tool.py verify-closeout --expect-state CLOSED` after final push, not only draft/carrier validation before push.
- workflow: applied — require leave-open rows to receive live comments and state checks before marking the goal complete.
- capability: applied — `probe_host_logs.py` now audits the latest Codex rollout JSONL by default, so future retros see token-count snapshots, compactions, tool-call pressure, and repeated-command proxies without a manual follow-up search.
- memory: applied — this retro artifact and the goal Auto-Retro bind the closeout lesson to durable artifacts.

## Sibling Search

n/a — the reusable checks already exist in the issue closeout verifier and goal closeout floor; this retro reinforces their ordering rather than identifying a new missing sibling class.

## Persisted

Persisted: yes `charness-artifacts/retro/2026-06-01-open-issue-generative-closeout.md`.
