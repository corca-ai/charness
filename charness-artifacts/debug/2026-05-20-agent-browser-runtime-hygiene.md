# Agent Browser Runtime Hygiene Debug
Date: 2026-05-20

## Problem

After a successful full quality and push cycle, `agent_browser_runtime_guard.py
--doctor-check` found a PPID=1 `agent-browser` daemon tree. The earlier cleanup
hook lived only in pytest session finish, so a green non-pytest quality run
could still leave browser runtime state behind.

## Correct Behavior

Given a repo-owned local/pre-push quality gate, when the gate starts from a
clean agent-browser runtime baseline, then any new orphan daemon tree created
by the gate must be detected before the gate reports success, and failure
should leave an actionable cleanup command.

## Observed Facts

- The orphan tree found after the prior push attempt was removed by
  `python3 scripts/agent_browser_runtime_guard.py --repo-root .
  --cleanup-orphans --execute`.
- Current local probes did not reproduce a new orphan from `agent-browser
  --version`, `agent_browser_runtime_guard.py --doctor-check`,
  `scripts/doctor.py --skip-release-probe`, or `check_cli_skill_surface.py
  --run-probes`.
- `run-quality.sh` ran `check-cli-skill-surface` early but had no final
  runtime hygiene phase after pytest, specdown, eval, inventory, and runtime
  budget phases.
- `tests/conftest.py` cleaned orphans only at pytest session finish.
- `skills/support/web-fetch/scripts/acquire_public_url.py` opened
  `agent-browser` sessions but did not close them after render/network recon.
- `integrations/locks/agent-browser.json` <!-- reproduction-source --> contained a stale unhealthy
  healthcheck payload with volatile process details from an earlier run.
- A stale external shell loop from prior screenshot work was still invoking
  `agent-browser open/eval/screenshot`; it could recreate a daemon after a
  cleanup snapshot that initially had no orphan target.
- Follow-up fresh-eye critique found additional recurrence paths:
  `CHARNESS_AGENT_BROWSER_IGNORE_ORPHANS=1` could waive standing hygiene,
  wrapper-mediated probes could bypass the direct `agent-browser` blocker,
  web-fetch cleanup failure could still return success, and executable probes
  had no wall-clock timeout.
- A second fresh-eye pass found that web-fetch needed post-close runtime proof,
  support readiness and slice-closeout commands needed the same unsafe
  `agent-browser` scanner, and several release/issue/advisory helpers executed
  external tools without subprocess timeouts.

## Reproduction

- Original orphan: post-push `agent_browser_runtime_guard.py --doctor-check`
  found a PPID=1 daemon; later full `run-quality --read-only` caught a stale
  shell loop recreating one before final hygiene.

## Candidate Causes

- A non-pytest quality phase or operator-side browser command created a daemon
  after pytest's session cleanup.
- A stale daemon from earlier browser work survived into a green quality run
  because the gate did not assert a clean runtime baseline at start.
- Direct future `agent-browser` probes in adapter-configured command lists
  could reintroduce browser runtime side effects without lifecycle cleanup.
- The web-fetch support path could leave a session open after render/network
  acquisition.
- Cleanup could report success from an initially clean snapshot even when a
  still-running browser command recreated a daemon moments later.
- Operator-configured startup, side-effect, or evaluator commands could hang a
  standing gate without a timeout.

## Hypothesis

If `run-quality.sh` owns an initial assert-only baseline and a final orphan
assertion, then a green local/pre-push gate cannot silently leave new
agent-browser orphan daemon trees behind. If a direct adapter probe tries to
use browser-runtime commands, `check_cli_skill_surface.py` should block the
probe before it becomes a standing quality command.

## Verification

- Added `--assert-no-orphans` to `scripts/agent_browser_runtime_guard.py`; it
  inspects process state without running `agent-browser`.
- Added fail-fast `agent-browser-runtime-baseline` and final
  `agent-browser-runtime-hygiene` phases to `scripts/run-quality.sh`; the
  baseline is assert-only, and final failure runs best-effort cleanup before
  exiting nonzero.
- The quality runner unsets `CHARNESS_AGENT_BROWSER_IGNORE_ORPHANS` for both
  standing runtime gates.
