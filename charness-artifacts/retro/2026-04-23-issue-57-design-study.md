# Issue 57 Design Study Retro
Date: 2026-04-23

## Context

Issue #57 moved from comment-only planning into a bounded implementation slice after a mandatory fresh-eye premortem.

## Waste

The first implementation-integrity subagent misunderstood its role and tried to spawn another agent. The prompt needed to state that it was already the bounded angle reviewer.

## Critical Decisions

- Kept the implementation to a Markdown-only Capability Spectrum renderer.
- Excluded checked-in `model.json`, live doctor payload ingestion, dashboard UI, and phase timeline from the first slice.
- Let `run_slice_closeout.py` confirm surface ownership instead of changing `.agents/surfaces.json` preemptively.

## Expert Counterfactuals

Gary Klein would have made the first slice an explicit recognition-primed probe: prove whether the existing inventory can reduce operator judgment cost before designing a richer instrument.

Daniel Kahneman would have forced the counterweight pass earlier to separate aesthetic excitement from evidence. That would still have landed on the same narrow Markdown slice.

## Next Improvements

- workflow: When delegating a premortem angle, state that the receiving agent is already the bounded subagent and must not run the subagent capability check again.
- capability: Keep design-study renderers read-only and source-consuming until a stable artifact schema earns a surface entry.
- memory: Use this slice as the precedent for avoiding raw live doctor payloads in visible artifacts.

## Persisted

Yes: this artifact and the refreshed recent-lessons digest.
