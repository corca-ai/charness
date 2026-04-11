# Public Skill Validation Tiers

This document fixes the deeper-validation policy for current `charness` public
skills now that the standalone evaluator product boundary is wired into the
repo, but before maintained evaluator scenarios are part of the normal local
bar.

## Purpose

- keep repo-owned smoke, lint, validator, and bootstrap checks as the baseline
  for every public skill
- decide which skills need routine human review, evaluator scenarios, or both
- keep `cautilus` integration aligned with a fixed validation matrix instead of
  re-deriving validation expectations from scratch

## Baseline Rules

- every public skill must keep passing the repo-owned deterministic bar:
  package validation, adapter bootstrap checks, markdown and link checks, and
  smoke evals when the repo owns them
- the tier only describes extra validation beyond that baseline
- until maintained `cautilus` scenarios land in this repo, any
  `evaluator-required` skill still falls back to smoke plus targeted HITL
  sampling
- a skill can move upward to a stronger tier later, but should not move
  downward without evidence that the deeper gate is wasted effort

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
- `hitl`
- `ideation`
- `narrative`
- `quality`
- `release`
- `retro`

### `evaluator-required`

Use this when the skill produces durable artifacts, routing decisions, or
execution guidance whose silent semantic drift is costly enough that maintained
scenario-based evaluation should become part of the normal repo bar once the
standalone evaluator exists.

Current assignment:

- `create-skill`
- `debug`
- `find-skills`
- `gather`
- `handoff`
- `impl`
- `spec`

## Provisional Rationale

- `announcement`, `ideation`, `narrative`, `quality`, `release`, and `retro`
  are valuable, but their output quality still depends heavily on human
  judgment and context setting.
- `hitl` already exists to insert human judgment into a bounded loop, so its
  own quality bar should emphasize operator review rather than pretending the
  whole workflow can be scored automatically.
- `create-skill`, `find-skills`, `gather`, `handoff`, `spec`, `impl`, and
  `debug` shape later execution or durable repo state. Those are the highest
  leverage candidates for maintained scenario evaluation now that `cautilus`
  is the tracked evaluator boundary.

## Next Step

The next integration session should:

1. confirm that the upstream `cautilus` contract can exercise the
   `evaluator-required` set without host-specific assumptions
2. decide whether any current `HITL recommended` skill now has a cheap,
   defensible evaluator path
3. wire the evaluator-required matrix into `quality`, eval fixtures, and the
   control-plane tests without creating placeholder manifests
