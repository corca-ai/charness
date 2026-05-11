# Cautilus Dogfood
Date: 2026-05-11

## Trigger

- slice: 2026-05-11 issue #142 resolve — `announcement` skill gains
  host-extensible `in_progress_sources.kind`, a portable preflight
  (`announcement_preflight_lib.py` + `preflight_sources.py`) that requires
  every adapter-declared source surface to be recorded in the draft
  artifact's `## Source surfaces` section as `collected:` or `unavailable:`
  before delivery, and SKILL.md step 2 + step 7 wording for the new
  contract.
- source: corca-ai/charness#142 — "announcement should collect
  adapter-declared control repos before delivery".
- user approval: explicit approval to run the cautilus refresh in this
  slice after `validate_cautilus_proof.py` flagged the SKILL.md and
  references edits as prompt-affecting.

## Validation Goal

- goal: preserve
- reason: the change adds a portable invariant (preflight) and rewords
  step 2 / step 7 of `announcement` SKILL.md without renaming, removing,
  or rerouting any whole-repo skill trigger. Existing routing fixture
  cases (`checked-in-bootstrap-before-impl`,
  `compact-startup-bootstrap-before-impl`,
  `compact-startup-bootstrap-before-spec`,
  `validation-closeout-routes-before-hitl`, `slow-gate-routes-to-quality`)
  do not dispatch on `announcement` triggers.

## Change Intent

- `prompt_affecting_change` (matched policy patterns
  `skills/public/*/SKILL.md` and `skills/public/*/references/**`)
- `skill_core_change` (`announcement` SKILL.md step 2 record contract +
  step 7 delivery preflight added)
- `truth_surface_change` (slice closeout adds `#142 follow-ups` block to
  `docs/handoff.md` Active deferred follow-ups)
- `scenario_review_change` (one representative routing case reviewed —
  see Scenario Review)

## Prompt Surfaces

- `skills/public/announcement/SKILL.md` (step 2 record contract + step 7
  preflight + References)
- `skills/public/announcement/references/adapter-contract.md`
  (`in_progress_sources` field rewrite)
- `docs/handoff.md` (next-session pointer + #142 follow-ups record)

## Commands Run

- `cautilus eval test --repo-root . --adapter .agents/cautilus-adapter.yaml --fixture evals/cautilus/whole-repo-routing.fixture.json`
- `python3 scripts/validate_cautilus_proof.py --repo-root .`
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`

## Regression Proof

- eval test: 5 passed / 0 failed / 0 blocked, recommendation `accept-now`.
- run artifact: `.cautilus/runs/20260511T025345287Z-run/`
  - summary: `eval-summary.json`; counts 5 passed / 0 failed / 0 blocked.
  - All five cases matched expected routing:
    `checked-in-bootstrap-before-impl`,
    `compact-startup-bootstrap-before-impl`,
    `compact-startup-bootstrap-before-spec`,
    `validation-closeout-routes-before-hitl`, and
    `slow-gate-routes-to-quality`.
- cautilus tool recommendation: `accept-now`.

## Scenario Review

- No mutation to `evals/cautilus/scenarios.json`. The routing fixture
  does not exercise `announcement` triggers; the new SKILL.md wording
  scopes the record + preflight contract to adapters that already
  declare `in_progress_sources`, so no neighboring skill trigger is
  reshaped.
- Fixture case set unchanged from prior accept-now run (#142 slice
  reuses the same five cases).

## Outcome

- recommendation: `accept-now`
- The portable announcement preflight is additive: shape validation
  loosens (kind opens to host-defined identifiers) and adds a new
  delivery-readiness invariant that activates only when an adapter
  declares `in_progress_sources`. Whole-repo routing remains stable.

## Follow-ups

- `skills/public/announcement/scripts/collect_commits.py:38-57` still does
  not consume `in_progress_sources`; a follow-up dogfood that surfaces a
  step 2 record miss would re-promote a collection-side walker.
- shape-only-validator anti-pattern sibling sweep
  (`scripts/quality_adapter_lib.py`, `scripts/cautilus_adapter_lib.py`
  path-list fields) — recorded under `docs/handoff.md` Active deferred
  follow-ups #142 with the re-defer trigger.
