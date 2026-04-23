# Issue 57 Readiness Example Retro
Date: 2026-04-23

## Context

Issue #57's first artifact passed a fresh-eye read test, but the reader could not distinguish defined capability boundaries from current readiness.

## Waste

The initial spectrum artifact made access modes visible but did not explain what `binary`, `env`, `grant`, `human-only`, and `degraded` meant for operator judgment.

## Critical Decisions

- Added static access legend and sanitized readiness threshold examples.
- Kept live `doctor` payloads, current machine status, local paths, accounts, stdout, stderr, provenance, and tokens out of the artifact.
- Kept the slice as Markdown-only instead of introducing a JSON model or public CLI surface.

## Expert Counterfactuals

Gary Klein would treat the fresh-eye confusion as the cue for one recognition-friendly example, not a full diagnostic dashboard.

Daniel Kahneman would keep the examples explicitly non-current-state so readers do not overinterpret a design-study artifact as live evidence.

## Next Improvements

- workflow: After a read test surfaces confusion, fix only the confusion that changed the reader's answer.
- capability: Sanitized examples should describe threshold semantics without copying live command output.
- memory: Treat access-mode legends as part of operator-facing capability maps.

## Persisted

Yes: this artifact and refreshed retro indexes.
