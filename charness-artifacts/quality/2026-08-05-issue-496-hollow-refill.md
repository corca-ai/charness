# Quality Review
Date: 2026-08-05
Title: Issue 496 Hollow Refill Current Lifecycle

## Scope

Target boundary: the exact nested `mutation_testing.commands` refill fixture,
the narrow inert-default predicate, current top-level bootstrap conflict
behavior, source/plugin parity, and the #496 deferred-work closeout. No generic
empty-value policy or new leaf-warning consumer is proposed.

## Current Gates

Focused bootstrap, absence, and policy-merge proof passed 75 tests. Source and
plugin bootstrap-lib/lifecycle files are byte-identical. The current and
historical critique artifacts validate with current packet bindings; the
resolution critique and closeout draft returned valid/delegated and
`draft_verified`. A standalone real CLI fixture readback returned conflict,
preserved adapter bytes, safe migration guidance, no dotted hollow-leaf
surfaces, and stderr warning output. Remote CI and issue readback are pending
the carrier commit and publish; they are not claimed here.

## Runtime Signals

- runtime source: standalone temporary-repository CLI fixture; timing capture is
  missing, and no production timing capture was required for this deterministic
  configuration slice. <!-- reproduction-source -->
- runtime hot spots: not measured; focused pytest and CLI readback are the
  relevant local channels.
- coverage gate: focused standing proof, critique validation, closeout draft
  validation, and source/plugin parity passed.
- evaluator depth: deterministic gates only; Cautilus was not invoked under its
  ask-before-run contract.

## Healthy

- The exact full+summary fixture keeps real commands and does not surface
  omitted `commands.dry_run` or `.sample` as current dotted changes.
- Missing `commands.summary` remains reportable; explicit empty optional slots
  remain distinct; meaningful empty `prompt_asset_policy.exemption_globs` is
  not suppressed.
- Current ordinary bootstrap preserves adapter bytes on semantic conflict and
  directs the operator to review the top-level surface and explicitly rerun
  with `--migrate` or edit manually.
- Source/plugin parity is byte-identical and complete payload/stderr parity is
  asserted by the fixture.
- The issue resolution critique records the owner split and fresh-eye evidence;
  the carrier names a behavior verdict from a distinct CLI channel.

## Weak

- `_subkey_refills` and its narrow producer filter remain dead-but-deferred
  implementation provenance after the #507 lifecycle refactor; no current
  consumer is claimed for them.
- The standalone CLI fixture seeds a minimal temporary repository and proves
  the operator entrypoint locally, not an installed host/provider roundtrip.

## Missing

- Remote Quality Core and GitHub issue state readback are intentionally pending
  the commit/push boundary.
- Installed-host, provider, and live-agent rendering behavior remain
  unobservable in this repository and are not claimed.

## Deferred

- Remove or retire the dead producer/report provenance only when a concrete
  recurrence, consumer, or cleanup slice justifies widening #496.
- Do not generalize empty-value semantics, top-level symmetry, or sub-key
  deliberate absence from this fixture.

## Advisory

- structural review result (`artifact: charness-artifacts/critique/2026-08-05-issue-496-resolution-critique.md`): the current owner is split between
  `skills/public/quality/scripts/bootstrap_adapter.py` and
  `scripts/quality_bootstrap_lifecycle.py`; no new quality gate is needed
  (`charness-artifacts/critique/2026-08-05-issue-496-resolution-critique.md`).
- prose review result (`artifact: charness-artifacts/issue/2026-08-05-issue-496-closeout-body.md`): historical leaf-warning language is explicitly marked
  pre-#507 and current operator guidance is conflict-preserving and actionable
  (`charness-artifacts/issue/2026-08-05-issue-496-closeout-body.md`).
- inventory advisory (command: `scripts/run_standing_pytest.py`): no new inventory was needed; the exact focused command
  (`scripts/run_standing_pytest.py`), standalone CLI output summary, parity
  checks, and critique packet identity are recorded above and in
  `charness-artifacts/issue/2026-08-05-issue-496-closeout-body.md`.

## Delegated Review

- Delegated Review: satisfied — the required fresh-eye judgment ran through
  four bounded windows plus one unnamed delivery retry, with clean boundary
  fingerprints and current packet/artifact bindings.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): not_applicable — no standing slow-gate scope changed.

## Commands Run

- `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_quality_bootstrap.py --pytest-target tests/quality_gates/test_quality_bootstrap_absence.py --pytest-target tests/quality_gates/test_quality_policy_merge.py` — 75 passed.
- `cmp -s scripts/quality_bootstrap_lib.py plugins/charness/scripts/quality_bootstrap_lib.py` and lifecycle mirror check — passed.
- `python3 scripts/validate_critique_artifacts.py --repo-root . --paths charness-artifacts/critique/2026-08-05-issue-496-resolution-critique.md --include-worktree` — passed.
- `issue_tool.py validate-closeout-draft --classification deferred-work` — `draft_verified`.
- Standalone temporary-repository invocation of `skills/public/quality/scripts/bootstrap_adapter.py` — conflict, no dotted command surfaces, migration guidance, stderr warning, adapter preserved.
- Remote Quality Core and `verify-closeout --expect-state CLOSED` — pending publish; no remote claim yet.

## Recommended Next Quality Moves

- passive — because no current consumer recurrence exists, capability_needed=cleanup consumer ownership; next_center=quality
  bootstrap refill provenance; transformation=remove or repurpose dead
  `_subkey_refills` only with a concrete consumer; proof_boundary=producer
  report ownership; enforcement_posture=no-gate until recurrence.
- passive — because local CLI proof is explicit and the host capability is unavailable, capability_needed=installed/provider CLI roundtrip; next_center=public
  bootstrap entrypoint; transformation=run a host-level fixture if that
  capability becomes available; proof_boundary=operator invocation channel;
  enforcement_posture=no-gate because local behavior is already explicit.

## History

- [Previous quality review](history/2026-07-19-portable-proof-path-learning-review.md)
