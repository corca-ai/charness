---
name: create-skill
description: "Use when creating a new charness skill or improving a migrated one. Defines the canonical portable authoring contract: classify public/support/profile/integration boundaries, simulate failure modes, keep host-specific behavior in adapters and presets, and express external tool dependencies through manifests instead of hidden assumptions."
---

# Create Skill

Use this when the task is to create, migrate, split, or normalize a skill in
`charness`.

## Bootstrap

Every invocation starts here. Read only the files that affect the current change.

```bash
# Required Tools: rg
# 1. charness boundary and current product context
sed -n '1,220p' README.md
sed -n '1,220p' docs/handoff.md 2>/dev/null || true
sed -n '1,240p' docs/roadmap.md 2>/dev/null || true

# 2. existing target or source skill
rg --files skills/public skills/support
sed -n '1,240p' "$SKILL_DIR/../<skill-id>/SKILL.md"
sed -n '1,240p' "$SKILL_DIR/../../support/<skill-id>/SKILL.md"

# 3. external-tool or profile context when relevant
sed -n '1,240p' docs/control-plane.md
sed -n '1,260p' docs/public-skill-validation.md 2>/dev/null || true
sed -n '1,220p' docs/public-skill-dogfood.md 2>/dev/null || true
sed -n '1,260p' integrations/tools/manifest.schema.json
sed -n '1,260p' skills/support/capability.schema.json
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
   - candidate named anchors when a real reasoning frame should be retrieved in the public core
   - any ambient philosophy that should become a behavior rule across adjacent public skills, not only a reference note
   - for each named anchor, the exact move it should retrieve and any factual claim that needs source verification before you compress it
   - simulate cold start, warm start, error recovery, and 5-7 agent failure cases before changing files
3. Freeze the current consumer contract before editing an existing public skill.
   - read the current reviewed dogfood case or scaffold it first with `python3 "$SKILL_DIR/../quality/scripts/suggest_public_skill_dogfood.py" --repo-root . --skill-id <skill-id> --json`
   - decide whether the slice claims `preserve` or `improve` before changing the core trigger or behavior contract
   - if the skill is `evaluator-required`, inspect the maintained scenario surface and current cautilus proof plan before editing so the post-change proof obligation is explicit up front
   - when the checked-in contract is still too vague to freeze honestly, stop and tighten that consumer-facing scenario before broad edits
4. Decide the portability seams.
   - skill body stays generic
   - repo or host specifics move to adapter files or presets
   - optional fields must distinguish `unset` from `explicitly empty`
   - prefer strong defaults and inference over user-facing branches or flags
5. Decide dependency ownership honestly.
   - harness-owned support logic belongs in `skills/support/`
   - if `charness` owns the runtime capability, keep its machine-readable
     metadata next to the support skill as
     `skills/support/<skill-id>/capability.json`
   - external tools and upstream support skills belong in
     `integrations/tools/<tool-id>.json`
   - if an upstream support skill already exists, prefer reference, sync, or a
     thin wrapper over copying
   - if private access is involved, model capability grants, authenticated
     binaries, env fallback, and degradation explicitly instead of hiding
     secret assumptions in the skill body
   - when discovery surfaces should expose the dependency, keep manifest
     metadata rich enough to reveal capability kind and supported access modes
   - when setup prerequisites matter, express them as manifest readiness checks
     instead of burying them in operator prose only
   - if the work is really a repo-owned command-line product, use
     `create-cli` instead of burying CLI lifecycle decisions inside a generic
     skill migration
   - if the skill must ship inside a host plugin bundle, keep discovery,
     manifest, and install-surface proof in packaging, integrations, or the
     owning CLI contract rather than in the public skill body
6. Implement the smallest coherent package.
   - `SKILL.md` contains trigger contract and decision skeleton only
   - treat sparse named person anchors in `SKILL.md` core as a deliberate
     retrieval tool when they materially improve recall of a real reasoning
     frame
   - keep the behavior rule in core when the philosophy should shape repeated
     moves; put factual essence, nuance, and reference contents in
     `references/`
   - move schemas, examples, and theory into `references/`
   - add scripts for deterministic repeated checks, adapter bootstrap, and
     durable artifact handling when the skill would otherwise rely on hand-wavy
     repeated steps
7. Verify before stopping.
   - cold-start test from repo root
   - for public-skill changes, run one realistic consumer prompt instead of stopping at producer-side validators; use `python3 "$SKILL_DIR/../quality/scripts/suggest_public_skill_dogfood.py" --repo-root . --skill-id <skill-id>` to scaffold prompt, repo shape, expected artifact, and acceptance evidence
   - for public-skill semantic changes, decide in the same slice whether [docs/public-skill-dogfood.json](../../../docs/public-skill-dogfood.json), [evals/cautilus/scenarios.json](../../../evals/cautilus/scenarios.json), and/or [charness-artifacts/cautilus/latest.md](../../../charness-artifacts/cautilus/latest.md) should move; do not leave that proof-routing decision implicit
   - trigger collision check against adjacent skills
   - path check for every file named in the skill
   - schema or example validation for any profile, preset, or manifest touched
   - if the skill is meant to be deployable through Claude or Codex plugin
     surfaces, prove the packaging layout and host-visible payload delta at the
     install surface instead of claiming discovery from source-only inspection

## Rules

- Maximize reuse first. Port an existing skill body or reference when it
  already captures the right behavior.
- Do not let a public skill smuggle multiple concepts just because the old repo
  had several narrow expert surfaces.
- Use a named person anchor in the public core when it reliably retrieves a
  real reasoning frame; do not use names as decoration or strip them out when
  the public trigger actually benefits from the anchor.
- When one philosophy should shape several adjacent skills, encode its
  behavioral translation in each core and keep only the anchors that materially
  improve retrieval.
- Keep selection logic in `SKILL.md` core. References should deepen a chosen
  move, not become a second workflow that re-decides when to act.
- Keep expert references source-faithful and minimal. Verify fuzzy or
  non-obvious claims before compressing them into a public skill or reference.
- Host-specific behavior belongs in adapters and presets, not in `SKILL.md`.
- Do not reach for user-facing branches or flags just because the design is
  underspecified. First ask whether the right behavior can be inferred from context, current artifacts, or a stronger default.
- Add a new user-visible branch only when the behaviors are genuinely distinct,
  user-meaningful, and unsafe to infer.
- External tool dependencies must be explicit in manifests and degradation
  rules, not implied by a casual command example.
- When a host may be isolated, prefer grant-first and authenticated-binary
  flows over direct secret-file assumptions.
- Presets are explicit defaults, not hidden behavior changes.
- Use WebSearch explicitly for research steps; do not imply it weakly.
- Never ask users to paste secrets into chat.
- If a skill needs the same bootstrap, adapter resolution, artifact upsert, or
  recovery step more than once, ship a helper script instead of leaving the
  behavior as prose-only ritual.
- Treat public-skill frontmatter and generated AGENTS hints as classifier input,
  not only documentation; prove at least one realistic consumer prompt for the
  changed skill before calling the slice done.
- Do not rewrite an existing public-skill core until you have decided how the
  current intent is frozen: reviewed dogfood, cautilus scenario coverage, or a
  checked-in scenario review artifact.
- For `evaluator-required` skills, treat maintained scenario coverage and
  `cautilus` proof planning as part of the edit contract, not as optional
  closeout commentary after the behavior already changed.
- When adding a high-leverage reasoning or review pattern to one public skill,
  inspect adjacent public skills for obvious propagation opportunities before
  stopping.
- Keep `SKILL.md` concise. If the body approaches 200 lines, move detail into
  `references/`.

## Binary Preflight Philosophy

Public skills must not silently assume non-baseline binaries. If a Bootstrap
step calls a tool outside `CHARNESS_BASELINE` (`sh`, `git`, `python3`, `sed`,
`find`, `awk`, `grep`, and basic coreutils), declare it inline with
`# Required Tools: <name>` and point to `references/binary-preflight.md`.

Preflight is lazy, not eager: only trigger it when a command actually fails
with exit 127 or emits `MISSING_BIN: <name>`. On detection, stop, explain the
missing binary and why the step needs it, propose the mapped install command,
and wait for explicit consent. Auto-install is forbidden. Silent skip is forbidden.

Non-interactive callers use `CHARNESS_BINARY_PREFLIGHT=degraded`, which records
the degraded step in the durable artifact. Do not swallow `command not found`
with `2>/dev/null || true`; either let it fail or guard it with `command -v`.
If a support skill owns the binary, declare the support skill instead of the
binary and let `capability.json` stay the readiness source of truth.

## References

- `references/portable-authoring.md`
- `references/adapter-pattern.md`
- `references/preset-conventions.md`
- `references/integration-seams.md`
- `references/runtime-capabilities.md`
- `references/deployable-skill-packaging.md`
- `references/binary-preflight.md`
- `../create-cli/SKILL.md`
