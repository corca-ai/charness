# Quality Review
Date: 2026-06-12

## Scope

Bounded operator-requested pass: "nose 0.7.0 업데이트 후 코드 퀄리티 체크".
nose updated 0.6.0 → 0.7.0 via the upstream installer, then a full gate run
under the new scanner, the carried real-host `nose` lifecycle proof from the
v0.41.0 release artifact, a clone-advisory re-read under the 0.7.0 ranking
surface, and a C2/C3/C4 status refresh. Not a full four-lens re-derivation;
last full pass: [2026-06-11](history/2026-06-11-quality-review.md). Routing
`find-skills` → `quality`; one bounded fresh-eye reviewer.

## Current Gates

- `./scripts/run-quality.sh`: **74 passed, 0 failed, 71.1s** on a clean tree
  at `3a8ba3a1` (profile `local-linux-x86_64-36cpu`); `inventory-nose-clones`
  parsed nose 0.7.0 with no consumer-script change needed.
- `plan_cautilus_proof.py`: `next_action: none` → no evaluator run;
  deterministic gates own this closeout.
- Real-host `nose` proof: `charness tool doctor nose --json --no-write-locks`
  detects 0.7.0 OK; `charness tool sync-support nose --json` skips with
  "integration has no support_skill_source" (expected, integration-only);
  the upstream `nose-cli-installer.sh` update path worked on this host.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py` this turn; profile
  `local-linux-x86_64-36cpu`; runtime visibility configured.
- runtime hot spots: `check-coverage` 42.7s latest / 43.8s median vs 45.0s
  budget (still brushing — carried watch); `pytest` 22.2s/20.1s vs 140s;
  `check-current-pointer-writes` 14.4s; `check-duplicates` 11.9s median.
- coverage gate: ran and passed this turn; `check-runtime-budget` PASS.
- evaluator depth: deterministic gates only (`next_action: none`); proof =
  74 gates + one bounded fresh-eye review.

## Healthy

- All 74 gates pass under nose 0.7.0.
- nose tool lifecycle fully proven on this host: manifest installer update
  (0.6.0 → 0.7.0 observed), doctor detect/healthcheck OK, sync-support
  correctly a no-op — closes the `nose` portion of the v0.41.0 real-host
  proof carried in `docs/handoff.md`.
- **C2 CLOSED**: `aa8670c8` round-trips unknown adapter fields
  (`scripts/quality_bootstrap_lib.py:374`); `.agents/quality-adapter.yaml`
  retains `standing_doc_provenance`; `bootstrap_adapter.py` ran this turn
  with `adapter_status: unchanged`.
- **C3 CLOSED**: scheduled mutation lane runs under
  `.github/workflows/mutation-tests.yml` (cron `17 */3 * * *`) with the
  local pre-push changed-line gate as the primary lane.
- **C4 CLOSED**: `8288d54a` pulls `validate-handoff-artifact` to commit time
  when `docs/handoff.md` is staged (`scripts/staged_commit_gate_plan.py:79`);
  observed live on this pass's own commit. The reviewer's C4-open finding
  was falsified by this direct observation after the review.

## Weak

- **Clone-advisory trend is not cross-version comparable.** Reported-family
  dup lines moved 2156 (0.5.0) → 3045 (0.7.0), but 0.7.0 ranks by
  `extractability` over a new surface model, and the repo grew (+2609/−1368
  Python lines under `scripts/`+`skills/` since `a6888927`,
  reviewer-verified) so some real growth cannot be excluded. Treat 3045 as
  the new 0.7.0 baseline, not a regression signal.
- `check-coverage` keeps brushing its 45s budget (43.8s median) — carried.

## Missing

- None found in this bounded scope: the prior pass's C2/C3/C4 are all
  closed (evidence under Healthy), and the gate surface ran green; a full
  four-lens re-derivation was not in scope this pass.

## Deferred

- #184 (operator product-metrics ideation; handoff Discuss item);
  `host_surface_reference` portability advisories (carried).
- Remaining v0.41.0 real-host proof: the clean temp-home/second-machine
  operator path (`nose` checks closed this pass; that path is not).

## Advisory

- `inventory-nose-clones` (0.7.0): `family_count`=20 shown of
  `ranking.total_families`=520; `ranking.surface_counts` declaration=9,
  hidden=57, review=6, default=448, fragments total=63;
  `total_dup_lines`=3045 (reported `families` only). Consumer answer to the
  interpretation question: top `families` remain intentional per-package
  portability boilerplate — `resolve_adapter.py`/`init_adapter.py` copies
  (#1–#5, #10, #17), `_load_skill_runtime_bootstrap` shims × 75 files (#16),
  loader shims (#18, #20), bootstrap headers (#7, #9, #15); the Non-Goals
  fence holds there. Genuine candidates: **#11 `find_adapter`** (5
  byte-identical 6-line copies; trivially extractable, tiny payoff) and
  **#12 `validate_adapter_data`** (20 members/17 files, dup=570 but
  shared=24 — a field-spec validation framework, non-trivial). Reviewer
  correction folded: the fence is interpretive, not hard policy — the
  critique/proof_semantics/cautilus adapter libs are exported and reachable
  via `SKILL_RUNTIME.load_repo_module_from_skill_script`. #8 (scalar
  helpers, worked by `75eed2fb`) still reports 11 files/dup=84 — residual.
  Per the inventory `notes`: review only extractable non-bootstrap families.
- `check-python-lengths` warn-band files carried; gate PASS this turn
  (command: `./scripts/run-quality.sh`).

## Delegated Review

- Delegated Review: **executed**. Tier `high-leverage`;
  `.agents/critique-adapter.yaml` `reviewer_tiers.high-leverage` (gpt-5.5 /
  medium / priority) targets a Codex host — this Claude Code host resolved
  the tier to its default strongest reviewer; host exposure:
  `host-defaulted`. Fresh-eye context: parent-delegated, read-only shared
  worktree. Verdict **REVISE → folded**: (A) softened the tool-version-only
  dup-lines claim; (B) corrected the extraction fence for exported adapter
  libs and sized #12's core (shared=24/570); (C) C2/C3 closed — its
  C4-open finding was later falsified by live commit observation
  (`8288d54a`); (D) #8 residual + fragments breakdown.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): not re-delegated — no slow-gate scope in this pass.

## Commands Run

- `find-skills` recommendation probe (read-only) → `quality`; nose upstream
  installer (0.6.0 → 0.7.0); `./scripts/run-quality.sh` (74/0); `charness
  tool doctor nose --json --no-write-locks`; `charness tool sync-support
  nose --json`; `plan_cautilus_proof.py`; `render_runtime_summary.py`.
- Inventories (fields engaged above): `inventory_nose_clones.py` —
  `family_count`, `families` (members/shared_lines/params/sample_locations),
  `ranking` (total_families, surface_counts), `notes`. One bounded
  fresh-eye reviewer (read-only).

## Recommended Next Gates

- passive #11/#12 adapter-validation extraction, because it needs a
  field-spec helper design first and payoff is small vs the abstraction.
- passive nose `--baseline` adoption, because the advisory is non-gating by
  design today; revisit only if `--fail-on new` ever turns it gating.
- passive watch (kept passive because none is yet actionable): coverage
  budget brush, test-economics growth (not re-measured), #184.

## History

- [2026-06-11 quality review](history/2026-06-11-quality-review.md)
- [2026-06-06 quality review](history/2026-06-06-quality-review.md)
