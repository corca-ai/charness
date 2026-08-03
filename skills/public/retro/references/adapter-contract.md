# Retro Adapter Contract

The retro adapter keeps host-specific evidence, artifact paths, and metrics out
of the public skill body.

## Canonical Path

Use `<repo-root>/.agents/retro-adapter.yaml` for new repos.

Search order:

1. `<repo-root>/.agents/retro-adapter.yaml`
2. `<repo-root>/.codex/retro-adapter.yaml`
3. `<repo-root>/.claude/retro-adapter.yaml`
4. `<repo-root>/docs/retro-adapter.yaml`
5. `<repo-root>/retro-adapter.yaml` as compatibility fallback only

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
- `summary_path`

Retro-specific fields:

- `evidence_paths`
- `metrics_commands`
- `packet_sections`
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
summary_path: charness-artifacts/retro/recent-lessons.md
evidence_paths:
  - docs/handoff.md
metrics_commands: []
packet_sections:
  - id: changed-files-and-owning-surfaces
    title: Changed Files And Owning Surfaces
    content_kind: script
    command: "python3 scripts/render_critique_section_changed_surfaces.py"
auto_session_trigger_surfaces: []
auto_session_trigger_path_globs: []
```

## Field Semantics

- `summary_path` is optional and points at a compact human-readable digest of
  recent retro lessons for future session pickup.
- `evidence_paths` are additional local sources worth reading for retros.
- `metrics_commands` are optional. If absent, the retro may still run narratively.
- `packet_sections` are optional prepare-packet sections. When present, run
  `scripts/prepare_packet.py` before writing lessons and record the consumed
  packet path.
- `auto_session_trigger_surfaces` are optional changed-surface ids that should
  trigger a short `session` retro after closeout. Each id must resolve to a
  declared `surface_id` in `<repo-root>/.agents/surfaces.json`; an unresolved id is a
  broken adapter contract, not a normal non-match. The charness-maintained
  authoring-repo-internal contract lives at
  `<authoring-repo>/docs/conventions/surface-driven-adapter-triggers.md`.
- `auto_session_trigger_path_globs` are optional repo-relative glob patterns for
  the same purpose when surface ids alone are too coarse. Prefer surface ids
  for shared seams; reserve raw globs for narrow repo-specific exceptions.

## Design Rules

- missing adapter is soft; it hardens only when metrics or durable artifacts are
  expected
- never infer hidden machine-write locations
- `summary_path` should stay stable when used so `<repo-root>/AGENTS.md` and handoff can
  treat it as a repeatable memory surface instead of a one-off artifact
- `metrics_commands` must be real commands with real sources; never placeholders
- `packet_sections` reuse the critique prepare-packet section shape:
  `id`, `title`, `content_kind`, and exactly one of `content`, `content_path`,
  or `command`
- auto-trigger lists should stay bounded to repeat-trap seams such as
  install/update/support/export/discovery, not every code change
- use explicit empty lists to record intentional opt-out from evidence or metrics
