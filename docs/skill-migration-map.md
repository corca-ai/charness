# Skill Migration Map

This document maps the current Ceal official skills into the target `charness`
taxonomy. It also flags which skills need substantial body rewrites before they
can be considered portable.

## Destination Map

| Current Ceal skill | Target in `charness` | Action |
|---|---|---|
| `gather` | `public/gather` | migrate and review |
| `interview` | absorbed into `public/ideation` | merge, then retire standalone skill |
| `concept-review` | likely inputs/lenses for `public/quality` and architecture references elsewhere | redesign before migrating |
| `impl` | `public/impl` | migrate and review |
| `expert-debugging` | `public/debug` | rename and review |
| `retro` | `public/retro` | rewrite early |
| `handoff` | `public/handoff` | migrate and review |
| `announcement` | `public/announcement` | keep adapter-driven delivery model, continue review |
| `create-skill` | `public/create-skill` | rewrite first among migrated skills |
| `find-skills` | `public/find-skills` | migrate and review against charness packaging model |
| `test-improvement` | absorbed into `public/quality` | merge into broader quality skill |
| `workbench` | transitional support or future external integration | split toward standalone product |
| `agent-browser` | `support/agent-browser` integration layer only | prefer upstream tool ownership |
| `web-fetch` | `support/web-fetch` | keep as harness-owned support skill |
| `specdown` | `support/specdown` integration layer only | prefer upstream tool ownership |

## Rewrite Priority

### Priority 1

- `create-skill`
- `retro`
- `interview` -> `ideation`
- `concept-review` / `test-improvement` -> `quality`

Reason:

- these determine the shape of later migrations and currently carry the most
  taxonomy drift or Ceal-shaped assumptions

### Priority 2

- `spec` new skill
- `impl`
- `debug`
- `gather`
- `handoff`

### Priority 3

- `announcement`
- `hitl` new or migrated collaboration skill
- `find-skills`

### Priority 4

- support skill cleanup
- integration wrappers
- evaluation split from `workbench`

## Review Checklist For Every Migrated Skill

Each skill review session should answer these questions:

1. Is this still a single public concept, or is it smuggling multiple roles?
2. Does the body assume Ceal files, Ceal runtime state, or Slack-specific paths?
3. Can every host-specific behavior move into an adapter or preset?
4. Does the skill give first-use value before asking for too much setup?
5. Are optional proposals explained with reasons?
6. Does the skill distinguish `unset` from `explicitly empty` where that matters?
7. If the skill depends on an external tool, is the dependency represented as an
   integration seam instead of a hidden assumption?

## Known Rewrite Problems

### `retro`

Current issue:

- too short
- too Ceal-shaped
- weak as a portable public skill

Reference direction:

- use `gstack` and `claude-plugins` retro flows as depth references without
  copying their product assumptions directly

### `create-skill`

Current issue:

- improved recently, but still needs to become the canonical charness authoring
  contract

### `interview`

Current issue:

- too small to stand as the long-term public concept
- should become part of `ideation`

### `concept-review` and `test-improvement`

Current issue:

- both have real value, but the public taxonomy should present one `quality`
  skill instead of separate expert surfaces

### `workbench`

Current issue:

- currently a skill-shaped shell around what looks like a future standalone
  evaluation product

## Session Dependency Notes

- Do not migrate many skills before `create-skill` is rewritten.
- Do not finalize `quality` before sample presets are defined.
- Do not move support skills that depend on external tools before the
  integration manifest contract exists.
