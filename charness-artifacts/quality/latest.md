# Quality Review
Date: 2026-05-21

## Scope
Current slice: broad `charness:quality` posture review for the self-repo after
the #183 release. Scope covers standing gates, local enforcement, public/support
skill ergonomics, docs drift, CI/local parity, runtime/test economics, source
scan hygiene, security and supply-chain gates, and durable quality artifacts.

## Concept Risks
- The previous `latest.md` was a mutation-closeout artifact; this review
  restores the current-pointer role and archives that closeout under `history/`.
- The unresolved boundary is policy: local pre-push is enforced, while no
  non-exempt PR CI quality workflow mirrors it.

## Current Gates
- `./scripts/run-quality.sh` passed with `65` phases and now includes
  `inventory-gitignore-scan-hygiene`.
- `.githooks/pre-push` syncs plugin exports, validates current pointers, runs
  read-only quality, and fails if `charness-artifacts/` mutates.
- `scripts/validate_maintainer_setup.py` proved this clone uses `.githooks`.
- Security and supply chain are locally covered by `check-secrets`,
  `check-supply-chain`, `check-github-actions`, `check-shell`, and link gates.

## Runtime Signals
- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py` via `scripts/record_quality_runtime.py`.
- runtime hot spots: `check-coverage` 38.3s latest / 39.2s median, `pytest`
  21.3s latest / 32.4s median, `check-duplicates` 7.5s latest / 7.6s median,
  all within configured local-profile budgets.
- coverage gate: `check-coverage` passed in the read-only gate; the reference
  `coverage_floor_inventory.py` sample is not this repo's coverage carrier.
- evaluator depth: no live Cautilus run; this request was a generic quality
  review, so deterministic gates plus bounded fresh-eye review were the proof.

## Standing Test Economics
- `inventory_standing_test_economics.py` reported `test_file_count=177`,
  `nested_cli_file_count=75`, runner_snippets from shell/JS gates, and a
  measured pytest temp footprint of `3532247040` allocated bytes across `3`
  retained sessions.

## Testability and Selection
- The #183 mutation sampler owns mutation-line/selected-nodeid proof, but
  standing tests still contain many real CLI/subprocess smokes. Move repeated
  assertions below that boundary before adding another selector or budget.

## Coverage and Eval Depth
- `inventory_public_spec_quality.py` reported `public_spec_count=4`,
  `source_guard_row_count=0`, `implementation_path_ref_density=0.0`,
  `executable_block_count=8`; public specs are not the brittle proof layer.
- The `quality` dogfood case resolves to `charness-artifacts/quality/latest.md`
  and tier `hitl-recommended`.

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
- `inventory_gitignore_scan_hygiene.py` is now clean after replacing five
  repo-wide scans with git-visible file discovery and promoting it into
  `scripts/run-quality.sh`.
- `inventory_lint_ignores.py` found `blanket_count=0`, `file_level_count=0`,
  `codes` limited to narrow inline records, and `scope=inline`.

## Weak
- Docs ergonomics still has generated-reference noise, but README first-touch
  prose has been reduced: `README.md` now reports
  `core_nonempty_lines=135`, `internal_doc_link_count=37`, and no
  entrypoint-doc heuristics; `docs/cli-reference.md` remains a generated leaf
  with `core_nonempty_lines=670`.
- Standing test economics still shows nested CLI fanout across `75` files and
  a multi-GB retained pytest temp footprint from real packaging/tool tests.
- Usage-episodes validation is visible but intentionally disabled by
  [.agents/usage-episodes-adapter.yaml](../../.agents/usage-episodes-adapter.yaml);
  the next product decision is vocabulary, not adapter discovery.

## Missing
- No non-exempt standing PR CI workflow runs the local quality gate. Current
  proof is maintainer-local pre-push plus scheduled mutation deeper-check.

## Deferred
- Release-side real-host verification remains in `charness-artifacts/release/latest.md`.
- Do not add docs/runtime gates from the noisy inventories until a concrete
  ownership rule or duplicated-proof deletion candidate is selected.

## Advisory
- `inventory_entrypoint_docs_ergonomics.py` advisory: generated reference
  length remains visible in [docs/cli-reference.md](../../docs/cli-reference.md),
  but first-touch README route/procedure duplication has been moved to
  [docs/workflow-routes.md](../../docs/workflow-routes.md).
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
- Capability/bootstrap helpers; skill/docs/test-economics/spec/lint/CI/gitignore
  inventories; runtime summary and dogfood suggestion.
- `./scripts/run-quality.sh --read-only`, targeted gitignore hygiene quality
  run, ruff, and focused pytest inventory/doc-link tests (`65 passed`).

## Recommended Next Gates
- active `AUTO_EXISTING`: keep `inventory-gitignore-scan-hygiene` in
  `scripts/run-quality.sh`; existing-convention check found helper/inventory
  lineage via `git log -S inventory_gitignore_scan_hygiene` and `rg repo_file_listing`.
- passive `NON_AUTOMATABLE`: because CI policy is unresolved, decide whether PR CI should mirror
  `./scripts/run-quality.sh --read-only`; existing-convention check found
  `scheduled-deeper-check` as the only CI policy, so this is a policy choice,
  not an accidental local gate omission.
- passive `AUTO_CANDIDATE`: because the first clear cleanup is complete, keep
  docs ergonomics ownership separate before adding a gate; the remaining
  generated-reference length needs ownership review, not automatic failure.
  [README.md](../../README.md) is now below the entrypoint heuristic threshold,
  while [docs/cli-reference.md](../../docs/cli-reference.md) remains generated
  reference material rather than first-touch prose.

## History
- [2026-05-21 mutation-testability closeout](history/2026-05-21-mutation-testability-closeout.md)
- [2026-05-14 mutation testing dogfood](history/2026-05-14-mutation-testing-dogfood.md)
- [2026-05-12 archive](history/2026-05-12-quality-review.md)
