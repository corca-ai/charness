# Quality Review
Date: 2026-06-06

## Scope

Open `/charness:quality` posture pass on clean `main` at `v0.24.1`, run as
**slice 1 of the `2026-06-06-quality-scan-closeout-discipline` achieve goal**.
The prior artifact was stale at `v0.20.0` (0.21.0–0.24.1 shipped without a
refresh), so this is a full re-derivation: gates, four lenses, one bounded
fresh-eye reviewer. Deliverable = honest posture **plus a prioritized candidate
list scoping the goal's slices 2–5**. No production source changed; routing
`find-skills` → `quality`. Concept lens: no architecture/ownership drift; the one
standing tension is enforcement-vs-judgment (two unenforced debug-closeout steps,
see Missing).

## Current Gates

- `./scripts/run-quality.sh --read-only`: **71 passed, 0 failed, ~43.5s**
  (profile `local-linux-x86_64-36cpu`) on the final trimmed state. The reviewer
  caught an intermediate 230-line draft of this artifact tripping
  `validate-quality-artifact`'s 140-line cap (70/1); trimming restored 71/0.
- Advisory exit-0 WARN: `check-python-lengths` flags
  `skills/public/achieve/scripts/goal_artifact_closeout_evidence.py` at 348 code
  lines in band `[330,360]` (hard limit 360) — a trim nudge, exit 0.
- `validate_usage_episodes.py`: 596 records; `report_usage_episodes.py` flags the
  expected product-success veto gaps (engineering signal, not product proof);
  `validate_attention_state_visibility.py`: 72 files, no hidden exit-zero state.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py` (via `record_quality_runtime.py`) this
  turn; profile `local-linux-x86_64-36cpu`; runtime visibility configured.
- runtime hot spots: `check-coverage` 44.5s / 44.8s median vs 45.0s budget
  (recorded sample); `pytest` 17.0s / 17.7s, budget 140.0s;
  `check-current-pointer-writes` 13.4s; `check-duplicates` 10.0s.
- coverage gate: `run-quality --read-only` passed; `check-runtime-budget` PASS.
  `check-coverage` is changed-path-gated and did **not** run this turn (only
  markdown changed), so its 44.x s is the last recorded full-run sample, enforced
  and green when it runs, brushing budget (see Advisory).
- evaluator depth: no live Cautilus (`plan_cautilus_proof.py` next_action=none);
  proof is deterministic gates + one fresh-eye review.

## Healthy

- All 71 run gates pass with real fail semantics (`check_export_safe_imports.py`
  AST import-safety, `check_boundary_bypass_ratchet.py` no-increase ratchet).
- `inventory_lint_ignores.py`: `blanket`=0, file-level=0, `scope`=inline for all
  75 suppressions (down from 101); `codes` = 66 E402 + 5 ANN001 + 4 documented
  BLE001 — zero production-logic suppressions.
- `inventory_skill_ergonomics.py`: `checked_skill_count`=23,
  `heuristic_finding_count`=17, `prose_review_status`=required; `subcheck_counts`
  has one non-zero subcheck, `host_surface_reference`=92 (deferred portability),
  all of `core_overfill`/`mode_option_pressure`/`prose_ritual`/`path_ambiguity` 0.
- prose review result: across 19 public + 4 support skills, no trigger-overlap,
  undertrigger, mode/option pressure, taste-policing, or prose-ritual smell — the
  only non-zero signal is the deferred `host_surface_reference` advisory.
- `inventory_public_spec_quality.py`: 4 specs, `source_guard_row_count`=0 and
  `pointer_proof_marker_count`=0, thin `executable_block_count` (8; e2e=1+smoke=1)
  — no brittle source guards, no duplicated proof at the wrong layer.

## Weak

- `inventory_standing_test_economics.py` keeps rising: `test_file_count`=258 (247
  on 06-05); `nested_cli_file_count`=118 (was 109). Advisory-by-design;
  `runner_snippets` show the fan-out is real-binary smoke, not in-process proof
  via subprocess (no hidden broad-test compensation). Durable lever = shrink the
  release-only CLI lifecycle surface, not pruning tests.

## Missing

- **Two enforcement holes this goal closes** (not deferred-by-judgment):
  - #2b: the sibling-search reference requires a cross-file scan but
    `validate_debug_artifact.py` only shape-checks `## Sibling Search` via
    `validate_sibling_followups` — a within-file-only scan passes. Real gap
    (reviewer-confirmed); slice 2 adds an author-marker check in the `latest.md`
    branch (Option A; the 59 dated artifacts stay untouched).
  - #2a: a new `debug/*.md` with no matching `rca-ledger.jsonl` `ref` is
    unenforced — deliberately non-gated (anti-gaming); slice 3 adds an exit-0
    nudge. No other missing gate; tier = "extend existing gates" (reviewer-confirmed).

