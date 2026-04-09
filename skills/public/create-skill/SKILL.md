---
name: create-skill
description: Use when creating a new charness skill or improving a migrated one. Defines the canonical portable authoring contract: classify public/support/profile/integration boundaries, simulate failure modes, keep host-specific behavior in adapters and presets, and express external tool dependencies through manifests instead of hidden assumptions.
---

# Create Skill

Use this when the task is to create, migrate, split, or normalize a skill in
`charness`.

## Bootstrap

Every invocation starts here. Read only the files that affect the current
change.

```bash
# 1. charness boundary and migration context
sed -n '1,220p' README.md
sed -n '1,240p' docs/master-plan.md
sed -n '1,220p' docs/skill-migration-map.md

# 2. existing target or source skill
rg --files skills/public skills/support
sed -n '1,240p' skills/public/<skill-id>/SKILL.md
sed -n '1,240p' skills/support/<skill-id>/SKILL.md

# 3. external-tool or profile context when relevant
sed -n '1,240p' docs/control-plane.md
sed -n '1,260p' integrations/tools/manifest.schema.json
sed -n '1,240p' profiles/profile.schema.json
sed -n '1,220p' presets/README.md
```

If the target file does not exist yet, inspect the closest existing upstream
skill before writing from scratch.

## Workflow

1. Classify the artifact before editing.
   - public skill: one user-facing concept
   - support skill: teaches tool usage without becoming product philosophy
   - profile: default bundle of public and support skills
   - preset: opt-in default values for adapters or hosts
   - integration: external ownership contract, never a hidden dependency
2. Write a short brief.
   - concept, audience, trigger, external dependencies, accumulated state
   - simulate cold start, warm start, error recovery, and 5-7 agent failure
     modes before changing files
3. Decide the portability seams.
   - skill body stays generic
   - repo or host specifics move to adapter files or presets
   - optional fields must distinguish `unset` from `explicitly empty`
   - prefer strong defaults and inference over user-facing modes or options
4. Decide dependency ownership honestly.
   - harness-owned support logic belongs in `skills/support/`
   - external tools and upstream support skills belong in
     `integrations/tools/<tool-id>.json`
   - if an upstream support skill already exists, prefer reference, sync, or a
     thin wrapper over copying
5. Implement the smallest coherent package.
   - `SKILL.md` contains trigger contract and decision skeleton only
   - move schemas, examples, and theory into `references/`
   - add scripts for deterministic repeated checks, adapter bootstrap, and
     durable artifact handling when the skill would otherwise rely on hand-wavy
     repeated steps
6. Verify before stopping.
   - cold-start test from repo root
   - trigger collision check against adjacent skills
   - path check for every file named in the skill
   - schema or example validation for any profile, preset, or manifest touched

## Rules

- Maximize reuse first. Port an existing skill body or reference when it
  already captures the right behavior.
- Do not let a public skill smuggle multiple concepts just because the old repo
  had several narrow expert surfaces.
- Host-specific behavior belongs in adapters and presets, not in `SKILL.md`.
- Do not reach for user-facing modes or options just because the design is
  underspecified. First ask whether the right behavior can be inferred from
  context, current artifacts, or a stronger default.
- Add a mode or option only when the behaviors are genuinely distinct,
  user-meaningful, and unsafe to infer.
- External tool dependencies must be explicit in manifests and degradation
  rules, not implied by a casual command example.
- Presets are explicit defaults, not hidden behavior changes.
- Use WebSearch explicitly for research steps; do not imply it weakly.
- Never ask users to paste secrets into chat.
- If a skill needs the same bootstrap, adapter resolution, artifact upsert, or
  recovery step more than once, ship a helper script instead of leaving the
  behavior as prose-only ritual.
- Keep `SKILL.md` concise. If the body approaches 200 lines, move detail into
  `references/`.

## References

- `references/portable-authoring.md`
- `references/adapter-pattern.md`
- `references/preset-conventions.md`
- `references/integration-seams.md`
