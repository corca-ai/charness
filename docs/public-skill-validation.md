# Public Skill Validation Tiers

This document fixes the deeper-validation policy for current `charness` public
skills now that the standalone evaluator product boundary is wired into the
repo, but before maintained evaluator scenarios are part of the normal local
bar.

Canonical machine-readable policy lives in
[docs/public-skill-validation.json](./public-skill-validation.json). This
markdown file stays as the human-readable narrative and rationale layer for the
same assignments. Reviewed consumer-dogfood cases live in
[docs/public-skill-dogfood.json](./public-skill-dogfood.json).
When a new public skill is missing from the policy, run
`python3 scripts/suggest_public_skill_validation.py --repo-root .` to list the
bucket choices before editing the JSON.

## Purpose

- keep repo-owned smoke, lint, validator, and bootstrap checks as the baseline
  for every public skill
- decide which skills need routine human review, evaluator scenarios, or both
- decide which skills must ship checked-in adapter contracts versus which can
  stay adapter-free honestly
- decide whether missing-adapter behavior is allowed silently, must stay
  visible, or must stop before high-leverage work continues
- keep `cautilus` integration aligned with a fixed validation matrix instead of
  re-deriving validation expectations from scratch

## Baseline Rules

- every public skill must keep passing the repo-owned deterministic bar:
  package validation, adapter bootstrap checks, markdown and link checks, and
  smoke evals when the repo owns them
- public-skill review should also inspect progressive disclosure honesty:
  `SKILL.md` owns selection and sequencing, while references deepen the chosen
  move without becoming a parallel workflow
- load-bearing reviewed consumer prompts should stay explicit in
  [`docs/public-skill-dogfood.json`](./public-skill-dogfood.json); that registry is operator-reviewed evidence,
  not a fake claim of fully automated routing proof
- the tier only describes extra validation beyond that baseline
- the tier is routing metadata, not a claim that local CI already runs a
  distinct standing evaluator path for that skill today
- maintained `cautilus` proof is now part of the repo story: instruction-surface
  dogfood is checked in and should be refreshed when prompt-affecting repo
  surfaces change
- a skill can move upward to a stronger tier later, but should not move
  downward without evidence that the deeper gate is wasted effort

## Prompt-Affecting Changes

When a slice changes repo-owned instruction or prompt surfaces that can steer
agent behavior, plan the matching checked-in `cautilus` proof before closeout.

Default prompt-affecting surfaces in this repo:

- [`AGENTS.md`](../AGENTS.md)
- public/support `SKILL.md` trigger contracts
- public/support skill `references/**` that materially steer routing or
  operator-facing behavior
- `.agents/*-adapter.yaml` entries that change prompt or evaluator behavior

Default proof split:

- `regression proof`: preserve routing, contract boundaries, and the existing
  first-skill shape with `cautilus instruction-surface test --repo-root .`
- `scenario review`: inspect one or two representative scenarios when the
  change is high-leverage enough that "not broken" is weaker than "did the
  intended reader or reasoning behavior actually improve?"
- `improve`: when the slice claims behavioral improvement rather than only
  preservation, also record a baseline compare path with
  `cautilus workspace prepare-compare` plus
  `cautilus mode evaluate --baseline-ref <ref>`

The checked-in artifact should say whether the slice claims `preserve` or
`improve`, list the touched prompt surfaces, record the active intent tags, and
separate regression proof from scenario review when both matter.

## Execution Policy

`cautilus` is on-demand proof, not an always-run closeout side effect.

Repo policy lives in [`.agents/cautilus-adapter.yaml`](../.agents/cautilus-adapter.yaml):

- `run_mode: auto`: the repo allows cautilus proof to run without an extra
  confirmation step when the workflow decides it is needed
- `run_mode: ask`: the repo always asks before cautilus runs
- `run_mode: adaptive`: low-cost regression proof may proceed automatically,
  and short scenario review may run automatically too; explicit confirmation is
  reserved for maintained scenario-registry mutations such as
  [evals/cautilus/scenarios.json](../evals/cautilus/scenarios.json)

`run_slice_closeout.py` should act as a gatekeeper, not as the evaluator
runner: it decides whether proof is required and whether the refreshed artifact
is present, but it should not silently launch cautilus itself.

## Intent Classes

Intent is part of the proof contract, not only a chat-side interpretation.

- `prompt_affecting_change`: repo-owned instruction or prompt bytes moved
- `skill_core_change`: public/support `SKILL.md` core changed
- `truth_surface_change`: README or other repo-truth docs changed
- `adapter_contract_change`: repo adapter contract changed
- `cross_repo_communication_change`: guidance for cross-repo issue shaping changed
- `scenario_review_change`: the repo policy says this slice needs semantic
  review in addition to regression proof

## On-Demand Behavioral Proof

Behavioral contract meaning should default to on-demand proof through
`cautilus` or an explicit HITL workflow, not to ever-widening repo-owned
standing evals.

- repo-owned standing checks still own deterministic seams: packaging,
  validators, adapter bootstrap, helper scripts, and thin acceptance smoke
