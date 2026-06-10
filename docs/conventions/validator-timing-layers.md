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
about 0.5s combined; treat ~1s of additional typical-path latency as the line
that requires removing something before adding more.

## Classification table (2026-06-10 audit)

Where each broad-gate check ran before the audit, and its timing verdict.
"already earlier" = the commit-time dispatcher (or pre-push) invoked it before
this audit; those rows are listed compressed.

| Check (broad-gate label) | Ran before audit | Verdict | Reason |
| --- | --- | --- | --- |
| py-compile, ruff, check-python-lengths, validate-attention-state-visibility, validate-skills, run-evals, validate-skill-ergonomics, validate-profiles, validate-adapters, validate-presets, validate-integrations, check-doc-links, check-markdown, check-boundary-bypass-ratchet, staged mirror drift, skill-core headroom, artifact shape | commit-time + broad | already earlier | pulled by prior work; unchanged |
| validate-packaging(-committed), validate-current-pointer-freshness, check-changed-line-mutation-coverage | pre-push + broad (now also CI) | already earlier | bundle-range semantics; pre-push is their natural earliest timing |
| check-python-filenames | broad only | **pulled → commit-time** | <0.3s, deterministic, only a staged .py can flip it |
| check-skill-contracts | broad only | **pulled → commit-time** | <0.1s, skills/-scoped |
| check-skill-bootstrap-vars | broad only | **pulled → commit-time** | <0.1s, skills/-scoped |
| validate-surfaces | broad only | **pulled → commit-time** | <0.1s, flips only on a [surfaces manifest](../../.agents/surfaces.json) edit; a broken manifest degrades every surface-driven gate |
| check-title-slug-drift | broad only | **pulled → commit-time** | <0.1s, flips only on a markdown edit |
| check-python-runtime-inheritance | broad only | stays | borderline cost (~0.75s) for a rare verdict flip; revisit if the class recurs |
| check-export-safe-imports, check-plugin-import-smoke | broad only | stays | import-graph / import-execution cost |
| check-command-docs | broad only | stays | ~3.3s, over budget |
| validate-usage-episodes, report-usage-episodes, check-cli-skill-surface, validate-inference-interpretation | broad only | stays | adapter/runtime-state sweeps, not changed-scoped |
| validate-public-skill-validation, validate-public-skill-dogfood, cautilus trio | broad only | stays | policy/proof sweeps over standing artifacts (validate-all class) |
| validate-handoff/debug/quality artifact, debug-seam/retro-lesson indexes, inventory-quality-handoff, validate-quality-closeout-contract, validate-critique-artifacts (sweep form), validate-maintainer-setup, check-inventory-declaration-coverage, validate-inventory-consumption(-declaration) | broad only | stays | validate-all artifact/contract sweeps (the critique/ideation/retro *shape* checks are already pulled per-file via the artifact-shape dispatcher) |
| check-secrets, check-supply-chain(-online), check-shell, check-github-actions, check-links-internal/external, check-doc-near-duplicates, check-spec-evidence-durability, check-references-link-inventory, check-seed-fixture-budget, check-test-completeness, check-test-production-ratio, check-current-pointer-writes | broad only | stays | repo-wide scans, network, or suite-metric checks — boundary class |
| pytest (broad), check-coverage, specdown, measure-startup-probes, check-runtime-budget, inventory-* | broad only | stays | expensive / measuring / inventory class — the boundary IS their timing |

The #N-anchor scan's edit-time pull is slice 2 of the same goal (the
`skill_anchor_edit_guard` adapter intent), recorded in
[authoring-preflight.md](./authoring-preflight.md) — listed here only so the
audit is complete; it was not re-pulled.

## Adding a new timing pull

1. Verify where the validator runs today (this table + the dispatcher) — do
   not re-pull what is already pulled.
2. Classify against the four criteria above; record a "stays" verdict with its
   reason when it fails one.
3. Wire the earlier invocation through the existing dispatcher
   (`staged_commit_gate_plan.py` path conditions or
   `FAST_SURFACE_VERIFY_COMMANDS`), with the exact broad-gate command so the
   verdicts cannot drift.
4. Add a dispatcher test per pulled guard and re-check the budget rule.
