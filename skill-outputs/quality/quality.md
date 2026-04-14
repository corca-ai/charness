# Quality Review
Date: 2026-04-14

## Scope

Repo-wide quality posture after landing the `quality` installable-CLI probe-contract rewrite and dogfooding it against `charness` install/update/doctor/tool surfaces, operator docs, and tool recommendation flow.

## Current Gates

- `./scripts/run-quality.sh` is the canonical standing bar, and `./scripts/self-validate-install-update.sh` remains the on-demand install/update proof.
- `.githooks/pre-push` plus `scripts/validate-maintainer-setup.py` make the maintainer-local gate explicit instead of implied.
- `validate-public-skill-validation`, `validate-cautilus-scenarios`, and `run-evals` keep evaluator-required skill policy tied to maintained scenarios.
- `validate-packaging`, `check-coverage`, `check-secrets`, `check-supply-chain`, and `check-links-external` cover install-surface drift, scoped control-plane coverage, secret posture, supply chain, and external URL health.
- `./charness --help`, `./charness doctor --help`, `./charness update --help`, `./charness reset --help`, and `./charness tool doctor --help` now serve as the concrete probe-layer honesty sample for `quality`.
- `python3 skills/public/find-skills/scripts/list_capabilities.py --repo-root . --recommend-for-skill gather` is the repo-owned exact install/recommendation path for missing-tool follow-up.

## Runtime Signals

- runtime hot spots: `pytest` 56.5s, `check-coverage` 8.9s, `check-secrets` 5.1s, `check-markdown` 2.7s, and `run-evals` 1.8s.
- coverage gate: `python3 scripts/check-coverage.py --repo-root . --json` reports `62.9%` (`741/1178`) against a `60.0%` floor; weakest modules are `support_sync_lib.py` `30.6%`, `install_provenance_lib.py` `55.9%`, `install_tools.py` `57.7%`, and `upstream_release_lib.py` `57.0%`.
- evaluator depth: the maintained cautilus scenario registry exists, but deeper local proof is unavailable in this clone because `cautilus` is missing (`python3 scripts/doctor.py --repo-root . --json --tool-id cautilus`).
- runtime retention: timings stay in `skill-outputs/quality/runtime-signals.json` and rotate into monthly `history/runtime-signals-YYYY-MM.jsonl`.

## Healthy

- one repo-owned standing entrypoint still covers validators, docs, lint, pytest, evals, duplicate detection, and supply-chain checks.
- maintainer-local enforcement is honest: checked-in pre-push hook, repo-owned installer, and standing validator all exist.
- adapter-required public skills fail closed when bootstrap artifacts drift, and evaluator-required skills keep a maintained cautilus scenario registry.
- the installable-CLI probe lens passes on the checked-out repo: `charness` keeps `--help`, `doctor`, `update`, `reset`, and `tool doctor` as distinct seams.
- `README.md`, `INSTALL.md`, `UNINSTALL.md`, and `docs/host-packaging.md` stay aligned with that split and keep managed install, refresh, and host-visible plugin state separate.
- the recommendation flow is specific enough to use operationally: `gws-cli` reports `doctor_status = ok` with provenance and readiness, while `cautilus` reports `install-needed` plus upstream docs and a repo-owned verify command.
- packaging drift, markdown-link discipline, and external URL health are checked by separate owners instead of one noisy mixed gate.

## Weak

- external-link validation still depends on network reachability and upstream host health when online mode is enabled.
- live advisory coverage is opt-in and only as strong as the locally installed npm/pnpm/uv binaries plus registry reachability.
- the `gitleaks`-installed branch was not exercised live in this clone.
- the coverage gate is honest but intentionally scoped; several control-plane modules still sit below `60%` even though the aggregate floor passes.
- the installed managed checkout on this machine may lag the current source checkout, so `--repo-root .` proofs and managed-install proofs should stay separate.

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

## Recommended Next Gates

- `AUTO_CANDIDATE`: add one repo-owned doc/help drift check for the install/update/doctor/reset contract so probe-layer semantics cannot slide in docs or help text independently.
- `AUTO_CANDIDATE`: install `cautilus` on at least one standing maintainer machine and keep the exact install plus verify path in the quality artifact honest when evaluator-backed depth is locally unavailable.
- `AUTO_CANDIDATE`: add one or two traced flows that exercise
  `support_sync_lib.py`, `install_tools.py`, and release-provenance branches
  before raising the `60%` control-plane floor.
- `AUTO_CANDIDATE`: add an opt-in CI or maintainer profile that installs the
  required binaries and runs `check-supply-chain-online` with an explicit
  flaky-host policy.
- `AUTO_CANDIDATE`: exercise the `gitleaks`-installed branch in at least one
  standing environment instead of proving only the fallback path.
- `AUTO_CANDIDATE`: if evaluator depth needs model-backed variance rather than
  repo-local `run-evals`, connect the cautilus scenario runner to a maintained
  external execution surface and artifact contract.

## History

- [2026-04-09 through 2026-04-10 archive](history/2026-04-09-through-2026-04-10.md)
