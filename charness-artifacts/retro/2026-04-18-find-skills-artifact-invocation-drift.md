# Session Retro: Find-Skills Artifact Invocation Drift

## Context

- The user repeatedly pointed out discomfort with `charness-artifacts/find-skills/latest.*` becoming dirty after ordinary inspection.
- The miss mattered because I kept treating the dirty state as something to discuss, instead of first classifying whether it was intended durable evidence or invocation-shaped churn.

## Waste

- I collapsed two different things into one artifact surface: canonical capability inventory and ad hoc recommendation query output.
- That made `latest.*` drift when the same command was run with different flags, even though the underlying repo capability surface had not changed.
- After the user signaled the smell, I still framed the state as a judgment call instead of checking whether the diff reflected actual repo truth or only query shape.

## Critical Decisions

- The right durable contract is that `latest.*` should represent canonical local-first inventory, not the caller's transient query shape.
- Recommendation queries should remain stdout payloads or move to a different artifact, but should not rewrite canonical inventory evidence.

## Expert Counterfactuals

- Gary Klein: classify the anomaly before discussing it. The first question should have been "what exact invariant changed in the artifact?" rather than "should we keep this?"
- John Ousterhout: separate deep concerns. A single `latest.*` file should not carry both durable inventory state and ephemeral recommendation query output.

## Next Improvements

- workflow: when an artifact turns dirty during inspection, diff it before mentioning it and classify it as canonical evidence, intended query artifact, or incidental churn.
- capability: make `find-skills` persist only canonical inventory into `latest.*` so query-shape flags do not rewrite durable evidence.
- capability: tighten the `find-skills` skill wording so `latest.*` is explicitly the canonical inventory artifact, while recommendation queries stay ad hoc.
- memory: persist this retro because the miss reflects a workflow and contract-design gap, not a one-off wording slip.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-04-18-find-skills-artifact-invocation-drift.md
