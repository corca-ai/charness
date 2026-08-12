# Quality Review
Date: 2026-08-12
Title: Issue 594 consolidated closeout-draft scope

## Scope

Target boundary: #594's author-facing consolidated closeout guidance and the
manual `close-with-comment` floor that performs the irreversible tracker write.

Ambient repo findings: GitHub state, live tracker readback, provider behavior,
and other classifications' intentionally lighter manual-close ledger are out of
scope for this local proof-surface repair.

## Surface Contract Review

- semantic coverage: `observed` — renderer guidance and the mutation-adjacent
  manual carrier are both exercised.
- surface: closeout-draft shape and close-with-comment pre-mutation refusal.
- owner: the consolidated body owner defines claim/destination grammar; the
  close carrier supplies the invoked issue identity and backend readback.
- projections: public source scripts and generated plugin scripts.
- state scope: consolidated only; other manual-close classifications retain their
  pre-existing ledger scope.
- transitions: render permitted carrier guidance; reject auto-closing/reparative
  routes; reject destination equal to the invoked issue without a keyword.
- proof boundary: deterministic local rendering and carrier-floor tests; no
  GitHub mutation or remote readback occurred.
- unexamined axes: a live tracker destination's open/body/chain state.

## Current Gates

- `validate-closeout-draft` remains the preflight shape validator.
- `close-with-comment` refuses a consolidated body that violates its own
  ledger before comment or close mutation.

## Healthy

- Generic draft guidance still serves classifications without a carrier-specific
  contradiction.
- The manual carrier does not require a non-operative `Closes #N` comment line.

## Weak

- Tracker destination readback is necessarily external and is not established by
  these local tests.

## Delegated Review

- Delegated Review: round 1 caught misleading readback timing, an overbroad
  keyword claim, and a keyword-free self-reference escape; a clean-boundary
  round-2 retry approved the repair. The later critique found selected-guide
  conflict and colon-form keyword equivalence; those repairs are accepted-
  unreviewed under the two-round proof-surface cap and are recorded in the
  #594 critique artifact.
- Slow-gate lenses: not applicable; this is a bounded deterministic validator
  seam. Cautilus is not approved and would not improve carrier grammar proof.

## Commands Run

- `pytest tests/quality_gates/test_check_artifact_surface_preflight.py tests/quality_gates/test_issue_consolidated_closeout.py tests/quality_gates/test_issue_close_comment_floor.py -q` — 107 passed.
- `python3 skills/public/issue/scripts/describe_closeout_draft_shape.py` — rendered the consolidated route for direct inspection.

## Recommended Next Quality Moves

- active closeout scope — capability_needed=truthful author guidance;
  next_center=consolidated manual carrier; transformation=derive special-case
  prose from live body/carrier owners; proof_boundary=renderer and carrier-floor
  regression; enforcement_posture=existing-gate-reuse.
- passive tracker proof — capability_needed=remote destination state; next_center=
  actual issue closeout; transformation=use the existing readback before a
  separately authorized close; proof_boundary=provider readback; enforcement_posture=
  external-boundary-only.
