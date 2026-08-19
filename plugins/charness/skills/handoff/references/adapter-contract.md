# Handoff Adapter Contract

The handoff adapter keeps artifact location and host defaults out of the public
skill body.

## Canonical Path

Use `<repo-root>/.agents/handoff-adapter.yaml`.

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

Optional size budget:

- `max_content_words` — CONTENT words the handoff may occupy. Blank lines, the
  required `##` headings and the whole `## References` block are NOT counted, and
  what remains is charged per whitespace-separated token, so this is a different
  measurement from debug/quality's `max_artifact_lines` (which counts LINES) and
  the two numbers are not interchangeable in magnitude OR in unit. Omit it to keep
  the shipped default. The gate, the scaffold, the run planner's
  `over_limit`/`near_limit` status and the doc-authoring preflight all resolve the
  same value. Must be a positive integer; a refused value is an adapter error and
  leaves the default enforced. There is no upper bound: the ceiling is this repo's
  to set.
- `max_content_lines` — RETIRED on 2026-08-19 and now an adapter ERROR, not a
  silently ignored key. A line count charged for the author's wrap width (a 3.3x
  swing on identical prose, against a linter that enforces no width at all), and no
  automatic conversion exists — the old bar admitted 222-1240 words. Restate the
  bar you want in `max_content_words`. It refuses rather than warns because a
  warning would let the adapter resolve `valid: true` while the repo's declared
  ceiling did nothing.

Optional chunk policy:

- `chunk_policy.max_package_sources`: positive integer; default `5`
- `chunk_policy.broad_boundary_tokens`: label/path tokens that cannot be the
  sole merge basis by default
- `chunk_policy.allowed_broad_boundary_tokens`: repo-local broad tokens that are
  meaningful enough to allow as a merge basis

## Artifact Rule

The durable handoff artifact filename is fixed to handoff.md and the
default location is `<repo-root>/docs/handoff.md`.

To change the location, override `output_dir` in the adapter.
