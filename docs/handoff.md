# charness Handoff

## Workflow Trigger

- Pickup = session start with no explicit task -> **invoke `charness:handoff`**
  directly (the session-start hook routes it now, not `find-skills`); bare
  `/handoff` runs chunked routing over handoff + open issues.

## Current State

- **D36 RESOLVED this session (uncommitted at handoff write; commit lands with this
  work).** Single-sourced the question/decision-needed floor-exemption advisory into
  `issue_verify_closeout_body.review_advisory_for_classification` (unified
  `(classification, *, numbers, source)` signature), re-exported through
  `issue_verify_closeout.py`, `issue_close_comment_floor.py` reduced to a re-export;
  the commit-msg carrier now surfaces it non-blocking (exit 0). No new authored dup
  (dup-ratchet clean for changed files; one collateral clustering-rotation family
  scoped-accepted among untouched files). Fresh-eye SHIP, all six angles
  execution-confirmed. Critique:
  [d36-close-exemption-advisory-single-source](../charness-artifacts/critique/2026-07-04-d36-close-exemption-advisory-single-source.md).
- **PR #419 (north-star P1-P3 sweep) MERGED to main; released `v0.62.0`.**
  Public surface distinct-channel verified (https-fetch HTTP 200), install
  refreshed `0.61.0 -> 0.62.0`, auto-retro persisted, worktree clean.
- **Post-merge boundary fix landed (commit `5aa3f3fd`).** Adversarial
  verification of PR #419 found the issue-close commit-msg gate fence-stripped
  the commit message before scanning, so a fenced close keyword auto-closed an
  issue while the gate reported `not_applicable` (irreversible-boundary
  escape). Fix: scan the raw message (GitHub treats backticks as literal).
  Also corrected a stale achieve `SKILL.md` pointer to `goal-artifact.md`.
  Critique: [pr419-adversarial-fix-closeout](../charness-artifacts/critique/2026-07-04-pr419-adversarial-fix-closeout.md).

## Next Session

Advantageous order designed this session (signal-first → boundary-while-gate-stable →
batched baseline-rotating work → largest sweep last). Slice 1 (D36) is DONE; remaining:

1. **Audit follow-ups (own slices).** wire `vulture` (configured, never run, land
   advisory/default-off then triage findings separately); `dup_ratchet` module split
   (WARN band) — batch with the D30 residuals (S4-Defer-1/-3) so the ratchet engine is
   opened once and re-baselined once; 81-site argparse-help debt (default-off, biggest
   churn) as its own batch LAST so its baseline rotation does not contaminate other review.
2. **Optional CI hygiene (cheap, independent — do as a warm-up whenever).** the
   non-required "Changed-line mutation coverage (PR mirror)" check is environment-red —
   `test_quality_runner` hardcodes `-n 16` (fails on <16-core runners) and a release test
   rejects CI's detached HEAD; both pass locally. Relax to core-relative + guard detached HEAD.
3. **Trip-wire (not scheduled): D33** — `run_skill_efficiency_ab.py` is at 479/480; any
   slice that touches it MUST extract a module first before appending.

## Discuss

- **D34 (announcement self-attest independence) and D35 (release probe
  shape-match) DECLINED** by the operator (2026-07-04) — accepted as disclosed
  presence-floor residuals, not pursued; reopen only if the recorded failure
  materializes (see [deferred-decisions.md](./deferred-decisions.md)).

## References

- pickup: [pr419-adversarial-fix-closeout](../charness-artifacts/critique/2026-07-04-pr419-adversarial-fix-closeout.md) · [deferred-decisions.md](./deferred-decisions.md) · [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)
