# Empty Policy Silent Pass Retro

## Context

The setup skill cleanup exposed a repeated quality pattern: `gate_rules` or
similar list fields can be empty, leaving a validator advisory-only while the
standing gate still reports a clean pass.

## Evidence Summary

- `skill_ergonomics_gate_rules: []` let `validate_skill_ergonomics.py` skip all
  skill checks without a structured warning.
- The repo-root wrapper only failed on `violations`, so configured-rule
  discovery errors could pass through that entrypoint.
- `run-quality` suppressed successful phase logs, so even pass-time warnings or
  weak findings were not visible by default.
- A debug sibling scan separated true siblings from false positives such as
  absent `.cautilus/runs/`, HITL initial `rules: []`, and retro's already
  explicit missing-vs-empty trigger payload.
- A delegated sibling scan found `release` requested-review commands returning
  a bare `ok` when `requested_review_commands: []`.

## Waste

- The first interpretation was too local: "fix skill ergonomics rules" instead
  of "empty policy disables enforcement invisibly."
- Prior all-skill health review surfaced core pressure, but the empty-rule
  state meant the relevant quality gate did not explain why that pressure was
  advisory-only.

## Critical Decisions

- Keep empty ergonomics rules as a passing state, but emit a structured warning
  when discoverable skills exist.
- Make `run-quality` replay passing phase logs that contain `WARNING`, `WARN`,
  `WEAK`, or `ADVISORY` lines.
- Add `configuration_status: not_configured` plus a warning to the release
  requested-review gate instead of treating empty requested-review commands as
  an unqualified `ok`.
- Treat bootstrap resolver warnings as visible in their own workflow rather
  than promoting every optional empty adapter field into a hard standing gate.

## Expert Counterfactuals

- Nancy Leveson would have modeled the missing control signal: the controller
  had no observable feedback that the enforcement channel was disabled.
- Gary Klein would have asked what a green gate would hide from a maintainer in
  a release hurry; the answer was pass-time warning output.

## Next Improvements

- workflow: when a validator has a valid empty-policy state, require a warning
  or weak finding if a relevant checked surface exists.
- capability: consider a future skill-ergonomics rule opt-in or refactor plan
  for the remaining long-core public skills instead of letting advisory
  inventory stay invisible.
- memory: classify empty config as one of absent surface, intentional opt-out,
  advisory-only, or disabled enforcement before accepting a green gate.

## Persisted

Persisted directly as `charness-artifacts/retro/2026-05-17-empty-policy-silent-pass.md`.
