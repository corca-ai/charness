# Quality Review
Date: 2026-05-20

## Scope

Current slice: critique and harden the agent-browser runtime hygiene surface
after a green quality/push cycle still left a PPID=1 browser daemon tree. The
slice covers standing-gate lifecycle assertions, adapter/integration probe
safety, support script browser cleanup, bounded lock persistence, and probe
timeouts.

## Current Gates

- `run-quality.sh` now includes an assert-only fail-fast
  `agent-browser-runtime-baseline` at the start and
  `agent-browser-runtime-hygiene` at the end; both unset
  `CHARNESS_AGENT_BROWSER_IGNORE_ORPHANS`.
- `agent_browser_runtime_guard.py --assert-no-orphans` provides an
  inspection-only final assertion for orphan daemon trees.
- `check_cli_skill_surface.py` and `validate_integrations.py` block risky
  bare or wrapper-mediated `agent-browser` probes.
- Web-fetch browser fallback now closes the named `agent-browser` session after
  render/network recon and degrades the result if close fails.
- Doctor lock persistence truncates command stdout/stderr and failure details.
- Startup probes, CLI side-effect probes, and the Cautilus wrapper now enforce
  wall-clock timeouts.

## Runtime Signals

- runtime source: `.charness/quality/runtime-signals.json` <!-- reproduction-source --> rendered by
  `render_runtime_summary.py` plus focused
  command output from the hygiene label run.
- runtime hot spots: `render_runtime_summary.py` remains the standing summary
  helper; full `run-quality --read-only` took `79.1s`, with pytest and
  check-coverage still the dominant phases.
- coverage gate: focused pytest for runtime guard, CLI-surface, quality-runner,
  web-fetch cleanup, probe timeouts, and doctor lock payload passed.
- evaluator depth: no Cautilus run; deterministic repo-local hygiene and
  fresh-eye review were the appropriate proof for this external-runtime gate.
- Reproduction probes after cleanup showed `orphan_daemon_count=0` after
  `agent-browser --version`, `agent_browser_runtime_guard.py --doctor-check`,
  `scripts/doctor.py --skip-release-probe`, and
  `check_cli_skill_surface.py --run-probes`.
- The new final gate then caught a stale external shell loop that kept invoking
  `agent-browser open/eval/screenshot`; after cleanup, check-cli and coverage
  passed standalone again.
- Focused runtime hygiene labels passed locally before the broader closeout.

## Healthy

- A green full quality run can no longer silently leave a new agent-browser
  orphan daemon tree behind when the runtime baseline starts clean.
- A dirty runtime baseline now fails fast before other gates instead of
  mutating unrelated local browser state.
- The fix is lifecycle-based rather than pytest-only; non-pytest phases are
  now covered by the final gate.
- Future direct or wrapper-mediated `agent-browser open/get/network/screenshot/snapshot`
  probes are blocked as unsafe standing CLI-plus-skill or integration probes.
- The actual support script that uses browser runtime now owns session close
  and does not return unqualified success on cleanup failure.
- Pytest session cleanup now retries until the runtime is clean or the retry
  budget expires, covering asynchronous daemon shutdown races.
- Large volatile healthcheck output no longer becomes durable lock noise.
- Executable startup, side-effect, and Cautilus evaluator probes cannot hang
  indefinitely.

## Weak

- The exact command that created the previously observed post-push orphan was
  not reproduced from the current local probes.
- The direct-probe denylist is intentionally scoped to `agent-browser`; other
  long-lived external runtimes would need their own classifier.
- The similar-pattern scan found many ordinary `subprocess.run` call sites; the
  fixed ones are the operator-configured executable probes and evaluator
  forwarding surfaces, not every bounded git/doc helper.

## Missing

- No live browser roundtrip was run as part of closeout; focused tests use fake
  binaries and the local hygiene probe validates process state.
- No release/version bump yet, so installed users receive the hardened plugin
  surface after the next update/release path consumes this repo state.

## Deferred

- Generalize probe side-effect classification beyond agent-browser when another
  external runtime shows the same lifecycle risk.
- Add richer runtime-family metadata to integration manifests only if repeated
  command-specific denylist edits start accumulating.

## Advisory

- artifact: fresh-eye review executed via subagents. They identified baseline
  fail-fast, waiver bypass, wrapper-mediated probes, web-fetch cleanup failure,
  executable probe hangs, and baseline mutation risk.
- inventory: similar-pattern scan found adapter probe commands, integration
  healthchecks, support scripts, startup/side-effect probes, Cautilus
  forwarding, and doctor lock payloads as adjacent surfaces; bounded fixes
  shipped for the recurrence paths.

## Delegated Review

- status: executed. Fresh-eye reviewers returned `Act Before Ship` items for
  final `run-quality` hygiene, agent-browser probe blocking, web-fetch cleanup,
  lock output bounding, waiver bypass, wrapper probes, and executable probe
  timeouts.
## Commands Run

- `python3 scripts/agent_browser_runtime_guard.py --repo-root . --cleanup-orphans --execute --json`
- `agent-browser --version`
- `python3 scripts/agent_browser_runtime_guard.py --repo-root . --doctor-check --json`
- `python3 scripts/doctor.py --repo-root . --json --skip-release-probe`
- `python3 scripts/check_cli_skill_surface.py --repo-root . --run-probes --json`
- `pytest -q tests/test_agent_browser_runtime_guard.py tests/test_doctor_lock_payload.py`
- `pytest -q tests/quality_gates/test_cli_skill_surface.py tests/quality_gates/test_quality_runner.py`
- `pytest -q tests/test_web_fetch_support.py::test_acquire_public_url_uses_agent_browser_network_recon_for_collect_intent`
- `pytest -q tests/quality_gates/test_startup_probe_measure.py tests/quality_gates/test_quality_cli_side_effect_probes.py tests/quality_gates/test_run_cautilus_eval.py`
- `pytest -q tests/test_web_fetch_support.py tests/test_web_fetch_cleanup.py && python3 scripts/agent_browser_runtime_guard.py --repo-root . --assert-no-orphans --json`
- `ruff check scripts/agent_browser_probe_policy.py scripts/run_cautilus_eval.py ...`
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- `python3 scripts/doctor.py --repo-root . --json --write-locks --skip-release-probe --tool-id agent-browser`
- `./scripts/run-quality.sh --read-only`
- `python3 scripts/run_slice_closeout.py --repo-root . --ack-cautilus-skill-review`

## Recommended Next Gates

- active `AUTO_EXISTING`: run slice closeout after this artifact update.
- passive `AUTO_CANDIDATE` because only agent-browser currently shows this
  daemon/process pressure: if another external runtime gains similar behavior,
  promote the agent-browser-specific probe classifier into a manifest-driven
  runtime-family side-effect gate.

## History

- [2026-05-14 mutation testing dogfood](history/2026-05-14-mutation-testing-dogfood.md)
- [2026-05-12 archive](history/2026-05-12-quality-review.md)
- [2026-05-10 archive](history/2026-05-10-quality-review.md)
- [2026-04-30 archive](history/2026-04-30-quality-review.md)
- [2026-04-09 through 2026-04-10 archive](history/2026-04-09-through-2026-04-10.md)
