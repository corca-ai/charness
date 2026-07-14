# v1.0.6 Dup-Ratchet Resolution Critique
Date: 2026-07-14

## Decision Under Review

Whether the duplicate-family drift introduced by the lifecycle truthfulness
slice represents code that must be consolidated before v1.0.6, or reviewed
fingerprint rotation / intentionally local glue that may be baselined.

## Failure Angles

- Shared-domain drift: separate timestamp, path, schema discovery, JSON loading,
  and manifest validation implementations could disagree between lifecycle and
  feedback writers and silently produce incompatible telemetry.
- Portability: extracting the issue/release post-boundary wrappers could replace
  two self-contained loaders with a new bootstrap dependency that fails in an
  installed plugin layout.
- Truth semantics: generalizing release artifact list construction could couple
  distinct-channel publication evidence to lifecycle non-claim wording merely
  because both render Markdown lines.
- Baseline integrity: accepting a rotated fingerprint as a brand-new family
  without linking it to its reviewed predecessor would erase the audit trail.

## Counterweight Pass

- Act before ship: consolidate the five shared-domain lifecycle utilities into
  the existing usage-feedback / usage-record owners. This removed four of the
  original seven new families and preserved caller-specific error rendering.
- Rotation: `3a2a1a48f75e2333` replaces reviewed intentional family
  `6962d4713943ed31`; only the CLI dispatch/error skeleton remains shared while
  the reporter gained objective-lifecycle output.
- Intentional: `76dbe167ecaf4a81` shares four generic list-building lines, not a
  stable proof-semantic abstraction. The counterweight rejected pre-release
  extraction after one reviewer raised it.
- Intentional: `82b2e7b16bc79773` keeps portable skill-local failure containment;
  actual event IDs, schemas, append behavior, and conflict handling are already
  centralized in `lifecycle_usage_capture.py`.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/usage_episode_records.py | action: fix | note: move manifest validation to the usage-record owner and reuse existing feedback timestamp, path, schema, lock, and JSON utilities
- F2 | bin: bundle-anyway | evidence: strong | ref: scripts/report_usage_episodes.py | action: document | note: rotate reviewed intentional renderer family 6962d4713943ed31 to 3a2a1a48f75e2333 with the prior rationale preserved
- F3 | bin: over-worry | evidence: contested | ref: skills/public/release/scripts/publish_release_artifact_sections.py | action: defer | note: four generic Markdown list-building lines do not form a stable truth-bearing abstraction before v1.0.6
- F4 | bin: valid-but-defer | evidence: strong | ref: skills/public/issue/scripts/issue_close.py | action: document | note: baseline the two portable post-boundary loaders as intentional while core capture semantics remain shared

## Reviewer Tier Evidence

- Requested tier: bounded high-leverage fresh-eye review plus counterweight.
- Requested spawn fields: `model=gpt-5.4`, `reasoning_effort=high`, no-tool read-only envelope.
- Host exposure state: metadata-hidden
- Application state: spawn accepted the requested fields; provider application was not exposed.

## Fresh-Eye Satisfaction

parent-delegated. Packet Consumed:
`charness-artifacts/critique/2026-07-14-v1-0-6-dup-ratchet-packet.md`.
Two independent no-tool reviewers covered structure and installed portability;
a third no-tool counterweight resolved their disagreement on the four-line
artifact renderer family. Parent-side reviewer-boundary verification reported
no worktree or index drift.

## Boundary Ownership

- Producer: issue/release workflows produce objective lifecycle events; usage
  record utilities validate their shared adapter; release renderers describe
  proof without converting it into satisfaction.
- Consumer: usage reporting, release operators, and installed-plugin runtimes.
- Owning surface: `usage_episode_records.py` for shared adapter validation,
  `lifecycle_usage_capture.py` for capture semantics, and each skill-local
  wrapper for portable post-boundary failure containment.
- Verdict: moved-to-owner

## Verification Evidence

- Focused usage episode, feedback, validator, and lifecycle suite: 114 passed.
- Ruff passed for source, plugin mirrors, and directly relevant tests.
- Dup ratchet reduced from seven new families to the three reviewed families
  above before any baseline mutation.
- The reviewer-boundary snapshot verified clean after all three delegated
  reviews.

## Deliberately Not Doing

- No generic Markdown section builder for four shared list-construction lines.
- No cross-skill lifecycle-loader package whose own bootstrap would recreate
  the portability problem it claims to remove.
- No new blocking gate: the existing dup ratchet found the problem and forced
  structural reduction before scoped review.
