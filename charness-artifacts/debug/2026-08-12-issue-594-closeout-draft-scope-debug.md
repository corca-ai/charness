# Issue #594 Closeout Draft Scope Debug
Date: 2026-08-12

## Problem

The describe-first closeout-draft shape presents ordinary close keywords,
auto-closing carriers, and repair-oriented ledger expectations to an author
selecting `consolidated`, although the live consolidated floor refuses those
claims and requires a manual `not planned` close.

## Correct Behavior

Given the consolidated disposition, when an author renders the draft shape,
then it states only the carrier, body grammar, and external-readback boundary
that the live enforced path permits. It must not prescribe a body the same gate
will refuse.

## Observed Facts

- GitHub #594 is open, has `comments_read: true`, and has no comments.
- The live consolidated owner rejects repair keywords, auto-closing carriers,
  repair claims, invalid destination arity/self-reference, and requires close
  reason `not planned`.
- The current `required_shape()` is generic: it advertises all carrier choices
  and close-keyword forms before inspecting the selected classification.
- Existing preflight coverage checks that tokens appear somewhere, not that a
  rendered consolidated instruction has the same applicability as the floor.

## Reproduction

- Render the current draft shape, then use its generic direct-commit or pr-body
  and Fixes/Resolves guidance for `Classification: consolidated`; production
  consolidated validation refuses the carrier or repair claim before mutation.

## Candidate Causes

- The shape producer renders global constants rather than observing
  classification-specific floor applicability.
- Consolidated-only body grammar was added after the generic draft surface.
- Tests assert vocabulary presence instead of a full rendered instruction to
  validator agreement.

## Hypothesis

- Confirmed: a consolidated-specific block derived from the live body owner and
  carrier evaluator presents the permitted manual route and body constraints
  without asserting backend-readback facts. The self-reference identity must
  come from the invoked manual-close number, not from an inert comment keyword;
  disconfirmer: render `--classification consolidated` and run the actual
  manual floor with a keyword-free self-destination.

## Verification

- `python3 -m pytest tests/quality_gates/test_check_artifact_surface_preflight.py
  tests/quality_gates/test_issue_consolidated_closeout.py
  tests/quality_gates/test_issue_close_comment_floor.py -q` — 107 passed.
- The rendered shape states the required `close-with-comment --reason 'not
  planned'` route, names direct-commit/pr-body as auto-closing carriers, calls
  neutral `Closes` inert in a comment, and describes readback as pre-mutation.
- A carrier-level regression calls the manual floor with issue `#42` and body
  `Consolidated into: #42`, without a close keyword; it refuses before mutation.
- Critique added the representation counterexample `Fixes #5` → `Fixes: #5`.
  Both spellings now refuse, while colon-form `Closes: #5` remains neutral only
  on the manual-comment carrier and is an auto-close on commit/PR carriers.
- `--classification consolidated` now emits a non-conflicting selected guide;
  the unqualified command explicitly identifies itself as the full catalog.

## Root Cause

The generic renderer had no consolidated applicability layer, so it presented
global carrier/keyword guidance as though it were valid for every
classification. Separately, the consolidated self-reference check inferred the
issue identity only from close keywords, but the required manual comment route
intentionally has no operative close keyword. The repair-keyword predicate also
accepted only whitespace spelling even though the canonical GitHub keyword
reader accepts colon spelling.

## Invariant Proof

- Invariant: a describe-first carrier guide must not prescribe an instruction
  its own live validation path refuses for that classification.
- Producer Proof: the consolidated block queries the live carrier/body owners;
  no local backend-fact list or carrier tuple is declared.
- Final-Consumer Proof: focused tests cover the rendered guidance and the actual
  manual close-comment floor, including keyword-free self-reference refusal,
  selected-guide rendering, and colon/space keyword equivalence.
- Interface-Shape Sibling Scan: source and plugin projections were synchronized;
  question/decision-needed remain on their generic light-floor route because no
  classification-specific carrier contradiction exists there.
- Non-Claims: no GitHub close, backend readback, or provider mutation has run.

## Detection Gap

- Draft-shape test surface | token presence did not check classification-specific
  applicability | add rendered shape-to-live-floor behavior coverage.

## Sibling Search

- Mental model: a human-facing describe-first surface can safely restate a
  global rule even when a classification changes the actual floor.
- same layer: question/decision-needed shape handling | decision: leave generic |
  proof: neither has a required manual consolidated carrier or destination rule.
- cross-file: generated plugin issue scripts | decision: synchronize source |
  proof: sync reports all five touched issue-script projections changed.

## Seam Risk

- Interrupt ID: none
- Risk Class: none
- Seam: author-facing draft renderer to irreversible closeout validator.
- Disproving Observation: a consolidated draft rendered from live facts still
  advises a refused carrier or repair claim.
- What Local Reasoning Cannot Prove: GitHub's later tracker state or backend readback.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Critique Scope: closeout-draft proof surface and irreversible author guidance.
- Next Step: impl
- Handoff Artifact: this record.

## Prevention

Render classification-specific applicability by observing the owner that
enforces it, and make behavior tests consume the same rendered guidance an
author receives.