- Added shared blocking for bare and wrapper-mediated `agent-browser`
  browser-runtime probes such as `open`, `wait`, `get`, `network`, `snapshot`,
  `screenshot`, and direct `--help` in CLI-surface and integration validation.
- Added `agent-browser --session <session> close` cleanup to the web-fetch
  browser fallback after render/network recon; close failure now degrades the
  acquisition result.
- Added timeouts to startup probes, CLI side-effect probes, and
  `run_cautilus_eval.py` forwarding.
- Added lock-safe truncation for doctor command stdout/stderr and failure
  details so stale lock payloads do not preserve large volatile process dumps.
- Focused tests passed for runtime guard, CLI skill surface, quality runner,
  web-fetch cleanup, and lock-safe doctor payload.

## Root Cause

The repo treated agent-browser orphan cleanup as a pytest fixture concern
instead of a standing-gate lifecycle concern. It also treated cleanup as the
same thing as proof, so dirty local runtime state could be hidden or recreated
instead of stopping the gate before later probes.

## Detection Gap

- `tests/conftest.py` cleanup did not prove the whole quality gate ended with
  clean runtime state.
- `run-quality.sh` had no final external-runtime assertion.
- `cli_skill_surface_probe_commands` treated direct binary probes as generic
  read-only commands without classifying long-lived browser runtime risk.
- Integration healthchecks and wrapper-mediated commands were not covered by
  the same unsafe-probe policy.
- Operator-configured executable probes had no timeout boundary.
- Release/issue helper commands and advisory tools had the same unbounded
  external subprocess shape as the original probe timeout gap.
- Doctor locks stored raw command output, making stale runtime observations
  look like current evidence during later investigation.
- Cleanup did not wait and re-inspect for respawned orphan daemon trees.

## Sibling Search

- Mental model: process cleanup can live inside the narrow test framework that
  happened to expose the leak.
- Same layer: adapter-configured probe commands can be side-effectful unless
  classified by runtime family.
- Adjacent operation: support scripts that call long-lived external runtimes
  need lifecycle cleanup in the support script, not only in tests.
- Same evidence layer: lock files should store bounded readiness summaries,
  not volatile process dumps.

## Seam Risk

- Interrupt ID: agent-browser-runtime-hygiene
- Risk Class: operator-visible-recovery
- Seam: external browser daemon lifecycle across support scripts, quality
  probes, pytest, pre-push, and doctor lock persistence.
- Disproving Observation: a full local/pre-push gate that starts from baseline
  assertion, ends with `--assert-no-orphans`, and leaves
  `orphan_daemon_count=0`.
- What Local Reasoning Cannot Prove: every future upstream `agent-browser`
  command remains side-effect-free.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: docs/handoff.md

## Prevention

- `run-quality.sh` now owns baseline assertion and final runtime hygiene.
- `agent_browser_runtime_guard.py --assert-no-orphans` provides an
  inspection-only final gate.
- `agent_browser_runtime_guard.py --cleanup-orphans --execute` now fails if
  cleanup cannot establish a clean baseline after a grace period.
- Direct and wrapper-mediated risky `agent-browser` probes are blocked in CLI
  plus skill surface, integration validation, support readiness, and slice
  closeout surface commands.
- Web-fetch browser fallback closes its named session after render/network
  recon and degrades on close failure or post-close dirty runtime proof.
- Startup probes, CLI side-effect probes, and Cautilus forwarding have
  wall-clock timeouts.
- Release helpers, issue backend helpers, markdown-preview `glow`, online
  supply-chain audit, SLOC inventory, dead-code advisory, and slice closeout
  commands have wall-clock timeouts.
- Pytest session cleanup retries runtime cleanup until clean or timeout.
- Doctor lock persistence truncates volatile command output.

## Related Prior Incidents

- `charness-artifacts/debug/2026-05-12-agent-browser-update-command.md`:
  earlier agent-browser lifecycle work.
- `charness-artifacts/debug/2026-05-20-mutation-execution-score-semantics.md`:
  the slice whose closeout exposed the orphan-runtime hygiene gap.
