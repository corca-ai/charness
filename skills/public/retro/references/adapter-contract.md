# Retro Adapter Contract

The retro adapter keeps host-specific evidence, artifact paths, and metrics out
of the public skill body.

## Canonical Path

Use `<repo-root>/.agents/retro-adapter.yaml`.

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
- `artifact_sections`
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
metrics_commands: []
artifact_sections: []
packet_sections:
  - id: changed-files-and-owning-surfaces
    title: Changed Files And Owning Surfaces
    content_kind: script
    command: "python3 scripts/render_critique_section_changed_surfaces.py"
auto_session_trigger_surfaces: []
auto_session_trigger_path_globs: []
```

## Field Semantics

- `output_dir` is a repo-relative directory. It is canonicalized on load -- a
  leading `./`, a trailing `/`, and doubled separators are normalized away -- and
  an absolute or repo-escaping value is a broken adapter, not a fallback.
  Canonicalizing is not tidiness: the scaffold builds its write path by joining
  this string, while the validator derives its owned prefix through a path type,
  so an untidy value made the two name different directories and a `--paths` run
  reported `Validated 0 retro artifact(s).` over the artifact it was handed.
  Retro is currently the only skill that normalizes and refuses on this shared
  field name; the siblings still accept whatever they are given.
- `summary_path` is optional and points at a compact human-readable digest of
  recent retro lessons for future session pickup. It is NOT derived from
  `output_dir`, so a repo that moves one should move both.
- Optional here means three states, not two, and the resolver reports which one
  an adapter declared in `field_state.summary_path`:
  - the key is ABSENT (`unset`) — the default digest path applies;
  - the key carries a path (`configured`) — that path applies;
  - the key is declared `null` (`explicit-null`) — the Markdown projection is
    DISABLED. `persist` writes no digest, `plan` reads none, and
    `refresh-recent-lessons` refuses rather than reporting a no-op success over a
    path the repo asked not to have.

  Declare `null` when the repository's own lesson ledger is the sole lesson
  surface. An empty string is not the spelling: it stays a string and resolves to
  the repository root. Omission is not the spelling either — that is `unset`, and
  it is what makes the default apply.
- `evidence_paths` are additional repo-relative file or directory locators worth
  reading for retros. The planner preserves their declared order and reports
  missing optional locators without turning them into a blocking prerequisite.
  A path may expose a repo-owned evaluator contract, but the path string alone
  never implies one.
- `metrics_commands` are optional. If absent, the retro may still run narratively.
- `artifact_sections` are optional exact lines appended to the retro scaffold
  before `## Next Improvements`. They let a repo-owned evaluator expose its
  authoring form without hard-coding that form into the public skill. Empty
  strings preserve intentional blank lines.
- `packet_sections` are optional prepare-packet sections. When present, run
  `scripts/prepare_packet.py` before writing lessons and record the consumed
  packet path.
- `auto_session_trigger_surfaces` are optional changed-surface ids that should
  trigger a short `session` retro after closeout. Each id must resolve to a
  declared `surface_id` in `<repo-root>/.agents/surfaces.json`; an unresolved id is a
  broken adapter contract, not a normal non-match. The charness-maintained
  authoring-repo-internal contract lives at
  `<authoring-repo>/docs/surface-driven-adapter-triggers.md`.
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
- `artifact_sections` own form only; the repo's evidence path owns the meaning
  and validator, and unrelated repos keep the default empty list
- `packet_sections` reuse the critique prepare-packet section shape:
  `id`, `title`, `content_kind`, and exactly one of `content`, `content_path`,
  or `command`
- auto-trigger lists should stay bounded to repeat-trap seams such as
  install/update/support/export/discovery, not every code change
- use explicit empty lists to record intentional opt-out from evidence or metrics
