# Quality Review
Date: 2026-07-18
Title: Quality inventory YAML-first contract

## Scope

Target boundary: agent-facing quality inventory output, its source/plugin ownership,
and the standing-test cost of proving the interface.

Ambient repo findings: the dup ratchet reports older anchor drift and reviewed clone
fingerprint rotations; these are baseline maintenance, not evidence that YAML output is
incorrect. D18 remains deliberately ignored per operator direction.

## Current Gates

- Existing YAML-output contract, focused inventory tests, ruff, packaging validation,
  dup ratchet, and repo read-only quality closeout.
- Maintainer-local enforcement is healthy; worktree doctor and hook inventory passed.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; local default profile.
- runtime hot spots: read-only quality median 55.7s versus 90s budget; pytest median
  35.9s versus 140s budget.
- coverage gate: read-only quality passed 81 phases with 4,742 pytest cases;
  verification-locked closeout and changed-line mutation coverage also passed.
- evaluator depth: deterministic-gates-only; this interface contract is fully observable
  without Cautilus, and evaluator execution requires separate operator approval.

## Healthy

- Nine high-value inventories now return compact YAML for `--summary` and full YAML for
  `--detail`, while hidden JSON remains available to programmatic consumers.
- The canonical YAML renderer degrades to JSON syntax, which remains valid YAML, when
  PyYAML is unavailable.
- One shared helper owns selection semantics and the plugin mirror is generated.

## Weak

- The pre-slice workflow mixed YAML planner output with JSON-only inventory packets and
  duplicated renderer behavior, increasing token use and migration drift risk.
- Some legacy inventories remain text/JSON-first; the catalog now names that boundary
  honestly instead of promising universal migration.

## Missing

- Before this slice, no test derived live commands from the inventory dispatch and ran
  every migrated command across both source and packaged plugin layouts.

## Deferred

- Compact AGENTS.md routing is a plausible universal context saving, but needs a separate
  scenario review so operating teeth are not lost.
- Broad subprocess-to-in-process test conversion, low-confidence dead-code candidates,
  and unmarked legacy inventory migrations lack a sufficiently specific payoff now.

## Advisory

- structural review result: artifact: `../critique/2026-07-18-inventory-yaml-critique.md`;
  capability_needed=coherent compact inventory packets;
  current centers were planner YAML, duplicated renderers, and per-script JSON flags;
  next_center=`summary_output_lib.py` plus dispatch-declared support;
  transformation=summary YAML/detail YAML/hidden JSON with generated mirrors;
  proof_boundary=live source and plugin commands; enforcement reuses the existing YAML
  contract test, so no new floor is added.
- prose review result: command: `inventory_skill_ergonomics.py --summary` reported
  `prose_review_status=required`, 22 checked skills, and 16 heuristic findings;
  specifically `checked_skill_count=22` and `heuristic_finding_count=16`;
  artifact: `../critique/2026-07-18-063610-packet.md` records the required judgment
  that quality trigger boundaries and progressive disclosure remain
  intact; `inventory-dispatch.md` now distinguishes migrated and legacy commands, and
  every copied migrated command includes `--repo-root .`.
- command: `inventory_skill_ergonomics.py --summary` shrank the first-read
  packet from 12,195 to 9,424 bytes; standing-test economics shrank from 7,173 to 6,364.
- command: `inventory_standing_test_economics.py --summary` found 399 test files,
  169 nested-CLI files, and 154 standing nested-CLI files
  (`test_file_count=399`, `nested_cli_file_count=169`,
  `nested_cli_standing_file_count=154`); no specific conversion was safe enough
  to enter this slice.

## Delegated Review

- Delegated Review: executed — independent interface and ownership reviewers found the
  summary/detail ambiguity, capability overclaim, mirror drift, and missing live-command
  proof; all act-before-ship findings were fixed. A counterweight upheld the resulting
  scope and rejected redundant 18-way mutual-exclusion tests.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof):
  re-delegated through the counterweight; running on `tmp_path` reduced the new contract
  test from 57.29s to 10.06s without weakening the command boundary.

## Commands Run

- `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --detail`
- `python3 skills/public/quality/scripts/inventory_skill_ergonomics.py --repo-root . --summary`
- `python3 skills/public/quality/scripts/inventory_standing_test_economics.py --repo-root . --summary`
- focused pytest selection for the YAML contract and migrated inventories — 101 passed.
- `ruff check skills/public/quality/scripts plugins/charness/skills/quality/scripts tests/quality_gates/test_public_skill_yaml_output_contract.py`
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- `python3 scripts/validate_packaging.py --repo-root .`
- `./scripts/run-quality.sh --read-only` — 81 passed, 0 failed in 56.2s.
- verification-locked `run_slice_closeout.py --produce-mutation-coverage` — passed.

## Recommended Next Quality Moves

- passive preserve the current YAML inventory contract until another consumer earns
  expansion — capability_needed=trustworthy compact inventory packets;
  next_center=dispatch-declared support set; transformation=migrate one coherent
  consumer population at a time; proof_boundary=live source/plugin command equality;
  enforcement_posture=no-new-gate because the existing YAML contract owns it.
- passive compact first-touch agent routing because no validated safe compression
  contract exists yet — capability_needed=lower universal context
  cost; next_center=AGENTS.md routing shell; transformation=move detail behind linked
  owners; proof_boundary=operator scenario review; enforcement_posture=no-gate.

## History

- [Prior durable quality review](history/2026-07-14-open-issue-resolution-proof.md)
