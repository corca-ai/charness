<!-- charness-work-item-key: backlog-698 -->
# Existing Work Item #698 — Superseded lifecycle floor

## Purpose and premise

Name the superseded lifecycle floor and its required dispositions/handoff fields.
Re-read the existing transition fixtures before selecting the smallest repair.

## Owned change and acceptance

Superseded runs preserve surfaced improvements, required disposition, and
handoff identity; both positive transition and missing-field refusal are tested.
If verdict logic changes, the repaired surface receives the required second
bounded review round.

## Verification and evidence boundary

Run `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_goal_superseded_status.py`, then changed-line proof. No closeout is inferred from a status string alone.

## Current Progress — 2026-08-27

The Charness-owned implementation is integrated on the current implementation
branch. A superseded goal now requires `Retro:` evidence (or a typed explicit
non-claim), preserves the `Superseded by:` handoff identity, and applies the
existing deterministic `Auto-Retro` disposition floor only when the bound retro
surfaces improvements. Complete-only host, evaluator, coordination, and other
After-phase requirements remain out of scope.

Verification: the focused production gate passed 43 tests; related artifact,
disposition, and coordination floors passed 221 tests; documentation and Python
lint gates passed; canonical source/plugin mirror comparisons passed. Local
changed-line proof evidence is recorded in
`charness-artifacts/impl/2026-08-27-issue-698-superseded-floor.md`.

This update does not claim hosted/remote CI, installed export behavior, release,
push, or consumer migration. The separate closeout carrier and resolution
critique are recorded at
`charness-artifacts/issues/closeouts/2026-08-27-issue-698.md` and
`charness-artifacts/critique/2026-08-27-issue-698-resolution-critique.md`;
provider state is verified independently at the closeout boundary.
