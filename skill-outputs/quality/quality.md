# Quality Review
Date: 2026-04-14

## Scope

Repo-wide quality posture after landing `quality` blind-spot prevention follow-on
(`coverage_floor_policy`, anti-anchoring bootstrap, fresh-eye premortem, and
pytest-reference validator guidance) and dogfooding it against `charness`.

## Current Gates

- `./scripts/run-quality.sh` is the canonical standing bar, and `./scripts/self-validate-install-update.sh` remains the on-demand install/update proof.
- `.githooks/pre-push` plus `scripts/validate-maintainer-setup.py` make the maintainer-local gate explicit instead of implied.
- `validate-public-skill-validation`, `validate-cautilus-scenarios`, and `run-evals` keep evaluator-required skill policy tied to maintained scenarios.
- `validate-packaging`, `check-coverage`, `check-secrets`, `check-supply-chain`, and `check-links-external` cover install-surface drift, scoped control-plane coverage, secret posture, supply chain, and external URL health.
- `./charness --help`, `./charness doctor --help`, `./charness update --help`, `./charness reset --help`, and `./charness tool doctor --help` now serve as the concrete probe-layer honesty sample for `quality`.
- `python3 skills/public/find-skills/scripts/list_capabilities.py --repo-root . --recommend-for-skill gather` is the repo-owned exact install/recommendation path for missing-tool follow-up.
- `.agents/quality-adapter.yaml` now carries a portable `coverage_floor_policy`
  block and `spec_pytest_reference_format`, so blind-spot thresholds live in
  adapter data instead of prose-only review habits.

## Runtime Signals

- runtime hot spots: `pytest` 56.5s, `check-coverage` 8.9s, `check-secrets` 5.1s, `check-markdown` 2.7s, and `run-evals` 1.8s.
- coverage gate: `python3 scripts/check-coverage.py --repo-root . --json` reports `62.9%` (`741/1178`) against a `60.0%` floor; weakest modules are `support_sync_lib.py` `30.6%`, `install_provenance_lib.py` `55.9%`, `install_tools.py` `57.7%`, and `upstream_release_lib.py` `57.0%`.
- evaluator depth: the maintained cautilus scenario registry exists, but deeper local proof is unavailable in this clone because `cautilus` is missing (`python3 scripts/doctor.py --repo-root . --json --tool-id cautilus`).
- runtime retention: timings stay in `skill-outputs/quality/runtime-signals.json` and rotate into monthly `history/runtime-signals-YYYY-MM.jsonl`.

## Healthy

- one repo-owned standing entrypoint still covers validators, docs, lint, pytest, evals, duplicate detection, and supply-chain checks.
- maintainer-local enforcement is honest: checked-in pre-push hook, repo-owned installer, and standing validator all exist.
- this repo already demonstrates the adapter-driven local-enforcement pattern
  that `quality` should praise: checked-in hook config, repo-owned hook
  installer/checker, and repo-owned install/update surface for extra binaries.
- adapter-required public skills fail closed when bootstrap artifacts drift, and evaluator-required skills keep a maintained cautilus scenario registry.
- the installable-CLI probe lens passes on the checked-out repo: `charness` keeps `--help`, `doctor`, `update`, `reset`, and `tool doctor` as distinct seams.
- the quality adapter now carries `coverage_fragile_margin_pp` and `specdown_smoke_patterns`, so executable-spec smoke classification and fragile coverage-floor tagging have repo-owned config instead of prose-only thresholds.
- the quality adapter now also carries `coverage_floor_policy` and
  `spec_pytest_reference_format`, so unfloored-file inventory and
  `Covered by pytest:` note shape are explicit adapter knobs.
- `README.md`, `INSTALL.md`, `UNINSTALL.md`, and `docs/host-packaging.md` stay aligned with that split and keep managed install, refresh, and host-visible plugin state separate.
- the recommendation flow is specific enough to use operationally: `gws-cli` reports `doctor_status = ok` with provenance and readiness, while `cautilus` reports `install-needed` plus upstream docs and a repo-owned verify command.
- `quality` now reuses that same structured recommendation payload through `skills/public/quality/scripts/list_tool_recommendations.py` instead of re-deriving missing validation-tool guidance as prose.
- packaging drift, markdown-link discipline, and external URL health are checked by separate owners instead of one noisy mixed gate.
- the bootstrap posture now says the previous `quality.md` is history rather
  than authoritative scope, and the workflow requires a fresh-eye premortem
  before finalizing a report.

