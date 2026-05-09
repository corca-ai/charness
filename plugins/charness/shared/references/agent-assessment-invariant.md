# Agent Assessment + Recommended Disposition Invariant

Before asking a human to decide, approve, classify, or refine, the agent
presents both:

- **Agent Assessment**: the agent's own non-binding judgment against the
  active criteria, naming concrete risks, gaps, drift, or fit it noticed.
- **Recommended Disposition**: the agent's preferred next action
  (`accept`, `revise`, `defer`, or a surface-specific verb), explicitly
  display-only.

Then, and only then, comes the concrete decision prompt for the human.

The human reviews the agent's judgment instead of carrying the agent's
first-pass thinking. Question-only or choice-only surfaces are not enough.

This invariant applies to:

- HITL chunk presentation (`hitl/references/chunk-contract.md`).
- HITL applied-rewrite and full-target review surfaces.
- `quality` `NON_AUTOMATABLE` proposal handoff to HITL.
- `critique` findings or counterweight triage when a decision is returned to
  the caller for a human-owned choice.
- `spec` interactive ambiguity-reduction prompts that ask the user to choose.
- `narrative` rewrite-loop human-facing surfaces and brief-draft review.
- `setup` ideation-pass and scaffold decisions returned to the maintainer.

Suggestions never auto-record as approval; the human still owns the decision.

The HITL self-check helper
[check_chunk_contract.py](../../public/hitl/scripts/check_chunk_contract.py)
validates this contract on chunk text and is the canonical runtime probe
for surfaces that can stage a chunk before presentation.
