# Quality Review
Date: 2026-06-05

## Scope

Open `/charness:quality` posture pass on a clean `main` at `v0.20.0`, in sync
with `origin/main`, after the 0.20.0 release and #293–#300 closeouts. No bug was
named, so this is a full re-derivation: re-resolved the adapter and gate/source
surface, ran the existing gates, walked the four lenses, ran a bounded fresh-eye
reviewer. The wrong-boundary suspect was standing test-economics drift — a real
upward trend but advisory-by-design with its lever already shipped, not
architecture/ownership drift. No production source changed; the deliverable is
the honest posture.

## Current Gates

- `./scripts/run-quality.sh --read-only`: 71 passed, 0 failed, 41.2s (profile
  `local-linux-x86_64-36cpu`). All families green: packaging/import-safety,
  command-docs/doc-links/markdown, spec/specdown/run-evals,
  secrets/supply-chain/actions/shell, pytest/test-completeness/production-ratio/
  boundary-bypass-ratchet, coverage, current-pointer, inventory-consumption,
  closeout-contract validators.
- `validate_usage_episodes.py`: 548 records validated; `report_usage_episodes.py`
  flags the expected product-success veto gaps — an engineering signal, not
  product-success proof. `validate_attention_state_visibility.py`: 71 files, no
  hidden exit-zero attention state.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py` this turn; profile
  `local-linux-x86_64-36cpu`; runtime visibility configured.
- runtime hot spots: `check-coverage` 45.2s latest / 44.1s median vs 45.0s budget
  (brushing ceiling, see Advisory); `pytest` 15.3s / 43.4s median, budget 140.0s;
  `check-current-pointer-writes` 13.3s / 12.9s; `check-duplicates` 10.0s / 11.9s.
- coverage gate: `run-quality --read-only` passed (71 passed, 0 failed);
  `check-runtime-budget` PASS, so the coverage brush is within enforced tolerance.
- evaluator depth: no live Cautilus (`plan_cautilus_proof.py` next_action=none /
  must_ask_before_running=true); proof is deterministic gates + one fresh-eye review.

## Healthy

- All 71 gates pass; spot-checked gates prove behavior not wording —
  `check_export_safe_imports.py` (AST import-safety) and
  `check_boundary_bypass_ratchet.py` (no-increase ratchet) have real fail
  semantics.
- `inventory_lint_ignores.py`: `blanket`=0, file-level=0, every suppression
  `scope`=inline; `codes` dominated by E402 (post-bootstrap import order) plus a
  few ANN001/BLE001 — zero production-logic suppressions.
- `inventory_skill_ergonomics.py`: `checked_skill_count`=23,
  `heuristic_finding_count`=17, `prose_review_status`=required; `subcheck_counts`
  shows the only non-zero subcheck is `host_surface_reference_count`=92 (mode/
  option pressure, prose ritual, trigger overlap, path ambiguity all 0).
- prose review result: no trigger-overlap, undertrigger, mode/option pressure,
  taste-policing, or repeated-prose-ritual smell across 19 public + 4 support
  skills; the only flag is the deferred host-surface advisory.
- `inventory_public_spec_quality.py`: 4 specs, `source_guard_row_count`=0, thin
  `executable_block_count` (1 e2e + 1 smoke) — no brittle source guards, no
  duplicated proof. CLI-ergonomics, gate-verbosity, dual-implementation
  inventories also scan clean.

## Weak

- `inventory_standing_test_economics.py` keeps rising: `test_file_count`=247 (231
  on 2026-06-03, 188 on 2026-05-24); `nested_cli_file_count`=109 (was 104). It is
  advisory-by-design (no fail path) and tracked, but the slow release-only CLI
  lifecycle tail is the durable watch item; the next real win is shrinking that
  surface, not pruning tests or adding a count ceiling.

## Missing

- No missing standing gate. The four lenses are covered by existing enforcement;
  open items are deferred-by-judgment, not enforcement holes.

## Deferred

- #184 (product success metrics) deferred by design pending maintainer judgment;
  the usage-episode report deliberately vetoes product-success claims.
- `host_surface_reference` skill references are intentionally advisory/deferred
  (count 104 → 92, improving), not a blocking portability violation.
- `inventory-nose-clones` skipped because the optional `nose` binary is absent —
  an integration-manifest dependency, not a repo requirement.

## Advisory

- `check-coverage` runs 45.2s latest / 44.1s median against its 45.0s budget on
  this profile — brushing the ceiling. `check-runtime-budget` still PASS, so a
  watch item, not a breach; revisit if a median crosses budget.
- `inventory_lint_ignores.py` reports 101 inline suppressions vs 85 last pass,
  but the canonical delta is ~7 new `# noqa: E402` from the shared git-inventory
  and mutation-summary extraction refactors (the rest is generated `plugins/`
  mirror doubling). Revisit if any blanket/file-level suppression appears or codes
  spread beyond E402/ANN001/BLE001 into production logic.

## Delegated Review

- Delegated Review: executed. Tier requested `high-leverage` (adapter
  `reviewer_tiers` null → host default reviewer); read-only in the shared parent
  worktree.
- One bounded fresh-eye reviewer adversarially challenged the healthy/green call
  across five points and returned SOUND: no scattered/undeclared enforcement (all
  17 inventories declared or opted out), test-economics genuinely advisory with
  its lever shipped (#299), the lint delta benign E402 refactor fallout (0
  production suppressions), `host_surface_reference` correctly deferred and
  trending down. No revision required; no new deterministic gate surfaced.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof)
  were not separately re-delegated — standing test economics is an unchanged
  advisory carry-forward, not the slice under review.

## Commands Run

- `find-skills` → `quality`; adapter + artifact bootstrap.
  `./scripts/run-quality.sh --read-only` (×2 incl. final lock). `plan_cautilus_proof.py`
  (next_action=none → no eval), `validate_usage_episodes.py`,
  `report_usage_episodes.py`, `validate_attention_state_visibility.py`.
- `inventory_skill_ergonomics.py`, `inventory_standing_test_economics.py`,
  `inventory_lint_ignores.py`, `inventory_public_spec_quality.py`,
  `inventory_cli_ergonomics.py`, `inventory_standing_gate_verbosity.py`,
  `inventory_dual_implementation.py`, `render_runtime_summary.py`.
- `gh issue list/view` (#184 open; #293–#300 closed); one bounded fresh-eye
  reviewer subagent (read-only).

## Recommended Next Gates

- active `AUTO_CANDIDATE`: none this turn — fresh-eye review confirmed no
  repo-owned deterministic gate is hidden; the tier is "extend existing gates."
- passive `AUTO_EXISTING`: passive because existing inventories already cover both
  watch items (`check-runtime-budget` on the coverage brush, lint-ignore on the
  suppression trend); act only if a median crosses budget or a blanket appears.
- passive `NON_AUTOMATABLE`: keep watching standing test economics because the
  real win is shrinking the release-only CLI lifecycle surface (the #299 sentinel
  report makes that measurable), not pruning tests.
- passive `NON_AUTOMATABLE`: continue #184 because product-success target and
  metric choices need maintainer judgment, not a gate.

## History

- [2026-06-03 quality review](history/2026-06-03-quality-review.md)
- [2026-05-24 quality review](history/2026-05-24-quality-review.md)
