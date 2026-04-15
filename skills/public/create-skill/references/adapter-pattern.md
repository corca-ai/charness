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

## Search Order

Prefer repo-owned adapter paths first:

1. `.agents/<skill-id>-adapter.yaml`
2. `.codex/<skill-id>-adapter.yaml`
3. `.claude/<skill-id>-adapter.yaml`
4. `docs/<skill-id>-adapter.yaml`
5. `<skill-id>-adapter.yaml` as compatibility fallback only

## Design Rules

- Keep the skill body generic.
- Store durable repo outputs under `charness-artifacts/<skill-id>/` unless the repo
  already has a better checked-in home.
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
