# Create-Skill Adapter Contract

The `create-skill` adapter records repo-local skill authoring vocabulary that
should not live in the portable public skill body.

## Location

Search order:

1. `.agents/create-skill-adapter.yaml`
2. `.codex/create-skill-adapter.yaml`
3. `.claude/create-skill-adapter.yaml`
4. `docs/create-skill-adapter.yaml`
5. `create-skill-adapter.yaml`

The canonical checked-in location is `.agents/create-skill-adapter.yaml`.

## Fields

Common adapter fields:

- `version`: adapter schema version, currently `1`
- `repo`: repo name
- `language`: preferred operator language
- `output_dir`: default durable note location for create-skill work when a
  workflow needs one
- `preset_id`, `preset_version`, `customized_from`: optional preset
  provenance

Topology vocabulary fields:

- `implementation_identity_terms`: repo-local words for the implementation
  that owns the actual skill behavior, such as `canonical implementation` or
  `shared implementation`
- `placement_terms`: repo-local words for host-facing exposure points that may
  point at the same implementation, such as `trigger surface`, `alias`, or
  `host-facing registration`
- `intentional_fork_signals`: words or conditions that mean a separate copy is
  deliberate, such as behavior differences, data isolation, or independent
  lifecycle
- `topology_verification_hints`: repo-local checks or report wording that help
  the agent state whether it created one shared implementation or an
  intentional fork

Host extension fields:

- `host_extensions`: optional mapping reserved for host-owned metadata. The
  resolver validates only that it is a mapping and passes its contents through
  unchanged in the resolved adapter JSON.
- top-level `x-*` fields: optional host-owned extension blocks. The resolver
  preserves these fields unchanged so a host can add private flow metadata
  without editing Charness-authored skill files.

Use these extension fields for adapter metadata only. Host-specific behavior
still belongs in the host adapter, preset, or integration layer that consumes
the resolved JSON.

Topology glossary:

- `implementation identity`: the file or package location that owns the skill
  behavior.
- `placement`: a repo-local location or host-facing surface where the skill can
  be found.
- `trigger surface`: the prompt, command, manifest entry, or host hint that
  routes work to the skill.
- `alias`: a lightweight reference from one placement to an existing
  implementation.
- `intentional fork`: a separate implementation kept because behavior, data, or
  lifecycle boundaries are genuinely different.
- `host-facing registration`: any repo-declared surface that exposes or points
  to a skill implementation.

These terms do not imply any specific provider, delivery target, identifier
shape, or filesystem layout.

## Missing Adapter Behavior

When no adapter is present, `create-skill` may continue with generic inferred
terms, but the fallback must stay visible. The agent should say it is using
generic topology vocabulary instead of a repo-owned create-skill adapter.

Run `python3 "$SKILL_DIR/scripts/init_adapter.py" --repo-root .` to scaffold
the canonical `.agents/create-skill-adapter.yaml` file.

When an adapter file is present but invalid, stop and repair it before relying
on inferred topology terms. A broken repo-owned adapter is not the same as a
missing adapter.

## Non-Goals

- Do not store secrets or provider credentials.
- Do not encode consumer-specific delivery targets, provider ids, repo-local
  paths, or topology in the Charness public skill package.
- Do not require every repo to model multiple placements. Empty lists are valid
  and mean the repo has not declared that vocabulary.
- Do not require hosts to fork `resolve_adapter.py` for private adapter
  metadata. Use `host_extensions` or top-level `x-*` blocks instead.
