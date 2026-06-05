# A~C follow-ups resolution critique (#307/#308/#309/#310/#312)
Date: 2026-06-05

## Decision Under Review

Closeout of the A~C parallel follow-up bundle — #310/#309 (gather/web-fetch
acquisition signal fidelity), #312 (release publish-flow resilience B1+B2), and
#307/#308 (quality-gate economics) — landed as one commit per sub-slice on main
with `Close #N` carriers. This critique consumes the three per-chunk bounded
fresh-eye reviews (different agent contexts) and the bundle `--release` gate.

## Failure Angles

- A1 (#310): could preserving the original `.error` leak a confusing status on
  the collect-intent network-recon diagnostic attempt or mislead downstream
  selection/disposition?
- A2 (#309): does adding `next_step_kind` break the doctor/assert CLI or the
  run_slice_closeout hygiene command; is the mixed orphan+reparented case a loop?
- B1 (#312): does committing latest.md before push move HEAD ahead of the tag in
  a way that corrupts the push/verify/final-commit, or break resume idempotency?
- B2 (#312): could gating usage-episode emission on `CHARNESS_QUALITY_MODE`
  suppress a legitimate developer slice-closeout emission, or break the
  attention-state declaration?
- C1 (#307): does the new fast checker materially slow the aggregate or wastefully
  duplicate the broad pytest; is it reached at the real commit boundary?
- C2 (#308): is the reference discoverable and does the drift guard truly bind to
  the gate vocabulary; did it over/under-deliver vs the chosen level?
- Bundle: does the full `--release` gate (with CHARNESS_QUALITY_MODE set) keep
  the #194 User Acceptance test green and surface any regression the per-chunk
  checks missed?

## Counterweight Pass

- The three chunk reviewers each returned VERDICT: ship with no blockers; their
  raised concerns (A1 diagnostic mutation, B1 tag/HEAD divergence) were probed
  and dismissed with concrete reasons (diagnostics are excluded from
  selection/disposition; release is created off the tag ref and branch-ahead-of-
  tag matches the normal flow).
- The bundle `--release` gate DID surface two real blockers the per-chunk cheap
  checks missed — bare `#NNN` issue anchors in portable skill packages and a
  duplicate boundary-bypass candidate — both fixed before final ship. This is the
  bundle barrier doing its job; not an over-worry.
- The one residual honesty note (#307 reachability) is documented, not a blocker:
  the checker lands at the `run_slice_closeout` aggregate the issue itself names,
  not the separate hardcoded git pre-commit gate list.

## Structured Findings

- F1 | bin: act-before-ship | evidence: moderate | ref: skills/support/web-fetch/scripts/acquire_public_url.py | action: fix | note: bare `#310`/`#312` issue anchors in the portable web-fetch and release skill packages tripped portable_package_issue_anchor at the --release gate; reworded to drop the anchors (fixed in 9f08bdc3).
- F2 | bin: act-before-ship | evidence: moderate | ref: tests/test_authoring_preflight_reference.py | action: fix | note: the headroom subprocess assertion added a duplicate boundary-bypass candidate (no_increase ratchet); --headroom is already covered by test_closeout_headroom_and_mirror_gate.py, so the redundant test was dropped (fixed in 9f08bdc3).
- F3 | bin: valid-but-defer | evidence: moderate | ref: scripts/staged_commit_gate_plan.py | action: document | note: the #307 checker fires at the run_slice_closeout aggregate (the per-slice aggregate the issue names), not the hardcoded git pre-commit gate list; documented as an honesty note, not over-claimed.
- F4 | bin: over-worry | evidence: weak | ref: skills/support/web-fetch/scripts/acquire_public_url.py | action: defer | note: A1 mutating the collect-intent network-recon diagnostic attempt is benign — diagnostics are excluded from selection/disposition, so the content signal and original error survive.
- F5 | bin: over-worry | evidence: weak | ref: skills/public/release/scripts/publish_release_resume.py | action: defer | note: B1 moving HEAD ahead of the tag is benign — the GitHub release is created off the tag ref and branch-ahead-of-tag matches the normal post-publish commit pattern.

## Reviewer Tier Evidence

- Requested tier: high-leverage bounded fresh-eye review, one per chunk, each in a different agent context (read-only).
- Requested spawn fields: per-chunk slice packet (intent, changed files + owning/generated surfaces, expected invariants, tests/proof, non-claims, out-of-scope, reviewer questions); read-only constraint; inspect prior versions via `git show <ref>:<path>` only.
- Host exposure state: applied
- Application state: host-confirmed: three general-purpose subagents spawned via the parent Agent tool (chunk A: adaef8cdd14328229; chunk B: a88fd89d7cbd28996; chunk C: a5b2f037f5dbddfa3); each returned a structured VERDICT: ship with no blockers.

## Fresh-Eye Satisfaction

All three chunk reviewers ran in separate agent contexts and returned ship / no
blockers, each confirming the reproduce-then-fixed tests are genuine against the
pre-fix commits and that the plugin mirrors are synced. tool signal: the Agent
tool returned three structured verdicts (agentIds above) plus the per-chunk
answers folded into the Structured Findings; the bundle `--release` gate then
passed 72/0 on a clean tree after the two F1/F2 blockers were fixed.
