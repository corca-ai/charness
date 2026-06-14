# Retro — #367 quality CI-recoverability lens + command_timing_log ingest

Mode: session

## Context

Achieve goal `charness-artifacts/goals/2026-06-14-367-quality-ci-recoverability-and-timing-ingest.md`,
resolving GitHub issue #367 end-to-end (operator chose push + close + release).
Four slices: (1) `command_timing_log` adapter-key ingest into the runtime
helpers; (2) `inventory_ci_recoverable_gates` lens (the counterweight to the
local-proof guardrail); (3) docs/SKILL.md/dogfood + slice-1 review follow-ups;
(4) bundle closeout incl. registering the lens as an inference-layer surface.
Two fresh-eye subagent reviews, both SHIP, zero blockers. Broad pytest green
(3033 passed) over the final locked state.

## Evidence Summary

- Goal artifact slice log (4 slices) + two fresh-eye review transcripts (SHIP).
- Host-log probe (thread-wide, no goal window): 189 function calls, 55 patch
  applications, 2 subagent spawns, 0 compactions
  (`charness-artifacts/probe/2026-06-14-367-quality-ci-recoverability-and-timing-ingest.json`).
- Live gate failures observed: 3 commit-time gate rejections + 1 broad-pytest
  failure, all author-time structural requirements.

## Waste

The dominant waste was **author-time structural requirements surfacing late**,
each as a gate firing rather than being visible before authoring:

- `advisory-only` attention-state undeclared → blocked the slice-2 commit; fixed
  by declaring it. One round.
- `skipped` in a docstring tripped the same attention-state gate as a
  false-positive (internal record-filtering prose, not a closeout state) →
  reworded to `dropped`. One round.
- SKILL.md hit its hard 200-line ceiling after prose was added → had to compress
  to terse pointers and fold the lens into an existing soft-wrapped bullet. Two
  iterations to land exactly at 200.
- **The expensive one:** the new lens's 4-field `INTERPRETATION` dict is an
  inference-layer declaration that must be registered in
  `.agents/inference-interpretation-surfaces.json`. That requirement is enforced
  **only by a broad-pytest test** (`test_inference_interpretation_meta_validator`),
  not by the cheap commit-time structural sweep — so it cost a full ~4-minute
  broad-pytest run to surface, plus a second run after the count-assertion bump.

Broad pytest ran three times: a cached-fingerprint block (needed
`--refresh-broad-pytest-proof` — expected verification-lock behavior, not waste),
the real inference-surface failure, then clean. Two of the three were necessary;
the inference-surface re-run was avoidable waste a commit-time check would have
removed.

## Critical Decisions

- **Operate the lens on the cost-ranked (measured) gate set, not all gates.**
  Keeps it aligned with #367's "costly standing gate" wording and makes the safe
  under-flagging direction (unmeasured gates absent) the default.
- **Token-identity matching with declared blind spots + advisory-only / no
  blocking floor.** Honors Floor-Addition Restraint and keeps the local-proof
  guardrail intact (the safety gate: never flag a gate CI does not re-run).
- **Ingest before lens** slice ordering — the lens ranks by wall-clock the ingest
  provides; building the data source first de-risked the lens.
- **Asked the operator the closeout boundary (push+close+release) before
  activation** rather than assuming the irreversible outward steps.

## Expert Counterfactuals

- **Fast-feedback gate designer (CI/CD shift-left lens).** The irony is sharp:
  this very goal ships a lens about *which proof should run where* (move
  CI-recoverable gates off the slow path), yet the inference-surface registration
  check is itself a slow-feedback gate — a deterministic, offline, author-time
  structural fact enforced only in the ~4-min broad pytest. Shift it left into the
  commit-time structural sweep (where `validate_attention_state_visibility`
  already lives) and the late failure disappears. This lens changes the action:
  promote the meta-validator (or a fast unregistered-declaration subset) into the
  pre-commit aggregate.
- **Checklist-author lens (Atul Gawande).** Three separate registries
  (attention-state-visibility.json, inference-interpretation-surfaces.json, the
  dogfood EVIDENCE_OVERRIDES scaffold) plus the SKILL.md line budget all needed
  updating when adding one advisory inventory, and none were discoverable from a
  single authoring entry point. A short "new advisory surface" checklist in the
  quality/create-skill references would have front-loaded all four.

## Next Improvements

- **workflow/capability:** add the inference-interpretation meta-validator's
  unregistered-declaration scan to the commit-time structural sweep
  (`run_slice_closeout` pre-commit aggregate), so a new 4-field `INTERPRETATION`
  declaration surfaces its registration requirement at commit instead of at the
  ~4-min broad pytest. Highest-value; larger than this goal's scope (changes the
  commit-gate aggregate) → file as issue.
- **memory/capability:** a short "adding an advisory inventory/surface" checklist
  (the 3 registries + the SKILL.md ≤200 budget) in the quality references, so the
  next author front-loads the registrations. → file as issue (same structural
  cluster as the first; keep one tracked thread).

## Sibling Search

Transferable waste pattern: **an author-time, deterministic, offline structural
registry whose only enforcement is a broad-pytest test, not the fast commit-time
structural sweep.**

- by-gate: `validate_attention_state_visibility` IS in the commit-time sweep
  (caught `advisory-only`/`skipped` at commit — good). The
  inference-interpretation meta-validator is NOT (caught only at broad pytest —
  the gap). Same *class* of structural fact, opposite placement.
- by-registry: the dogfood `EVIDENCE_OVERRIDES` scaffold is enforced by
  `validate_public_skill_dogfood`, which DOES run in the sweep — so it caught my
  drift at slice 3 cheaply. So of three registries, two are fast-gated and one
  (inference-interpretation) is slow-gated.

Decision: **file a follow-up issue** to move the inference-interpretation
unregistered-declaration check into the commit-time sweep (the one slow-gated
sibling), bundled with the authoring-checklist note. Not applied in-session
because it changes the shared commit-gate aggregate and warrants its own
critique, outside this goal's #367 scope.

## Persisted
