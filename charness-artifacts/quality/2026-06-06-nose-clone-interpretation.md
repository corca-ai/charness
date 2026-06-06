# nose clone interpretation + two open questions
Date: 2026-06-06

Saved so the next session can discuss **without re-scanning**. Produced by
applying the advisory-interpretation contract
([`skills/shared/references/advisory-interpretation-contract.md`](../../skills/shared/references/advisory-interpretation-contract.md))
to the `nose` 0.5.0 advisory (`inventory_nose_clones.py`). Re-derive with
`python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --json`.

## Saved scan data — 20 families / 1951 dup-lines, classified

| # | members | dup | shared | sample | class |
| --- | --- | --- | --- | --- | --- |
| 1 | 86 | 425 | 4 | runtime_bootstrap header across scripts | bootstrap boilerplate — intentional |
| 2 | 8 | 406 | 23 | `init_adapter.py` | per-package adapter — intentional |
| 3 | 7 | 126 | 10 | `resolve_adapter.py` | per-package adapter — intentional |
| 4 | 8 | 126 | 9 | advise/list/suggest recommendation scripts | decomposition (shares repo-root helpers) |
| 5 | 9 | 112 | 9 | `goal_artifact_*` (achieve) | intentional module split |
| 6 | 15 | 98 | 5 | `*_adapter_lib.py` | per-skill adapter lib — borderline |
| 7 | 5 | 96 | 17 | `resolve_adapter.py` + preflight | per-package adapter — intentional |
| 8 | 10 | 90 | 9 | `resolve_adapter.py` | per-package adapter — intentional |
| 9 | 6 | 65 | 10 | `scaffold_*_artifact.py` | per-skill scaffold — intentional |
| 10 | 5 | 56 | 8 | closeout/preflight scripts | decomposition |
| 11 | 6 | 50 | 9 | chunked-routing + goal_artifact | decomposition |
| 12 | 2 | 50 | **41** | scaffold_debug ↔ scaffold_quality | **only real "extractable" pair** (cross-package) |
| 13 | 7 | 42 | 5 | adapter_lib + command-docs | decomposition |
| 14 | 9 | 40 | 3 | current-pointer/usage/artifact-path | low shared, residue |
| 15 | 3 | 38 | 17 | `validate_*_artifact.py` | already share `artifact_validator.py`; residue |
| 16 | 2 | 38 | 30 | `suggest_public_skill_dogfood.py` ×2 locations | **FALSE POSITIVE** — wrapper/invoker pair |
| 17 | 4 | 30 | 8 | `resolve_adapter.py` + review_adapter | per-package adapter — intentional |
| 18 | 4 | 24 | 8 | `issue_*.py` CLI | intentional command pattern |
| 19 | 4 | 21 | 7 | adapter_lib + resolve_adapter | per-package adapter — intentional |
| 20 | 4 | 18 | 6 | adapter_lib + adapter_policy | per-package adapter — intentional |

**Verdict:** ~62%+ (≈1212 lines: #1,#2,#3,#7,#8,#17,#19,#20) is per-package
adapter/bootstrap boilerplate copied *on purpose* for plugin-export
self-containment. #16 is a false positive (the smarter `inventory_dual_implementation`
clears it, `candidate_count=0` — nose is lexical and over-counts the wrapper
pair). #12 is the single genuine "could extract" case but the two files live in
different skill packages. Extractable real debt today ≈ **0 lines**; the advisory
stays `NON_AUTOMATABLE` (the dominant cause *requires* the copies).

## Open Question 1 — kill confirmed false positives at the source

**Q:** Can the confirmed false-positive class (e.g. #16) be made to never appear,
via the adapter (scan-target restriction/exclusions), quality-skill improvement,
or a `corca-ai/nose` issue?

**Opinion (agent, non-binding):**

- **Right layer = the charness quality skill / adapter, not nose.**
  "Portability boilerplate" is charness-specific policy; a generic lexical clone
  tool should not encode it.
- **Strongest move:** extend `inventory_nose_clones.py` to *classify* families
  (bootstrap-header / per-package-adapter / wrapper-pair / candidate) by
  structural rule (same basename across skill packages; known bootstrap header),
  and cross-reference `inventory_dual_implementation` to auto-drop
  semantically-cleared pairs (#16). Then the headline becomes honest:
  "1951 total, ~1900 intentional, ~50 candidate." This is the **tool-side
  implementation of the interpretation contract** — it folds into **#322**, and
  it is the `AUTO_CANDIDATE` path for the interpretation itself (clear
  one-sentence invariant + obvious response = classify, not extract).
- **Caution:** do NOT build a blanket exempt-family list (hides regressions, per
  `lint-ignore-discipline`). Use structural rules + a "new family vs baseline"
  ratchet (like `check_boundary_bypass_ratchet`) so genuinely-new
  non-intentional duplication still surfaces.
- **nose issue:** only for a *generic* capability gap — exclusion globs
  (`--exclude`), per-family category/metadata in output, or an
  "ignore same-basename-across-dirs" option. First check what nose 0.5 config
  already supports; file upstream only if the charness-side classifier needs a
  hook nose lacks. Charness policy stays in charness.

## Open Question 2 — is the intentional duplication truly unavoidable?

**Q:** By changing the current structure, is there really no way to reduce the
duplication? Is the "intentional" copy an unavoidable limit, or a chosen tradeoff?

**Opinion (agent, non-binding):**

- **"Intentional" ≠ "unavoidable."** It is a *chosen* tradeoff (per-package
  self-containment for portability/independence), not a physical limit.
- **Technically de-dup-able:** the plugin export ships repo-root `scripts/`, and
  skill scripts already reach repo-root modules via `runtime_bootstrap`
  (`import_repo_module(__file__, "scripts.artifact_validator")`). So a shared
  adapter-resolution core would not break export. Partial sharing already exists
  (`scripts/*_adapter_lib.py` = family #6) — the architecture is mid-way.
- **Real lever:** measure *actual divergence* across the `resolve_adapter` /
  `init_adapter` copies. If near-identical → a shared core + per-skill
  schema-only config cuts a large chunk; if they genuinely diverge → the
  duplication is real cohesion, leave it.
- **But ROI is low:** the duplication is cheap, mechanical, low-bug-risk,
  low-churn. De-dup trades duplication for coupling against the stated
  "self-contained skill package" principle. **My lean:** treat as a deferred
  `ideation` → `spec` architecture question for the maintainer; the nose number
  is a *weak* driver. The honest reframe is not "can we de-dup" (yes, partially)
  but "is the coupling worth it" (probably not until the copies drift and cause
  an inconsistency bug). Revisit when drift causes a real defect.

## Pointers

- Contract pilot + rollout: **#322**.
- Architecture surfaces for Q2: [`docs/harness-composition.md`](../../docs/harness-composition.md),
  [`docs/capability-resolution.md`](../../docs/capability-resolution.md).
