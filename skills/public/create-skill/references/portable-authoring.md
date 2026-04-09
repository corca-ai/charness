# Portable Authoring Contract

This is the canonical authoring contract for new or migrated `charness`
artifacts.

## Artifact Classifier

Choose the target surface before writing files.

| Artifact | Owns | Does not own | Canonical path |
|---|---|---|---|
| public skill | one user-facing concept | external tool installs, host defaults | `skills/public/<skill-id>/` |
| support skill | harness-owned tool usage guidance | public taxonomy, binary ownership | `skills/support/<skill-id>/` |
| profile | default bundle selection | host-specific secrets or runtime wiring | `profiles/<profile-id>.json` |
| preset | opt-in default values and vocabulary | mandatory hidden behavior | `presets/<preset-id>.md` |
| integration | external ownership, detection, degradation | product philosophy | `integrations/tools/<tool-id>.json` |

If the answer is "two of these at once", split the work.

## Skill Brief

Write this before editing:

```text
Name: create-skill
Audience: agent
Trigger: create, migrate, or improve a charness skill
External: WebSearch, optional tool manifests
Repo-specific: adapter paths, preset ids, output paths
Accumulates: only when the migrated skill needs durable notes
```

## Scenario Simulation

Simulate these before implementation:

1. cold start
2. warm start
3. error recovery
4. agent failure modes

Agent failure modes must be concrete. Good examples:

- edits `SKILL.md` before proving the boundary is public vs support
- hardcodes host or repo names into a portable skill
- hides an external dependency behind a one-off shell command
- copies an upstream support skill even though a manifest plus sync strategy
  would be enough
- treats `unset` and `explicitly empty` as the same thing and keeps re-asking
- leaves rationale in the body instead of moving it into `references/`
- forgets to validate example metadata against the schema it just changed

## Bootstrap Ordering

Put checks in dependency order:

1. required repo context
2. required existing source skill or adjacent files
3. external integration contracts when the skill uses a tool
4. profile or preset context when the change affects bundle defaults
5. cross-session notes only if the skill accumulates state

User-blocking setup comes first. Auto-creatable defaults come after the
blocking checks they depend on.

## Reasoned Proposal Rule

When proposing a non-blocking default, also state why.

Good:

- `portable-defaults` fits because the repo has no host-specific preset schema
  yet and already uses repo-owned metadata under `profiles/` and
  `integrations/`.

Bad:

- use `portable-defaults`

If the user declines a proposed optional field, record that as an explicit
empty or explicit alternative so later runs do not ask again.

## WebSearch Rule

If a step requires outside examples, standards, or upstream tool behavior, call
WebSearch explicitly instead of vaguely asking the agent to "research more".

- search with the exact tool, runtime, or error text
- prefer primary sources such as upstream repos or official docs
- store the conclusion in the changed reference or migration notes instead of
  leaving it as transient chat context

## File Layout

Keep packages minimal:

```text
skills/public/<skill-id>/
  SKILL.md
  references/
  scripts/
skills/support/<skill-id>/
  SKILL.md
profiles/<profile-id>.json
presets/<preset-id>.md
integrations/tools/<tool-id>.json
```

`SKILL.md` is the trigger contract and decision skeleton. Long explanations,
schemas, anti-patterns, and examples belong in `references/`.

## Reuse Rule

Default to porting before inventing:

1. inspect the upstream or prior-repo skill
2. keep the useful workflow spine
3. delete Ceal or host assumptions
4. move variable details into adapters, presets, or integration manifests
5. only then add new material

`create-skill` should preserve good existing structure, not reward rewriting
from zero.

## Verification

Before stopping:

- check trigger overlap with nearby skills
- verify every mentioned path exists
- validate changed JSON examples against repo schemas
- run scripts with `--help` or dry-run paths when present
- reread the body once for hidden host assumptions
