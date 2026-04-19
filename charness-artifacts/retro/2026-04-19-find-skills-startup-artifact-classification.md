# Session Retro: Find-Skills Startup Artifact Classification

## Context

- The user pointed out that I kept describing `charness-artifacts/find-skills/latest.*` as unrelated dirty state even though the mandatory startup `find-skills` call had created that diff.
- The actual miss was failure to classify whether the artifact change reflected canonical inventory truth or invocation/runtime-root drift before closeout.

## Waste

- I treated repeated startup artifact churn as something to mention at the end instead of a bug signal to investigate immediately.
- That hid the real problem: installed-plugin invocation was rewriting repo-local inventory with packaged skill paths and dropping synced support visibility.

## Critical Decisions

- Startup `find-skills` rewrites should be diffed immediately and classified before any commit decision.
- For source repos, installed-plugin invocation must preserve repo-owned skill inventory instead of falling back to packaged layout paths.

## Expert Counterfactuals

- Gary Klein: notice the anomaly at the moment it appears. The right first move was to diff `latest.*` before discussing whether it was related.
- John Ousterhout: keep the durable artifact contract shallow. Canonical capability inventory and invocation-path quirks should not be collapsed into one ambiguous dirty state.

## Next Improvements

- workflow: when startup discovery rewrites a checked-in artifact, classify it as canonical inventory change, intended generated update, or bug before closeout.
- capability: keep plugin invocation stable for source repos with a regression test that exercises the checked-in plugin export path.
- memory: encode the classification rule in `AGENTS.md` and handoff so the same ambiguity does not recur.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-04-19-find-skills-startup-artifact-classification.md
