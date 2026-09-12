# Release workflow regression evidence

> Status: current
> Source of truth: existing consumer tests and the incident record below
> Last verified: 2026-09-12

The September 2026 delay is a cross-repo release workflow incident.
Acceptance must exercise the actual review and publish consumers.

The standalone experimental runner and its dogfood were removed: only the
dogfood invoked that runner, so its green verdict did not prove production
release behavior. The experiment also duplicated process orchestration and
receipt handling and grew beyond the existing code-length limits.

## Existing consumer checks

Run the relevant tests through the standing runner:

```bash
python3 scripts/gates_support/run_standing_pytest.py --repo-root . \
  --pytest-target tests/test_review_followup.py \
  --pytest-target tests/quality_gates/test_reviewer_lifecycle.py \
  --pytest-target tests/quality_gates/test_release_resume_state_validation.py \
  --pytest-target tests/quality_gates/test_release_quality_status_binding.py
```

These check retained review input identity and tamper refusal, partial output
without approval, publish resume state, and quality receipt propagation.
They do not establish parallel reviewer scheduling, reviewer selection across
a whole release intent, or a published release. Those acceptance claims need
observations from the actual release path before they can be closed.

Historical experiment timings and reviewer findings remain in
[the incident record](../charness-artifacts/release/2026-09-12-cross-repo-release-workflow-incident.json).
Its simulation results are historical evidence, not current release approval.
