# Goal Producer and Export Boundary Debug
Date: 2026-08-04

## Problem

Three open issue records describe producer/export boundaries that can accept a
shape rejected by a sibling or fail only after the plugin is exported: the
handoff goal drafter does not share achieve's value guards (#500), the export
import gate does not inspect dotted module strings (#501), and the exported
adapter validator assumes authoring-tree package paths (#497).

## Correct Behavior

Given equivalent input at any supported goal producer, when it is rendered, the
producer applies the shared value/path safety contract and refuses the input or
emits a valid artifact. Given an exported plugin tree, when its validation
entrypoint is run, every imported helper resolves through the export's supported
layout, and the export gate detects the import form it is responsible for.

## Observed Facts

- `goal_artifact_lib.py` now owns the shared value normalization, prose-shape,
  and supplied-slug predicates; both `upsert_goal.py` and
  `draft_goal_from_chunk.py` call them on the values they will write.
- `draft_goal_from_chunk.py` still derives its slug from chunk objective text,
  but it now validates the exact rendered title/body and resolved slug before
  creating the directory or writing the artifact. Its post-write structural
  `check_goal` remains a separate check.
- The gathered primary issue record says #501's AST scan sees import
  statements but not dotted strings passed to `import_repo_module`, and says
  #497's exported `scripts/validate_adapters.py` hardcodes the authoring-tree
  `skills.public...` path and assumes an unflattened companion glob
  (`charness-artifacts/gather/2026-08-04-goal-issue-sources.md`).

## Reproduction

The following is the pre-repair reproduction record; the post-repair proof is
under `## Verification`.

- `draft_goal_from_chunk.py` with a real one-entry chunk and
  `objective_summary="Unsafe\n## Injected"` exits 0 and writes
  `# Achieve Goal: Unsafe\n## Injected`; its structural check still reports
  `status: draft`.
- Calling `upsert_goal._reject_unwritable_prose` with the same title refuses the
  value as a multi-line heading; a body containing `## Injected` is also refused.
- A temporary source file containing
  `module_name = "skills.public.quality.scripts.record_quality_runtime"` and
  `import_repo_module(__file__, module_name)` passes `check_export_safe_imports`.
- Running `python3 plugins/charness/scripts/validate_adapters.py --repo-root .`
  exits 1 before adapter validation with
  `ModuleNotFoundError: No module named 'skills.public'` at its hardcoded
  `skills.public.retro.scripts.resolve_adapter` import.

## Candidate Causes

- Control flow: the handoff drafter validates rendered structure only after
  writing and never enters the achieve producer's value-guard path.
- Ownership: safety rules live in a CLI script rather than a shared library
  boundary, so equivalent producers can drift.
- Export shape: the generated tree changes package/module layout while the
  validator and import gate reason about authoring paths or AST-only imports.
- Environment: a test run from the authoring checkout can mask an exported-copy
  resolution failure.

## Hypothesis

The hypothesis and its post-repair resolution are recorded together below.

- The primary causes were three distinct ownership gaps: goal value guards were
  private to `upsert_goal.py`, export validation modeled only AST import
  statements rather than supported helper-call literals, and the adapter
  validator assumed the authoring-tree package layout. Falsifiers were a shared
  value owner, a literal helper-call refusal, and an isolated generated-tree
  validator run. The Slice D repairs satisfy those falsifiers for the recorded
  supported forms; arbitrary dynamic imports and arbitrary future layouts remain
  outside the contract.
- Disconfirmation path: inspect both producers, run the smallest hostile input,
  and execute the exported validator in an isolated generated tree. The
  pre-repair reproductions confirmed the three gaps; the post-repair proofs
  below confirm the selected supported boundaries.

## Verification

- confirmed historically — the minimal hostile input distinguished the two goal
  producers, the AST gate missed the runtime string form, and the generated
  plugin copy failed on the authoring-only dotted package path.
- repaired and verified — focused producer/export tests pass; the source and
  exported import gate validate 645 files; source adapter validation reports 16
  resolvers and 18 YAML files; the checked-in exported validator reports 16
  resolvers from the flattened layout; and a freshly generated exported
  validator subprocess passes with `CHARNESS_REPO_ROOT` removed.

## Root Cause

The three issues have related but non-identical causes: #500 had value logic
owned by one producer instead of the shared value boundary; #501 had a proof
surface keyed only to import-statement syntax instead of the supported literal
helper-call contract; and #497 had a runtime loader and discovery glob keyed to
one source layout even though the exported consumer tree removes `public`.

## Invariant Proof

- Invariant #500: every supported goal producer validates the exact canonical
  values its final artifact reader will receive. Producer proof is the hostile
  handoff test and no-artifact refusal; final-consumer proof is the resulting
  goal artifact being checked through the shared goal contract.
- Invariant #501: the export gate refuses the supported literal
  `import_repo_module` call forms whose dotted path names the authoring-only
  package. The gate's verdict is the final consumer for this static contract;
  variables, aliases, f-strings, concatenation, qualified calls, and arbitrary
  dynamic imports are explicit non-claims.
- Invariant #497: the validator entrypoint resolves and discovers adapters in
  the layout it is actually running under. Final-consumer proof is the fresh
  generated-plugin subprocess with `CHARNESS_REPO_ROOT` cleared.
- Interface-Shape Sibling Scan: the achieve/handoff producer pair and the
  source/flattened validator pair are real siblings; each now has a selected
  owner and a proof channel rather than a pending candidate owner.
- Non-Claims: this does not claim every dynamic import or every host packaging
  layout is supported.

## Detection Gap

- Existing structural goal checks | do not reject all unsafe value forms | add
  producer-parity tests that exercise the shared value contract.
- Export AST import gate | misses runtime module strings | test the supported
  helper call shape or narrow the contract explicitly.
- Authoring-tree tests | can pass while the generated plugin cannot import | run
  a generated/export-tree smoke test through the public validator.

## Sibling Search

- Mental model: a local representation check is mistaken for the shared
  producer-to-consumer contract.
- same layer: `upsert_goal.py` and `draft_goal_from_chunk.py` | decision: fix now
  through the shared goal-value owner, preserving the drafter's slug derivation |
  proof: hostile-input and no-artifact tests.
- abstraction up: `goal_artifact_lib.py` and the runtime module resolver |
  decision: fix now at the shared value and layout-aware loader boundaries |
  proof: source inspection plus exported invocation.
- specialization down: plugin mirrors and flattened export layout | decision:
  fix now with a source/export smoke proof | proof: `ModuleNotFoundError`
  reproduction.
- cross-file: goal producer tests and `test_export_safe_asset_paths.py` |
  decision: fix now with behavioral regression tests beside each owner | proof:
  focused tests and the broad changed-line producer.

## Seam Risk

- Interrupt ID: none
- Risk Class: none
- Seam: export layout and runtime module resolution across source and flattened
  generated trees.
- Disproving Observation: the isolated generated validator subprocess now passes
  with the source-root override removed, while source and flattened adapter
  validation report the expected resolver sets.
- What Local Reasoning Cannot Prove: arbitrary dynamic loader dataflow or every
  future packaging layout beyond the two supported layouts.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Closeout note: Slice D implementation is complete; closeout evidence remains
- Handoff Artifact: this dated debug record

## Prevention

Goal value guards are reusable at the artifact-library boundary and both goal
producers are tested against the same hostile values. Export scanning now owns
the supported literal `import_repo_module` forms, and adapter validation is
executed from the generated plugin layout. Keep variables, aliases, f-strings,
concatenation, qualified calls, and arbitrary dynamic imports outside this
explicit contract rather than pretending to detect them.
