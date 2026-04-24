# Retro: Narrative Adapter Customer Failure

## Mode

session

## Context

The reviewed work unit changed the `narrative` public skill so agents can create
or check repo-local narrative adapters before rewriting README or other
first-touch truth surfaces.

The first pass was executed mostly as a `create-skill` / `impl` style package
change: update the skill body, helper scripts, adapter contract, plugin export,
tests, and proof. That was directionally right for editing a skill package, but
it did not start from the customer repo's first run of `$narrative`.

## Evidence Summary

- Current commit: `73004cc Improve narrative adapter review`
- Relevant skill guidance inspected: `create-skill`, `premortem`, `retro`
- Fresh-eye premortem findings from the work unit
- Direct review checks against `../cautilus`, `../ceal`, and `../crill`

## Waste

- The initial change optimized producer-side correctness before customer-side
  use. It improved the `narrative` package, but did not first ask what would
  happen when a real repo with no adapter, a stale adapter path, or a thin
  adapter ran `$narrative`.
- The first premortem came too late. It caught the important misses only after
  implementation: bad examples, empty scaffold fields, missing repair loop, and
  weak volatile-path detection.
- The available instructions hinted at consumer validation but did not force a
  customer-of-this-skill angle. `create-skill` says to use a realistic consumer
  prompt, and `premortem` offers blast-radius/current-consumer angles, but
  neither makes “run the changed skill as its customer would” a stop gate for
  repo-local skill changes.

## Critical Decisions

- The important correction was to treat the adapter as part of the user-facing
  product surface, not only as configuration. A missing or thin adapter is a
  customer workflow failure, not just a helper-script warning.
- The new `review_adapter.py` moved the workflow from prose advice to a
  deterministic gate. That made `ceal`, `cautilus`, and `crill` failures visible
  before README rewriting.
- Keeping `special_entrypoints` as labels-or-paths avoided overfitting the
  adapter contract to filesystem links only.

## Expert Counterfactuals

- Gary Klein premortem lens: before editing, ask “the customer ran `$narrative`
  and hated the README draft; what happened?” That would have produced
  `ceal`-style missing adapter, `cautilus`-style volatile handoff, and
  `crill`-style stale path probes before implementation.
- Jef Raskin discoverability lens: a workflow is not usable if the user must
  infer the next action from diagnostic JSON. The skill needed a visible
  `review -> repair -> rerun -> draft` loop and scaffold defaults that lead the
  agent toward a usable adapter.

## Next Improvements

- workflow: For public skill changes, start with the changed skill's customer
  journey, not the skill package. Name at least one real or synthetic consumer
  repo and run the first-use path before declaring the design good.
- capability: Strengthen `create-skill` so existing public-skill edits require
  a customer-of-this-skill premortem angle when the change affects adapters,
  examples, bootstrap, or first-touch docs.
- capability: Strengthen `premortem` angle selection with an explicit
  `customer-of-this-capability` angle. The angle should ask what the user or
  downstream agent experiences, not only what code/docs break.
- capability: For repo-local skill customization in other repos, use the same
  principle: validate the changed skill from the repo-local consumer's first
  prompt, including missing adapter, stale adapter, and thin adapter states.
- memory: Keep this lesson in recent retro lessons so future skill edits do not
  stop at producer-side validation.

## Persisted

yes