## Deferred

- #184 (product-success metrics) deferred by design pending maintainer judgment;
  `host_surface_reference` references (subcheck=92) are intentional portability
  advisories, not a blocking violation.
- Real-host / second-machine `nose` proof is a separate carry-forward (since
  v0.23.0); this pass proves `nose` runs on the local profile only.

## Advisory

- **`nose` clone inventory is now ACTIVE (delta from prior posture).** The `nose`
  binary (0.5.0) is present, so `inventory-nose-clones` ran: `family_count`=20,
  `total_dup_lines`=1951, `advisory`=true. The headline overstates real debt —
  the largest families are intentional per-package boilerplate (family #1 = 86
  members / 425 dup_lines of `resolve_adapter.py` duplicated for portability);
  the tool's `notes` say "refactoring candidates, not standing quality failures."
  This is the proxy-needs-interpretation surface slice 5 pilots (reviewer
  spot-checked top families, confirmed intentional).
- `check-coverage` brushes its 45.0s budget (44.5s/44.8s recorded);
  `check-runtime-budget` PASS, so a watch item, not a breach.

## Delegated Review

- Delegated Review: **executed**. Tier `high-leverage` (adapter `reviewer_tiers`
  null → host default); read-only in the shared parent worktree.
- The reviewer challenged the green/healthy call across 6 claims and returned
  **REVISE → folded**: VERIFIED the nose-intentional, lint, test-economics, and
  #2b-gap claims, and caught one real blocker — an intermediate 230-line draft
  tripped `validate-quality-artifact`'s 140-line cap (70/1), fixed by trimming to
  71/0 (it also corrected the coverage bullet). No new repo-owned gate missing.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof)
  were not separately re-delegated: standing test economics is an unchanged
  advisory carry-forward, not the slice under review.

## Commands Run

- `find-skills` → `quality`; `resolve_adapter.py` / `bootstrap_adapter.py`
  (unchanged) / `resolve_quality_artifact.py`; `run-quality.sh --read-only`;
  `plan_cautilus_proof.py` (next_action=none → no eval),
  `validate_usage_episodes.py`, `report_usage_episodes.py`,
  `validate_attention_state_visibility.py`, `render_runtime_summary.py`.
- Inventories (fields engaged in Healthy/Weak/Advisory above):
  `inventory_standing_test_economics.py`, `inventory_skill_ergonomics.py`,
  `inventory_lint_ignores.py`, `inventory_public_spec_quality.py`,
  `inventory_nose_clones.py`. One bounded fresh-eye reviewer (read-only).

## Recommended Next Gates

- active `AUTO_CANDIDATE`: **#2b cross-file sibling-scan marker** in the
  `validate_debug_artifact.py` `latest.md` branch (slice 2) — promotes the
  reference's cross-file requirement from prose to enforcement.
- passive `AUTO_EXISTING`: #2a RCA-ledger nudge stays exit-0 advisory because the rca-conversion-ledger spec fixes the append as anti-gaming (slice 3).
- passive `NON_AUTOMATABLE`: keep watching test economics because the win is shrinking the release-only CLI surface, and #184 because it needs maintainer judgment.
- passive advisory: the `nose` 1951-dup headline stays a proxy until slice 5's interpretation contract makes its blind spots self-declaring.

## History

- [2026-06-05 quality review](history/2026-06-05-quality-review.md)
- [2026-06-03 quality review](history/2026-06-03-quality-review.md)
