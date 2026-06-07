# Resolution Critique — #330 advisory-interpretation meta-validator + #331 surface-idiom lint

Date: 2026-06-07
Issue: #330 (a meta-validator that enforces the #322 advisory-interpretation
contract across ALL inference-layer surfaces: each surface emits the 4-field
`interpretation` self-declaration plus a paired consumer-must-answer line, and
verified facts never carry a declaration). Bundles the #331-deferred
surface-idiom lint.
Reviewer provenance: bounded fresh-eye subagent review (independent agent
context, read-only in the shared parent worktree), run at the bundle boundary per
the goal's high-confidence verification plan. Verdict: SHIP-WITH-NITS.
Fresh-eye satisfaction: satisfied — parent-delegated bounded review returned
SHIP-WITH-NITS; every NIT and the QUESTION were folded before ship (no deferral).

## Scope reviewed

- `.agents/inference-interpretation-surfaces.json` — NEW registry (8 surfaces: 7
  python declarations + 1 prose ranking) with declaration symbol + paired consumer
  reference/anchor.
- `scripts/validate_inference_interpretation.py` — NEW meta-validator: registry
  load+validate, AST leak scan, per-surface 4-field non-empty + consumer-pairing
  assertion, prose-anchor check, portable no-op when absent.
- `scripts/surfaces_lib.py` — surface-idiom lint (`_check_surface_idiom`) wired
  into `_validate_surface` for source and derived patterns.
- Gate wiring: `run-quality.sh` (`validate-inference-interpretation` after
  `validate-surfaces`), `tests/quality_gates/support.py` stub, and a new
  `inference-interpretation-contract` surface in `.agents/surfaces.json` for slice
  closeout.
- Tests: `test_inference_interpretation_meta_validator.py` (18), 3 added idiom
  tests in `test_surface_obligations.py`; synced plugin mirrors.

## Findings

- **BLOCKERS: none.** The live validator passes with the expected "8
  inference-layer surface(s) (7 python, 1 prose)" signature; the AST scan finds
  exactly the 7 registered declarations; mirrors byte-match; the gate is fail-closed
  on the load-bearing cases (remove a field / drop a consumer anchor / unregistered
  declaration each turn it red).
- **NIT (folded) — leak scan missed the annotated `X: dict = {...}` form.** The
  reviewer empirically showed `find_declaration_dicts` only walked `ast.Assign`,
  so an annotated declaration — a natural way to write the exact same dict — would
  silently bypass the leak scan, defeating the gate's whole fail-closed point. The
  docstring also overclaimed "any nesting." **Acted before ship:** added
  `ast.AnnAssign` handling, corrected the docstring to an honest scope boundary
  (dict literals bound to a name; non-literal `dict(...)`/dynamic forms stay owned
  by registration discipline + per-surface tests), and added detection + leak tests.
- **NIT (folded) — idiom lint missed a root-level `**/*.X`.** The regex required a
  `<dir>/` prefix, so a top-of-manifest `**/*.py` (the same fnmatch footgun) was not
  flagged. **Acted before ship:** made the directory optional; the required sibling
  is the bare `*.X`. Test added.
- **QUESTION (tightened) — two generic prose anchors carried no signal.** "It
  measures" / "it proxies for" could survive an incidental reword. The gate was
  already fail-closed via the distinctive anchors, but **tightened** both to
  content-specific substrings to remove dead signal.

## Structured Findings

- annassign-leak-hardening | bin: act-before-ship | evidence: strong | ref: scripts/validate_inference_interpretation.py find_declaration_dicts | action: fix | note: leak scan now catches the annotated `X: dict = {...}` form; docstring corrected from the false "any nesting" claim to an honest literal-dict scope boundary; detection + unregistered-AnnAssign leak tests added.
- root-level-idiom-lint | bin: act-before-ship | evidence: moderate | ref: scripts/surfaces_lib.py _RECURSIVE_EXTENSION_PATTERN | action: fix | note: optional `<dir>/` prefix so a root-level `**/*.X` is flagged against the bare `*.X` sibling; regression test added.
- generic-prose-anchors | bin: over-worry | evidence: weak | ref: .agents/inference-interpretation-surfaces.json prose_anchors | action: fix | note: tightened two generic 2-word anchors to distinctive substrings; gate was already fail-closed via the distinctive anchors, so this removes dead signal rather than closing a hole.
- file-granular-structural-scope | bin: valid-but-defer | evidence: strong | ref: scripts/validate_inference_interpretation.py module docstring | action: document | note: intra-file inference-vs-verified gating (warn-band vs over-limit) and non-literal dict constructions stay owned by the per-surface #322 tests + fresh-eye review; documented as an honest non-claim, NOT built (#330 Non-Goal: no content/semantic classifier).

## Reviewer Tier Evidence

- Requested tier: bounded fresh-eye subagent review (independent agent context, read-only in the shared parent worktree).
- Requested spawn fields: review packet — intent, changed files, expected invariants, non-claims, out-of-scope, and five adversarial reviewer questions (fail-closed completeness, consumer-anchor specificity, idiom-lint correctness, portability, gate wiring).
- Host exposure state: applied
- Application state: host-confirmed: subagent completed and returned a SHIP-WITH-NITS verdict with three findings, all dispositioned above.

## Verification proof

- Targeted meta-validator + surface tests after hardening: 54 passed
  (`test_inference_interpretation_meta_validator.py` 18,
  `test_surface_obligations.py` 36).
- Broad standing pytest at the bundle boundary: 2394 passed, 4 skipped, 26
  deselected.
- Live meta-validator: green (8 surfaces, 7 python + 1 prose); `validate_surfaces`
  clean (29 surfaces).
- `ruff`, `check_python_lengths` (validator 269/480), `validate_attention_state_visibility`,
  `inventory_gitignore_scan_hygiene`, `check_boundary_bypass_ratchet`,
  `validate_packaging_committed` (mirror byte-match): all green on the touched set.

## Counterweight pass

- Folding all three reviewer findings was not scope creep: NIT #1 and NIT #2 each
  close a real fail-closed hole in the exact guarantee #330 exists to provide (a
  new declaration cannot escape registration; the fnmatch footgun cannot return),
  and both fixes are a few lines plus a test. The QUESTION fix is cosmetic
  hardening of anchor specificity. None expands the validator beyond its structural,
  file-granular charter.
- The deliberate non-claim (file-granular, literal-dict scope; intra-file gating
  owned elsewhere) is honest and matches the disposition-floor discipline: prove the
  declaration exists and is paired; a human/reviewer judges whether the wording is
  honest. Pushing further would make the gate a content classifier (#330 Non-Goal).
