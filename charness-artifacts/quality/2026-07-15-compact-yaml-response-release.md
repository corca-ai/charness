# Quality Review
Date: 2026-07-15
Title: Compact YAML response release

## Scope

Target boundary: the root operational `charness` YAML response for `init`,
`update`, `doctor`, and `tool` lifecycle commands.

Ambient repo findings: none identified by the focused inventories.

## Current Gates

- `pytest -q tests/charness_cli`: passed (57 tests).
- Focused `release_only` lifecycle and YAML-branch suite: passed (12 tests).
- Command documentation and packaging validation passed after export sync.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` rendered by `scripts/render_runtime_summary.py`; no fresh timing capture was needed for this response-projection slice. <!-- reproduction-source -->
- runtime hot spots: no runtime budget regression was observed; the focused CLI suite completed in under 30 seconds.
- coverage gate: all `tests/charness_cli` tests passed before release preparation.
- evaluator depth: deterministic gates only; live Cautilus evaluation is ask-before-run and no behavior-evaluation request was made.

## Healthy

- Default high-fanout responses preserve status, transition, health, and next
  step while hiding commands, release metadata, routes, and probe output.
- `--detail` returns the complete YAML payload, so evidence inspection remains
  available without making the ordinary `update all` response unbounded.
- Legacy integration and executable-spec assertions that inspect raw fields now
  select `--detail`; ordinary assertions continue to exercise the summary.
- The parser rejects `doctor --detail --next-action`, eliminating a silently
  ignored selection flag.

## Weak

- A source-checkout test cannot prove an already installed CLI or a fresh host
  session has received the forthcoming patch release.

## Missing

- No byte-limit truncation is present by design: semantic projection, rather
  than arbitrary clipping, is the response-size contract.

## Deferred

- Private helper JSON protocols remain unchanged because they are subprocess
  interfaces, not root `charness` stdout.

## Advisory

- `inventory_cli_ergonomics.py --repo-root . --json` and
  `inventory_cli_side_effect_probes.py --repo-root . --json` reported clean
  inventories for the affected command surface.
- `artifact: charness-artifacts/critique/2026-07-15-compact-yaml-response-release-critique.md`
  records the independent release review and the repaired migration gaps.
- `command: pytest -q tests/charness_cli` is the direct regression
  proof; a live evaluator is unnecessary for a deterministic YAML schema path.
- The installed `nose` scanner moved from 0.18.0 to 0.19.0, so both clone
  baselines were deliberately regenerated rather than treating scanner IDs as
  new product duplication. `inventory_nose_clones.py` returned
  `status=baseline-written`, `family_count=639`, and paths `scripts`,
  `skills/public`, and `skills/support`.

## Delegated Review

- Delegated Review: executed — three bounded fresh-eye reviewers found two
  ship blockers and one coverage gap; all were repaired and rerun. Slow-gate
  lenses (fixture-economics, parallel-critical-path, duplicated-proof): not
  re-delegated because this change adds no slow gate or parallel topology.

## Commands Run

- `pytest -q tests/charness_cli`.
- `python3 scripts/render_cli_reference.py --repo-root .` and
  `python3 scripts/sync_root_plugin_manifests.py --repo-root .`.
- `python3 scripts/check_command_docs.py --repo-root .` and
  `python3 scripts/validate_packaging.py --repo-root .`.
- `python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --write-baseline --confirm-baseline-delta`.
- `python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --write-baseline --json`.

## Recommended Next Quality Moves

- active installed-release readback — capability_needed=operator update confidence; next_center=release workflow; transformation=run the released CLI through update and doctor after publication; proof_boundary=installed binary plus fresh host session; enforcement_posture=release-gate.
- passive response byte caps — capability_needed=none; next_center=output contract; transformation=do not add arbitrary truncation; proof_boundary=semantic summary projection; enforcement_posture=no-gate because a byte cap would hide useful state without fixing the execution-graph leak.

## History

- [Previous quality review](history/2026-07-14-open-issue-resolution-proof.md)
