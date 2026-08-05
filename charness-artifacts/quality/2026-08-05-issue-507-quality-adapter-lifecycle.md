# Quality Review
Date: 2026-08-05
Title: Issue 507 quality adapter lifecycle review

## Scope

Target boundary: quality adapter bootstrap lifecycle — normalized no-op,
conflict preservation/advisory, and explicit comment-retaining migration.

Ambient repo findings: broad quality and remote CI remain separate closeout
proof; no Cautilus evaluation was run because its contract is ask-before-run.

## Current Gates

Focused bootstrap tests and source/plugin parity tests are the primary evidence
for this slice. Structural skill, documentation, security, and broad closeout
gates remain required before publish.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json`;
  no fresh timing capture was required for this focused adapter slice. <!-- reproduction-source -->
- runtime hot spots: not measured; no timing capture was required for this focused
  adapter slice, and focused test duration is recorded only in the test runner output.
- coverage gate: focused tests passed; changed-line mutation proof remains a
  final closeout/push gate.
- evaluator depth: deterministic-gates-only; Cautilus was not invoked under its
  ask-before-run contract.

## Healthy

- The generic generated-write planner remains a difference detector; lifecycle
  authorization is now owned by the quality bootstrap caller.
- Actual CLI fixtures cover all three outcomes and read adapter bytes back.
- Source and checked-in plugin bootstrap surfaces were regenerated together.

## Weak

- Private consumer-repository and installed-cache behavior is not locally
  observable; local fixtures prove the reconstructed contract only.

## Missing

- No missing deterministic gate was found for this bounded slice; broad and
  remote verification are still pending at closeout time.

## Deferred

- A generic conflict planner for other generated writers is deferred; the
  reviewed markdown-preview sibling already has its own explicit force boundary.
- Comment placement preservation is deferred; migration retains comment text in
  a dedicated block, which is the current acceptance boundary.

## Advisory

- structural review result: command: `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root .`;
  the capability needed is operator control over
  consumer-owned adapter intent; the next center is the pre-write planner and
  CLI report, with no new blocking floor added beyond the explicit migration
  boundary.
- prose review result: `SKILL.md` keeps selection concise and the reference owns
  lifecycle detail; source/plugin docs were synchronized before validation.
- behavior evidence: `pytest -q tests/quality_gates/test_quality_bootstrap.py tests/quality_gates/test_quality_bootstrap_absence.py tests/quality_gates/test_quality_bootstrap_lifecycle.py`
  passed 76 tests, and adapter/YAML regressions passed 55 tests, including
  byte-stable conflict, silent normalized no-op, explicit migration comment
  retention, path-alias refusal, uninterpreted-YAML refusal, and quoted-hash
  parsing.

## Delegated Review

- Delegated Review: executed — unnamed bounded causal reviewer `019fd0b7`
  independently confirmed the write-authorization root cause, and repaired-
  surface reviewers `019fd0c9-31c6` / `019fd0c9-322d` challenged portability,
  parser edges, and counterweight scope. All boundary fingerprints verified
  clean with `drift: []`; final critique is recorded at
  `charness-artifacts/critique/2026-08-05-issue-507-resolution-critique.md`.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof):
  not re-delegated; this review targeted a focused adapter behavior boundary.

## Commands Run

- `python3 skills/public/quality/scripts/resolve_adapter.py --repo-root .`
- `python3 skills/public/quality/scripts/bootstrap_adapter.py --repo-root . --dry-run`
- `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root .`
- `pytest -q tests/quality_gates/test_quality_bootstrap.py tests/quality_gates/test_quality_bootstrap_absence.py tests/quality_gates/test_quality_bootstrap_lifecycle.py`
- `pytest -q tests/quality_gates/test_adapter_lib_yaml.py tests/test_adapter_lib.py tests/quality_gates/test_quality_adapter_block_rejections.py`
- `python3 scripts/export_plugin.py --repo-root . --host codex --output-root . --with-marketplace`
- `python3 scripts/check_skill_surface_preflight.py --repo-root . --path skills/public/quality/SKILL.md --preview-delta 8`

## Recommended Next Quality Moves

- active — capability_needed=proof that the repaired adapter contract survives
  the repository gates; next_center=closeout validation; transformation=run
  focused then locked broad verification; proof_boundary=pre-push gate plus
  remote CI; enforcement_posture=existing-gate-reuse.
- passive — capability_needed=private consumer roundtrip because the external
  repository is unavailable; next_center=external
  consumer fixture; transformation=run the same three-mode matrix when that
  repository is available; proof_boundary=consumer adapter readback because
  local fixtures cannot prove private behavior; enforcement_posture=no-gate
  because the external repository is unavailable in this workspace.

## History

- [Previous quality review](history/2026-07-19-portable-proof-path-learning-review.md)
