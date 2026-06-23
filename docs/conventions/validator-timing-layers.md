# Validator Timing Layers

One portable validator, invoked at as many cheap timings as fit — never a
forked rule copy per timing. The validator stays the single source of truth;
a timing layer is only an extra *invocation* of it, scheduled earlier so the
author learns the verdict closer to the keystroke that caused it.

## The decision frame

Timings, ordered by feedback latency (earliest first):

1. **Author-time preflight** — explicit, scoped to the artifact being authored
   ([check_skill_surface_preflight.py](../../scripts/check_skill_surface_preflight.py),
   [check_artifact_surface_preflight.py](../../scripts/check_artifact_surface_preflight.py)).
2. **Edit-time hook** — automatic per-edit firing, adapter-declared and
   host-specific (the `skill_anchor_edit_guard` PostToolUse hook; see
   [authoring-preflight.md](./authoring-preflight.md)).
3. **Commit-time** — the pre-commit dispatcher
   ([staged_commit_gate_plan.py](../../scripts/staged_commit_gate_plan.py)),
   shared verbatim by `.githooks/pre-commit`, the closeout structural sweep,
   and `run_slice_closeout --predict-commit`.
4. **Bundle boundary** — the broad gate
   ([run-quality.sh](../../scripts/run-quality.sh)) plus the pre-push hook and
   the changed-line mutation producer/consumer.
