# Issue Resolve Preflight Ordering Code Critique
Date: 2026-07-13

## Decision Under Review

Reject a valid-adapter `issue plan --intent resolve --target ...` invocation
before backend resolution or GitHub preflight while preserving invalid-adapter
precedence, exact rc/error semantics, valid paths, and source/plugin parity.

Packet Consumed:
`charness-artifacts/critique/2026-07-13-round4-issue-preflight-packet.md`.

## Failure Angles

- Diagnostic/ownership: the new order is adapter validity, local target misuse,
  then backend/preflight. The no-call regression fails if backend resolution,
  preflight, or resolve invocation runs, so the fix sits at the argument owner.
- Operator/public CLI: the subprocess path keeps rc=2 and the same error, uses a
  fake GitHub environment, and the public source and plugin mirror are identical.
- Compatibility: valid `new` and `resolve` paths still build preflight before
  their plan; invalid adapter still exits rc=1 before target classification.

## Counterweight Pass

- Act Before Ship: none.
- Bundle Anyway: none; both proposed extra assertions duplicate a stronger
  existing seam proof or lock an unobserved intersection.
- Over-Worry: exact full subprocess payload/absence assertions would duplicate
  the in-process exact payload and three no-call sentinels.
- Valid but Defer: a combined invalid-adapter plus forbidden-target test is
  reasonable only if this adjacent ordering is refactored again.
- Verdict: APPROVE the current bounded diff.

## Public Skill Evaluation Review

- The maintained `issue-sibling-search-concept-fixtures` and
  `representative-skill-contracts` scenarios were inspected. They own routing,
  representative contract markers, and sibling-search behavior; they do not
  observe local invalid-input side effects.
- The dogfood contract remains unchanged: GitHub source-of-truth selection,
  causal review, feature-brief behavior, and mutation paths are untouched.
- No scenario or dogfood-matrix change is warranted. The exact rc/error payload
  plus three in-process no-call sentinels and the fake-backend subprocess test
  are the cheaper, directly observing evidence channel for this ordering fix.
- Cautilus was not run: repo policy is ask-before-run, and the user has not
  separately authorized an evaluator invocation. This is a deliberate
  non-claim, not evaluator-backed evidence.

## Structured Findings

- F1 | bin: over-worry | evidence: strong | ref: tests/quality_gates/test_issue_tool_runners.py | action: document | note: do not duplicate exact payload and no-call proof in the subprocess test
- F2 | bin: valid-but-defer | evidence: moderate | ref: skills/public/issue/scripts/issue_plan.py | action: defer | note: add the combined invalid-adapter and forbidden-target intersection only if ordering is refactored again

## Reviewer Tier Evidence

- Requested tier: high-leverage for a public-skill workflow boundary.
- Requested spawn fields: model=gpt-5.5, reasoning_effort=medium, service_tier=priority.
- Host exposure state: requested_fields_sent
- Application state: provider application not exposed; no application claim.

## Fresh-Eye Satisfaction

parent-delegated — two distinct angle reviewers and one separate counterweight
completed; rail-1 fingerprint verification reported zero worktree/index drift
after every reviewer.

## Boundary Ownership

- Producer: `issue_plan.command_plan` produces argument-shape validation and
  plan sequencing.
- Consumer: issue-skill operator or caller consuming plan JSON and exit status.
- Owning surface: public issue skill source plus checked-in plugin mirror.
- Verdict: owned-correctly
