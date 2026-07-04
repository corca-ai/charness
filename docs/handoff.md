# charness Handoff

## Workflow Trigger

- Pickup = session start with no explicit task -> **invoke `charness:handoff`**
  directly (the session-start hook routes it now, not `find-skills`); bare
  `/handoff` runs chunked routing over handoff + open issues.

## Current State

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

1. **D36 (operator-scheduled): single-source the question/decision-needed close
   exemption advisory** so the commit-msg carrier surfaces it like
   `close-with-comment`. The direct copy was reverted (dup-ratchet P2 block);
   the real fix needs a shared owner both carriers import — full plan in
   [deferred-decisions.md D36](./deferred-decisions.md).
2. Audit follow-ups worth their own slices: wire `vulture` (configured, never
   run); 81-site argparse-help debt (opt-in rule landed, default-off);
   `dup_ratchet` module split (WARN band).
3. Optional CI hygiene: the non-required "Changed-line mutation coverage (PR
   mirror)" check is environment-red — `test_quality_runner` hardcodes `-n 16`
   (fails on <16-core runners) and a release test rejects CI's detached HEAD;
   both pass locally. Relax to core-relative + guard detached HEAD to get CI green.

## Discuss

- **D34 (announcement self-attest independence) and D35 (release probe
  shape-match) DECLINED** by the operator (2026-07-04) — accepted as disclosed
  presence-floor residuals, not pursued; reopen only if the recorded failure
  materializes (see [deferred-decisions.md](./deferred-decisions.md)).

## References

- pickup: [pr419-adversarial-fix-closeout](../charness-artifacts/critique/2026-07-04-pr419-adversarial-fix-closeout.md) · [deferred-decisions.md](./deferred-decisions.md) · [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)
