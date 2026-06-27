# Quality Review
Date: 2026-06-27

## Scope

Target boundary: public-skill capability/north-star rollout after the completed
`create-cli` pilot. Mutated rollout targets: `create-skill`, `ideation`,
`spec`, and `impl`; no all-skill migration claim is made.

Ambient repo findings: existing v0.56.7 release WIP is ignored for this local
design-skill goal. Skill-ergonomics host-surface heuristic hits are mostly
portable-package review prompts, not direct capability-migration failures.

## Current Gates

- `check_goal_artifact.py --pursue-ready` passed for
  `charness-artifacts/goals/2026-06-27-capability-first-skill-rollout.md`.
- `inventory_skill_ergonomics.py --summary` scanned 24 skill packages and
  reported `finding_status=heuristics_present`; prose review remains required.
- `plan_quality_run.py --target-skill create-skill|ideation|spec|impl --json`
  resolved the target-skill structural packet with quality-move cards.

## Runtime Signals

- runtime source: missing; timing capture is not the subject of this audit.
- runtime hot spots: unavailable; timing capture was intentionally not
  refreshed.
- coverage gate: not run yet for this active rollout slice; focused skill/doc
  validation passed after mutation and mirror sync; broad pytest remains skipped
  because this is an active local rollout slice with unrelated release WIP.
- evaluator depth: deterministic-gates-only; Cautilus planner reported
  `next_action: none` and required scenario review only, not live execution.

## Healthy

- `quality` now emits `Recommended Next Quality Moves` and the planner packet
  asks for `capability_needed`, `current_centers`, `next_center`,
  `proof_boundary`, and `enforcement_posture`.
- `create-cli` already has the concrete pilot hook, so it is not the next
  rollout target.
- `find-skills`, `handoff`, `gather`, and `hotl` already carry native
  capability language.

## Weak

- `create-skill` had only a light sequencing hook; its pre-edit brief did not
  force a capability delta/current-center/next-center freeze before improving
  an existing public skill.
- `achieve`, `critique`, `issue`, and `release` still need separate
  irreversible-boundary review before any capability-surface changes.

## Missing

- No public-skill-wide migration proof exists yet. This artifact is the first
  rollout matrix, not a completion claim.
- `create-cli`, `create-skill`, `ideation`, `spec`, and `impl` are improved
  targets; other public skills remain non-claimed.

## Deferred

- Apply this lens to additional public skills only through separate slices, not
  vocabulary sweeps.
- `release` is deferred because existing release WIP is dirty and this goal
  explicitly excludes version/publish work.
- `achieve`, `critique`, `issue`, and `release` have irreversible-boundary
  responsibilities; any future changes there need separate critique and proof.

## Advisory

- structural review result: command `plan_quality_run.py --target-skill
  create-skill --json` says public-skill improvement starts from consumer
  capability, not form or gate language.
- prose review result: command `inventory_skill_ergonomics.py --summary` found
  mostly host-surface prompts; the manual gap was `create-skill` lacking
  current/next center freeze.
- rollout matrix result: command `for f in skills/public/*/SKILL.md; do ...`
  ranked `create-skill`, `ideation`, `spec`, and `impl`; all four were mutated
  in separate focused slices.

## Delegated Review

- Delegated Review: completed — slice review remediated the `create-skill`
  proof-boundary and universal-sequencing risks; final rollout review found the
  matrix stale, which this revision fixes.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): not_applicable because this slice does not recommend moving
  or weakening standing gates.

## Commands Run

- quality planner: default plus target probes for `create-skill`, `ideation`,
  `spec`, and `impl`.
- quality inventory/dogfood: `inventory_skill_ergonomics.py --summary` and
  `suggest_public_skill_dogfood.py --skill-id create-skill --json`.
- skill preflight: `check_skill_surface_preflight.py` before and after mutation.
- `python3 scripts/validate_skills.py --repo-root .`
- `python3 scripts/check_doc_links.py --repo-root .`
- `./scripts/check-markdown.sh ... create-skill rollout files ...`
- `python3 scripts/validate_skill_ergonomics.py --repo-root .`
- `python3 scripts/validate_cautilus_proof.py --repo-root .`
- `python3 scripts/validate_cautilus_diagnostics.py --repo-root .`
- `python3 scripts/check_skill_ownership_overlap.py --repo-root .`
- `python3 scripts/validate_public_skill_dogfood.py --repo-root .`
- `python3 scripts/validate_packaging.py --repo-root .` and committed variant.
- `python3 scripts/validate_public_skill_validation.py --repo-root .`
- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `run_slice_closeout.py --skip-broad-pytest --ack-cautilus-skill-review`
  completed for `create-skill`, `ideation`, `spec`, and `impl`.
- `cmp -s skills/public/create-skill/SKILL.md plugins/charness/skills/create-skill/SKILL.md`

## Recommended Next Quality Moves

- active strengthen `create-skill` capability brief — capability_needed=public
  skill improvements start from the consumer capability being created or
  repaired; next_center=pre-edit capability brief; transformation=replace the
  short brief/freeze bullets with capability/current-center/next-center/proof
  boundary language without making the sequencing lens universal;
  proof_boundary=consumer dogfood prompt scaffold plus skill preflight, mirror
  sync, and `validate_skills.py`; enforcement_posture=advisory.
- active scenario-review disposition — `create-skill` remains
  evaluator-required, but the changed lines do not alter the trigger,
  frontmatter, or maintained `representative-skill-contracts` scenario mapping;
  `docs/public-skill-dogfood.json` freezes the current contract; no Cautilus
  scenario registry change or live evaluator run is claimed.
- active carry capability through `ideation` -> `spec` -> `impl` — each target
  has dogfood freeze and no scenario registry mutation or live Cautilus claim.
- passive keep `release` out of this rollout until v0.56.7 WIP is reconciled
  because release has irreversible-boundary proof obligations.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
