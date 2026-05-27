# Issue 224/219 Mutation Annotation-Filter Debug
Date: 2026-05-27
Source: GitHub issues #224, #219 (scheduled Mutation Tests red on `main`)

## Problem

The scheduled Cosmic Ray gate keeps failing on `main` with sub-threshold
reachable scores (#219: 66.1%, 38 survived; one run had `artifact_closeout_status`
with 33 survived mutants). The workflow auto-files/auto-closes these issues, so
the symptom recurs whenever a sampled file's equivalent mutants survive.

## Correct Behavior

PEP 604 union `|` operators inside annotations are behavior-equivalent mutants
under `from __future__ import annotations` (PEP 563): the annotation is never
evaluated, so no test can kill them. The post-init filter must skip them so they
leave the reachable-score denominator, wherever the annotation lands.

## Observed Facts

- `scripts/artifact_closeout_lib.py` uses a multi-line signature; lines 11-13
  carry `str | None` / `bool | None` parameter annotations.
- Cosmic Ray emits 33 `core/ReplaceBinaryOperator_BitOr_*` mutants on those 3
  lines (distinct positions `(11,26)`, `(12,33)`, `(13,29)`).
- The old filter skipped none of them: `should_skip_mutation` returned `False`
  for all three lines.
- A static AST scan over `scripts/` + `skills/` found 625 annotation-union `|`
  operators; 212 sit on non-`def ` lines, and all 212 are in modules with
  `from __future__ import annotations` (zero exceptions), across 81 files.

## Reproduction

Built a Cosmic Ray session on `scripts/artifact_closeout_lib.py` and inspected
work items: 50 mutants, 33 of them `BitOr` on the multi-line annotation lines.
Ran the (pre-fix) filter's `should_skip_mutation` against those positions — all
returned `False`, so the 33 equivalent mutants would survive and tank any sample
that included the file.

## Candidate Causes

- The filter's `is_function_annotation_union` only matched lines whose stripped
  text starts with `def `, missing every continuation line of a multi-line
  signature (and variable annotations). [confirmed]
- The score gate wrongly counted equivalent mutants in the denominator. [ruled
  out: the denominator is reachable-only; the defect is that equivalents were
  never skipped, not how they were scored].
- Sampler/filter coverage-oracle divergence like #216. [ruled out: both share
  `should_skip_mutation`, so they classify identically].
- Genuine test-strength gaps in sampled files. [partly true: a separate residual
  class of real survivors exists, but it is not the dominant recurring cause].

## Hypothesis

If annotation-union detection walks the module AST (function arg/return
annotations + `AnnAssign`) and matches the `|` operator's exact `(line, col)`
against Cosmic Ray's `start_pos`, then equivalent mutants are skipped wherever
the annotation lands, the 33-survivor case disappears, and no real (evaluated)
`|` expression is silenced.

## Verification

- Replaced the line-text heuristic with an AST detector
  (`annotation_union_operator_positions`); `should_skip_mutation` now matches
  exact operator positions.
- Empirically confirmed Cosmic Ray reports the `|` operator's own `(line, col)`
  as `start_pos`; the detector reproduces those positions exactly.
- Real Cosmic Ray run on `scripts/artifact_closeout_lib.py`: 33 equivalent
  mutants skipped, the 17 real mutants killed, **100.0% reachable** (0 survived).
- Unit tests pin precision: default expressions (`def f(x: int|None = A|B)`),
  string literals (`Literal["a|b"]`), TypeAlias/runtime `set|set`, and
  non-future-import modules are NOT skipped.
- Full `tests/quality_gates` suite green (984 passed); ruff, packaging,
  adapters, GitHub-actions validators pass; plugin mirror synced.

## Root Cause

`scripts/filter_cosmic_ray_mutants.py` decided an AST-level equivalence property
(`|` is inside a never-evaluated annotation) with a line-text heuristic that
required the source line to start with `def `. Multi-line signatures, return
types on continuation lines, and module/local variable annotations all leaked
equivalent mutants into the reachable score — the missing invariant was
"recognize annotation unions by AST position, not by line prefix".

## Detection Gap

The filter's own unit test
(`tests/quality_gates/test_quality_mutation_testing.py`) only fed single-line
`def ...` strings to `is_function_annotation_union`, so it passed while the
multi-line case shipped broken. Smallest fire: one assertion that a continuation
parameter line with a union is recognized. The new AST tests cover multi-line
signatures, vararg/kwarg, split-line return unions, and variable annotations.

## Sibling Search

Mental model: a line-text heuristic standing in for an AST/semantic property.

- same layer: `is_trivial_entry_guard_mutation` (filter_cosmic_ray_mutants.py)
  shares the `startswith` text-heuristic class | decision: same class,
  diagnostic-only for this slice | proof: static scan only
- abstraction up: the sampler reuses `should_skip_mutation`
  (mutation_sampling_lib.py:302), so the fix corrects its `mutable` count too |
  decision: same bug, fix now | proof: runtime/provider roundtrip
- over-reach contrast: real survived mutants named in #224 (`build_payload`
  comparison operators, worktree `timeout` NumberReplacer) are genuine
  test-strength gaps this fix deliberately does not touch | decision: valid
  follow-up outside the slice | proof: not inspected | follow-up: deferred
  docs/handoff.md (Next Session mutation-gate residuals)
- critique-surfaced: a `|` inside `Annotated[...]` metadata is runtime-observable
  and would be wrongly skipped (latent; repo has zero `Annotated` usage today) |
  decision: valid follow-up outside the slice | proof: local payload proof |
  follow-up: deferred docs/handoff.md (Next Session mutation-gate residuals)

## Seam Risk

- Interrupt ID: issue-224-219-mutation-annotation-filter
- Risk Class: none
- Seam: Cosmic Ray work-item `start_pos` semantics for BitOr mutations
- Disproving Observation: none — a real Cosmic Ray init+exec on this host
  confirmed the local fix (host confirms local reasoning)
- What Local Reasoning Cannot Prove: future scheduled fill samples may surface
  unrelated real-survivor gaps; tracked as a residual follow-up
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: docs/handoff.md

## Prevention

The detector now keys on AST annotation position with a `from __future__ import
annotations` gate, so the equivalent-mutant class is recognized structurally
rather than by line prefix. Regression tests pin the multi-line, vararg/kwarg,
variable-annotation, and negative (default-expression / non-future) cases, plus
a documented pin for the deferred `Annotated`-metadata limitation. Real
test-strength survivors and the `Annotated` guard are deferred to the handoff
residuals anchor, not silenced.
