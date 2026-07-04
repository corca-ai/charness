# charness Handoff

## Workflow Trigger

- Pickup = session start with no explicit task -> **invoke `charness:handoff`**
  directly (the session-start hook routes it now, not `find-skills`); bare
  `/handoff` runs chunked routing over handoff + open issues.

## Current State

- **This session (commits land with the work):**
  - **dup_ratchet module split DONE** — extracted `dup_ratchet_scan.py` (live
    fingerprint/drift-signature collection) and `dup_ratchet_git.py` (git stagnation
    seams) as leaf modules; both WARN-band helpers back under 330 (check 357→250,
    lib 340→309). Triage kept **S4-Defer-1/-3 DEFERRED** (reopen triggers unmaterialized:
    post-Slice-4 baseline rotations track real code edits, not phantom comment edits).
    The mechanical rename touched accepted cloned spans → 2 internal-boilerplate
    fingerprints rotated, scoped-accepted (+2/-0). Caught+fixed a moved-code
    attention-state-declaration regression (`skipped` relocated to `dup_ratchet_scan.py`).
    Fresh-eye SHIP. Critique:
    [dup-ratchet-split](../charness-artifacts/critique/2026-07-04-dup-ratchet-module-split.md).
- **Prior session (already committed):**
  - **D36 RESOLVED** — single-sourced the question/decision-needed floor-exemption
    advisory into `issue_verify_closeout_body.review_advisory_for_classification`
    (`(classification, *, numbers, source)`), re-exported through `issue_verify_closeout.py`;
    the commit-msg carrier now surfaces it non-blocking. No new authored dup (one collateral
    clustering rotation scoped-accepted among untouched files). Fresh-eye SHIP. Critique:
    [d36](../charness-artifacts/critique/2026-07-04-d36-close-exemption-advisory-single-source.md).
  - **vulture dead-code advisory WIRED** into `run-quality.sh` as a DEFAULT-OFF opt-in
    advisory gate (`CHARNESS_QUALITY_DEAD_CODE=1` / `CHARNESS_QUALITY_LABELS=dead-code-advisory`),
    never blocks, surfaces an `ADVISORY:` line. End-to-end verified (33 findings); triage deferred.
  - **CI hygiene** — `test_quality_runner` asserts core-relative workers via
    `choose_xdist_workers(env)` (was hardcoded `16`); `test_release_real_host` pins
    `current_branch` so it no longer breaks on CI's detached HEAD. Test-only.
- **PR #419 (north-star P1-P3 sweep) MERGED; released `v0.62.0`;** post-merge boundary fix
  `5aa3f3fd` (issue-close gate now scans the raw commit message). Critique:
  [pr419](../charness-artifacts/critique/2026-07-04-pr419-adversarial-fix-closeout.md).

## Next Session

Advantageous order designed this session (signal-first → boundary-while-gate-stable →
batched baseline-rotating work → largest sweep last). D36 + CI hygiene + vulture wiring
are DONE; remaining:

1. **vulture findings triage (follow-up to the wiring).** The gate now flags 33
   review_candidate dead-code findings (of 43 total) on a real run. Triage them:
   delete genuine dead code, or add `# noqa`-style vulture allowlist entries / raise
   `[tool.vulture] min_confidence` for confirmed false positives. Run it with
   `CHARNESS_QUALITY_LABELS=dead-code-advisory ./scripts/run-quality.sh`.
2. **Remaining audit follow-ups (own slices).** `dup_ratchet` module split **DONE** this
   session (see Current State); S4-Defer-1/-3 kept **DEFERRED** (triage: reopen triggers
   unmaterialized — reopen only when an in-place-comment false-rotation or membership-shrink
   friction is actually observed). Remaining: 81-site argparse-help debt (default-off,
   biggest churn) as its own batch LAST so its baseline rotation does not contaminate other
   review.
3. **Trip-wire (not scheduled): D33** — `run_skill_efficiency_ab.py` is at 479/480; any
   slice that touches it MUST extract a module first before appending.

## Discuss

- **D34 (announcement self-attest independence) and D35 (release probe
  shape-match) DECLINED** by the operator (2026-07-04) — accepted as disclosed
  presence-floor residuals, not pursued; reopen only if the recorded failure
  materializes (see [deferred-decisions.md](./deferred-decisions.md)).

## References

- pickup: [pr419-adversarial-fix-closeout](../charness-artifacts/critique/2026-07-04-pr419-adversarial-fix-closeout.md) · [deferred-decisions.md](./deferred-decisions.md) · [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)
