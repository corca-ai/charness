# v2.1.6 Release Critique
Date: 2026-07-19

## Execution

Three parent-delegated release angles covered operational sequencing, public
communication, and recovery usability. The first pass found two release
blockers: missing public notes and a post-publication resume path that could
reach a missing draft-validation key when the original issue-close inputs were
omitted. Both were repaired and independently re-reviewed. A separate
counterweight then consumed the final JSON packet and found no code-level hold.
Reviewer-boundary fingerprint verification reported zero drift after each
shared-worktree review phase.

The first publish attempt stopped before mutation when the release-only quality
bundle found four duplicate families. Two same-owner artifact/Git commit clones
were extracted into a cohesive release-local module; two portable CLI/bootstrap
families were reviewed as intentionally independent rather than force-shared.
The duplicate ratchet was then moved into ordinary skill and repo-Python slice
closeout surfaces. A final packet-bound reviewer confirmed the extraction,
classification, source/plugin parity, and earlier gate placement.

The refreshed broad suite then found that isolated/partial installs lacked the
new artifact helper and failed during policy-module import. The loader now
degrades to an unavailable action and emits a typed error only when artifact
commit behavior is actually requested. Direct real-file and partial-install
tests cover that boundary. The coverage selector learned the one-argument
release-local loader, eliminating an unnecessary full-instrumentation fallback;
the focused producer and authoritative changed-line consumer passed afterward.

## Decision Under Review

Publish v2.1.6 with a post-publication evidence carrier for linked-issue close
keywords, compact YAML-first release planning, a shared portable delta owner,
and faster inventory contract tests.

## Target

Release critique before version bump, tag, push, public GitHub release, and
installed-machine refresh.

## Release Scope

Target version and tag: `2.1.6` / `v2.1.6`. Consumers receive a safer release
publication/recovery boundary and denser planner evidence without a migration
or configuration change.

## Capability at Stake

Release publication must be independently observable before any branch update
can auto-close a linked issue, and an interrupted maintainer must receive an
actionable, identity-preserving recovery path.

## Failure Angles

- Gawande / operations: check publication, evidence-carrier ordering, resume
  topology, mirror synchronization, clean-tree publication, and public readback.
- Minto / communication: ensure notes lead with operator value and state
  upgrade, migration, rollback, recovery, and non-claims explicitly.
- Raskin / humane interface: exercise the natural minimal resume invocation and
  inspect whether omitted irreversible inputs fail early and actionably.
- Counterweight: distinguish boundary evidence from speculative extra gates and
  keep reversible details judgment-led.

## Counterweight Pass

- Act Before Ship: commit this packet and critique artifact, restore a clean
  worktree, and run the normal locked release checks before publication.
- Bundle Anyway: none after the notes and recovery diagnostic repairs.
- Over-Worry: do not add more carrier guards or reopen release-note phrasing;
  exact message/tree/tag/remote checks and the current notes cover the observed
  risks.
- Valid but Defer: consider binding critique identity into a future carrier
  record or narrowing help wording to the exact enforced guarantee. Current
  recovery still cannot accept a mismatched issue carrier or remote identity.
