# Validator Timing Layers

> Status: current
> Source of truth: this page and its linked executable surfaces
> Last verified: 2026-09-04

One portable validator, invoked at as many cheap timings as fit — never a
forked rule copy per timing. The validator stays the single source of truth;
a timing layer is only an extra *invocation* of it, scheduled earlier so the
author learns the verdict closer to the keystroke that caused it.

## The decision frame

Timings, ordered by feedback latency (earliest first):

1. **Author-time preflight** — explicit, scoped to the artifact being authored
   ([check_skill_surface_preflight.py](../scripts/gates/check_skill_surface_preflight.py),
   [check_artifact_surface_preflight.py](../scripts/gates/check_artifact_surface_preflight.py)).
2. **Edit-time hook** — automatic per-edit firing, adapter-declared and
   host-specific (the `skill_anchor_edit_guard` PostToolUse hook; see
   [authoring-preflight.md](./authoring-preflight.md#portable-skill-packages);
   `--scan-issue-anchors` and [host_hook_registry.py](../scripts/hooks/host_hook_registry.py)).
3. **Commit-time** — the pre-commit dispatcher
   ([staged_commit_gate_plan.py](../scripts/staged_commit_gate_plan.py)),
   the cheap owners of staged files
   ([check_staged_cheap_owners.py](../scripts/hooks/check_staged_cheap_owners.py))
   in `.githooks/pre-commit`, plus the commit-msg release-lane receipt check
   (`Slice-reopen:` skips that receipt, not the cheap owners).
4. **Bundle boundary** — the broad gate
   ([run-quality.sh](../scripts/run-quality.sh)) plus the pre-push hook.
   Ordinary implementation stops at focused tests plus the default core lane;
   changed-line coverage and mutation have one owner in the release-final lane.
5. **CI / scheduled** —
   [quality-core.yml](../.github/workflows/quality-core.yml) (push/tag/PR)
   and [mutation-tests.yml](../.github/workflows/mutation-tests.yml) (cron
   deeper check).

A validator qualifies for an earlier timing only when the invocation at that
timing is **cheap** (sub-second at commit time), **changed-scoped** (only the
staged change class can flip its verdict, so the trigger is a path condition),
**deterministic** (no network, no host-state dependence), and **not
validate-all** (its verdict is about the change, not a sweep over standing
artifacts whose freshness is a boundary concern). Anything expensive
(mutation, coverage, full pytest, import smoke), networked, measuring, or
inventory/sweep-shaped stays at the bundle boundary or later. Earlier timing
is a faster feedback LAYER, never a replacement: the broad gate and CI remain
the enforcement floor, and pre-commit stays bypassable (`--no-verify`) with the
production spawn-form check and staged test-boundary advisory providing early
feedback.

Budget rule: the pulled commit-time subset stays small enough that the hook
never tempts `--no-verify`; roughly one second of added typical-path latency is
the line for removing something before adding more, and the three full-tree AST
scans on a `scripts/`|`skills/` `*.py` commit
(`validate-attention-state-visibility`, `validate-inference-interpretation`,
`check-bootstrap-shim-consistency`) are the revisit-first items. Measured
history:
[leak-scan shift-left critique](../charness-artifacts/critique/2026-06-15-issue-368-leak-scan-shift-left.md).

## Classification table
<!-- BEGIN GENERATED: validator timing layers -->
| Check (broad-gate label) | Timing layer |
| --- | --- |
| pytest-release, pytest, agent-browser-runtime-baseline, quality-tool-fixtures, dead-code-advisory, check-cli-skill-surface, validate-public-skill-validation, validate-public-skill-dogfood, validate-debug-artifact, validate-retro-lesson-index, validate-lesson-ledger, validate-quality-artifact, validate-inventory-consumption, inventory-skill-script-references, check-unreferenced-scripts, validate-quality-closeout-contract, validate-critique-artifacts, validate-ideation-artifact, validate-retro-artifact, validate-maintainer-setup, check-python-runtime-inheritance, check-script-lookup-form, check-wall-clock-form, check-timeout-bound-form, check-module-eviction-form, check-runtime-budget-universe, check-command-dominance, check-export-safe-imports, check-export-self-sufficiency, check-plugin-import-smoke, check-command-docs, check-doc-links, docs-graph, check-links-internal, check-links-external, check-plugin-asset-command-carriers, check-documented-command-flags, check-documented-subcommands, check-spec-evidence-durability, check-artifact-referents, check-references-link-inventory, check-secrets, check-supply-chain, check-github-actions, check-supply-chain-online, check-shell, check-rust, check-coverage, check-test-completeness, check-test-production-ratio, check-closeout-classification-parity, specdown, doc-duplicates, validate-inventory-consumption-declaration, dup-ratchet, check-seed-fixture-budget, inventory-gitignore-scan-hygiene, check-current-pointer-writes, measure-startup-probes, inventory-sloc, inventory-cli-ergonomics, inventory-nose-clones, check-runtime-budget, agent-browser-runtime-hygiene | stays |
| validate-skills, validate-skill-ergonomics, validate-profiles, validate-presets, validate-adapters, validate-integrations, validate-packaging, validate-attention-state-visibility, validate-current-pointer-freshness, check-python-lengths, py-compile, ruff, run-evals | already earlier |
| validate-quality-reference-catalog, validate-surfaces, validate-inference-interpretation, check-inventory-declaration-coverage, check-python-filenames, check-subprocess-form, check-skill-contracts, check-skill-bootstrap-vars, check-bootstrap-shim-consistency, check-timing-layer-completeness, check-plugin-doc-links, check-plugin-dir-references, inventory-ci-local-gate-parity | **pulled → commit-time** |
| validate-packaging-committed | moved to release boundary |
| validate-debug-seam-index, check-docs-length | pulled → commit-time |
| check-public-doc-coupling | stays (advisory) |
| check-regenerable-facts | **stays (broad)** |
| check-docs | **pulled → commit-time + broad** |
| check-markdown | **narrowed -> scoped commit-time + broad** |
| check-consumer-validator-catalog, check-provenance-contract | pulled to commit-time |
| release-changed-line-coverage | release-final owner |
<!-- END GENERATED: validator timing layers -->
## Adding a new timing pull

1. Verify where the validator runs today (this generated table + the dispatcher) — do
   not re-pull what is already pulled.
2. Classify against the four criteria above; record a "stays" verdict with its
   reason when it fails one. This step is now CI-enforced: `check-timing-layer-completeness`
   fails if a declared `run-quality.sh` gate label has no verdict row here; list
   the exact label, not a glob shorthand.
3. Wire the earlier invocation through the existing dispatcher
   ([`staged_commit_gate_plan.py`](../scripts/staged_commit_gate_plan.py) path conditions or
   `FAST_SURFACE_VERIFY_COMMANDS`), with the exact broad-gate command so the
   verdicts cannot drift.
4. Add a dispatcher test per pulled guard and re-check the budget rule.
