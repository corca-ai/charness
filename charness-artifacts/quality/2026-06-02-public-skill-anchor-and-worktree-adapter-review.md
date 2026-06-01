# Public Skill Anchor And Worktree Adapter Review

Date: 2026-06-02
Scope: public skill core incident anchors, skill ergonomics prevention, and repo-local adapter dogfood.

## Scenario Review Decision

`scripts/plan_cautilus_proof.py --repo-root . --json` reported `next_action: none`,
`run_mode: ask`, and `scenario_registry_review_required: true`. No live Cautilus
run was requested or required.

Reviewed dogfood suggestions for `achieve`, `find-skills`, `handoff`, `issue`,
`quality`, and `setup`. The edited public skill core behavior is unchanged:
the slice removes issue-number and dated incident provenance from core wording,
but preserves the same trigger, routing, artifact, and closeout contracts.

Reviewed `evals/cautilus/scenarios.json`:

- `find-skills`: existing `find-skills-local-first` coverage still applies.
- `handoff`: existing `handoff-adapter-bootstrap` coverage still applies.
- `issue`: existing `issue-sibling-search-concept-fixtures` and
  `representative-skill-contracts` coverage still applies.
- `setup`: existing `setup-adapter-bootstrap`, `setup-inspect-states`, and
  `setup-compact-skill-routing-discoverability` coverage still applies.
- `achieve` and `quality` are `hitl-recommended`, not evaluator-required in this
  planner result; reviewed dogfood contracts are sufficient for this wording and
  gate-rule slice.

Decision: no scenario registry change. The new deterministic prevention is the
`skill_ergonomics_gate_rules` pair `issue_anchor_in_core` and
`dated_incident_in_core`, backed by unit tests and enabled in this repo's quality
adapter.

## Adapter Inventory

`validate_adapters.py` now passes with 15 resolver/YAML pairs after adding
`.agents/worktree-adapter.yaml`.

Repo-local adapters present:

- `create-skill`, `critique`, `handoff`, `hitl`, `narrative`, `quality`,
  `release`, `retro`, `setup`
- integrations: `t-events`, `usage-episodes`, `worktree`

Public skills with adapter examples but no repo-local adapter:

- `announcement`, `debug`, `find-skills`, `gather`, `impl`, `issue`

Decision: do not seed these six in this slice. Their resolvers explicitly report
valid fallback defaults, and the current task did not expose a missing
repo-local contract for them. `worktree` is different: public `impl`/`hitl`
bootstrap treats worktree readiness as a mutate-phase guard, and
`charness worktree create --prepare` surfaced a concrete missing-adapter failure.

## Dogfood Gap

Why the worktree adapter was missing:

- `setup` already had a `seed_worktree_adapter.py` helper and an inspection rule.
- The inspection rule recommends the adapter when a hook manager is detected or
  `git worktree list` reports more than one worktree.
- Before this task created an isolated worktree, this checkout did not have the
  active-worktree signal; no lefthook/husky/simple-git-hooks signal was present.
- Therefore normal setup dogfood did not force `.agents/worktree-adapter.yaml`
  into this repo.

Why dogfood still missed a bug:

- The seed helper rendered a manifest without `repo` and `language`, but
  `validate_adapters.py` requires `repo`.
- That means even when the helper was used, the generated adapter could be
  invalid until manually repaired.

Applied prevention:

- `.agents/worktree-adapter.yaml` is now present and validates.
- `seed_worktree_adapter_lib.py` now renders `repo: <repo-dir>` and
  `language: en`.
- `test_seed_worktree_adapter.py` checks the rendered fields so the helper cannot
  regress silently.
