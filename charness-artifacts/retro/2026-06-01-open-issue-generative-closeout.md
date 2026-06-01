# Retro: Open issue generative closeout

Mode: session

## Context

This retro covers the 2026-06-01 goal that turned the active handoff plus all 12 open issues into a sequenced closeout run. The run closed the implementation-backed issue set through a final direct-commit carrier and intentionally left #261 and #184 open with carry-forward comments.

## Evidence Summary

Evidence used: the goal artifact `charness-artifacts/goals/2026-06-01-handoff-open-issue-generative-closeout.md`, final carrier `charness-artifacts/issue/2026-06-01-open-issue-final-carrier.md`, final broad `./scripts/run-quality.sh --read-only` pass, `issue_tool.py verify-closeout --expect-state CLOSED`, live `gh issue` state for #261/#184, and final fresh-eye review by Ptolemy.

## Waste

The main cost was not implementation churn; it was coordination cost from carrying many issue dispositions until the final carrier. The most expensive risk was ambiguity around when engineering success could close #185 while product success #184 stayed open. Resolving that before the final carrier prevented a broad, misleading closeout.

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
- memory: applied — this retro artifact and the goal Auto-Retro bind the closeout lesson to durable artifacts.

## Sibling Search

n/a — the reusable checks already exist in the issue closeout verifier and goal closeout floor; this retro reinforces their ordering rather than identifying a new missing sibling class.

## Persisted

Persisted: yes `charness-artifacts/retro/2026-06-01-open-issue-generative-closeout.md`.
