# Quality Review
Date: 2026-05-17

## Scope

Repo-wide setup/quality slice for issue 171 follow-up: shrink the overloaded
`setup` skill core, investigate the repeated `empty gate_rules -> silent pass`
pattern with `debug`, and run an all-skill health sweep across public/support
skills plus release/quality validator seams.

## Current Gates

- `./scripts/run-quality.sh`: 60 passed / 0 failed in 81.7s on the current
  local runner.
- The gate now replays passing phase logs that contain `WARNING`, `WARN`,
  `WEAK`, or `ADVISORY` lines. The expected visible warning in this run is
  `skill_ergonomics_gate_rules_empty` because the repo intentionally still has
  `skill_ergonomics_gate_rules: []`.
- `validate-skill-ergonomics` now reports 22 discoverable skills with disabled
  skill-structure enforcement instead of returning a silent empty payload.
- Explicit `skill_ergonomics_skill_paths` that resolve zero non-vendored skills
  also produce a warning while preserving the advisory-only exit status.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json`, recorded by `scripts/record_quality_runtime.py`, rendered by `render_runtime_summary.py`. <!-- reproduction-source -->
- runtime hot spots: rendered by `render_runtime_summary.py`: `pytest` 58.1s,
  `check-coverage` 40.8s, `validate-inventory-consumption-declaration` 16.2s,
  `check-duplicates` 7.0s, `specdown` 3.5s.
- coverage gate: `check-coverage` passed in 40.8s.
- evaluator depth: `run-evals` passed in 2.0s; no Cautilus run was triggered
  for this deterministic validator/refactor slice.

## Healthy

- `setup` core pressure is repaired: the core now routes optional bootstrap
  seams through [bootstrap-seams.md](../../skills/public/setup/references/bootstrap-seams.md)
  and `inventory_skill_ergonomics.py` no longer flags `setup`.
- Support skills remain small and structurally healthy: `gather-notion`,
  `gather-slack`, `markdown-preview`, and `web-fetch` stay between 27 and 43
  nonempty core lines.
- The main deterministic surfaces are green after sync: skill validation,
  skill contracts, public-skill dogfood, debug/retro artifacts, packaging,
  plugin import smoke, markdown, ruff, pytest, coverage, specdown, evals, and
  runtime budget.
- `release` requested-review gate now distinguishes
  `configuration_status: not_configured` and emits a `WARNING` when
  `requested_review_commands: []`, instead of reporting a bare `ok`.

## Weak

- Skill ergonomics enforcement remains advisory-only because
  `skill_ergonomics_gate_rules` is still empty. This is now visible in
  `run-quality`, not hidden.
- All-skill inventory still shows public core pressure by `core_nonempty_lines`
  outside `setup`; `reference_file_count` confirms those skills generally have
  references, so this is compression backlog rather than missing references.
- `gather`, `find-skills`, `create-cli`, `create-skill`, `hitl`, `ideation`,
  `retro`, and `spec` still show mode/option pressure terms. That is not a
  hard failure under the current adapter, but it is the next ergonomics backlog.

## Missing

- No hard skill-ergonomics rules are enabled yet. The repo now warns on that
  empty-policy state, but does not fail on `long_core`, mode/option pressure,
  or progressive-disclosure risk.
- No CI lane is present in this checkout; security and quality proof remain
  local runner / maintainer-machine enforced.

## Deferred

- Refactors for `gather`, `release`, and other long-core public skills are
  deferred. The urgent `setup` core split and silent-empty-policy repair landed
  first.
- A future release-policy decision can decide whether empty
  `requested_review_commands` should stay warning-only or become blocking for
  release branches.

## Advisory

- Debug artifact `charness-artifacts/debug/latest.md`:
  [empty-policy silent pass](../debug/latest.md) records the root cause,
  detection gap, and sibling search.
- Retro memory `charness-artifacts/retro/2026-05-17-empty-policy-silent-pass.md`:
  [2026-05-17-empty-policy-silent-pass.md](../retro/2026-05-17-empty-policy-silent-pass.md)
  and [recent-lessons.md](../retro/recent-lessons.md) now carry the repeat
  trap: classify empty config as absent surface, intentional opt-out,
  advisory-only, or disabled enforcement before accepting a green gate.
- Fresh `find-skills` inventory was refreshed after public skill reference
  changes because the capability map changed semantically.

## Delegated Review

- status: executed.
- reviewers: `Laplace` audited public skill health and empty-policy patterns;
  `Rawls` audited support/validator/export surfaces and run-quality masking.
- actionable reviewer findings that landed: warning on empty skill ergonomics
  rules, pass-time attention replay in `run-quality`, wrapper discovery-error
  exit parity, plugin export sync, and `release` requested-review empty-command
  warning.

## Commands Run

- `python3 skills/public/quality/scripts/inventory_skill_ergonomics.py --repo-root . --json`
- `CHARNESS_QUALITY_LABELS=validate-skill-ergonomics ./scripts/run-quality.sh`
- `python3 /home/hwidong/.codex/plugins/cache/local/charness/0.5.34/skills/find-skills/scripts/list_capabilities.py --repo-root . --recommend-for-task "setup refactor and empty policy silent pass warning scan"`
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- `pytest -q tests/quality_gates/test_skill_ergonomics_gate.py tests/quality_gates/test_quality_runner.py::test_run_quality_replays_passing_attention_logs tests/quality_gates/test_quality_runner.py::test_run_quality_keeps_passing_non_attention_logs_quiet tests/quality_gates/test_release_publish.py::test_requested_review_gate_warns_when_commands_are_empty tests/quality_gates/test_release_publish.py::test_requested_review_gate_blocks_unavailable_release_record tests/quality_gates/test_release_publish.py::test_requested_review_gate_allows_explicit_waiver`
- `pytest -q tests/quality_gates/test_setup_seed_usage_episodes.py tests/quality_gates/test_setup_retro_memory.py tests/quality_gates/test_docs_and_misc.py`
- `python3 scripts/validate_debug_artifact.py --repo-root .`
- `python3 scripts/build_debug_seam_risk_index.py --repo-root . --check`
- `python3 scripts/build_retro_lesson_selection_index.py --repo-root . --check`
- `python3 scripts/validate_public_skill_dogfood.py --repo-root .`
- `python3 scripts/validate_skills.py --repo-root .`
- `python3 scripts/check_skill_contracts.py --repo-root .`
- `python3 scripts/validate_packaging.py --repo-root .`
- `python3 scripts/validate_packaging_committed.py --repo-root .`
- `./scripts/check-markdown.sh`
- `./scripts/run-quality.sh`

## Recommended Next Gates

- active `AUTO_CANDIDATE`: decide whether Charness itself should opt into one
  low-noise skill ergonomics rule after the remaining long-core backlog is
  priced.
- passive `AUTO_CANDIDATE` because current releases still surface the warning:
  if empty requested-review commands recur during a
  real release, add an adapter field that makes that warning blocking for
  release branches.
- passive `AUTO_CANDIDATE` because this slice already pins replay behavior:
  keep pass-time attention replay in any future
  quality runner refactor so `WARNING`/`WEAK` lines do not disappear behind a
  green summary.

## History

- [2026-05-12 archive](history/2026-05-12-quality-review.md)
- [2026-05-10 archive](history/2026-05-10-quality-review.md)
- [2026-04-30 archive](history/2026-04-30-quality-review.md)
- [2026-04-09 through 2026-04-10 archive](history/2026-04-09-through-2026-04-10.md)
