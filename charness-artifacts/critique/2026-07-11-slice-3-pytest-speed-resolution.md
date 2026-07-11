# Slice 3 Pytest Speed Resolution Critique
Date: 2026-07-11

## Decision Under Review

Replace one nested real-repository six-gate pytest integration with an
in-process orchestration contract while leaving every real gate and its owning
validation surface intact.

## Failure Angles

- The change could manufacture speed by deleting the only real execution of a
  portable-package validator.
- A fake runner could prove only the happy path and lose ordering, diagnostics,
  or nonzero-result propagation.
- A targeted node speedup could be laundered into an unsupported full-suite
  performance claim.

## Counterweight Pass

- Real validators remain on closeout/quality/operator surfaces and retain their
  individual tests; the removed node redundantly nested them inside pytest.
- The replacement proves full command order, cwd/timeout forwarding, id/command
  mapping, stdout/stderr tail trimming, failure aggregation, and blocked status.
- Standalone wall median improved from 4.88s to 0.655s. Mixed isolated A/B
  suite deltas make the suite-wide effect explicitly inconclusive.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: charness-artifacts/quality/2026-07-11-issue-create-safety-quality-speed-sweep.md | action: document | note: persist the targeted speedup and full-suite non-claim together
- F2 | bin: valid-but-defer | evidence: moderate | ref: .agents/surfaces.json | action: defer | note: exact command parity with the surface registry may be useful later, but the removed test never proved it and this slice need not add a new floor
- F3 | bin: over-worry | evidence: strong | ref: tests/quality_gates/test_skill_surface_preflight.py | action: defer | note: rerunning six real validators inside this node is redundant because validator correctness stays with their individual gates and closeout surfaces

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model=gpt-5.5, reasoning_effort=high
- Host exposure state: requested_fields_sent
- Application state: spawn accepted requested fields; host application metadata was not exposed.

## Fresh-Eye Satisfaction

parent-delegated — one bounded read-only reviewer consumed
`charness-artifacts/critique/2026-07-11-slice3-pytest-speed-packet.md`;
parent fingerprint verification found zero worktree or index drift.

## Boundary Ownership

- Producer: `check_skill_surface_preflight.py::_check_commands`.
- Consumer: `_run_checks`, `build_report`, operator `--run-checks`, and repo closeout/quality surfaces.
- Owning surface: orchestration behavior in the focused test; validator correctness in each real gate.
- Verdict: owned-correctly
