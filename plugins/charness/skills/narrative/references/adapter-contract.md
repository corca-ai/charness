# Narrative Adapter Contract

`narrative` stays portable by loading repo-specific truth-surface defaults from
an adapter instead of hardcoding one repo's document set into the public core.

Canonical path for new repos:

- `.agents/narrative-adapter.yaml`

Fallback lookup order:

1. `.agents/narrative-adapter.yaml`
2. `.codex/narrative-adapter.yaml`
3. `.claude/narrative-adapter.yaml`
4. `docs/narrative-adapter.yaml`
5. `narrative-adapter.yaml`

## Fields

- `version`: adapter schema version, currently `1`
- `repo`: repo display name for artifact labeling
- `language`: default durable artifact language
- `output_dir`: durable artifact directory, default `skill-outputs/narrative`
- `preset_id`, `preset_version`, `customized_from`: provenance metadata only
- `source_documents`: ordered list of truth-surface docs to read first
- `mutable_documents`: ordered list of docs the skill may realign directly
- `remote_name`: git remote to compare against when checking freshness

## Durable Artifact

The default artifact is:

- `skill-outputs/narrative/narrative.md`

Keep the durable alignment artifact separate from any audience-specific brief
when the brief is ephemeral or audience-local.
