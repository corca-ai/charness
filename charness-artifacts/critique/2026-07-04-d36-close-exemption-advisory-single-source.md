# D36 Close-Exemption Advisory Single-Source Closeout
Date: 2026-07-04

## Decision Under Review

Resolving deferred-decision D36: single-source the `question`/`decision-needed`
floor-exemption advisory so the commit-message close carrier surfaces it (non-blocking,
exit 0) the way `close-with-comment` already does. Shipped: `review_advisory_for_classification`
moved to the shared owner `issue_verify_closeout_body.py` with a unified
`(classification, *, numbers=None, source=None)` signature, re-exported through
`issue_verify_closeout.py`, and `issue_close_comment_floor.py` reduced to a re-export;
`check_issue_closeout_commit_msg.py` now computes `_exemption_advisories` and surfaces
them via `_emit_human_output` + a `review_advisory` JSON field. This is the "do it right"
form D36 named: the first PR #419 attempt copied the advisory and was correctly
dup-ratchet-blocked as P2 displaced duplication; this slice has ONE advisory body.

## Failure Angles

- The single-owner refactor could leave a second copy (displaced duplication returning).
  Checked: exactly one `def review_advisory_for_classification` remains (the body module);
  both other surfaces are `= _BODY.review_advisory_for_classification` re-exports, verified
  by grep and by the fresh-eye reviewer.
- The historical `close-with-comment` output could shift (regression on an existing carrier).
  Checked: the classification-only call yields `scope=""`, byte-identical to the pre-change
  string; pinned by `test_close_with_comment_call_form_is_byte_identical` and independently
  byte-compared by the reviewer against `HEAD`.
- The advisory could change what the gate permits (block↔pass). Checked: `review_advisory`
  is an additive field never fed into `ok`/exit in either `evaluate` or `verify_closeout`;
  exempt closes stay exit 0, non-exempt closes surface nothing.
- The dup-ratchet baseline accept could mask an authored duplication. Checked: the accepted
  family `97ac3e8f904686f5` contains only UNTOUCHED files
  (`check_prose_pin.py`, `check_skill_cut_safety.py`, `render_critique_section_changed_surfaces.py`);
  the changed files belong to no clone family after the change. It is a collateral nose
  global-clustering rotation of a pre-existing accepted family (`3d4af4`, which gained
  `render_critique` as a third member) triggered because the legitimate `main()` thinning
  removed a pre-existing clone (`d38941` = old `main()` ↔ `plan_quality_run`). Reproduced
  by fingerprint set-diff and independently by the fresh-eye reviewer running the collector.
- The tests could be non-falsifiable. Checked: on revert the `review_advisory` field
  disappears (KeyError) failing both commit-msg tests; the exempt/non-exempt arms assert
  `len==1`+`#N` vs `[]`, so a trivially-empty impl fails the exempt arm.

## Counterweight Pass

- Real work folded now: the shared-owner refactor + commit-msg surfacing (the D36 outcome),
  and the `main()` thinning that removed a pre-existing clone (`d38941`) — a net improvement,
  leaving the authored file clone-free.
- Accepted collateral (not a defect to fix): the `97ac` fingerprint rotation among untouched
  files is the known nose-clustering brittleness D30's residuals (S4-Defer-1/-3) and the
  latest quality review already name as active dup-ratchet churn. Refactoring three untouched
  files to break a clone this change did not author would be scope-creep; the designed
  `--accept-family` scoped re-baseline (+1/-0 to the baseline) is the honest, minimal path.
- Deliberately not pursued here: pruning the now-orphan baseline fingerprints (`3d4af4`,
  `d38941`) — scoped-accept is additive by design; a full `--write-baseline` prune would
  re-accept unreviewed families and is riskier than leaving two harmless orphans.

## Structured Findings

- F1 | bin: over-worry | evidence: strong | ref: skills/public/issue/scripts/issue_verify_closeout_body.py:54 | action: document | note: single `def` confirmed; both carriers re-export the owner, no duplicated advisory body (dup-ratchet clean for authored files)
- F2 | bin: over-worry | evidence: strong | ref: skills/public/issue/scripts/issue_close.py:137 | action: document | note: classification-only call keeps the close-with-comment string byte-identical (scope="" when numbers is None), pinned by a regression test
- F3 | bin: over-worry | evidence: strong | ref: scripts/check_issue_closeout_commit_msg.py:276 | action: document | note: advisory is additive to the report, never fed into ok/exit; exempt surfaces + never blocks, non-exempt silent — proven by the falsifiable per-arm hook tests
- F4 | bin: bundle-anyway | evidence: strong | ref: charness-artifacts/quality/dup-ratchet-baseline.json | action: fix | note: accepted collateral clustering rotation (97ac, untouched files only) via scoped --accept-family; verified the change authored zero new duplication, so the accept masks nothing
- F5 | bin: valid-but-defer | evidence: moderate | ref: charness-artifacts/quality/dup-ratchet-baseline.json | action: defer | note: two orphan baseline fingerprints (3d4af4, d38941) left by additive scoped-accept; pruning needs a riskier full re-baseline, deferred as the known D30 residual churn

Fresh-eye satisfaction: parent-delegated — a bounded fresh-eye subagent (general-purpose,
id a6df5264c88bce448) adversarially reviewed the staged diff across all six requested angles
and returned SHIP with no blockers, each angle CONFIRMED by execution (it re-ran the nose
collector to independently verify the accepted family contains only untouched files, byte-compared
the close-comment string against HEAD, and confirmed the advisory never flips exit). The shipped
change is exactly what it reviewed.

## Reviewer Tier Evidence

- Requested tier: bounded fresh-eye subagent in a different agent context, adversarial, read-only in the shared parent worktree
- Requested spawn fields: the full staged diff scope, the D36 claim, and six adversarial angles (duplication elimination, close-comment regression, boundary honesty/never-block, baseline-accept masking, test falsifiability, signature-unification bugs)
- Host exposure state: applied
- Application state: host-confirmed: subagent a6df5264c88bce448 ran to completion and returned verdict SHIP with per-angle commands and observations
