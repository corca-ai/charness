# Issue #608 Claims-Review Release Stage Critique

Date: 2026-08-13

## Decision Under Review

Add a supported, pre-publication release stage for #608: normal execute creates
an immutable prepared release record (P), a distinct reviewer adds one bound
claims-evidence record (R), and only `--resume --publish-current` may publish
the exact P/R topology.

## Capability at Stake

The release helper must let a reviewer inspect the versioned final release
record before tag, push, or GitHub release creation, without turning a failed
publish attempt into an undocumented workflow step.

## Failure Angles

- Jackson / problem framing: the exact P-to-R recovery shape must be a new,
  marked state rather than a weakened use of generic failed-publish recovery.
- Weinberg / boundary ownership: the producer is the release-record executor;
  the final publication consumer is the tag/push/create tail. It must consume
  committed P/R blobs, not a mutable worktree artifact.
- Gawande / operations: retries must distinguish a missing remote leg from a
  mismatched remote identity and never duplicate a tag, evidence commit, or
  release creation.
- R2 repaired-contract check: preserving P while rerunning pre-push gates is
  coherent only when claims-lane resume does not rewrite the pre-publication
  artifact before publication.

## Counterweight Pass

- Act Before Ship: retain the marked direct-parent P-to-R classifier, committed
  path/blob/tag/version binding, and the precise recovery state table. Those
  are control-flow requirements, not documentation polish.
- Bundle Anyway: give the artifact one explicit JSON schema and one named CLI
  input; prove behavior through both source and shipped-plugin execution paths.
- Over-Worry: do not add cryptographic signatures, a new remote protocol, or a
  post-publication/issue-closeout redesign. Git/tree identity and existing
  publication recovery are the appropriate local boundary.
- Valid but Defer: the pre-existing resume release-surface preflight gap remains
  a separate contract change and is not smuggled into #608.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_resume.py:161-179 | action: fix | note: implement a marked P-to-R claims-review state; current resume only recognizes a release commit at HEAD.
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_execute.py:92-105 | action: fix | note: bind the reviewer artifact to P's committed release-record path and blob before every publication-adjacent call.
- F3 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_resume.py:293-301 | action: fix | note: claims-lane resume must not rewrite P because R isolation preserves the reviewed record.
- F4 | bin: bundle-anyway | evidence: moderate | ref: skills/public/release/scripts/publish_release_cli.py:167-170 | action: fix | note: expose the claims-review artifact as an explicit source/plugin CLI contract and help path.
- F5 | bin: over-worry | evidence: weak | ref: charness-artifacts/issue/2026-08-13-issue-608-resolution-brief.md | action: document | note: do not require signatures or a new remote protocol for a local commit/tree identity boundary.
- F6 | bin: valid-but-defer | evidence: strong | ref: skills/public/release/scripts/publish_release_resume.py:193-199 | action: defer | follow-up: deferred charness-artifacts/issue/2026-08-13-issue-608-resolution-brief.md | note: existing resume release-surface preflight gap remains separate.

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: model gpt-5.6-terra, reasoning_effort medium, service_tier priority, fork_turns none.
- Host exposure state: requested_fields_sent
- Application state: host did not return applied-model metadata.
- Delivery state: findings-received.

## Fresh-Eye Satisfaction

parent-delegated — causal review, three contrasting code-critique angles, a
separate counterweight, and a repaired-contract fresh-eye check returned to the
parent. All reviewer-boundary fingerprints verified clean.

## Reviewed Input Identity

- Packet consumed: `charness-artifacts/critique/2026-08-13-issue-608-resolution-final-packet.md`
- Packet path: `charness-artifacts/critique/2026-08-13-issue-608-resolution-final-packet.json`
- Packet SHA256: `7faa720861f01151269b9095c795dd14652f7f5d5843fe1256c64267c7f412e5`
- Identity SHA256: `34b8360c398ede6defbadbe596f0e07e5864277ab376cb488a9a747385e51114`

## Boundary Ownership

- Producer: `publish_release_execute.py` creates the versioned prepared record
  and its marker.
- Consumer: `publish_release_resume.py` validates P/R and then the release
  backend sees the tag, branch, and release creation.
- Owning surface: release helper state machine and release-record renderer.
- Verdict: owned-correctly.

## Next Move

Implementation completed locally. The state machine now preserves the exact
legacy unmarked recovery shapes and separately recognizes marked P/R, its
post-publication carrier, and its final closeout topology. A second review
round found and the implementation repaired two remote-retry defects: P's tag
and R's branch are reconciled independently, and R must be the current
publish-branch HEAD rather than a side-branch candidate. Per the two-round cap,
the R2 repairs are recorded as accepted-unreviewed; they remain covered by the
release regression suite below.

## Resolution Evidence

- Source and shipped plugin mirrors are synchronized for the claims helper,
  execute, CLI, artifact renderer, resume, and resume-closeout modules.
- `tests/quality_gates/test_release_publish.py`,
  `tests/quality_gates/test_release_publish_resilience.py`, and
  `tests/quality_gates/test_release_publish_critique_artifact.py` passed after
  the repair (source prepare, P-only refusal before auth, remote-tag-only retry,
  plugin execution, legacy recovery, claims carrier, and claims final recovery).
- No live release, tag, push, or issue closure was performed for this change.
- R3 found that claims-derived post-publication recovery did not revalidate R's
  JSON binding. The repair extends the required artifact validation to claims
  carrier/final phases before their recovery tail. It is an R3 repair under the
  two-round cap and is recorded as accepted-unreviewed.
