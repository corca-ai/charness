# Quality Review
Date: 2026-05-24

## Scope

Continuation of user-requested quality plus critique: current gates, #211, fresh-eye review, autonomous fixes, and deferred issues.

## Current Gates

- `./scripts/run-quality.sh --read-only` passed before edits: 67 passed,
  0 failed, 35.4s.
- Targeted touched-surface tests passed after fixes: RCA ledger, mutation
  sampling, current-pointer scanner, `sync-support`, and pytest-temp economics.
- Packaging mirror was synced; packaging validators passed after sync.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py` via `scripts/record_quality_runtime.py`.
- runtime hot spots: `check-coverage` 40.3s latest / 40.2s median, budget 45.0s;
  `pytest` 39.9s latest / 33.1s median, budget 140.0s; `check-duplicates`
  8.8s latest / 8.4s median, budget 11.0s.
- coverage gate: `run-quality --read-only` passed.
- evaluator depth: no live Cautilus run; deterministic gates plus fresh-eye review were the proof.

## Standing Test Economics

- `inventory_standing_test_economics.py` reported `test_file_count=188`,
  `nested_cli_file_count=81`, and advisory `pytest_temp_footprint`.
- Follow-up after release: passing pytest sessions use a repo-keyed cache temp
  root and failed-only tmp retention, so successful release-only runs should not
  retain large tmp trees.

## Testability and Selection

- #211 reproduced before the fix: changed-line blockers named RCA scripts and
  mutation-line exclusions hit RCA scripts.
- Fixed: continuation lines in executed multiline simple statements count as
  covered without propagating across enclosing function bodies.
- Fixed: RCA tests cover optional/error branches, timestamps, and seed/live behavior.
- Fixed: standing-test economics tolerates pytest temp directories disappearing
  during xdist cleanup.
- Fixed: `run-quality.sh` isolates pytest temp retention from unrelated repos
  and points the seed fixture budget at the same repo-keyed temp root.
- Final committed mutation sampler `final5` reported 0 changed-line blockers and
  0 mutation-line coverage exclusions.

## Coverage and Eval Depth

- Deterministic gates and fresh-eye subagents were used; no live Cautilus run.
- Delegated review: three initial bounded reviewers plus one counterweight.
- Counterweight caught overbroad `FunctionDef` coverage propagation; a negative
  test now pins it.

## Maintainer-Local Enforcement

- Healthy: `.githooks/pre-push` and `./scripts/run-quality.sh --read-only`
  remain the standing enforcement path.
- `inventory_ci_local_gate_parity.py` scanned one workflow and found 0 parity
  issues; the only workflow is exempt as `scheduled-deeper-check`.

## CI/Local Gate Parity

- Current posture is intentional maintainer-local enforcement until the
  operating-contract reopen trigger fires.

## Enforcement Triage

- `AUTO_EXISTING`: read-only quality, packaging validation, current-pointer
  scan, RCA ledger validation, mutation sample reporting, runtime budgets,
  secrets/supply chain, and CI/local parity inventory.
- `AUTO_CANDIDATE`: behavior-shaped command docs and CLI registry inputs (#214).
- `NON_AUTOMATABLE`: RCA recorder idempotency semantics (#212).

## Healthy

- Skill ergonomics: 22 checked, 0 heuristic findings; prose review still
  required. No immediate trigger blocker found in this pass.
- Current-pointer write scan is clean after constant-propagation and
  local-shadowing regressions.
- `charness tool sync-support` now aligns with `tool doctor` by failing only
  on blocking doctor dispositions.
- `inventory_standing_test_economics.py` now skips volatile pytest temp paths
  that disappear mid-scan.
- `check-seed-fixture-budget` now runs against the repo-keyed pytest temp root;
  focused proof showed 1.1 MiB retained and no breaches.

## Weak

- Standing test economics still shows 188 test files and 81 nested CLI files.
- Release-only CLI lifecycle tests still materialize large repo/home surfaces
  during execution; the current fix reduces retained disk, not execution-time
  copy volume.
- Generated [docs/generated/cli-reference.md](../../docs/generated/cli-reference.md)
  is 786 lines; structural CLI ergonomics lacks registry/archetype inputs
  (#214).
- Direct `validate_packaging_install_surface.py` needs `PYTHONPATH=.` (#213).

## Missing

- No missing standing gate under the current maintainer-local policy.

## Deferred

- RCA ledger `class_key` idempotency: #212.
- CLI ergonomics structural inventory setup: #214.
- Direct bootstrap fix for `validate_packaging_install_surface.py`: #213.

## Advisory

- `inventory_quality_handoff.py` still reflects the older PR-CI recommendation
  pattern; this artifact aligns the recommendation to the operating contract.

## Delegated Review

- Delegated Review: executed. Fresh-eye satisfaction: parent-delegated.
- Reviewers covered fixture-economics, parallel-critical-path,
  duplicated-proof, bug/RCA sibling scan, architecture/code critique, and counterweight.
- Counterweight found one Act Before Ship issue; it was corrected.

## Commands Run

- Commands included read-only quality, mutation probes, targeted `pytest`,
  `ruff`, length checks, packaging validators, current-pointer scan, standing
  economics, CI/local parity, skill ergonomics, runtime summary, quality handoff
  inventory, and issue creation for #212-#214.
- Follow-up pytest temp proof: selected `check-seed-fixture-budget` and `pytest`
  labels in `run-quality.sh`, focused tests, and packaging validators after sync.

## Recommended Next Gates

- passive `AUTO_CANDIDATE`: because registry shape is undecided, design CLI
  ergonomics inputs before promoting structural findings (#214).
- passive `NON_AUTOMATABLE`: because metric semantics change, spec RCA ledger
  idempotency before changing append behavior (#212).

## History

- [2026-05-21 mutation-testability closeout](history/2026-05-21-mutation-testability-closeout.md)
