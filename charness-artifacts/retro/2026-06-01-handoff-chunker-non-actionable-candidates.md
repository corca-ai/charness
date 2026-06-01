# Session Retro: Handoff Chunker Non-Actionable Candidates

## Context

The user pointed out that the handoff chunker again surfaced meaningless pickup choices: local-state verification appeared as a selectable chunk, and an already completed achieve goal was still offered for activation.

## Waste

- The chunker treated every numbered `## Next Session` entry as selectable work.
- The parent ranking pass did not re-check whether an entry was operator setup, stale activation state, or an execution constraint.
- This cost a correction turn and made the handoff output look less trustworthy than the underlying repo state.

## Critical Decisions

- Fix the parser/chunker source rather than relying on better wording in future handoff docs.
- Filter local-state preflight, completed goal activation entries, and cadence/invariant constraints before merge/rank.
- Keep incomplete goal activation entries selectable, because those are real pickup work.

## Expert Counterfactuals

- A Gary Klein premortem would have asked which ranked choices a human could actually choose; that would have exposed setup and stale-state entries before presenting the list.
- A Daniel Kahneman base-rate check would have treated numbered handoff entries as mixed-purpose prose, not as evidence that every item is a work option.

## Next Improvements

- workflow: chunker pickup should present only actionable work chunks; setup and constraints shape execution silently.
- capability: parser now owns the filter with tests, so the rule is executable instead of relying on handoff prose discipline.
- memory: this retro records the miss and points to the structural fix in `skills/public/handoff/scripts/chunked_routing_parser.py`.

## Sibling Search

Searched the handoff chunker parser/proposer/issue-source surfaces. The transferable bug belongs at parser candidate selection: issue-source entries are open tracker issues, and proposer/ranker should not guess stale state after parsing.

## Persisted

Persisted: yes `charness-artifacts/retro/2026-06-01-handoff-chunker-non-actionable-candidates.md`
