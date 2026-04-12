# Quality Review
Date: 2026-04-12

## Scope

Pre-skill-update classification pass for which verification surfaces should
stay in the standing hook bar versus move to explicit on-demand
self-validation.

## Current Gates

- `./scripts/run-quality.sh` is the canonical local gate.
- `.githooks/pre-push` enforces that gate in clones that installed
  `./scripts/install-git-hooks.sh`.
- The standing bar currently includes direct validators, markdown/doc checks,
  security and supply-chain checks, `run-evals`, `check-duplicates`, and a
  monolithic `pytest -q`.
- Runtime summaries land in `skill-outputs/quality/runtime-signals.json`.

## Runtime Signals

- The dominant local cost is still `pytest -q` at about `23-24s`.
- The next most expensive standing commands are `check-secrets` at about `4s`
  and `check-markdown` at about `2.4s`.
- `run-evals` stays around `1.2s` and `check-duplicates` around `0.5s`.

## Coverage and Eval Depth

- Standing deterministic coverage exists for packaging, adapters, docs,
  security, quality-runner behavior, managed CLI/control-plane seams, and
  repo-owned smoke evals.
- Real Claude/Codex install visibility and Codex cache refresh behavior remain
  HITL/operator-run proof, not repo-local deterministic coverage.

## Standing vs On-Demand Draft

- `KEEP_IN_HOOK`: all direct validators already called by
  `./scripts/run-quality.sh`, plus `run-evals` and `check-duplicates`.
- `KEEP_IN_STANDING_PYTEST_SUBSET`: `tests/charness_cli/*`,
  `tests/control_plane/*`, `tests/quality_gates/*`, and
  `tests/test_plugin_preamble.py`.
- `FIRST_ON_DEMAND_CANDIDATES`: `tests/test_gather_google_workspace.py`,
  `tests/test_notion_support_export.py`, and
  `tests/test_list_external_links.py`.
- `HITL_ONLY`: interactive Codex cache refresh, Claude/Codex plugin
  visibility after update, and multi-machine install/update dogfood.
- `SPLIT_NEXT`: replace the single standing `pytest -q` label with an explicit
  standing subset plus an explicit on-demand self-validation surface.

## Healthy

- Most repo contracts already have direct deterministic owners.
- Maintainer-local enforcement is explicit: checked-in `pre-push`, installer,
  and validator all exist.
- `run-evals` and `check-duplicates` are cheap enough that they are not the
  first demotion targets.

## Weak

- The current standing `pytest` label hides a policy question because core
  CLI/control-plane regressions are mixed together with narrower helper-script
  proofs.
- Some public skills still lack an adapter-requirement classification.
- Real-host update proof and live advisory/audit behavior still sit outside the
  deterministic local bar.

## Missing

- No repo-owned manifest yet records `reason`, `trigger`, and `owner` when a
  test moves out of the hook.
- No maintained evaluator-backed `cautilus` scenarios yet exist for the
  `evaluator-required` skills.

## Deferred

- Any broader host-packaging strategy beyond the current checked-in install
  surface.
- Any online advisory gate that would add new flaky network/tooling ownership.

## Commands Run

- `./scripts/run-quality.sh`
- `pytest --durations=15 -q`

## Recommended Next Gates

- Add an explicit validation matrix for `standing` versus `on-demand`.
- Split `pytest` into named subsets before removing any coverage from the hook.
- If helper/support tests move out of the hook, give them a repo-owned home
  such as `scripts/self-validate/` plus machine-readable metadata.
- Keep real host proof in handoff/state artifacts instead of pretending it is
  standing pre-push automation.

## History

- [2026-04-09 through 2026-04-10 archive](history/2026-04-09-through-2026-04-10.md)
