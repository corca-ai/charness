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

- **Reviewer A** (closeout-draft readiness refusal):
  packet `v894-release-critique-a-packet.md` (+ `.json`) — verdict PASS.
- **Reviewer B** (quality failure-log sweep):
  packet `v894-release-critique-b-packet.md` (+ `.json`) — verdict PASS.

## Open Risks

- Concurrent quality runs can still race the failure-log sweep window
  (noted pre-release; inherent to the tool, no repair demanded).
