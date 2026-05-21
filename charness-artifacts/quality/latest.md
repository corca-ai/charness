# Quality Review
Date: 2026-05-22

## Scope
Current slice: broad self-repo quality posture after the #183 release: standing
gates, local enforcement, skill ergonomics, docs drift, CI/local parity,
runtime/test economics, security/supply-chain gates, and artifacts.

## Concept Risks
- The previous `latest.md` was a mutation-closeout artifact; this review
  restores the current-pointer role and archives that closeout under `history/`.
- The unresolved boundary is policy: local pre-push is enforced, while no
  non-exempt PR CI quality workflow mirrors it.

## Current Gates
- `./scripts/run-quality.sh --read-only` passed; the standing queue now includes
  `inventory-gitignore-scan-hygiene` and `check-current-pointer-writes`.
- `.githooks/pre-push` syncs plugin exports, validates current pointers, runs
  read-only quality, and fails if `charness-artifacts/` mutates.
- `scripts/validate_maintainer_setup.py` proved this clone uses `.githooks`.
- Security and supply chain are locally covered by `check-secrets`,
  `check-supply-chain`, `check-github-actions`, `check-shell`, and link gates.

## Runtime Signals
- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py` via `scripts/record_quality_runtime.py`.
- runtime hot spots: `check-coverage` 38.3s latest / 39.2s median, `pytest`
  21.3s latest / 32.4s median, and `check-duplicates` 7.5s latest / 7.6s
  median, all within configured local-profile budgets.
- coverage gate: `check-coverage` passed in the read-only gate; the reference
  `coverage_floor_inventory.py` sample is not this repo's coverage carrier.
- evaluator depth: no live Cautilus run; deterministic gates plus bounded
  fresh-eye review were the proof.

## Standing Test Economics
- `inventory_standing_test_economics.py` reported `test_file_count=177`,
  `nested_cli_file_count=75`, runner_snippets from shell/JS gates, and a
  measured pytest temp footprint of `3532247040` allocated bytes across `3`
  retained sessions.

## Testability and Selection
- Mutation sampling starts subprocess coverage with inherited pytest context,
  selects CLI/script nodeids, and splits changed-file exclusions into
  file-coverage-floor and mutation-line buckets.
- Mutation changed-file diff discovery now fails closed when a base SHA is set
  and `git diff --name-only` fails, before sample manifests or Cosmic Ray
  config rewrites.
- Read-only changed-path discovery and shell markdown/link/secret/shell file
  discovery now fail closed when required collectors fail.

## Coverage and Eval Depth
- `inventory_public_spec_quality.py` reported `public_spec_count=4`,
  `source_guard_row_count=0`, `implementation_path_ref_density=0.0`,
  `executable_block_count=8`; public specs are not the brittle proof layer.
- `quality` dogfood resolves to `charness-artifacts/quality/latest.md` and tier
  `hitl-recommended`.
- Public-skill closeout review kept scenario coverage unchanged: `find-skills`
  already has `find-skills-local-first` plus read-only current-pointer dogfood,
  and `release` remains HITL-recommended with reviewed dogfood evidence.

## Maintainer-Local Enforcement
- Healthy: checked-in `.githooks/pre-push`, `scripts/install-git-hooks.sh`, and
  clone validator exist and passed; the hook also fails on artifact mutation.

## CI/Local Gate Parity
- `inventory_ci_local_gate_parity.py` scanned one workflow with `0`
  parity-issue steps; the only workflow is exempt as `scheduled-deeper-check`.

## Enforcement Triage
- `AUTO_EXISTING`: pre-push/read-only quality, validators, runtime budgets,
  coverage, secrets/supply chain, CI/local parity, and gitignore scan hygiene.
- `AUTO_CANDIDATE`: docs ownership and repeated CLI-boundary test fanout.
- `NON_AUTOMATABLE`: whether PR CI should mirror local pre-push.

## Healthy
- `inventory_skill_ergonomics.py` returned `scope_status=scanned`,
  `checked_skill_count=22`, `heuristic_finding_count=0`, and
  `prose_review_status=still_required`.
- prose review result: no skill trigger boundary blocker found for this pass.
- `inventory_gitignore_scan_hygiene.py` and `check_current_pointer_writes.py`
  are clean; release/find-skills/Cautilus current snapshot writers now use the
  shared symlink-safe current-pointer writer.
- `inventory_lint_ignores.py` found `blanket_count=0`, `file_level_count=0`,
  `codes` limited to narrow inline records, and `scope=inline`.

## Weak
- Docs ergonomics still has generated-reference noise, but README first-touch
  prose is reduced: `README.md` reports `core_nonempty_lines=135`,
  `internal_doc_link_count=37`, and no entrypoint-doc heuristics; generated
  [docs/cli-reference.md](../../docs/cli-reference.md) remains `670` lines.
- Standing test economics still shows nested CLI fanout across `75` files and
  a multi-GB retained pytest temp footprint from real packaging/tool tests.
- Usage-episodes validation is visible but disabled by
  [.agents/usage-episodes-adapter.yaml](../../.agents/usage-episodes-adapter.yaml);
  the next decision is vocabulary, not adapter discovery.

## Missing
- No non-exempt standing PR CI workflow runs the local quality gate. Current
  proof is maintainer-local pre-push plus scheduled mutation deeper-check.

## Deferred
- Release diff, broken real-host config, previous-tag base-ref lookup/fetch, and
  post-create verification suppression are now fail-closed with explicit proof.
- Next sibling: run a completion audit over remaining bug-pattern surfaces.
- Do not add docs/runtime gates from the noisy inventories until a concrete
  ownership rule or duplicated-proof deletion candidate is selected.

## Advisory
- `inventory_entrypoint_docs_ergonomics.py`: generated reference length remains
  visible in [docs/cli-reference.md](../../docs/cli-reference.md), but
  first-touch duplication moved to [docs/workflow-routes.md](../../docs/workflow-routes.md).
- `inventory_standing_test_economics.py` advisory: `nested_cli_files` are the
  review queue; reduce process-boundary proof before changing budgets.
- `inventory_adapter_gate_design.py` advisory: phrase detectors stay advisory
  unless adapter policy makes them reviewable.

## Delegated Review
- Delegated Review: executed. Fresh-eye satisfaction context: parent-delegated.
  Reviewer confirmed the artifact scope gap, gitignore gate promotion, CI
  policy gap, docs noise, and standing-test risk through slow-gate lenses:
  fixture-economics, parallel-critical-path, duplicated-proof.

## Commands Run
- Capability/bootstrap helpers; inventories; current-pointer scan; runtime
  summary; dogfood suggestion; `./scripts/run-quality.sh --read-only`;
  targeted quality labels, ruff, focused pytest, and narrow mutation proof.

## Recommended Next Gates
- active `AUTO_EXISTING`: keep `inventory-gitignore-scan-hygiene` and
  `check-current-pointer-writes` in `scripts/run-quality.sh`.
- passive `NON_AUTOMATABLE`: because CI policy is unresolved, decide whether PR
  CI should mirror `./scripts/run-quality.sh --read-only`; current CI has only
  `scheduled-deeper-check`.
- passive `AUTO_CANDIDATE`: because generated-reference ownership is unresolved,
  keep docs ergonomics separate; README is below the threshold and generated
  [docs/cli-reference.md](../../docs/cli-reference.md) remains separate.
## History
- [2026-05-21 mutation-testability closeout](history/2026-05-21-mutation-testability-closeout.md)
- [2026-05-14 mutation testing dogfood](history/2026-05-14-mutation-testing-dogfood.md)
