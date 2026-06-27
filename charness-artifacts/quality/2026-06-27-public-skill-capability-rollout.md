# Quality Review
Date: 2026-06-27

## Scope

Target boundary: public-skill capability/north-star rollout after the completed
`create-cli` pilot. Mutated rollout targets: `create-skill`, `ideation`,
`spec`, `impl`, `narrative`, `debug`, `quality`, `issue`, `achieve`, `hitl`,
`critique`, `setup`, `handoff`, `gather`, `hotl`, and `announcement`; no
all-public-skill migration claim is made.

Ambient repo findings: existing v0.56.7 release WIP is ignored for this local
design-skill goal. Skill-ergonomics host-surface heuristic hits are mostly
portable-package review prompts, not direct capability-migration failures.

## Current Gates

- `check_goal_artifact.py --pursue-ready` passed for
  `charness-artifacts/goals/2026-06-27-capability-first-skill-rollout.md`.
- `inventory_skill_ergonomics.py --summary` scanned 24 skill packages and
  reported `finding_status=heuristics_present`; prose review remains required.
- `plan_quality_run.py --target-skill ... --json` resolved the target-skill
  structural packet for each mutation slice.

## Runtime Signals

- runtime source: missing; timing capture is not the subject of this audit.
- runtime hot spots: unavailable; timing capture was intentionally not
  refreshed.
- coverage gate: broad pytest was not run; focused skill/doc validation passed
  after each mutation and mirror sync. Broad pytest remains out of scope because
  this is local skill/design work with unrelated release WIP.
- evaluator depth: deterministic-gates-only; Cautilus planner reported
  `next_action: none` and required scenario review only, not live execution.

## Healthy

- `quality` now emits `Recommended Next Quality Moves` and the planner packet
  asks for `capability_needed`, `current_centers`, `next_center`,
  `proof_boundary`, and `enforcement_posture`.
- `create-cli` already has the concrete pilot hook, so it was not re-mutated in
  this continuation.
- `quality` now requires skill-design findings to name the capability or
  capability failure before proposing a gate, helper, or wording change.
- Fresh-eye review found no reflexive gate addition in the later slices.

## Weak

- `announcement` is a minor output-shape reinforcement, not a strong new
  workflow decision point; keep it classified as closeout shape, not major
  capability redesign.
- `find-skills` and `retro` were intentionally left unchanged because current
  wording is already capability-native enough that the next edit looked like
  vocabulary churn absent a concrete failure.

## Missing

- No public-skill-wide migration proof exists. This artifact is a rollout matrix
  and claim boundary, not a completion claim for every support file, scenario, or
  evaluator fixture.
- `release` remains non-claimed and out of scope because existing v0.56.7 release
  WIP is dirty and release carries irreversible-boundary proof obligations.

## Deferred

- Apply this lens to additional public or support surfaces only through separate
  failure-backed slices, not vocabulary sweeps.
- `release` is deferred because existing release WIP is dirty and this goal
  explicitly excludes version/publish work.
- `find-skills` and `retro` should remain unchanged unless a concrete
  capability-routing or retrospective-memory failure appears.

## Advisory

- structural review result: command `plan_quality_run.py --target-skill
  create-skill --json` says public-skill improvement starts from consumer
  capability, not form or gate language.
- prose review result: command `inventory_skill_ergonomics.py --summary` found
  mostly host-surface prompts; the manual gap was `create-skill` lacking
  current/next center freeze.
- rollout matrix result: the goal artifact now records changed skills,
  intentionally unchanged skills, release deferral, and global non-claims.

## Delegated Review

- Delegated Review: completed — slice review remediated the `create-skill`
  proof-boundary and universal-sequencing risks; final rollout review found the
  goal and quality artifacts stale after later slices, which this revision
  fixes.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): not_applicable because this slice does not recommend moving
  or weakening standing gates.

## Commands Run

- quality planner: default plus target probes for each mutated public skill.
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
  completed for `create-skill`, `ideation`, `spec`, `impl`, `narrative`,
  `debug`, `quality`, `issue`, `achieve`, `hitl`, `critique`, `setup`,
  `handoff`, `gather`, `hotl`, and `announcement`.
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
- complete carry capability through the changed public-skill surfaces — each
  target has dogfood freeze and no live Cautilus claim.
- passive stop mutating non-release public skills in this loop — the remaining
  candidates are either already capability-native enough (`find-skills`, `retro`)
  or excluded (`release`).
- passive keep `release` out of this rollout until v0.56.7 WIP is reconciled
  because release has irreversible-boundary proof obligations.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
