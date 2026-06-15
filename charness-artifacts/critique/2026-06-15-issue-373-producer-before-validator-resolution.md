# Resolution Critique #373 - producer-before-validator ordering

Date: 2026-06-15
Issue: #373
Classification: bug
Reviewer: bounded fresh-eye causal-review subagent plus bounded fresh-eye
resolution-critique subagent, read-only shared parent worktree.

## Slice under review

Fix the `achieve` bootstrap instruction inversion where `check_goal_artifact.py`
was shown before `upsert_goal.py`, audit sibling public skills that produce
templated artifacts and expose validators or readiness checks, and add a
deterministic guard so producer/scaffold examples stay before validator/check
examples.

Changed surfaces:

- `skills/public/achieve/SKILL.md`
- `plugins/charness/skills/achieve/SKILL.md`
- `tests/quality_gates/test_artifact_producer_order.py`
- `charness-artifacts/debug/2026-06-15-issue-373-producer-before-validator.md`
- `charness-artifacts/debug/seam-risk-index.json`

## Causal Review

JTBD: artifact scaffold/producer instructions must precede validators/readiness
checks, and validators must be described as post-shape gates.

Classification confirmation: bug, specifically a workflow-boundary propagation
bug on public operator instructions rather than a helper implementation bug.

Root cause: the debug substrate names the structural cause as a missing
deterministic guard on public skill bootstrap examples, which let validator
commands be treated as harmless inspection commands before the artifact
producer. Debug artifact:
`charness-artifacts/debug/2026-06-15-issue-373-producer-before-validator.md`.

Invariant proof: the authored `achieve` skill now shows `upsert_goal.py` before
`check_goal_artifact.py`, describes the checker as a post-scaffold gate, and the
generated plugin mirror matches. The new quality-gate test asserts ordering for
known public artifact producer/validator pairs.

Detection gap: prior tests proved produced artifact shape, not the public
operator command sequence.

Sibling search: sibling shape is public skills with scaffold/template helpers
plus validators or readiness checks. The audit covered achieve, debug, quality,
ideation, critique, handoff, retro, and hitl.

Fresh-Eye Satisfaction: parent-delegated.

## Resolution Critique Findings

### Act Before Ship

- `hitl` was initially a recurrence hole because it uses the same script for
  produce/check modes: `sync_review_artifact.py` produces the durable artifact,
  while `sync_review_artifact.py --check` validates freshness. The first test
  table only modeled filename pairs, so a future inversion of the `hitl` check
  before sync would have passed.

Disposition: fixed before commit. `tests/quality_gates/test_artifact_producer_order.py`
now includes a same-script mode pair for `hitl`.

### Bundle Anyway

- Keep the table data shape able to represent same-script, different-mode
  producer/check pairs.

Disposition: bundled with a short comment above the `hitl` case.

### Valid but Defer

- Auto-deriving producer/validator pairs from an owning registry such as
  `scripts/check_artifact_surface_preflight.py` could reduce manual table drift,
  but is broader than closing #373.

Disposition: deferred; explicit table coverage is sufficient for this slice.

### Over-Worry

- Do not expand this into scaffold-output roundtrip testing for every artifact
  producer; the reported failure is public operator instruction order.
- Do not add duplicate assertions over the generated plugin mirror; packaging
  and mirror validators already cover that generated surface.

## Structured Findings

- bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_artifact_producer_order.py | action: fix | note: add hitl same-script sync versus --check ordering coverage
- bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_artifact_producer_order.py | action: document | note: keep the table capable of same-script mode pairs
- bin: valid-but-defer | evidence: moderate | ref: scripts/check_artifact_surface_preflight.py | action: defer | note: deriving the table from a registry is useful but broader than #373
- bin: over-worry | evidence: moderate | ref: plugins/charness/skills/achieve/SKILL.md | action: defer | note: duplicate generated-mirror assertions are unnecessary with packaging validation

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: model=gpt-5.5, reasoning_effort=medium, service_tier=priority.
- Host exposure state: requested_fields_sent
- Application state: unverified-by-host; spawn tool accepted the requested fields and returned reviewer agent ids `019ecb13-d4ea-7412-86c7-ad0246d1de65` and `019ecb13-fd1e-7fd2-8686-bb44063abe2f`, but did not confirm provider application.

## Fresh-Eye Satisfaction

Fresh-Eye Satisfaction: parent-delegated. The causal-review and
resolution-critique subagents both completed; the Act Before Ship `hitl`
same-script mode finding was fixed before commit.

## Verification

- `pytest -q tests/quality_gates/test_artifact_producer_order.py tests/quality_gates/test_goal_artifact_producers.py` passed after the `hitl` addition.
- `ruff check tests/quality_gates/test_artifact_producer_order.py` passed.
- `python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing` passed with only the pre-existing advisory on `scripts/staged_commit_gate_plan.py`.
