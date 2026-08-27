# Adapter Pattern

Make a skill portable across repos by separating repo-specific config from the
skill body.

## Structure

```text
skills/public/<skill-id>/
  SKILL.md
  references/
  scripts/
.agents/<skill-id>-adapter.yaml
charness-artifacts/<skill-id>/
```

The adapter lives in the repo, not in the installed skill bundle.

## When To Use

Use an adapter when both are true:

1. the value differs across hosts or repos
2. deriving it every invocation would waste meaningful time

If either is false, keep the value in the skill body or let the agent infer it
from the repo.

## Shared Adapter Core

Prefer a thin shared core:

- `version`
- `repo`
- `language`
- `output_dir`
- `preset_id`
- `preset_version`
- `customized_from`

Anything beyond this needs a concrete justification tied to repeated work.

Adapters may record capability ids, provider preferences, or env var names when
those are genuinely repo-local defaults. They must not carry secret values.

### `version` gates the whole document

A resolver reconciles `version` against the one it speaks, and on a version it
does not speak it honors **none** of the declared siblings — the resolved payload
is the inferred defaults, and the only error is the version refusal. Absent is
still legal and leaves the defaults in place; the commit-time adapter gate is the
stricter reader that requires one.

Write it that way in a new resolver:
`data = declared_fields_after_version_check(data, validated, errors)` from
`scripts/adapter_lib`, rebinding `data` so the passes below it read the contained
mapping. The reason it is a mapping rather than an early return: most validators
derive keys their `infer_defaults` never seeds, and a bare `return` hands
consumers a payload missing keys they index directly.

A version the reader cannot interpret says nothing about what its siblings
*mean*, so honoring them lets a declaration steer a gate through a schema no
reader read. `<authoring-repo>/tests/quality_gates/test_adapter_version_reconciliation.py`
holds this for every resolver family; a new one is covered there the day it is
added.

## Location

Use the single repo-owned path `<repo-root>/.agents/<skill-id>-adapter.yaml`.

## Design Rules

- Keep the skill body generic.
- Store durable repo outputs under `<repo-root>/charness-artifacts/<skill-id>/` unless the repo
  already has a better checked-in home.
- Default visible artifacts to `YYYY-MM-DD-<slug>.md`. Add `latest.md` only
  when the repo genuinely benefits from one current pointer over those dated
  records. Rolling canonical artifacts may keep a clearer fixed filename, such
  as the repository's canonical documentation index.
- Declare the artifact behavior in the adapter resolver as `artifact_class`:
  `history` for dated records, `current` for a single maintained surface, or
  `rolling` for a canonical rolling file.
- Auto-create missing adapters only when the defaults are low risk.
- Distinguish `unset` from `explicitly empty` for optional list-like fields.
- Keep official presets separate from adapters. The adapter records which preset
  was applied; the preset remains an explicit choice.

## Anti-Patterns

- putting host secrets or mutable config inside the skill bundle
- putting raw secret material in adapters
- adding fields just because they vary
- using a preset as a secret transport
- hardcoding repo names in `SKILL.md`
