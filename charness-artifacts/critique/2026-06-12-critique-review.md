# Critique Review
Date: 2026-06-12

## Decision Under Review

Template-first artifact gates slice: quality scaffold fill-time guard
comments (line cap, bullet grammar), `--report-all` wired into the standing
`validate-quality-artifact` gate, and a "Template-First Artifact Gates"
doctrine section in `adapter-gate-review.md` for consumer repos.

## Failure Angles

- Cap-constant drift: `MAX_ARTIFACT_LINES` now duplicated in validator and
  scaffold with no parity proof; template could teach a wrong cap.
- Kept guard comments interacting with validator token scans (false
  pass/fail) or consuming cap lines.
- Exported-plugin layout: changed template or missing `--report-all` in the
  plugin validator copy breaking consumer round-trips.
- Doctrine overreach: report-all property had no enforcement tier and five
  sibling charness validators lack the flag — invites over-blocking reviews.
- Root cause half-addressed: scaffold still prints to stdout (no `--write`),
  so scratch-authoring stays roughly equal-effort.

## Counterweight Pass

- Real and folded this slice: parity test (F1), doctrine tier sentence +
  D28 deferral entry (F4). Valid-but-defer: `--write` mode (F5) — folded
  into D28 because quality-only would fork the shared scaffold lib, and
  `--report-all` already collapses the n-run pain on either path.
- Over-worry: guard comments cannot flip any validator rule (all 10 checks
  scanned; round-trip test proves tolerance); plugin validator copy already
  ships `--report-all`; multi-line failure output is consumed by exit code.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: tests/test_quality_scaffold.py | action: fix | note: assert the template cap against the validator module constant, not a third hardcoded literal — fixed this slice
- F4 | bin: act-before-ship | evidence: moderate | ref: skills/public/quality/references/adapter-gate-review.md | action: fix | note: missing report-all mode classified `AUTO_CANDIDATE` at most, never a blocker by itself — fixed this slice
- F5 | bin: valid-but-defer | evidence: moderate | ref: scripts/scaffold_artifact_lib.py | action: document | note: `--write` mode and five-family generalization recorded as D28 in docs/deferred-decisions.md with a reopen trigger
- F2 | bin: over-worry | evidence: strong | ref: scripts/validate_quality_artifact.py | action: defer | note: guard comments verified inert across all validator checks; cost is two cap lines

## Reviewer Tier Evidence

- Requested tier: high-leverage (public-skill/validator surface decision).
- Requested spawn fields: `.agents/critique-adapter.yaml` reviewer_tiers
  mapping targets a Codex host; not sendable on this Claude Code host.
- Host exposure state: host-defaulted
- Application state: host resolved the tier to its default strongest
  reviewer; two bounded reviewers (angle, counterweight) actually spawned.

## Fresh-Eye Satisfaction

parent-delegated. Angle reviewer verdict SHIP-after-two-additions; separate
counterweight reviewer verdict SHIP-with-named-fixes (parity test, doctrine
tier sentence, D28 entry) — all three folded before commit. Concrete
signals: both reviewers ran read-only in the shared worktree and verified
mirror sync, plugin-side `--report-all`, and round-trip tests green.
