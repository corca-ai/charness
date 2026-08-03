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

- `upsert_goal.py` owns `_reject_unwritable_prose` and `_resolve_slug`, while
  `draft_goal_from_chunk.py` calls `goal_path` and writes the rendered text
  directly; the latter does not call either guard.
- `draft_goal_from_chunk.py` derives its slug from chunk objective text and
  passes objective/title/body into the renderer before running only the
  structural `check_goal` result.
- The gathered primary issue record says #501's AST scan sees import
  statements but not dotted strings passed to `import_repo_module`, and says
  #497's exported `scripts/validate_adapters.py` hardcodes the authoring-tree
  `skills.public...` path and assumes an unflattened companion glob
  (`charness-artifacts/gather/2026-08-04-goal-issue-sources.md`).

## Reproduction

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

- The primary cause is split ownership at two representation boundaries: goal
  value guards are private to `upsert_goal.py`, and export validation models
  only syntactic imports rather than the runtime module-resolution contract.
  falsifier: a shared library already validates the drafter's values and the
  exported validator's runtime imports from the generated layout.
  disconfirmer: inspect both producers, run the smallest hostile input, and execute
  the
  exported validator in an isolated generated tree before changing code. Result:
  disconfirmed for neither boundary; the reproductions confirm split ownership
  and the exported layout failure.

## Verification

- confirmed — the minimal hostile input distinguishes the two goal producers,
  the AST gate misses the runtime string form, and the generated plugin copy
  fails on the authoring-only dotted package path.
- repaired and verified — focused producer/export tests pass; the source and
  exported import gate validate 645 files; source adapter validation reports 16
  resolvers and 18 YAML files; the checked-in exported validator reports 16
  resolvers from the flattened layout; and a freshly generated exported
  validator subprocess passes with `CHARNESS_REPO_ROOT` removed.

## Root Cause

The three issues are instances of boundary logic owned by a narrower
representation than the final consumer: `upsert_goal.py` owns prose guards
that the handoff writer bypasses; `check_export_safe_imports.py` owns AST import
nodes but not the string contract of `import_repo_module`; and
`validate_adapters.py` imports one source-tree package spelling even though the
exported consumer tree removes `public`.

## Invariant Proof

- Invariant: every supported producer/export preserves the semantic safety and
  portability contract through its final consumer.
- Producer Proof: source and handoff reproductions show equivalent goal values
  taking different verdict paths; the export copy fails before its validator
  runs.
- Final-Consumer Proof: the exported validator invocation is the final consumer
  reproduction for #497; the string-form import is a direct proof of #501's AST
  blind spot.
- Interface-Shape Sibling Scan: achieve/handoff producer pair and source/export
  validator pair are the relevant siblings; repair ownership remains to be
  chosen by implementation review.
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
  through a shared goal-value owner, preserving the drafter's slug derivation |
  proof: hostile-input reproduction.
- abstraction up: `goal_artifact_lib.py` and the runtime module resolver |
  decision: candidate owners for implementation | proof: source inspection and
  exported invocation.
- specialization down: plugin mirrors and flattened export layout | decision:
  fix now with a source/export smoke proof | proof: `ModuleNotFoundError`
  reproduction.
- cross-file: goal producer tests and `test_export_safe_asset_paths.py` |
  decision: add behavioral regression tests beside each owner | proof: existing
  test inventory; new tests pending.

## Seam Risk

- Interrupt ID: none
- Risk Class: none
- Seam: export layout and runtime module resolution are under investigation.
- Disproving Observation: the checked-in generated validator fails in the
  exported tree while source-tree validation is the path covered by current
  tests.
- What Local Reasoning Cannot Prove: that authoring and exported copies resolve
  the same module identity.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: this dated debug record

## Prevention

Goal value guards are reusable at the artifact-library boundary and both goal
producers are tested against the same hostile values. Export scanning now owns
the supported literal `import_repo_module` forms, and adapter validation is
executed from the generated plugin layout. Keep variables, aliases, f-strings,
concatenation, qualified calls, and arbitrary dynamic imports outside this
explicit contract rather than pretending to detect them.
