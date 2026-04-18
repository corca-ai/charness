# Narrative Adapter Contract

`narrative` stays portable by loading repo-specific truth-surface defaults from
an adapter instead of hardcoding one repo's document set into the public core.

Canonical path for new repos:

- [`.agents/narrative-adapter.yaml`](../../../../.agents/narrative-adapter.yaml)

Fallback lookup order:

1. [`.agents/narrative-adapter.yaml`](../../../../.agents/narrative-adapter.yaml)
2. `.codex/narrative-adapter.yaml`
3. `.claude/narrative-adapter.yaml`
4. `docs/narrative-adapter.yaml`
5. [`narrative-adapter.yaml`](../../../../.agents/narrative-adapter.yaml)

## Fields

- `version`: adapter schema version, currently `1`
- `repo`: repo display name for artifact labeling
- `language`: default durable artifact language
- `output_dir`: durable artifact directory, default `charness-artifacts/narrative`
- `preset_id`, `preset_version`, `customized_from`: provenance metadata only
- `source_documents`: ordered list of truth-surface docs to read first
- `mutable_documents`: ordered list of docs the skill may realign directly
- `brief_template`: ordered section labels for one audience-neutral brief
  skeleton
- `scenario_surfaces`: optional ordered labels for main first-class use cases
  or evaluation archetypes that should stay visible in the durable docs
- `scenario_block_template`: optional ordered slot labels for scenario blocks;
  keep this as a template, not a promise that every scenario must use every
  slot
- `remote_name`: git remote to compare against when checking freshness

## Durable Artifact

The default artifact is:

- [`charness-artifacts/narrative/latest.md`](../../../../charness-artifacts/narrative/latest.md)

Dated narrative records should use `charness-artifacts/narrative/YYYY-MM-DD-<slug>.md`.

Keep the durable alignment artifact separate from any audience-specific brief
when the brief is ephemeral or audience-local.

`brief_template` should stay audience-neutral. It is the repo-specific skeleton
for compressing the aligned story, not the place to encode language, tone,
channel, or one delivery backend.

`scenario_block_template` should stay concrete and first-run oriented. It is a
reader-scaffolding device for products with multiple first-class use cases, not
an invitation to duplicate the whole contract in cards.
