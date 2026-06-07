feat(quality,find-skills): roll out advisory-interpretation contract to inference-layer surfaces (Close #322)

Close #322.

Classification: feature.
Issue closeout carrier: direct-commit.
Issue: #322 roll out the advisory-interpretation contract (4-field
`interpretation` self-declaration + paired consumer-must-answer requirement),
piloted on the `nose` clone advisory, to the remaining inference-layer surfaces.

JTBD: a reader of an inference-layer output (heuristic, proxy, ranking, trend)
must receive the agent's interpretation of what the number means and cannot
answer, not a bare proxy presented as a verdict — so deterministic sensors keep
the repository's judgment in the loop instead of quietly displacing it.

Boundary: inference-layer ONLY. Verified facts (green gates, exact counts, AST
results, the hard length limit, the function-length check, the capability
inventory) stay trusted and never carry the declaration. Each declaration is a
terse positive-form block (not a repeated distrust banner); each is paired with a
consumer-must-answer line in its consuming reference.

Resolution brief: add the 4-field `interpretation` self-declaration to six
inference-layer surfaces mirroring the `nose` pilot — (1) ergonomics heuristics
`inventory_skill_ergonomics.py`, (2) test-economics trend
`inventory_standing_test_economics.py`, (3) suppression pressure
`inventory_lint_ignores.py`/`lint_ignore_inventory_lib.py`, (4) length warn-band
/ `--headroom` near-limit `check_python_lengths.py` (advisory only), (5)
recommendation rankings (`find-skills` `recommendation_interpretation` +
`quality` `Recommended Next Gates` ordering), (6) runtime hot-spot trend
`render_runtime_summary.py` — and pair each with its consumer-must-answer line in
`automation-promotion.md`, `find-skills/references/discovery-order.md`, and
`gate-classification.md`. Spec-light, per-surface; the shared-schema decision is
recorded as keep-per-surface.

Implementation: per-surface `INTERPRETATION` dict emitted in JSON payload and a
positive-form human line, gated so it rides only the inference-layer output and
never a verified fact (length: warn-band/near-limit only, `ADVISORY:`-prefixed so
`run-quality.sh` surfaces it on a pass; find-skills: only when a ranking is
produced; runtime: only when hot spots exist). The rollout dogfooded its own
length contract — it tripped the warn band on two libs, which was interpreted and
resolved by relocating the test-economics declaration to its emitter script and
compacting the find-skills constant. Generated `plugins/` mirror synced.

Prevention: per-surface tests assert BOTH halves (the 4-field declaration with
non-empty values AND the paired consumer requirement) plus cardinal-error
negative guards (no declaration on the over-limit/clean-pass/function-length
facts, on a plain capability inventory, or on an empty runtime report), so a
regression that leaks a declaration onto a verified fact or drops a consumer
pairing trips a test.

Tests: targeted per-surface suites 140 passed; broad pytest 2511 passed, 4
skipped; `ruff`, `check_doc_links.py`, and `check-links-internal.sh` all clean.

Schema decision: keep per-surface (spec-light) — recorded; no shared
schema/validator forced. A meta-validator enumerating inference-layer surfaces is
noted as a deferred capability beyond this rollout's scope.

Critique #322: charness-artifacts/critique/2026-06-07-issue-322-advisory-interpretation-rollout.md
Retro: charness-artifacts/retro/2026-06-07-322-advisory-interpretation-rollout.md
