# Retro Adapter Contract

The retro adapter keeps host-specific evidence, artifact paths, and metrics out
of the public skill body.

## Canonical Path

Use `.agents/retro-adapter.yaml` for new repos.

Search order:

1. `.agents/retro-adapter.yaml`
2. `.codex/retro-adapter.yaml`
3. `.claude/retro-adapter.yaml`
4. `docs/retro-adapter.yaml`
5. `retro-adapter.yaml` as compatibility fallback only

## Fields

Required shared core:

- `version`
- `repo`
- `language`
- `output_dir`

Optional shared provenance:

- `preset_id`
- `preset_version`
- `customized_from`
- `snapshot_path`
- `summary_path`

Retro-specific fields:

- `default_mode`
  - `session`
  - `weekly`
  - `auto`
- `weekly_window_days`
- `evidence_paths`
- `metrics_commands`
- `auto_session_trigger_surfaces`
- `auto_session_trigger_path_globs`

## Example

```yaml
version: 1
repo: my-repo
language: en
output_dir: charness-artifacts/retro
preset_id: portable-defaults
customized_from: portable-defaults
default_mode: session
weekly_window_days: 7
snapshot_path: .charness/retro/weekly-latest.json
summary_path: charness-artifacts/retro/recent-lessons.md
evidence_paths:
  - docs/handoff.md
metrics_commands: []
auto_session_trigger_surfaces: []
auto_session_trigger_path_globs: []
```

## Field Semantics

- `default_mode` only breaks ties after explicit user wording and obvious context.
- `weekly_window_days` matters only for `weekly` mode.
- `snapshot_path` is optional and only used when `weekly` wants a compact
  machine-readable snapshot in addition to prose output.
- `summary_path` is optional and points at a compact human-readable digest of
  recent retro lessons for future session pickup.
- `evidence_paths` are additional local sources worth reading for retros.
- `metrics_commands` are optional. If they are absent, weekly mode may still
  run narratively.
- `auto_session_trigger_surfaces` are optional changed-surface ids that should
  trigger a short `session` retro after closeout.
- `auto_session_trigger_path_globs` are optional repo-relative glob patterns for
  the same purpose when surface ids alone are too coarse.

## Design Rules

- missing adapter is soft for `session`
- missing adapter is stronger for `weekly`, especially when metrics or durable
  artifacts are expected
- `snapshot_path` must be explicit; never infer hidden machine-write locations
- `summary_path` should stay stable when used so `AGENTS.md` and handoff can
  treat it as a repeatable memory surface instead of a one-off artifact
- `metrics_commands` must be real commands with real sources; never placeholders
- auto-trigger lists should stay bounded to repeat-trap seams such as
  install/update/support/export/discovery, not every code change
- use explicit empty lists to record intentional opt-out from evidence or metrics
