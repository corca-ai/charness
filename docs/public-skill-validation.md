# Public Skill Validation Tiers

> Status: current
> Source of truth: this page and its linked executable surfaces
> Last verified: 2026-09-02

This document fixes the deeper-validation policy for current `charness` public
skills without making a standalone evaluator part of the normal local bar.

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
- a skill can move upward to a stronger tier later, but should not move
  downward without evidence that the deeper gate is wasted effort

## Prompt-Affecting Changes

When a slice changes repo-owned instruction or prompt surfaces that can steer
agent behavior, use the smallest sufficient deterministic checks before
requesting semantic review. A prompt-affecting diff alone is not a reason to
launch a broad evaluator or create a new standing gate.

Default prompt-affecting surfaces in this repo:

- [`AGENTS.md`](../AGENTS.md) — root agent instruction file: session entry and link index.
- public/support `SKILL.md` trigger contracts
- public/support skill `references/**` that materially steer routing or
  operator-facing behavior
- shared skill references that materially steer routing or operator-facing
  behavior
- `.agents/*-adapter.yaml` entries that change prompt or evaluator behavior

Default proof split:

- `deterministic validation`: schema, adapter, fixture syntax, and proof-artifact
  format checks stay in the local quality bar for every relevant slice
- `scenario review`: inspect one or two representative scenarios or use
  explicit operator review when the
  change is high-leverage enough that "not broken" is weaker than "did the
  intended reader or reasoning behavior actually improve?"

If a behavior claim needs evidence beyond deterministic checks, keep the source
input and the reviewer or consumer-owned evaluator result together. Do not
create a Charness-specific proof artifact merely because a prompt changed.

## Execution Policy

Deterministic local gates own ordinary closeout. Prompt-affecting diffs do not
trigger a live evaluator, generated proof artifact, or new scenario registry by
themselves. When a consumer needs behavioral evidence, use its existing
evaluator or an explicit bounded human review and record the result at the
consumer boundary.

## Intent Classes

Intent is part of the proof contract, not only a chat-side interpretation.

- `prompt_affecting_change`: repo-owned instruction or prompt bytes moved
- `skill_core_change`: public/support `SKILL.md` core changed
- `truth_surface_change`: README or other repo-truth docs changed
- `adapter_contract_change`: repo adapter contract changed
- `cross_repo_communication_change`: guidance for cross-repo issue shaping changed
- `scenario_review_change`: the repo policy says this slice needs semantic
  review in addition to regression proof

## On-Demand Behavioral Review

Behavioral questions that deterministic checks cannot answer should stay
on-demand through an explicit bounded human review or a consumer-owned
evaluator. Do not turn every prompt-affecting change into a standing Charness
evaluation suite.

- repo-owned standing checks still own deterministic seams: packaging,
  validators, adapter bootstrap, helper scripts, and thin acceptance smoke
- consumer repos and reviewers own deeper questions about routing, artifact
  usefulness, recovery, and decision support
- when stronger evidence is requested, preserve the source input and the result
  together at the consumer boundary
- closeout should state when requested proof is missing; it should not hide that
  gap behind a passing markdown or packaging bundle
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
- `hotl`
- `ideation`
- `narrative`
- `critique`
- `quality`
- `release`
- `retro`

### `evaluator-required`

Use this when the skill produces durable artifacts, routing decisions, or
execution guidance whose silent semantic drift is costly enough that maintained
scenario-based evaluation should become part of the normal repo bar once the
standalone evaluator exists.

Current assignment:

- `setup`
- `create-skill`
- `debug`
- `gather`
- `impl`
- `issue`
- `spec`

## Provisional Rationale

- `announcement`, `create-cli`, `ideation`, `narrative`, `critique`,
  `quality`, `release`, and `retro` are valuable, but their output quality
  still depends heavily on human judgment and context setting.
- `hitl` already exists to insert human judgment into a bounded loop, so its
  own quality bar should emphasize operator review rather than pretending the
  whole workflow can be scored automatically.
- `hotl` supervises applied live behavior whose proof quality (packet rigor,
  honest dispositions, staleness handling) is operator judgment; sample it by
  review rather than a standing evaluator suite.
- `critique` now has a stronger canonical subagent contract, but that still
  makes it a poor standing evaluator target. Keep repo-owned seam checks for
  the contract and use on-demand proof or reviewed dogfood for the real
  behavioral question.
- `create-skill`, `gather`, `setup`, `issue`, `spec`, `impl`, and `debug` shape
  later execution or durable repo state. They deserve clear deterministic
  seams and, when a consumer has a real behavioral risk, an explicitly scoped
  review rather than an automatically widened local gate.

## Adapter Requirements

### `adapter-required`

Use this when the skill owns durable artifacts, repo-local normalization
preferences, or bootstrap/runtime seams that would otherwise drift into hidden
host assumptions.

An adapter-owned skill ships `adapter.example.yaml` and a real resolver such as
[quality's resolver](../skills/public/quality/scripts/resolve_adapter.py). An
explicit initializer such as [quality's initializer](../skills/public/quality/scripts/init_adapter.py)
is optional and remains skill-owned; it is not part of the shared adapter requirement.

Current assignment:

- `announcement`
- `create-skill`
- `critique`
- `debug`
- `gather`
- `hitl`
- `hotl`
- `impl`
- `setup`
- `issue`
- `narrative`
- `quality`
- `release`
- `retro`

### `adapter-free`

Use this when the skill can stay portable with repo inspection alone and does
not need a checked-in artifact path or repo-specific bootstrap contract.

Current assignment:

- `create-cli`
- `ideation`
- `spec`

## Fallback Policy

### `allow`

Use this when the skill can continue with inferred defaults without burying a
repo-truth, review-state, or release-policy decision.

Current assignment:

- `create-cli`
- `debug`
- `gather`
- `ideation`
- `impl`
- `issue`
- `critique`
- `retro`

### `visible`

Use this when the skill may continue without a checked-in adapter, but it must
say that it is using inferred defaults and avoid presenting those defaults as a
repo-owned contract.

Current assignment:

- `announcement`
- `create-skill`
- `setup`
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
- `announcement`, `create-skill`, `hotl`, `setup`,
  `quality`, and `spec` still benefit from adapters, but they can continue honestly when the
  skill names the inferred-default boundary instead of pretending the repo
  already declared it.
- the remaining skills are either low-risk enough, narrow enough, or already
  anchored by adjacent artifacts strongly enough that silent fallback is an
  acceptable bootstrap tradeoff.

## Next Step

The next integration session should:

1. revisit any `HITL recommended` skill that gains a cheap, defensible review
   path
2. revisit any `visible` skill that starts rewriting repo-truth or review
   policy surfaces often enough that it should graduate to `block`
3. keep the JSON policy and deterministic dogfood evidence in sync without
   creating placeholder manifests, evaluator artifacts, or fake adapter
   requirements
