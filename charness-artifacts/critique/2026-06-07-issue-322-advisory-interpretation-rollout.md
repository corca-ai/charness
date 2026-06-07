# Resolution Critique — #322 advisory-interpretation contract rollout

Date: 2026-06-07
Issue: #322 (roll out the advisory-interpretation contract to remaining
inference-layer surfaces)
Reviewer provenance: bounded fresh-eye subagent review (independent agent
context, read-only in the shared parent worktree), run at the bundle boundary
per the goal's high-confidence verification plan.

## Scope reviewed

Six inference-layer surfaces gained the 4-field `interpretation` self-declaration
(measures / proxy-for / blind-spots / interpretation-question) plus a paired
consumer-must-answer requirement, mirroring the `nose` pilot:

1. `inventory_skill_ergonomics.py` (ergonomics heuristics / `subcheck_counts`)
2. `inventory_standing_test_economics.py` (test-economics trend; declaration in
   the script wrapper)
3. `inventory_lint_ignores.py` / `lint_ignore_inventory_lib.py` (suppression
   pressure)
4. `check_python_lengths.py` warn band / `--headroom` near-limit (length smell
   only — the hard over-limit gate and the function-length AST check stay
   verified facts)
5. `list_capabilities*.py` recommendation ranking (find-skills) +
   `Recommended Next Gates` ordering (quality, agent-authored prose)
6. `render_runtime_summary.py` runtime hot-spot trend

Consumer references: `automation-promotion.md` (per-surface list),
`find-skills/references/discovery-order.md`, `quality/references/gate-classification.md`.

## Findings

- **BLOCKERS: none.** All seven expected invariants hold.
- **Cardinal error (declaration on a verified fact): none found.** The reviewer
  verified each gated surface:
  - length: declaration rides only the warn-band / near-limit advisory; the
    over-limit `ValidationError` path, the clean pass, the exact `limit-current`
    numbers, and the function-length AST check never carry it (guarded by
    negative-assertion tests).
  - find-skills: declaration rides only the recommendation ranking
    (`has_recommendations` gate); a plain inventory run and the canonical
    artifact stay clean.
  - runtime: declaration rides only when hot spots exist.
- **Half-contract: none.** Every surface that gained a declaration also gained a
  paired consumer-must-answer line in the correct consuming reference.
- **Blind-spot quality:** each `blind_spots` field names a concrete proxy/reality
  divergence (not a vacuous "I might be wrong" disclaimer).
- **Surfacing gap: none.** `check_python_lengths.py` is the only changed
  standing gate; its declaration line carries the load-bearing `ADVISORY:` prefix
  so `run-quality.sh` surfaces it on a warn-band pass. The five on-demand
  inventories are read in full by their consumer, so no prefix is required.
- **Mirror parity:** `plugins/charness/` copies byte-match canonical sources.

### NIT (dispositioned, no change made)

`inventory_lint_ignores.py` and `inventory_standing_test_economics.py` print the
human-mode INTERPRETATION line on every successful run (even at zero findings),
whereas `inventory_skill_ergonomics.py` gates on `if skills`.

**Disposition: keep as-is.** This is not the cardinal error — these two surfaces
are entirely inference-layer with no verified-fact variant to distrust, and the
declaration is *about the measure* (valid regardless of finding count), so
emitting it once per on-demand invocation is the contract's intended
"once-per-measure-output", not a per-line banner. It matches the `nose` pilot
precedent (which emits on success regardless of family count). The ergonomics
asymmetry is justified: ergonomics has a genuine no-measure state (unconfigured /
no skills) where there is nothing to declare; lint/test-economics always measure
the surface. These are on-demand surfaces, not standing CI gates, so there is no
per-run spam.

## Verification proof

- Targeted per-surface tests: 140 passed (the 4-field shape + non-empty values +
  paired consumer requirement + cardinal-error negative guards).
- Broad pytest at the bundle boundary: 2511 passed, 4 skipped.
- `ruff` clean; `check_doc_links.py` clean; `check-links-internal.sh` 0 errors.
- Length contract dogfooded: the rollout pushed two libs into the warn band; the
  signal was interpreted (cohesive but tight) and resolved by relocating the
  test-economics declaration to its emitter script and compacting the find-skills
  constant — both back under the warn floor.

## Schema decision (S7)

**Keep per-surface (spec-light); no shared schema/validator forced.** Rationale:
the 4-field declaration is irreducibly per-surface content (the value of the
contract); the per-kind render wording is deliberate honest framing, not
duplication to DRY away; the only genuinely near-identical duplication is the
test-assertion shape, which is small and clear. A shared schema would add
indirection without removing the irreducible per-surface content. The one
genuinely-shared, regression-preventing artifact worth considering later is a
meta-validator that enumerates the inference-layer surfaces and asserts each
emits the 4-field declaration AND carries a paired consumer line — recorded as a
deferred capability (a new gate beyond #322's rollout scope), not built here.
