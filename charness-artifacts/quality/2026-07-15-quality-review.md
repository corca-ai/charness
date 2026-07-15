# Quality Review
Date: 2026-07-15
Title: Compact Aggregate YAML Response Follow-Up Quality Review

## Scope

Target boundary: installed CLI aggregate YAML responses and external-tool update
provenance.

Ambient repo findings: the skills ergonomics inventory reports existing
host-surface references, but no changed skill surface or quality move.

## Current Gates

- Focused CLI/control-plane regressions passed; standing release quality remains
  to be run after the mutation set is locked.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json`. <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: `run-quality-full-release` 89.1s latest / 83.0s median;
  this is a necessary release proof, not a new optimization finding.
- coverage gate: focused evidence passed; locked-diff release quality is pending.
- evaluator depth: deterministic-gates-only; Cautilus is ask-before-run and is
  not needed for this structured CLI seam.

## Healthy

- The shared projector now has a direct fixture proof for an aggregate response
  and a retained `--detail` evidence path.

## Weak

- v1.0.10's release proof did not run the real installed `update all` path,
  allowing a composed per-tool list to escape.

## Missing

- No missing deterministic mechanism is proposed: the added fixture boundary
  closes the identified composition seam without a new standing floor.

## Deferred

- Tool installations whose provenance remains only `path` stay manual; adding
  provenance inference needs a separate evidence-backed design.

## Advisory

- structural review result: evidence: the aggregate projector is the shared
  owner, and the fixture proves its counts-plus-attention boundary.
- prose review result: evidence: `docs/control-plane.md` and the generated CLI
  reference define the same aggregate/detail boundary; skills are ambient.
- `inventory_skill_ergonomics.py --summary` found 16 existing host-surface
  reference heuristics across 21 skills; this slice changes no inspected skill.
- command: `pytest -q -m 'not release_only' tests/control_plane/test_update_manifest_contract.py
  tests/control_plane/test_sync_support.py tests/charness_cli/test_update_output.py
  tests/charness_cli/test_tool_lifecycle.py::test_tool_install_can_select_quality_validation_recommendations
  tests/charness_cli/test_yaml_output_branch_coverage.py` passed 20 tests and
  deselected two release-only tests.

## Delegated Review

- Delegated Review: not_applicable — this quality record does not replace the
  required fresh-eye release critique, which is tracked in the critique artifact.
- Slow-gate lenses: not applicable; no slow-gate design change is proposed.

## Commands Run

- `pytest -q -m 'not release_only'` focused CLI/control-plane
  selection — passed 20 tests and deselected two release-only tests.
- `python3 scripts/validate_integrations.py --repo-root .` — passed.
- `python3 scripts/sync_support.py --repo-root . --json` — dry-run diagnostics.
- `python3 scripts/update_tools.py --repo-root . --json` — `gitleaks`, `ruff`,
  and `specdown` now report manual rather than a guessed updater failure.

## Recommended Next Quality Moves

- passive provenance inference because capability_needed=automatic updates for
  non-symlink package installs; next_center=install provenance; transformation=
  collect stronger installer evidence before any inference; proof_boundary=a
  separate design and runtime fixtures; enforcement_posture=no-gate.

## History

- [Previous quality review](history/2026-07-14-open-issue-resolution-proof.md)
