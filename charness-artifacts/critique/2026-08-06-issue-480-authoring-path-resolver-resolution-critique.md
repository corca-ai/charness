# Issue #480 Authoring Path Resolver Resolution Critique
Date: 2026-08-06

## Decision Under Review

Generalize `<authoring-repo>/` inventory from a `scripts/`-only matcher to an
authoring-tree-relative path matcher, while preserving the separate
`<plugin-dir>/scripts/` consumer-package rule and keeping source/plugin mirrors
identical.

Success means that an existing docs or `charness-artifacts` target is checked
and a missing target is reported in both source and shipped scans. This slice
does not claim remote consumer execution or GitHub state.

## Failure Angles

- **Matcher coverage**: a regex or extraction path that still assumes
  `scripts/` could leave the exact docs/artifact class silently unverified.
- **Root ownership**: shipped mirrors could resolve `<authoring-repo>/` against
  the plugin tree, or `<plugin-dir>/scripts/` could accidentally resolve against
  the authoring tree, producing false positives or false negatives.
- **Verdict regression**: a missing-target fixture could be added without being
  wired into strict inventory, or a formatter could mark an unresolved row as
  resolved.
- **Truth-surface drift**: source and plugin copies or repaired stale references
  could diverge and make the checked-in consumer surface different from the
  authoring surface.

## Counterweight Pass

The concerns are bounded by the actual changed seam. The source/plugin script
and both edited documentation mirrors compare byte-for-byte; the focused tests
exercise present and missing docs/artifact targets in both layouts; and strict
inventory reports 514 references with zero findings and zero unreadable files.
The stale roadmap and external Cautilus references were repaired explicitly.
No blocker remains before shipping this slice. Remote consumer installation and
external repository state are valid but deferred because they are outside the
local contract and have no executed proof here.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: `scripts/inventory_skill_script_references.py` authoring placeholder loop and `tests/test_skill_script_references.py::test_the_authoring_marker_resolves_docs_and_artifacts_in_both_layouts` | action: fix | note: the resolver must derive a full authoring-relative target while retaining the plugin-script root as a separate rule; implemented and covered by the focused suite.
- F2 | bin: bundle-anyway | evidence: strong | ref: `skills/public/critique/references/autonomous-trigger.md`, `skills/public/quality/references/behavior-testing.md` and their plugin mirrors | action: fix | note: widening the matcher exposed two stale references; repairing them keeps the strict inventory green and makes the new enforcement honest.
- F3 | bin: over-worry | evidence: weak | ref: remote consumer installation and external repository behavior | action: defer | note: no local acceptance check claims this proof; remote/consumer validation remains an explicit non-claim.
- F4 | bin: valid-but-defer | evidence: moderate | ref: `charness-artifacts/quality/2026-08-06-issue-480-authoring-path-resolver.md` | action: defer | note: broadened non-markdown or command-carrier coverage belongs to the already sequenced #484/#482/#483 portability slices, not this resolver slice.

## Reviewer Tier Evidence

- Requested tier: `gpt-5.6-terra` with `medium` reasoning effort.
- Requested spawn fields: model `gpt-5.6-terra`, reasoning effort `medium`, service tier `priority`, `fork_context: false`, unnamed one-shot bounded reviewer.
- Host exposure state: applied
- Application state: host-confirmed: unnamed reviewer `019fd45b-b60b-7072-9c74-7d0deba15f20` returned findings with a clean verdict.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated: round 1 reviewer `019fd45b-b60b-7072-9c74-7d0deba15f20`
read the repaired source, tests, mirrors, and strict-inventory result; it found
no blockers. Boundary fingerprint window `issue480-authoring-path-r1` verified
clean immediately after return. Because round 1 produced no repairs, the
proof-surface second-round obligation is discharged.

## Reviewed Input Identity

No critique packet was consumed; the reviewer read the changed source, tests,
mirrors, and quality artifact directly.

## Boundary Ownership

- Producer: `scripts/inventory_skill_script_references.py` extracts and resolves authoring-repo and plugin-dir references.
- Consumer: strict inventory and its maintainers' validation gate render the resolved/unresolved verdict.
- Owning surface: `scripts/inventory_skill_script_references.py`, with its focused regression tests and synchronized plugin mirror.
- Verdict: owned-correctly
