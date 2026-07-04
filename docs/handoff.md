# charness Handoff

## Workflow Trigger

- Pickup = session start with no explicit task -> **invoke `charness:handoff`**
  directly (the session-start hook routes it now, not `find-skills`); bare
  `/handoff` runs chunked routing over handoff + open issues.

## Current State

- **This session (commits land with the work):**
  - **vulture dead-code triage DONE** — triaged all 33 `review_candidate` findings:
    deleted 15 zero-reference dead symbols + 2 cascade orphans + 1 dead P4 duplicate
    (`has_ai_provenance_marker`; live floor `evaluate_ai_provenance` untouched) + 1
    vestigial 0-test file; fixed 7 test-local mock/protocol params. ≈−135 lines. PRIMARY
    advisory pass now CLEAN; SWEEP 33→10 (all benign). The attention-state pre-commit gate
    caught + blocked an over-deletion (2 marker consts in `report_usage_product_review.py`
    are gate-required, not dead) — restored + commented. Fresh-eye SHIP. Critique:
    [vulture-triage](../charness-artifacts/critique/2026-07-05-vulture-dead-code-triage.md).
  - **dup_ratchet module split DONE** — extracted `dup_ratchet_scan.py` + `dup_ratchet_git.py`
    leaf modules; both WARN-band helpers back under 330 (check 357→250, lib 340→309). Kept
    **S4-Defer-1/-3 DEFERRED** (reopen triggers unmaterialized). 2 boilerplate fingerprints
    rotated → scoped-accepted (+2/-0). Fresh-eye SHIP. Critique:
    [dup-ratchet-split](../charness-artifacts/critique/2026-07-04-dup-ratchet-module-split.md).
- **Prior (committed):** D36 close-exemption advisory single-sourced; vulture advisory WIRED
  (default-off); CI hygiene (core-relative xdist workers, pinned release branch). PR #419
  north-star P1-P3 sweep MERGED, released `v0.62.0` (post-merge boundary fix `5aa3f3fd`).

## Next Session

Advantageous order designed earlier (signal-first → boundary-while-gate-stable →
batched baseline-rotating work → largest sweep last). DONE: D36, CI hygiene, vulture
wiring, vulture triage, dup_ratchet split. Remaining:

1. **81-site argparse-help debt (the largest, churn-heavy batch, run LAST).** Default-off;
   its baseline rotation is designed to run alone so it does not contaminate other review.
   This is the last scheduled audit follow-up. (`dup_ratchet` split and vulture triage are
   both DONE — see Current State; S4-Defer-1/-3 stay **DEFERRED** until a reopen trigger is
   actually observed.)
2. **Optional follow-up (unscheduled):** silence the 10 residual vulture SWEEP
   review_candidates via a classifier allowlist — deferred as a disproportionate default-off
   gate-contract change; only worth it if a maintainer wants a fully-quiet sweep.
3. **Trip-wire (not scheduled): D33** — `run_skill_efficiency_ab.py` is at 479/480; any
   slice that touches it MUST extract a module first before appending.

## Discuss

- **D34 (announcement self-attest independence) and D35 (release probe
  shape-match) DECLINED** by the operator (2026-07-04) — accepted as disclosed
  presence-floor residuals, not pursued; reopen only if the recorded failure
  materializes (see [deferred-decisions.md](./deferred-decisions.md)).

## References

- pickup: [pr419-adversarial-fix-closeout](../charness-artifacts/critique/2026-07-04-pr419-adversarial-fix-closeout.md) · [deferred-decisions.md](./deferred-decisions.md) · [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)
