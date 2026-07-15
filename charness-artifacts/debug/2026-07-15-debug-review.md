# Debug Review
Date: 2026-07-15

## Problem

`charness update all` in the installed v1.0.10 CLI returned 8,608 bytes of
default stdout because its nested `tool_update.results` still contained all
13 per-tool records. The command exited 1 after three tool updater failures,
but the default response buried their identities in that list.

## Correct Behavior

Given an aggregate tool operation (including `charness update all`), when it
emits its default YAML response, then it must provide aggregate status counts
and the bounded identities requiring attention, not every tool's record.
`--detail` remains the route to complete evidence. A one-tool operation may
keep that tool's compact result because it is not high fan-out. Auto-update
must run only for a recognized installer provenance; an unknown path install
must report a manual action instead of guessing from a manager on PATH.

## Observed Facts

- The installed command `charness update all` reported `response_level:
  summary` at both levels, yet its `tool_update.results` field listed all
  13 tools; captured stdout was 8,608 bytes.
- The result's summary counted `failed: 3`, `manual: 2`, `ok: 2`, and
  `refreshed: 6`; `gitleaks`, `ruff`, and `specdown` had `status: failed`.
- `charness` v1.0.10 at `project_runtime_response()` calls
  `project_tool_response()` for `tool_update`, but
  `project_tool_response()` unconditionally assigns its projected per-tool
  map to `results`.
- The command's `--detail` flag was not present; `main()` continues to ignore
  legacy `--json` exactly as intended.
- The recorded tool command errors were: obsolete `github.com/gitleaks/...`
  module identity, `uv tool upgrade ruff` against a non-uv installation, and a
  403 from Specdown's raw installer. All three binaries still passed doctor.

## Reproduction

- Run installed `charness update all` with no `--detail`; it reproduces the
  nested list and returns its normal nonzero updater status. A fixture-backed
  CLI test can exercise the same aggregate response without real tool writes.

## Candidate Causes

- The runtime projector may have been skipped entirely for `update all`.
- A legacy `--detail` or `--json` path may have selected raw output.
- The nested tool projector may compact each result but never collapse the
  aggregate result collection.
- The three updater failures may be transient upstream errors rather than
  manifest ownership mistakes.

## Hypothesis

- The third cause is true: if an aggregate-aware nested projection omits
  `results` and reports status-grouped attention ids, then fixture-backed
  `update all` default output will have no per-tool records while `--detail`
  retains them. Disconfirmer: inspect the existing projector and run the
  installed v1.0.10 command with no detail flag.

## Verification

- result: confirmed — the outer projector runs and the default flag path is
  active, while `project_tool_response()` always returns `results`; the actual
  installed command matches that control flow. The updater errors are also
  confirmed manifest contract errors: official Gitleaks declares the historical
  `github.com/zricethezav/gitleaks/v8` module, while the other two were guessed
  installers despite path-only provenance.

## Root Cause

The initial compact-output change treated each direct tool operation as compact
because it removed raw probes, but did not distinguish a compact per-tool item
from a compact aggregate response. The runtime projector composed that
per-tool map into `update all` unchanged, so the high-fan-out boundary leaked.
Separately, three manifests equated an executable found on PATH with ownership
by an available updater. That assumption made `update all` fail even though
doctor reported each binary healthy.

## Invariant Proof

- Invariant: when the tool projector receives multiple tool results, the root
  runtime response must surface counts and attention ids before it can claim a
  default summary; per-tool evidence belongs only to `--detail`.
- Producer Proof: `project_tool_response()` derives status counts from all
  tools and can derive attention ids from the same source map.
- Final-Consumer Proof: the installed `charness update all` response is the
  operator-facing aggregate consumer; its fixture-backed regression test and
  a post-release installed run must show no nested `results`.
- Interface-Shape Sibling Scan: `cmd_tool_update`, `cmd_tool_doctor`, and
  `cmd_tool_install` share `project_tool_response()` and therefore inherit the
  aggregate policy.
- Non-Claims: the three real tool updater failures are not attributed yet; this
  response-boundary repair does not claim to infer path-install ownership; the
  manual fallback intentionally leaves that unproven action to the operator.

## Detection Gap

- `tests/charness_cli/test_update_output.py` | its installed `update all`
  assertion explicitly accepted per-tool `results` | assert aggregate default
  output omits `results`, identifies failed/manual tool ids, and keeps details
  only with `--detail`.
- Broad release quality | it validated the mistaken fixture contract and did
  not perform a non-fixture installed aggregate-output size/shape probe | add
  the fixture boundary assertion now; use an installed aggregate command as
  release proof before publishing the follow-up.
- `integrations/tools/*.json` | script-mode updates guessed an installer from
  PATH without an installer-provenance check | represent unknown path installs
  as manual and retain automatic update only through recognized provenance.

## Sibling Search

- Mental model: compacting leaves is sufficient even when a parent aggregates
  an unbounded collection.
- same layer: `project_tool_response()` callers in `cmd_tool_update`,
  `cmd_tool_doctor`, and `cmd_tool_install` | decision: same bug, fix now via
  one aggregate-aware projection policy | proof: static scan plus shared
  function call.
- abstraction up: `project_runtime_response()` nesting `tool_update` |
  decision: same bug, fix now | proof: installed runtime reproduction.
- specialization down: a single explicitly selected tool | decision:
  intentional plain-text or non-rendering boundary is inapplicable; retain one
  compact result because it is bounded | proof: contract decision, to verify
  by focused tests.
- cross-file: tests/charness_cli/test_update_output.py owns the installed
  aggregate CLI fixture and must enforce the final-consumer contract.
- manifest axis: `gitleaks`, `ruff`, and `specdown` update contracts | decision:
  same bug, fix now | proof: persisted command stderr plus dry-run manual
  statuses after the manifest repair.

## Seam Risk

- Interrupt ID: aggregate-yaml-summary-leak
- Risk Class: operator-visible-recovery
- Seam: helper payload -> nested root YAML response -> installed CLI operator.
- Disproving Observation: a default aggregate response with no per-tool
  `results` is still materially large because another unbounded sibling leaks.
- What Local Reasoning Cannot Prove: the live installed command's final shape
  until after the follow-up release is installed and run.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: charness-artifacts/quality/2026-07-15-quality-review.md

## Prevention

- Make the shared tool projector aggregate-aware, expose only status counts and
  bounded attention groups by default, and preserve complete payloads behind
  `--detail`.
- Add a fixture-backed aggregate response regression that fails on any nested
  per-tool `results`, plus a released installed-CLI `update all` proof before
  calling the repair complete.
- Keep speculative installer inference out of the updater: supported package
  provenance may route automatically; path-only installations stay manual until
  a separate design proves a safe classifier.