- `cautilus` or HITL own the deeper question of whether a skill contract still
  produces the intended routing, artifact, or decision support behavior
- checked-in latest artifacts such as [`charness-artifacts/cautilus/latest.md`](../charness-artifacts/cautilus/latest.md)
  are the source of truth for those on-demand runs
- closeout should block when proof is required but missing; it should not hide
  that gap behind a passing markdown or packaging bundle
- `specdown` may project those checked artifacts into a readable report so
  operators can inspect the latest proof, but that viewer page is not the
  underlying evaluator state or storage layer
- public executable spec pages should not fall back to fixed-string source
  guards to simulate semantic proof; those guards belong in lower
  deterministic layers when they are still justified at all

## Tier Definitions

### `smoke-only`

Use this when the meaningful regressions are mostly structural or deterministic,
and deeper semantic review does not add enough signal to justify the ongoing
cost.

Current assignment:

- none

### `HITL recommended`

Use this when the skill still benefits from smoke checks, but output quality is
mostly about judgment, taste, prioritization, or operator usefulness that is
better sampled by deliberate human review than by a standing evaluator suite.

Current assignment:

- `announcement`
- `create-cli`
- `hitl`
- `ideation`
- `narrative`
- `premortem`
- `quality`
- `release`
- `retro`

### `evaluator-required`

Use this when the skill produces durable artifacts, routing decisions, or
execution guidance whose silent semantic drift is costly enough that maintained
scenario-based evaluation should become part of the normal repo bar once the
standalone evaluator exists.

Current assignment:

- `init-repo`
- `create-skill`
- `debug`
- `find-skills`
- `gather`
- `handoff`
- `impl`
- `spec`

## Provisional Rationale

- `announcement`, `create-cli`, `ideation`, `narrative`, `premortem`,
  `quality`, `release`, and `retro` are valuable, but their output quality
  still depends heavily on human judgment and context setting.
- `hitl` already exists to insert human judgment into a bounded loop, so its
  own quality bar should emphasize operator review rather than pretending the
  whole workflow can be scored automatically.
- `premortem` now has a stronger canonical subagent contract, but that still
  makes it a poor standing evaluator target. Keep repo-owned seam checks for
  the contract and use on-demand proof or reviewed dogfood for the real
  behavioral question.
- `create-skill`, `find-skills`, `gather`, `handoff`, `init-repo`, `spec`, `impl`, and
  `debug` shape later execution or durable repo state. Those are the highest
  leverage candidates for maintained scenario evaluation now that `cautilus`
  is the tracked evaluator boundary.

## Adapter Requirements

### `adapter-required`

Use this when the skill owns durable artifacts, repo-local normalization
preferences, or bootstrap/runtime seams that would otherwise drift into hidden
host assumptions.

Current assignment:

- `announcement`
- `debug`
- `find-skills`
- `gather`
- `handoff`
- `hitl`
- `impl`
- `init-repo`
- `narrative`
- `quality`
- `release`
- `retro`

### `adapter-free`

Use this when the skill can stay portable with repo inspection alone and does
not need a checked-in artifact path or repo-specific bootstrap contract.

Current assignment:

- `create-cli`
- `create-skill`
- `ideation`
- `premortem`
- `spec`

## Fallback Policy

### `allow`

Use this when the skill can continue with inferred defaults without burying a
repo-truth, review-state, or release-policy decision.

Current assignment:

- `create-cli`
- `create-skill`
- `debug`
- `gather`
- `ideation`
- `impl`
- `premortem`
- `retro`

### `visible`

Use this when the skill may continue without a checked-in adapter, but it must
say that it is using inferred defaults and avoid presenting those defaults as a
repo-owned contract.

Current assignment:

- `announcement`
- `find-skills`
- `handoff`
- `init-repo`
- `quality`
- `spec`

### `block`

Use this when the missing adapter would make the skill invent repo truth,
human-review state, or release policy too early. These skills should stop to
shape or scaffold the adapter before proceeding in earnest.

Current assignment:

- `hitl`
- `narrative`
- `release`

## Fallback Rationale

- `hitl`, `narrative`, and `release` mutate high-leverage review, truth, or
  publication surfaces. Silent fallback here creates convincing but
  ungrounded repo behavior, so the safe default is to stop.
- `announcement`, `find-skills`, `handoff`, `init-repo`, `quality`, and
  `spec` still benefit from adapters, but they can continue honestly when the
  skill names the inferred-default boundary instead of pretending the repo
  already declared it.
- the remaining skills are either low-risk enough, narrow enough, or already
  anchored by adjacent artifacts strongly enough that silent fallback is an
  acceptable bootstrap tradeoff.

## Next Step

The next integration session should:

1. decide whether any current `HITL recommended` skill now has a cheap,
   defensible evaluator path
2. widen `cautilus` proof beyond instruction-surface cases when a public skill
   claim needs stronger held-out or A/B evidence
3. revisit any `visible` skill that starts rewriting repo-truth or review
   policy surfaces often enough that it should graduate to `block`
4. keep the JSON policy, adapter gate, maintained scenario registry, and
   checked-in cautilus proof artifact in sync
   without creating placeholder manifests or fake adapter requirements