## Weak

- external-link validation still depends on network reachability and upstream host health when online mode is enabled.
- live advisory coverage is opt-in and only as strong as the locally installed npm/pnpm/uv binaries plus registry reachability.
- the `gitleaks`-installed branch was not exercised live in this clone.
- the coverage gate is honest but intentionally scoped; several control-plane modules still sit below `60%` even though the aggregate floor passes.
- the installed managed checkout on this machine may lag the current source checkout, so `--repo-root .` proofs and managed-install proofs should stay separate.
- `charness` itself does not keep a standing specdown smoke surface, so the new smoke-vs-behavior ratio path is adapter-backed and tested but not heavily exercised by the current repo artifact.
- `charness` does not yet keep a bounded lower+upper test-ratio gate, so test
  maintenance cost is still judged indirectly rather than by one named signal.

## Missing

- no repo-owned deterministic gate yet checks that install/update docs and CLI help stay probe-contract aligned when command semantics change.
- no local `cautilus` install exists in this clone, so evaluator-backed depth remains unavailable here beyond repo-local smoke plus the maintained scenario registry.

## Deferred

- `profile extends`
- preset structure depth beyond the current markdown-first contract
- any stronger host packaging artifact strategy beyond the checked-in root
  manifests

## Commands Run

- `./scripts/run-quality.sh`
- `git config --get core.hooksPath`
- `find .git/hooks -maxdepth 1 -type f | sort`
- `python3 scripts/check-coverage.py --repo-root . --json`
- `python3 scripts/validate-quality-artifact.py --repo-root .`
- `python3 scripts/validate-packaging.py --repo-root .`
- `./charness --help`
- `./charness doctor --help`
- `./charness update --help`
- `./charness reset --help`
- `./charness tool doctor --help`
- `./charness doctor --repo-root . --json`
- `python3 scripts/plugin_preamble.py --repo-root . --json`
- `python3 scripts/doctor.py --repo-root . --json --tool-id gws-cli`
- `python3 scripts/doctor.py --repo-root . --json --tool-id cautilus`
- `python3 skills/public/find-skills/scripts/list_capabilities.py --repo-root . --recommend-for-skill gather`
- `python3 skills/public/quality/scripts/list_tool_recommendations.py --repo-root .`

## Recommended Next Gates

- active `AUTO_CANDIDATE`: add one repo-owned doc/help drift check for the install/update/doctor/reset contract so probe-layer semantics cannot slide in docs or help text independently.
- active `AUTO_CANDIDATE`: dogfood the new `coverage_floor_policy` reference
  implementation on one repo that already keeps per-file floors so the glob +
  operational meta-check path gets live proof.
- active `AUTO_CANDIDATE`: add one or two traced flows that exercise
  `support_sync_lib.py`, `install_tools.py`, and release-provenance branches
  before raising the `60%` control-plane floor.
- passive `AUTO_CANDIDATE`: add a bounded lower+upper test-ratio signal because
  this repo should only need it if test/support surface starts growing faster than `src`; the
  pattern is useful but not yet the highest-leverage missing proof for
  `charness`.
- passive `AUTO_CANDIDATE`: install `cautilus` because evaluator-backed depth
  is useful but not the
  highest-leverage blocker for this repo's current support-tool slice.
- passive `AUTO_CANDIDATE`: add an opt-in CI or maintainer profile because
  online advisory reachability is still costlier and noisier than the repo's
  default offline bar; that profile should install the required binaries and run `check-supply-chain-online` with an explicit
  flaky-host policy because online advisory reachability is still costlier and
  noisier than the repo's default offline bar.
- passive `AUTO_CANDIDATE`: exercise the `gitleaks`-installed branch because
  the fallback path already proves repo-owned
  behavior and the missing branch does not block current local confidence.
- passive `AUTO_CANDIDATE`: defer model-backed evaluator variance because it
  needs an external execution owner;
  connect the cautilus scenario runner to a maintained
  external execution surface and artifact contract because that depends on an
  external execution owner, not only this repo.

## History

- [2026-04-09 through 2026-04-10 archive](history/2026-04-09-through-2026-04-10.md)
