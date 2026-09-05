# Taxonomy-Axis Checkpoint

Use this before adding a new user-facing mode, kind, strategy, profile, target,
or similar enum value to a spec, CLI, API, adapter, or skill contract.

## Mechanism

Charness-owned JSON Schema files hold the axis. A generic field named `kind`,
`mode`, `type`, `strategy`, `profile`, or `target` with two or more enum values
must declare `x-axis` from the closed set in
`<plugin-dir>/scripts/gates/check_schema_enum_axis.py`. A field already
named after its axis (`delivery_kind`, `access_modes`) does not need the
annotation.

A new axis is a new field. Do not add a value that belongs on a different axis
to an existing enum.

Absence is omit, not a sentinel. Install/update `mode` is an install method
(`manual`, `script`, `package_manager`, `git_checkout`). There is no `none`:
a tool that does not install is not represented by a fake method.

`python3 scripts/gates/check_schema_enum_axis.py --repo-root .` refuses a
generic enum that omits `x-axis`.

## Contracts that are not yet schema-backed

Ask these before naming a prose or adapter-only value:

- Are the existing values on the same conceptual axis?
- Is the new value a kind, or an objective, evidence focus, trigger, selection
  policy, or internal preset that should be a different field?
- Should the agent infer it behind a strong default instead of exposing a
  choice?

A user-facing enum is still honest when values need different acceptance
checks, the operator must choose at an irreversible boundary, or an external
API already exposes the vocabulary.
