# Quality Review
Date: 2026-06-25

## Scope

Target boundary: repo-wide quality slice for standing test-economics signal quality
and agent-facing token efficiency; no single public skill target.

Ambient repo findings: existing Python near-limit warnings and doc duplicate
advisories are not caused by this slice. Per operator direction, `nose` latest
checks are no longer part of this loop.

## Current Gates

- Focused `pytest` passed 11 tests for `test_standing_test_economics.py`.
- Changed-surface validators passed for packaging, skills, public-skill policy,
  dogfood, inference interpretation, inventory-consumption declaration,
  attention-state visibility, boundary-bypass ratchet, and ruff.
- Broad `./scripts/run-quality.sh --read-only` passed 79/79 after this slice.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: `run-quality-read-only` 38.1s / 65.7s median, `pytest`
  25.3s / 26.9s, `check-coverage` 18.7s / 19.0s; all budgeted hot spots were
  within profile budgets.
- coverage gate: broad read-only gate, focused closeout producer, and
  branch-wide changed-line coverage consumer all passed.
- evaluator depth: deterministic gates only. No Cautilus run was in scope
  because this changed inventory output shape, not prompt behavior.

## Healthy

- `inventory_standing_test_economics.py --summary` reports nested CLI fanout as
  `nested_cli_file_count=150`, `nested_cli_release_only_file_count=4`, and
  `nested_cli_standing_or_mixed_file_count=146`.
- Summary samples are split by bucket, so the advisory no longer shows an
  unsplit sample beside split counts.
- `--summary-yaml` emits the same compact summary as YAML for agent review:
  5,066 bytes versus 5,732 bytes for compact JSON on this checkout.
- Full attribution remains available with `--json`; compact JSON/YAML keep only
  samples.
- `standing_test_economics_lib.py` stayed below the length warn band after
  marker detection moved into `surface_marker_lib.py`.

## Weak

- `surface_marker_lib.py` uses conservative regex detection for module-level
  release-only; multiline, tuple, call-style, or function/class-only markers
  stay in `standing_or_mixed`.
- YAML savings are real but modest on this payload: about 12% byte reduction
  versus compact JSON, not an order-of-magnitude token change.

## Missing

- No missing deterministic gate is justified by this slice. Existing
  `validate-inventory-consumption*`, `validate-inference-interpretation`,
  focused pytest, and changed-surface validators cover the changed contract.

## Deferred

- Nested CLI fanout remains the real test-economics backlog: 146 standing/mixed
  files still spawn nested processes and need structural conversion only where
  honest.
- AST-backed release-only marker sharing with
  `inventory_release_only_sentinels.py` is deferred; regex false negatives are
  conservative and do not understate standing/mixed cost.

## Advisory

- structural review result: command:
  `plan_quality_run.py --repo-root . --json`; planner required
  runtime/test-economics review, and the next structural move was a cheaper and
  more precise inventory packet, not a new blocking floor.
- prose review result: command:
  `inventory_standing_test_economics.py --repo-root . --summary`; summary
  engages `test_file_count`, `nested_cli_file_count`,
  `nested_cli_release_only_file_count`,
  `nested_cli_standing_or_mixed_file_count`, and `runner_snippets`.
- runtime interpretation: command:
  `render_runtime_summary.py --repo-root . --json`; current hot spots are
  budgeted, so this loop improved the decision signal for the next nested-CLI
  cleanup rather than weakening standing test proof.
- YAML interpretation: command:
  `inventory_standing_test_economics.py --repo-root . --summary-yaml`; YAML is
  useful for agent-facing summary output, while checked machine-contract JSON
  remains unchanged.
- fresh-eye review result: artifact: delegated reviewer outputs in this
  session; reviewers found no act-before-ship blockers, and their non-blocking
  notes drove split samples and explicit conservative-marker wording.
- dup-ratchet interpretation: command:
  `check_dup_ratchet.py --repo-root . --write-baseline`; the initial helper
  split rotated two existing full-scan family ids that no longer included
  changed files, so the gate baseline was regenerated after all code edits.

## Delegated Review

- Delegated Review: executed — fresh-eye reviewer
  `019efe53-f295-7b03-9a6d-d95c082cc37c` found no blockers and confirmed
  focused coverage/import risk was adequate; counterweight reviewer
  `019efe54-09e5-7390-b4bf-4501968c6a22` found no blockers and requested
  sample/wording tightening.
- Reviewer-tier evidence: requested bounded quality closeout review under repo
  Subagent Delegation; host exposed `multi_agent_v1.spawn_agent`; applied model
  details hidden by host.
- Slow-gate lenses: fixture-economics reviewed via pytest temp footprint,
  parallel-critical-path reviewed via runtime hot spots, and duplicated-proof
  reviewed via nested CLI fanout. No re-delegation was needed because the slice
  changed advisory inventory shape rather than removing or relocating tests.

## Commands Run

- `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --json`
- `python3 skills/public/quality/scripts/render_runtime_summary.py --repo-root . --json`
- `python3 skills/public/quality/scripts/inventory_standing_test_economics.py --repo-root . --summary[,-yaml]`
- `python3 skills/public/quality/scripts/inventory_standing_test_economics.py --repo-root . --json`
- `pytest -q tests/quality_gates/test_standing_test_economics.py`
- `ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts`
- `python3 scripts/check_changed_line_mutation_coverage.py --repo-root . --base-sha origin/main --head-sha HEAD --reuse-coverage --require-fresh-coverage`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root .`
- `python3 scripts/validate_inference_interpretation.py --repo-root . --require-git-file-listing`
- `python3 scripts/validate_inventory_consumption_declaration.py --repo-root .`
- `python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --write-baseline`
- `python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --json`
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- `./scripts/run-quality.sh --read-only`

## Recommended Next Gates

- active none — this slice adds an advisory output mode and focused tests
  without a new low-noise blocking invariant.
- passive convert nested CLI fanout to in-process seams because 146
  standing/mixed files still spawn nested processes.
- passive evaluate YAML for other agent-facing summaries until a measured
  payload shows enough savings to justify changing another output surface.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
