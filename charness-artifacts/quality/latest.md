# Quality Review
Date: 2026-04-15

## Scope

Repo-wide quality posture after separating quiet pre-push enforcement from the
full `quality` review path, installing the preferred local security/runtime
tooling, removing the experimental `crill` integration, and fixing release
probes to use authenticated GitHub access when available.

## Current Gates

- `./scripts/run-quality.sh` remains the quiet maintainer-local/pre-push gate.
- `./scripts/run-quality.sh --review` is now the fuller quality-review command:
  it replays PASS-phase logs and validates declared external links online.
- `.agents/quality-adapter.yaml` records both `gate_commands` and
  `review_commands`, plus runtime budgets for `pytest`, `check-secrets`,
  `check-coverage`, and `run-evals`.
- `check-secrets` now exercises the installed `gitleaks` fast path on this
  machine instead of falling back to npm `secretlint`.
- `check-links-external` validates only the repo-declared URL list in online
  mode instead of treating each URL as a page to crawl.
- release/tool probes now prefer authenticated `gh api` before falling back to
  unauthenticated GitHub REST calls.

## Runtime Signals

- runtime hot spots: `pytest` `23.8s`, `check-coverage` `8.8s`,
  `check-markdown` `3.6s`, `check-secrets` `2.6s`, and `run-evals` `1.7s`.
- `./scripts/run-quality.sh --review`: `33 passed, 0 failed`, total `39.2s`.
- current budgeted phases: `pytest` `23.8s / 40.0s`, `check-coverage`
  `8.8s / 15.0s`, `check-secrets` `2.6s / 5.0s`, `run-evals` `1.7s / 5.0s`.
- online external links: `30 Total`, `30 OK`, `0 Errors`.
- coverage gate: `65.9%` (`877/1330`) against the `60.0%` aggregate floor.
  Weakest control-plane modules are `upstream_release_lib.py` `46.7%`,
  `install_provenance_lib.py` `55.9%`, `install_tools.py` `64.4%`, and
  `support_sync_lib.py` `65.3%`.
- evaluator depth: maintained repo-local eval scenarios pass; Cautilus is
  installed and its scenario registry remains validation-gated.
- runtime signals continue to persist under `.charness/quality/`.

## Healthy

- Pre-push stays compact while `quality` review now exposes hidden PASS logs,
  online-link status, and runtime budget output.
- `gitleaks` `8.30.1` and `go` `1.26.2` are installed through Homebrew and
  exposed on this machine through `~/.local/bin`.
- `crill` is no longer a tracked `charness` integration while it remains a
  future paid-product candidate.
- GitHub release metadata probes no longer burn the unauthenticated 60/hour API
  bucket when `gh` auth is available.
- Generated plugin export is synchronized with the source tree.

## Weak

- Online link checking remains dependent on upstream host behavior, but the
  current declared URL set resolves without errors or redirects.
- `check-markdown` verbose output is large; useful for review, too noisy for
  pre-push.
- `upstream_release_lib.py` is now a more important seam and has the weakest
  control-plane coverage in the current report.
- Supply-chain online probing is intentionally kept out of default review
  because registry reachability remains an operator-triggered diagnostic.

## Missing

- No deterministic doc/help drift gate yet checks install/update/doctor/reset
  command semantics against first-touch docs.
- No bounded lower+upper test-ratio signal exists yet; test maintenance cost is
  still judged indirectly.

## Deferred

- Keep `check-supply-chain-online` as an operator-triggered only diagnostic.
  Do not add it to default `--review` unless a future policy change assigns
  explicit triage ownership for registry or provider outages.
- Reintroduce `crill` only after the product and support surface stabilize.

## Commands Run

- `brew install gitleaks`
- `brew install go`
- `./scripts/check-secrets.sh`
- `CHARNESS_LINK_CHECK_ONLINE=1 ./scripts/check-links-external.sh`
- `python3 scripts/update_tools.py --repo-root . --json`
- `python3 scripts/validate-integrations.py --repo-root .`
- `python3 -m pytest tests/quality_gates/test_quality_runner.py tests/quality_gates/test_quality_bootstrap.py::test_quality_bootstrap_adapter_records_installed_and_inferred_fields tests/control_plane/test_upstream_release.py`
- `python3 -m pytest tests/quality_gates tests/control_plane tests/test_*.py tests/charness_cli/test_doctor_cache_selection.py tests/charness_cli/test_tool_lifecycle.py`
- `./scripts/run-quality.sh --review`

## Recommended Next Gates

- active `AUTO_CANDIDATE`: add focused tests around `upstream_release_lib.py`
  failure modes, especially `gh` unavailable, `gh` unauthenticated, and 404
  no-release behavior.
- active `AUTO_CANDIDATE`: add one repo-owned doc/help drift check for the
  install/update/doctor/reset contract.
- passive `AUTO_CANDIDATE`: keep `check-supply-chain-online` out of default `--review` because registry reachability is an operator-triggered diagnostic by policy; future work should only document the on-demand command and expected triage owner.

## History

- [2026-04-09 through 2026-04-10 archive](history/2026-04-09-through-2026-04-10.md)
