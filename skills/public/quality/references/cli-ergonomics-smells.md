# CLI Ergonomics Smells

When a repo ships a CLI, `quality` should treat some command-surface problems as
discoverability smells, not only as copy issues.

Two repeatable smells came up sharply while hardening `Cautilus`, and both are
worth carrying into `charness` quality posture.

## 1. Flat `--help` Lists

If `--help` or a command registry exposes more than roughly ten commands as one
undifferentiated flat list, a first-time reader cannot tell where to start.

Advisory prompt:

- group commands by purpose rather than only by implementation namespace
- keep one obvious "choose your path" entry when the product has multiple
  first-class use cases
- prefer a registry-backed `group` field over hand-maintained prose grouping

`inventory_cli_ergonomics.py` treats a large command registry with no `group`
field as a smell.

## 2. Cross-Archetype Schema Leakage

When one CLI subcommand accepts schemas from multiple archetype namespaces, the
product's internal helper reuse leaks into the user's mental model.

Typical smell:

- subcommand name says `skill`
- accepted schema ids include both `skill_*` and `workflow_*`
- example fixtures are named from the other archetype namespace

Advisory prompt:

- either split the command by archetype
- or re-examine whether the archetypes are actually separate user-facing
  concepts
- keep subcommand, schema id namespace, and example fixture naming aligned 1:1
  when the repo claims first-class archetypes

The helper can inspect an explicit `command-archetypes.json` style contract
when the repo publishes one. Keep the contract machine-readable instead of
re-deriving it from prose-only docs every time.

## Guardrail

These smells stay advisory unless the repo has explicitly chosen a stricter
policy. The goal is to surface discoverability and naming leakage early, not to
force one command taxonomy across all CLIs.
