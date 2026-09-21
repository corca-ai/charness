# Release Critique — charness 8.9.4 (v8.9.4)

- **Release Scope**: `8.9.3` → `8.9.4` (tag `v8.9.4`), patch. One-line
  consumer story: a closeout draft whose new checks failed can no longer
  ship as ready, and stale quality failure logs are swept so a green run
  never reports red names.
- **Bump rationale**: patch, not minor: two tooling repairs (failed-draft
  readiness refusal, stale failure-log sweep) plus regression tests; no new
  surface and no invocation break.
- **Reviewed delta**: `v8.9.3..HEAD` (commit `4e24ed9ee` plus release
  receipts; production code delta is the validator refusal and the log
  sweep).
- **Substrate**: two bounded fresh-eye reviewers (spawned subagents, lenses
  below), parent-owned integration here. No same-agent substitution.

Fresh-eye satisfaction: parent-delegated — reviewers A and B both returned
PASS with extra edge cases exercised beyond the cited suites; no findings
requiring repair before release.

## Reviewer Tier Evidence

- **Requested tier**: `n/a` (no tier requested; host-defaulted)
- **Requested spawn fields**: `n/a` (subagent defaults; no explicit model/effort ask)
- **Host exposure state**: `host-defaulted`
- **Host detail**: parent spawned two subagent reviewers (roles
  `release-critique-reviewer-a` / `release-critique-reviewer-b`); no
  provider-confirmed model or effort application claim
- **Application state**: `both reviewers delivered; verdicts PASS received, approval not inferred`
- **Delivery state**: `findings-received`
- **Execution mode**: `typed-subagent`
- **Reviewer A** (closeout-draft readiness refusal):
  packet `v894-release-critique-a-packet.md` (+ `.json`) — verdict PASS.
- **Reviewer B** (quality failure-log sweep):
  packet `v894-release-critique-b-packet.md` (+ `.json`) — verdict PASS.

## Boundary Ownership

- **Producer:** the issue skill owns closeout-draft readiness
  (`issue_validate_closeout_draft.py`); the quality engine owns
  failure-log lifecycle (`run_quality_engine_output.py`).
- **Consumer:** operators relying on ready/draft_blocked closeout status
  and on quality failure summaries naming current-run logs.
- **Owning surface:** the issue-validation and quality-engine tooling
  surfaces — release scope, receipt schema, and adapter machinery are
  untouched, so their semantics do not move with this change.
- **Verdict:** `owned-correctly` — each repair lives in the module that
  owns the refused behavior, with standing tests beside it.

## Open Risks

- Concurrent quality runs can still race the failure-log sweep window
  (noted pre-release; inherent to the tool, no repair demanded).
