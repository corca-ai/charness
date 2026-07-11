# Critique Review
Date: 2026-07-11

## Decision Under Review

Delete only `MODULE_RELEASE_ONLY_RE`, a private regex superseded by the live AST
implementation, while retaining every advisory candidate with a gate-marker,
dynamic-consumer, or documented vocabulary role.

## Failure Angles

- Vulture's low-confidence output includes framework and dynamic-use false
  positives; five sibling candidates were explicitly retained after history and
  consumer review.
- `re` remains required by `NESTED_CLI_RE`; only the unused assignment was
  removed.
- The canonical public-skill helper and checked-in plugin mirror must move as
  one derived pair.

## Counterweight Pass

- No compatibility shim, new test, or dead-code floor is needed for a private
  constant with zero consumers and an already-tested replacement.
- Do not broaden this deletion into the documented intentional constants or the
  deferred prompt-mutation helper.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/surface_marker_lib.py | action: fix | note: remove the superseded private regex from source and derived mirror; cleared
- F2 | bin: over-worry | evidence: strong | ref: skills/public/release/scripts/publish_release_post_create.py | action: document | note: retain intentional public vocabulary and gate-marker constants despite low-confidence dead-code findings
- F3 | bin: valid-but-defer | evidence: moderate | ref: scripts/prompt_mutation_bundle_lib.py | action: defer | note: retain the broad stream helper until its deferred contract is resolved

## Reviewer Tier Evidence

- Requested tier: medium for a two-file derived deletion.
- Requested spawn fields: lower-power read-only explorer fields were sent through the host spawn surface.
- Host exposure state: metadata-hidden
- Application state: unverified; host acceptance did not confirm provider application.

## Fresh-Eye Satisfaction

parent-delegated; the reviewer first classified six advisory candidates, then
consumed the working-tree packet and confirmed the exact two-file deletion.
Rail-1 verification returned zero drift.

## Boundary Ownership

- Producer: the canonical public quality helper.
- Consumer: the AST-based standing-test economics inventory; plugin mirror is derived.
- Owning surface: `skills/public/quality/scripts/surface_marker_lib.py`.
- Verdict: owned-correctly
