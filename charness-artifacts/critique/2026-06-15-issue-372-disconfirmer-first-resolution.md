# Resolution Critique #372 - disconfirmer-first debug rung

Date: 2026-06-15
Issue: #372
Classification: bug
Reviewer: bounded fresh-eye causal-review subagent plus bounded fresh-eye
resolution-critique subagent, read-only shared parent worktree.

## Slice under review

Add a debug workflow rung requiring absence, attribution, liveness, and
frequency claims to run the cheapest falsifier before being treated as
confirmed. Keep runtime-state claims grounded in runtime evidence rather than
source inference alone, and make bug-class issue causal review consume the same
debug substrate.

Changed surfaces:

- `skills/public/debug/SKILL.md`
- `skills/public/debug/references/disconfirmer-first.md`
- `skills/public/issue/references/causal-review.md`
- `plugins/charness/skills/debug/SKILL.md`
- `plugins/charness/skills/debug/references/disconfirmer-first.md`
- `plugins/charness/skills/issue/references/causal-review.md`
- `tests/quality_gates/test_debug_rca_reference_cite_chain.py`
- `charness-artifacts/debug/2026-06-15-issue-372-disconfirmer-first-debug.md`
- `charness-artifacts/debug/seam-risk-index.json`

## Causal Review

JTBD: debug/diagnosis workflows must not promote absence, attribution,
liveness, or frequency claims from partial evidence before running the cheapest
falsifier; runtime state must outrank source inference for liveness and
running/wired claims.

Classification confirmation: bug. The implied debug contract allowed recurring
premature conclusions because named-target runtime verification was narrower
than the four claim classes in #372.

Root cause: the debug substrate lacked a claim-type gate. It had runtime
verification for specific named targets, but no reusable cheapest-falsifier rule
before confirmation.

Invariant proof: `skills/public/debug/references/disconfirmer-first.md` defines
the claim triggers, probe preference, output fields, and over-reach boundary.
`skills/public/debug/SKILL.md` invokes the rung, and the generated plugin mirror
matches. After fresh-eye review, `skills/public/issue/references/causal-review.md`
also names this substrate for bug-class issue causal review.

Detection gap: tests guarded other debug hooks but did not pin a
disconfirmer-first claim gate or the four trigger classes.

Sibling search: `named-target-verification.md` is complementary same-layer
coverage; `issue resolve` is the abstraction-up consumer; liveness/wired/running
claims are specialization-down examples; and the recurring mental model is that
a narrow source search is enough to conclude absence.

Fresh-Eye Satisfaction: parent-delegated.

## Resolution Critique Findings

### Act Before Ship

- Bug-class issue causal-review prompts could still omit the new
  disconfirmer-first rung because `skills/public/issue/references/causal-review.md`
  listed five-whys, invariant-first, detection-gap, and sibling-search substrate
  cites but not `disconfirmer-first.md`.

Disposition: fixed before commit. The causal-review prompt contract and Lens 1
now include `disconfirmer-first.md`, and the focused test pins both.

### Bundle Anyway

- The debug artifact's non-claim relies on issue resolution consuming debug
  substrate. After the causal-review cite-chain fix, this is accurate enough
  without a broader public-skill sweep.

Disposition: bundled by the same causal-review reference/test update.

### Valid but Defer

- Live agents can still choose a weak cheapest falsifier. Stronger evaluator
  coverage for falsifier quality is real future work, but this slice makes the
  obligation explicit and auditable.

### Over-Worry

- Do not require every diagnostic sentence to carry the output fields. The new
  reference correctly limits the rung to claims that steer diagnosis, closeout,
  or next action.
- Do not add separate mirror-specific tests; sync and packaging validation cover
  the generated mirror.

## Structured Findings

- bin: act-before-ship | evidence: strong | ref: skills/public/issue/references/causal-review.md | action: fix | note: add disconfirmer-first.md to issue causal-review substrate cites and Lens 1
- bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_debug_rca_reference_cite_chain.py | action: fix | note: pin the issue causal-review prompt contract and Lens 1 consumption
- bin: valid-but-defer | evidence: moderate | ref: skills/public/debug/references/disconfirmer-first.md | action: defer | note: evaluator coverage for falsifier quality is broader than this slice
- bin: over-worry | evidence: moderate | ref: plugins/charness/skills/debug/SKILL.md | action: defer | note: generated mirror-specific tests are unnecessary with sync and packaging validation

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: model=gpt-5.5, reasoning_effort=medium, service_tier=priority.
- Host exposure state: requested_fields_sent
- Application state: unverified-by-host; spawn tool accepted the requested fields and returned reviewer agent ids `019ecb1d-3ae3-7ef0-9934-efe7a272f8a6` and `019ecb1d-62b2-7fc3-9a9f-d3f6dffbd238`, but did not confirm provider application.

## Fresh-Eye Satisfaction

Fresh-Eye Satisfaction: parent-delegated. The causal-review and
resolution-critique subagents both completed; the Act Before Ship
issue-causal-review cite-chain finding was fixed before commit.

## Verification

- `pytest -q tests/quality_gates/test_debug_rca_reference_cite_chain.py` passed after the cite-chain fix.
- `python3 scripts/validate_critique_artifacts.py --repo-root . --report-all` passed for this artifact.
