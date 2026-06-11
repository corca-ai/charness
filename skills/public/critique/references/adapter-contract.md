# Critique Adapter Contract

`critique` reads its repo policy from `.agents/critique-adapter.yaml`.
The adapter is optional. Without it, `critique` runs with inferred
defaults and consumes no prepare packet. Newly scaffolded adapters include the
Codex `high-leverage` reviewer tier (`model: gpt-5.5`,
`reasoning_effort: medium`, `service_tier: priority`) plus a routine `medium`
tier (`reasoning_effort: medium` with the inherited model), so repos adopting the
adapter get the current Codex default without making adapter-less non-Codex
hosts inherit a provider-specific model.

## Lookup Order

The adapter loader searches:

1. `.agents/critique-adapter.yaml` (default)
2. `.codex/critique-adapter.yaml`
3. `.claude/critique-adapter.yaml`
4. `docs/critique-adapter.yaml`
5. `critique-adapter.yaml`

First file wins. Missing adapter is a valid state.

## Adapter Fields

```yaml
version: 1
repo: <repo-name>
language: en
output_dir: charness-artifacts/critique
reviewer_tiers:        # values are host-specific; Codex shown, Claude Code uses sonnet-4.6
  high-leverage:
    model: gpt-5.5
    reasoning_effort: medium
    service_tier: priority
  medium:
    reasoning_effort: medium
packet_sections:
  - id: changed-files-and-owning-surfaces
    title: Changed Files And Owning Surfaces
    content_kind: script
    command: "python3 scripts/render_critique_section_changed_surfaces.py --json"
  - id: known-deferred-concerns
    title: Known Deferred Concerns
    content_kind: static
    content_path: docs/deferred-decisions.md
  - id: non-goals
    title: Non-Goals
    content_kind: static
    # `content` accepts a string or a list of strings (one per line).
    # Block scalars (`|`) are not supported by the repo-local YAML loader.
    content:
      - "- This critique should not relitigate the host/worker boundary portability decision."
      - "- This critique should not redesign the adapter slot shape."
```

Field semantics:

- `version` — adapter schema version, integer, currently always `1`
- `repo` — display name; defaults to the repo directory name
- `language` — render language hint for the markdown packet
- `output_dir` — repo-relative directory where packet artifacts land;
  defaults to `charness-artifacts/critique`
- `packet_sections` — list of declared sections; empty list is valid
  (signals "no opt-in" same as omitting the field)
- `reviewer_tiers` — optional mapping from a portable reviewer tier
  (`high-leverage`, `medium`, or `standard`) to host-specific spawn fields. The tier is
  host-plural: it translates the portable policy in
  [fresh-eye-subagent-review.md](../../../shared/references/fresh-eye-subagent-review.md)
  into the values for whichever host this repo runs on. Use `medium` for
  routine bounded fresh-eye packets and reserve `high-leverage` for release,
  issue, quality closeout, deployment-confidence, or explicitly justified
  high-risk reviews. Known host defaults for the `high-leverage` tier: a Codex
  host uses `model: gpt-5.5`, `reasoning_effort: medium`,
  `service_tier: priority`; a Claude Code host uses `model: sonnet-4.6`. Each
  tier value may set `model`, `reasoning_effort`, and `service_tier` (all
  strings, all optional); `reasoning_effort` /
  `service_tier` apply only where the host exposes them. Unknown tier names
  warn; unknown sub-fields error. A host without subagent model overrides
  ignores it. Newly scaffolded adapters default the Codex `high-leverage` tier
  to `gpt-5.5` with `medium` reasoning and the routine `medium` tier to an
  inherited model with `medium` reasoning.

Each `packet_sections` entry:

- `id` — slug, lowercase with hyphens, unique within the packet
- `title` — display title
- `content_kind` — `static` or `script`
- `command` (when `script`) — repo-relative shell command; stdout is
  the section content
- `content` (when `static`) — inline string or list of strings (one
  per line); block scalars (`|`) are not supported by the repo-local
  YAML loader, so use `content_path` for multi-line content
- `content_path` (when `static`) — repo-relative file path; contents
  are inlined verbatim

Exactly one of `command`, `content`, `content_path` must be present.

## Opt-In Signal

Repos opt in by declaring ≥1 `packet_sections` entry. When the list is
empty or the field is omitted, the conditional hard-block in
`critique` SKILL.md stays dormant.

## What The Adapter Does Not Own

- The packet envelope shape (`charness.critique_prepare_packet.v1`) —
  see [prepare-packet.md](./prepare-packet.md)
- Scanner content correctness — adapters point at producers; producers
  decide what they find
- Cross-skill packet sharing — the retro skill, if it later grows a
  prepare-packet contract, reads `.agents/retro-adapter.yaml`'s own
  section slot, not this adapter

## Migration For Existing Repos

A repo that already runs critique can adopt this contract without
touching critique-time behavior: omit `packet_sections` and nothing
changes. To opt in, declare one or more sections and confirm
`prepare_packet.py` produces a packet before invoking critique. The
critique closeout validator only fires the conditional hard-block when
the adapter declares sections.
