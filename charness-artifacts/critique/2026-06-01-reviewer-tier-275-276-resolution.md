# Critique: Reviewer Tier, Issue #275, and Issue #276 Resolution

Date: 2026-06-01
Goal binding: reviewer-tier-closeout-and-issue-275
Fresh-Eye Satisfaction: parent-delegated
Packet Consumed: `charness-artifacts/critique/2026-06-01-123352-packet.md`
Target: code critique / issue resolution critique

## Change

The carrier resolves the reviewer-tier closeout bundle, issue #275's installed
plugin layout regression, and issue #276's achieve Before-phase activation
discussion gap.

## Angles

- Causal review for #275: installed plugin topology and sibling-skill lookup.
- Causal review for #276: structural goal readiness versus operator-facing
  activation readiness.
- Code critique for #275 runtime topology and diagnostics.
- Code critique for #276 discussion-trigger behavior.
- Counterweight pass over remaining concerns.

## Counterweight Triage

### Act Before Ship

- Fixed: #275 issue-skill resolver must not fall back to consumer repo
  `skills/issue` when the installed plugin lacks its sibling issue skill.
  `chunked_routing_issue_backend.py` now resolves from package/script parents
  only and tests diagnostic fallback instead of consumer shadowing.
- Fixed: #275 installed layout should prefer installed `skills/issue` over stale
  source-layout `skills/public/issue` when the running handoff script is
  installed-layout. Added explicit regression coverage.
- Fixed: malformed issue-provider JSON must become an issue-source diagnostic,
  not `issue_source_diagnostic: null` plus zero issues.
- Fixed: #276 empty `Discuss before activation:` labels no longer count as
  non-empty summaries.
- Fixed: #276 broad bundled scope now catches combined/together/repeated-issue
  and "all N proposed" shapes.
- Fixed: new required `goal_artifact_discussion.py` files are included in both
  source and plugin export surfaces.

### Bundle Anyway

- Added installed-layout issue-source test assertions for resolved repo and
  limit argv.
- Added listing-failure diagnostic assertions for `stage`,
  `provider_attempted`, exception type, and message.
- Added #276 per-trigger positive tests and a negative "Plan critique not yet
  run" test to avoid over-broad proof non-claim detection.

### Valid But Defer

- Broader resolver unification across all public/support cross-skill imports.
  The handoff issue/achieve paths named by #275 are covered; other helper
  topology questions should be handled as a separate runtime resolver design.
- Stronger auto-draft installed-achieve end-to-end proof using the real achieve
  bundle. Current `--help` import-time proof covers the reported #275 failure.
- Making `--pursue-ready` also run the full artifact validator. The current
  command intentionally answers activation readiness instead of full shape
  validation.

### Over-Worry

- More installed/source layout permutations and broader discussion-trigger regex
  expansion would overfit this carrier. Current tests cover the reported
  failures and the critique-discovered same-class risks.

## Next Move

Commit the carrier locally with explicit `Close #275. Close #276.` semantics.
Do not push or verify GitHub issue closure until the operator asks for push.