5. **CI / scheduled** —
   [quality-core.yml](../../.github/workflows/quality-core.yml) (push/tag/PR)
   and [mutation-tests.yml](../../.github/workflows/mutation-tests.yml) (cron
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
the enforcement floor, and pre-commit stays bypassable (`--no-verify`) with
[check_boundary_bypass_ratchet.py](../../scripts/check_boundary_bypass_ratchet.py)
guarding erosion.

Budget rule: the pulled commit-time subset must stay small enough that the
hook never tempts `--no-verify`. The 2026-06-10 audit's five pulled guards add
about 0.5s combined (the 2026-06-11 handoff pull adds ~0.1s more, only when
`docs/handoff.md` is staged); treat ~1s of additional typical-path latency as
the line that requires removing something before adding more. The 2026-06-14
leak-scan pulls (#368) are the costliest additions: `validate-inference-interpretation`
(~0.9s full-tree AST leak scan — no cheaper changed-scoped subset, since the
whole-tree scan IS the leak check) and `check-bootstrap-shim-consistency`
(~0.28s). Honest combined-path cost: a `scripts/`|`skills/` `*.py` commit now
runs `validate-attention-state-visibility` (~0.8s) + `validate-inference-interpretation`
(~0.9s) + `check-bootstrap-shim-consistency` (~0.28s) ≈ **~2.0s of full-tree AST
scans**, above the ~1s "add nothing more without removing" line. These three are
explicitly the revisit-first items if the commit path starts tempting
`--no-verify`. They earn the budget anyway because the alternative timing was the
~4-min broad gate (a ~100× feedback win) and pre-commit stays bypassable.

## Classification table (2026-06-10 audit)

Where each broad-gate check ran before the audit, and its timing verdict.
"already earlier" = the commit-time dispatcher (or pre-push) invoked it before
this audit; those rows are listed compressed.

| Check (broad-gate label) | Ran before audit | Verdict | Reason |
| --- | --- | --- | --- |
| py-compile, ruff, check-python-lengths, validate-attention-state-visibility, validate-skills, run-evals, validate-skill-ergonomics, validate-profiles, validate-adapters, validate-presets, validate-integrations, check-doc-links, check-markdown, check-boundary-bypass-ratchet, staged mirror drift, skill-core headroom, artifact shape | commit-time + broad | already earlier | pulled by prior work; unchanged |
| validate-packaging, validate-packaging-committed, validate-current-pointer-freshness, check-changed-line-mutation-coverage | pre-push + broad (now also CI) | already earlier | bundle-range semantics; pre-push is their natural earliest timing |
| check-python-filenames | broad only | **pulled → commit-time** | <0.3s, deterministic, only a staged .py can flip it |
| check-skill-contracts | broad only | **pulled → commit-time** | <0.1s, skills/-scoped |
| check-skill-bootstrap-vars | broad only | **pulled → commit-time** | <0.1s, skills/-scoped |
| validate-surfaces | broad only | **pulled → commit-time** | <0.1s, flips only on a [surfaces manifest](../../.agents/surfaces.json) edit; a broken manifest degrades every surface-driven gate |
| check-title-slug-drift | broad only | **pulled → commit-time** | <0.1s, flips only on a markdown edit |
| inventory-ci-local-gate-parity | broad only (inventory + the real-repo pytest watchdog) | **pulled → commit-time** | <0.1s, flips only on a workflow edit; the commit-time pull carries `--require-canonical-gate-match` so it enforces the same bar as the pytest watchdog (pulled at the goal's own bundle boundary, where the watchdog fired two slices after the workflow was authored) |
| adapter-vs-integration-schema (inside validate-adapters) | runtime only (`invalid_adapter` at the usage-episodes emitter) + example-fixture tests | **pulled → commit-time + broad** | #342: an adapter file had two validation owners and only the weaker ran at commit time; [validate_adapters.py](../../scripts/validate_adapters.py) now jsonschema-validates `.agents/<name>-adapter.yaml` against `integrations/<name>/manifest.schema.json` when it exists (usage-episodes, t-events, worktree), parsing with `yaml.safe_load` like the runtime owner. No new gate command — ~0.07s inside the already-pulled validate-adapters; degrades to no gate without the schema or the `jsonschema` dep. Known asymmetry: the usage-episodes emitter falls back to the charness-bundled schema when a consumer repo has no `integrations/usage-episodes/`, so in that layout the runtime owner still validates while the commit gate inherits nothing — vendoring the schema is the opt-in |
| check-python-runtime-inheritance | broad only | stays | borderline cost (~0.75s) for a rare verdict flip; revisit if the class recurs |
| check-export-safe-imports, check-plugin-import-smoke | broad only | stays | import-graph / import-execution cost |
| check-command-docs | broad only | stays | ~3.3s, over budget |
| validate-usage-episodes, report-usage-episodes, check-cli-skill-surface | broad only | stays | adapter/runtime-state sweeps, not changed-scoped |
| validate-inference-interpretation, check-inventory-declaration-coverage, check-bootstrap-shim-consistency | broad only | **pulled → commit-time** (#368, 2026-06-14) | corrects the original "not changed-scoped" bundling above: each is a cheap, offline, blocking structural check that flips ONLY when a staged file adds a new entrant or drifts a duplicated block — exactly changed-scoped, like `check-python-filenames`. `validate-inference-interpretation` (~0.9s) scans every git-tracked `*.py` outside the registry exclude prefixes (`plugins/`\|`mutants/`\|`tests/`), so its trigger covers that whole domain (including root modules like [runtime_bootstrap.py](../../runtime_bootstrap.py)), NOT just `scripts/`\|`skills/` — a declaration authored in a root module would otherwise escape the commit gate; the full-tree AST scan IS the leak scan (no cheaper subset to split off — the heavier *live-count* assertion stays in the broad-gate pytest `test_live_repo_contract_holds`). `check-inventory-declaration-coverage` (~0.06s, trigger `skills/public/quality/scripts/inventory_*.py`) and `check-bootstrap-shim-consistency` (~0.28s, trigger `scripts/`\|`skills/` `*.py` = its `SCAN_PATTERNS`) round out the cheap-offline-blocking set. All degrade to no gate when the validator is absent (consumer/tmp repo). Evidence: #367 added an `INTERPRETATION` declaration to a new file (`ci_recoverable_gates_lib.py`) whose missing registration surfaced only after a ~4-min broad run, the recurring #314/#319/#332/#366 shift-left class |
| check-public-doc-coupling | broad only | stays (advisory) | always exits 0 — emits `ADVISORY:` lines, never a blocking verdict, so there is no gate-fail to shift left; it surfaces in run-quality output for human attention. (Audited alongside #368; recorded here so the table is complete.) |
| check-timing-layer-completeness | broad only | **pulled → commit-time** (#368, 2026-06-14) | the meta-gate that makes THIS table the enforced single source of truth: it asserts every `run-quality.sh` `queue_selected` label has a verdict in this table, so a new validator cannot sit broad-only and unclassified (the recurrence mechanism). Cheap (~0.05s, reads two checked-in files), flips only when [run-quality.sh](../../scripts/run-quality.sh) or this doc changes — its commit trigger. Degrades to no gate when either file is absent (consumer/tmp repo) |
| validate-public-skill-validation, validate-public-skill-dogfood, validate-cautilus-call-provenance, validate-cautilus-proof, validate-cautilus-scenarios, validate-cautilus-diagnostics | broad only | stays | policy/proof/diagnostic sweeps over standing artifacts (validate-all class; the cautilus checks are the proof + diagnostic family). `validate-cautilus-diagnostics` is changed-scoped when called with `--paths`, but the standing gate intentionally checks existing diagnostic bundles keep parseable machine evidence so negative evaluator findings stay first-class instead of side bundles. |
| validate-handoff-artifact | broad only (was grouped with the sweeps below) | **pulled → commit-time** (2026-06-11) | ~0.1s and changed-scoped after all — it validates exactly one file (`docs/handoff.md`), so the sweep argument never applied; pulled when that file is staged. Evidence: a goal-closeout commit (bc70d76a) emptied a required handoff section AFTER the session's final broad run and sat red-but-unpushed in the commit→push window |
| validate-debug-artifact, validate-quality-artifact, validate-ideation-artifact, validate-retro-artifact, validate-debug-seam-index, validate-retro-lesson-index, inventory-quality-handoff, validate-quality-closeout-contract, validate-critique-artifacts, validate-maintainer-setup, validate-inventory-consumption, validate-inventory-consumption-declaration | broad only | stays | validate-all artifact/contract sweeps (the critique/ideation/retro *shape* checks are already pulled per-file via the artifact-shape dispatcher). `validate-inventory-consumption(-declaration)` stays because it subprocess-runs each inventory's `--json` (over budget); its cheap sibling `check-inventory-declaration-coverage` — a pure glob/JSON new-entrant scan — was pulled to commit-time (#368, row above) |
| check-secrets, check-supply-chain, check-supply-chain-online, check-shell, check-github-actions, check-links-internal, check-links-external, doc-duplicates, check-spec-evidence-durability, check-references-link-inventory, check-seed-fixture-budget, check-test-completeness, check-test-production-ratio, check-current-pointer-writes | broad only | stays | repo-wide scans, network, or suite-metric checks — boundary class |
| pytest, check-coverage, specdown, measure-startup-probes, check-runtime-budget, inventory-cli-ergonomics, inventory-gitignore-scan-hygiene, inventory-nose-clones, inventory-sloc, inventory-ubiquitous-language | broad only | stays | expensive / measuring / inventory class — the boundary IS their timing |
| dup-ratchet | broad only | stays | repo-wide nose code scan (~0.6s) + reuses the broad path's doc-duplicates drift JSON (the boy-scout duplicate ratchet, item 5). Broad-path only by design — kept OUT of the pre-push docs-only subset so the broad path carries the doc-dup teeth the fast subset omits; degrades to advisory when nose/overlay/baseline are absent |

The #N-anchor scan's edit-time pull is slice 2 of the same goal (the
`skill_anchor_edit_guard` adapter intent), recorded in
[authoring-preflight.md](./authoring-preflight.md) — listed here only so the
audit is complete; it was not re-pulled.

## Adding a new timing pull

1. Verify where the validator runs today (this table + the dispatcher) — do
   not re-pull what is already pulled.
2. Classify against the four criteria above; record a "stays" verdict with its
   reason when it fails one. This step is now CI-enforced: `check-timing-layer-completeness`
   fails if a `run-quality.sh` `queue_selected` label has no verdict row here, so
   the table cannot silently fall behind a newly added validator (the #368
   recurrence-mechanism fix — list the exact label, not a `(-suffix)` / glob shorthand).
3. Wire the earlier invocation through the existing dispatcher
   (`staged_commit_gate_plan.py` path conditions or
   `FAST_SURFACE_VERIFY_COMMANDS`), with the exact broad-gate command so the
   verdicts cannot drift.
4. Add a dispatcher test per pulled guard and re-check the budget rule.