- Over-Worry: do not unify independently executable root/public-skill CLI
  presentation or bootstrap seams merely to reduce lexical duplication; that
  would replace local repetition with cross-package runtime coupling.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/release/2026-07-19-v2.1.6-notes.md | action: fix | note: public notes now state scope, normal upgrade, no migration or operator rollback, maintainer recovery, and bounded non-claims
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_resume_closeout.py | action: fix | note: post-publication resume now validates the complete original closeout-input envelope before carrier preflight
- F3 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_release_publish_resilience.py | action: fix | note: a real CLI fixture constructs publication plus carrier-push interruption and proves the minimal resume fails with complete guidance
- F4 | bin: over-worry | evidence: strong | ref: skills/public/release/scripts/publish_release_resume.py | action: defer | note: additional recovery machinery is not justified beyond exact topology, evidence-tree, message, tag, and remote-SHA validation
- F5 | bin: valid-but-defer | evidence: moderate | ref: skills/public/release/scripts/publish_release_cli.py | action: defer | note: future work may bind critique identity into carrier state or narrow help wording, but no unsafe carrier or reconcile path results today
- F6 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/release_issue_closeout_artifact.py | action: fix | note: artifact writing and Git commit/push behavior now have one cohesive release-local owner instead of two duplicated policy-module tails
- F7 | bin: act-before-ship | evidence: strong | ref: .agents/surfaces.json | action: fix | note: duplicate coupling now fails at ordinary skill or repo-Python slice closeout instead of first appearing in the release-only bundle
- F8 | bin: over-worry | evidence: strong | ref: charness-artifacts/quality/dup-review.json | action: document | note: portable CLI and bootstrap families remain intentionally independent because extraction would couple unrelated payload, exit, timeout, and installation boundaries
- F9 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/release_issue_closeout.py | action: fix | note: optional artifact-helper absence no longer breaks module import and fails with a typed message only at the requested action boundary
- F10 | bin: bundle-anyway | evidence: strong | ref: scripts/suggest_mutation_coverage_command.py | action: fix | note: release-local loader ancestry now maps the new module to standing tests and avoids an unnecessary broad instrumentation fallback
- F11 | bin: valid-but-defer | evidence: moderate | ref: scripts/suggest_mutation_coverage_command.py | action: defer | note: identifier-boundary and comment-aware loader matching can be tightened later; the changed-line consumer remains the final fail-closed check against an optimistic suggestion

## Surface-Lock Inventory

- Consumer behavior: release-content commits contain no issue-close keywords;
  only the independently observed evidence carrier may contain them.
- Recovery behavior: carrier/final topology, exact message, evidence tree, tag,
  remote branch identity, ambiguous push, and restart-input checks.
- CLI surface: `--resume --publish-current` help and actionable missing-input
  diagnostic; YAML-first planner/checker detail with hidden JSON compatibility.
- Public documentation: publication-boundary recovery invariant and v2.1.6
  release notes.
- Distribution: source release skill, checked-in plugin mirror, versioned
  manifest/tag, generated release artifact, and installed-machine refresh.
- Proof: release resilience, edge, state, distinct-channel, real-host-delta,
  YAML-output, packaging, and changed-line gates.

## Operator Action Required

Ordinary operators use the normal Charness update workflow. Release maintainers
must publish from a clean tree with this critique artifact and notes file. If a
linked-issue closeout publish is interrupted after publication, repeat the exact
original issue, classification, carrier-file, behavioral-evidence, repository,
and critique arguments with `--resume --publish-current`.

## Upgrade Path

No data or configuration migration is required. No ordinary operator rollback
step is expected. Release maintainers use the identity-checked resume path after
an interrupted publish; they do not reconstruct closeout intent from commit
text.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model gpt-5.6-terra; reasoning_effort medium; service_tier priority; fork_turns none
- Host exposure state: requested_fields_sent
- Application state: host accepted the requested fields but exposed no provider-application confirmation

## Fresh-Eye Satisfaction

parent-delegated

## Packet Consumed

`charness-artifacts/critique/v2-1-6-release-candidate-packet.json`

## Reviewed Input Identity

- Packet path: charness-artifacts/critique/v2-1-6-release-candidate-packet.json
- Packet SHA256: b5a82c30f976c7111dd12fc6e56b87cd7f1e976980803538e8fe4fb8413b8030
- Identity SHA256: a21b9612f12c2ac8091ebb9cc11222b4297f192df070550862377bdc09f7c374

## Boundary Ownership

- Producer: release publisher produces immutable release content, observer
  evidence, issue-close carrier, and final state artifact.
- Consumer: GitHub branch processing consumes close keywords; operators and the
  resume state machine consume durable evidence and restart inputs.
- Owning surface: public release publication/resume capability and its exported
  plugin mirror.
- Verdict: owned-correctly

## Deliberately Not Doing

- No new resume command, recovery database, webhook timing model, or mandatory
  live issue closure for a release that closes no linked issue.
- No claim that fake-host fixtures prove GitHub webhook timing.
- No extra gate on reversible planner presentation beyond the immutable range,
  path count/digest, and actual trigger evidence.

## Next Move

Commit the refreshed packet and critique, run the duplicate ratchet and locked
closeout on the clean final candidate, then retry the release helper with the
reviewed notes file. Treat the public observer, remote ref readback, and
installed-machine readback as the irreversible-boundary evidence.
