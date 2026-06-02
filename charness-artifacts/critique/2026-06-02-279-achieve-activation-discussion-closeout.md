# Resolution Critique: #279 Achieve Activation Discussion Closeout

Date: 2026-06-02
Issue: #279
Goal:
`charness-artifacts/goals/2026-06-02-279-achieve-activation-discussion-closeout.md`
Debug artifact:
`charness-artifacts/debug/2026-06-02-279-achieve-activation-discussion-closeout.md`
Reviewer: Franklin (`019e8779-1d16-7813-9400-f8b93da5198d`)
Fresh-Eye Satisfaction: parent-delegated bounded review

## Findings

- Blocking recurrence risk: none found. The helper can still report
  `pursue_ready: true` structurally, but both direct helper output and
  `charness goal check` output now warn that surfaced activation discussion is
  not resolved and must be resolved or confirmed before `/goal`.
- Low follow-up folded during the slice: the initial implementation did not
  test the repo-owned CLI wrapper. Added
  `tests/charness_cli/test_goal_helpers.py` coverage for JSON passthrough and
  concise `REASON:` output.
- Residual wording risk: "resolve or explicitly ask" is acceptable for #279.
  A future hardening could make stop-before-activation wording even stronger,
  but that is not required for this closeout.

## Counterweight

- No extra Cautilus run is required by this slice. The changed `achieve` public
  skill is `hitl-recommended`; deterministic tests, checked-in dogfood evidence,
  and bounded fresh-eye review own the behavior proof.
- No live Ceal replay is claimed. The fix is a portable helper/prose contract
  update with synthetic fixtures.

## Verdict

Pass. The implementation closes the recurrence path that made
`discussion_summary_present` look like discussion completion, and the wrapper
test prevents the warning from being dropped by the repo CLI.
