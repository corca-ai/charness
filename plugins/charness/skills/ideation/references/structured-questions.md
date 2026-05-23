# Structured Questions

`Open Questions` and `Assumptions` shipped as plain bullets force the next skill
(`spec` or `impl`) to re-triage every item: which must be resolved before build
scope locks, which can be probed during implementation, and which depend on
another decision first. That re-classification cost recurs at every downstream
stage of the `ideation → spec → impl` pipeline.

When the synthesis carries open questions a downstream skill must act on, emit
an opt-in `## Structured Questions` section so the handoff is machine-legible.
Prose-only output stays valid; this section is additive, not a replacement for
the conversational `Open Questions` bullets.

## Schema

Each entry is a single bullet with `|`-separated fields:

```text
- <id> | urgency: <urgency> | depends-on: <id|null> | action: <action> | note: <text>
```

Required fields: `urgency`, `depends-on`, `action`, `note`. The leading `<id>`
token (any short stable handle, e.g. `Q1`) is optional but recommended so
`depends-on` can reference it.

- `urgency`:
  - `must-resolve` — blocks `spec`; the build contract cannot lock without it
  - `probe-in-impl` — safe to defer into implementation as a tracked probe
  - `defer` — not on the critical path for the current decision
- `depends-on`: the `<id>` of another question that must be answered first, or
  `null` when the item is independent
- `action`: where the item is routed next
  - `spec` — resolve while writing the build contract
  - `impl` — carry into implementation as a probe
  - `hold` — park until an upstream dependency or external signal arrives
- `note`: one line of context the downstream skill needs

## Example

```text
## Structured Questions

- Q1 | urgency: must-resolve | depends-on: null | action: spec | note: single-tenant vs multi-tenant decides the data model
- Q2 | urgency: probe-in-impl | depends-on: Q1 | action: impl | note: cache TTL can be tuned once the tenancy model is fixed
- Q3 | urgency: defer | depends-on: null | action: hold | note: SSO is a later-stage expansion surface, not the wedge
```

## Enforcement

`scripts/validate_ideation_artifact.py` validates the enum values and required
fields when the `## Structured Questions` heading is present. The section is
opt-in: artifacts without it pass unchanged. This reuses the same
section-gated, fail-when-present discipline as
`scripts/validate_critique_artifacts.py` (`## Structured Findings`) so
orchestrators that already consume `critique` output do not learn a parallel
taxonomy.
