# Retro: Cautilus Disabled After Miss

## Context

Mode: session.

- This session reviewed URL-to-gather routing and the repeated Cautilus exclusion reminder.
- The operator had already said Cautilus tests are intentionally excluded during rework, but the session still attempted a Cautilus eval.

## Evidence Summary

- User correction on 2026-05-05: do not use Cautilus while it is under full rework.
- Local process check confirmed no Cautilus process remained after stopping the attempted run.
- Repo policy before this slice still encoded Cautilus as the prompt-proof path without an executable disabled mode.

## Waste

- The workflow relied on chat memory for a temporary but important tool exclusion.
- The prompt-proof validator pushed toward a Cautilus artifact, so the agent followed the old path instead of treating the tool as unavailable.

## Critical Decisions

- Persist Cautilus exclusion in both `AGENTS.md` and `.agents/cautilus-adapter.yaml`.
- Add adapter-level `run_mode: disabled` so validators and closeout planning honor the same rule as the human-facing contract.
- Keep the URL-to-gather routing proof deterministic while Cautilus is disabled.

## Expert Counterfactuals

- A reliability-review lens would have asked whether the "do not run" policy existed in the same place that selected the proof command before executing any proof.
- A release-engineering lens would have converted the temporary exclusion into a versioned adapter state instead of another operator reminder.

## Next Improvements

- workflow: check tool adapter run modes before executing proof commands when the tool is known to be in rework.
- capability: use an explicit disabled run mode for temporarily unavailable evaluator integrations.
- memory: keep the disabled state in durable repo artifacts until the rework is complete and the adapter is deliberately re-enabled.

## Persisted

- yes: `charness-artifacts/retro/2026-05-05-cautilus-disabled-after-miss.md`
