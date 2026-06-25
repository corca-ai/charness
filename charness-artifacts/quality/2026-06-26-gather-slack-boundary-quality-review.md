# Quality Review
Date: 2026-06-26

## Scope

Target boundary: Google Workspace and Slack gather advice tests plus
boundary-bypass exemption hygiene for intentional real CLI smokes.

Ambient repo findings: broad gate runtime, doc-duplicate advisory, Python
warn-band files, and remaining nested-CLI fanout are not fully fixed here.

## Current Gates

- Focused pytest passed 17 tests for gather advice and output-schema coverage;
  ruff passed on the changed tests.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: `run-quality-read-only` 38.1s latest / 65.7s median,
  budget 90.0s; `pytest` 25.7s latest / 25.7s median, budget 140.0s.
- coverage gate: focused gather/output-schema pytest and ruff passed; broad
  closeout pending at draft time.
- evaluator depth: deterministic gates only; no live Cautilus run because this
  changes test execution structure and exemption hygiene, not agent behavior.

## Healthy

- `advise_google_workspace_path.py` now exposes `payload_for()`, matching the
  existing Slack seam and making Google Workspace advice behavior reachable
  below the script process boundary.
- `tests/test_gather_google_workspace.py` now checks Google Workspace and Slack
  payload behavior through `payload_for()`, removing repeated subprocess
  startup for ordinary payload assertions.
- Google Workspace direct, none, and host-mediated modes are covered
  in-process; the CLI smoke only proves process startup and JSON output.
- One real subprocess smoke remains for each advice command, preserving
  `--repo-root`, `__main__`, exit 0, and stdout JSON contracts.
- Boundary-bypass exemptions now document both intentional CLI smokes retained
  by these slices, reducing ratchet/advisory noise without hiding their
  in-process behavior tests.
- `dup-review.json` classifies the shared Google/Slack adapter-mode payload
  dispatch shape as intentional; provider-specific text remains separate.
- Boundary-bypass summary improved from 87 candidates / 149 keys / 50
  convertible files to 85 / 146 / 48, with 5 explicit exemptions.

## Weak

- The remaining boundary-bypass backlog is still large; this slice reduces one
  clean candidate and documents two intentional boundaries.
- The new Google `payload_for()` seam is small but production-facing; any future
  advice mode should update both in-process behavior tests and the CLI smoke.

## Missing

- Missing before this slice: Google Workspace advice behavior was not reachable
  below the script boundary, and intentional retained CLI smokes were not all
  listed in `scripts/boundary-bypass-exemptions.txt`.

## Deferred

- Tokenizer-specific prompt measurement remains deferred; this slice targets
  test process cost, script execution fanout, and advisory-token noise.

## Advisory

- structural review result: command: `check_boundary_bypass_ratchet.py --repo-root . --json`
  reports 85 candidates, 146 keys, 48 convertible files, and 5 exemptions.
- prose review result: `boundary-bypass-ratchet.md` requires exemptions to name
  a `# why:` rationale; the new entries include owner and revisit conditions.
- standing-test economics result: command:
  `inventory_standing_test_economics.py --repo-root . --json`;
  `test_file_count=333`, `nested_cli_file_count=149`, and
  `nested_cli_standing_or_mixed_file_count=145` justify reducing repeated
  subprocess fanout rather than adding another gate.
- fresh-eye result: artifact: `charness-artifacts/critique/2026-06-26-gather-slack-boundary.md`
  records the reviewer finding that operator-facing subprocess CLI smokes had
  to stay.
- public-skill review result: command: `plan_cautilus_proof.py --repo-root . --json`
  did not recommend Cautilus execution; `gather` remains mapped to the existing
  `gather-adapter-bootstrap` scenario because this slice changes helper
  execution seams, not first-skill routing or acquisition semantics.
- duplicate review result: command: `check_dup_ratchet.py --repo-root . --json`
  initially found the shared advice payload dispatch family; reviewed as
  intentional in `dup-review.json` because the scripts share adapter-mode
  semantics but keep provider-specific payloads separate.

## Delegated Review

- Delegated Review: executed — fresh-eye reviewer
  `019f011f-88da-7bb0-a33d-01965c9123ac` found an act-before-ship issue in the
  first draft, and reviewer `019f0124-a296-7ba2-b223-8e5a2b45b1ae` found
  plugin mirror drift after the Google seam; the final slice restores real
  subprocess CLI smokes and syncs plugin exports.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through boundary-bypass fanout, standing-test
  economics, and focused-test evidence; no test-removal change was made.

## Commands Run

- `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --json`
- `python3 skills/public/quality/scripts/inventory_standing_test_economics.py --repo-root . --json`
- `python3 skills/public/quality/scripts/render_runtime_summary.py --repo-root . --json`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root . --json`
- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id gather --json`
- `python3 scripts/validate_public_skill_dogfood.py --repo-root .`
- `python3 scripts/validate_public_skill_validation.py --repo-root .`
- `python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --json`
- `python3 scripts/check_python_lengths.py --repo-root . --paths skills/public/gather/scripts/advise_google_workspace_path.py tests/test_gather_google_workspace.py`
- command: python3 -m pytest -q tests/test_gather_google_workspace.py tests/test_skill_output_schemas.py
- `ruff check skills/public/gather/scripts/advise_google_workspace_path.py tests/test_gather_google_workspace.py tests/test_skill_output_schemas.py`

## Recommended Next Gates

- active none — the existing boundary-bypass ratchet and exemption rationale
  rule already cover this class of growth.
- passive convert another single-target clean candidate because the remaining
  convertible backlog is still 48 files.
- passive extract a shared advice-script smoke helper because two gather advice
  commands now use the same behavior-under-function plus one CLI-smoke pattern.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
