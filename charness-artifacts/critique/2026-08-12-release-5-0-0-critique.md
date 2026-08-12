# Release 5.0.0 Critique

Date: 2026-08-12

## Execution

Three bounded, read-only fresh-eye angle reviews and one separate counterweight
review completed before release mutation. All reviewer-boundary fingerprints
verified clean.

## Decision Under Review

Release the committed `v4.2.0..HEAD` change set as `charness` 5.0.0, through the
repo-owned release helper, with a durable public release note and no issue
closeout.

## Release Scope

- Version and tag: `5.0.0` / `v5.0.0`.
- Consumer effect: the release adds operator/maintainer evidence and validation
  capability, and it deliberately makes closeout provenance and handoff pickup
  ownership requirements enforceable for existing callers.
- SemVer rationale: major, not minor, because existing public automation can
  fail where `close-with-comment` lacks `AI-provenance:` or uses the removed
  handoff `--pickup-target` invocation.

## Surface-Lock Inventory

- Packaged CLI and checked-in plugin manifests/export.
- `issue_tool.py close-with-comment` provenance floor.
- Handoff pickup planner ownership and option behavior.
- Local quality/ratchet/timing and Cautilus observation evidence surfaces.
- Release notes, GitHub release body, update instructions, and install refresh.

## Failure Angles

- Operational: the publish helper requires a clean worktree, fresh-checkout
  probes, and distinct post-publication verification.
- Communication: the prior release record is for 4.2.0 and cannot stand in for
  the 5.0.0 public narrative.
- Operator experience: provenance and pickup invocation changes are compatibility
  breaks that need migration/recovery text.

## Findings

- The initial 4.3.0 proposal was not supportable because the two incompatible
  command changes are public invocation changes, not merely stricter internal
  diagnostics.
- A 5.0.0 note must state that the Cautilus evidence is one authorized local
  observation and that CI configuration is local/static; neither establishes
  hosted CI or consumer behavior.

## Counterweight Pass

- Counterweight conclusion: ship 5.0.0 rather than restoring compatibility in
  this release. Compatibility restoration would broaden the requested publish
  into a new implementation slice; the major boundary makes the present state
  explicit instead.
- An announcement is not separately required; the durable release note is the
  public source of truth.

## Operator Action Required

- Update with `charness update`, then restart Codex or Claude Code as directed
  by the updater.
- For issue closeout automation, add a nonempty `AI-provenance:` line to the
  carrier body before `close-with-comment`; its truth remains subject to the
  later closeout review.
- For handoff automation, remove `--pickup-target` and repair any unowned entry
  the planner reports before continuing.

## Upgrade Path

- No automatic migration is supplied. Resolve the two command-contract changes
  above, run the affected planner or closeout command, and retain its output as
  the migration proof.
- Operator rollback is not an updater subcommand. Reinstall or pin the prior
  `v4.2.0` source/release through the host's supported plugin mechanism, then
  restart the host and run `charness doctor`; report an unresolved host-specific
  rollback through the repository issue path.

## Deliberately Not Doing

- Do not claim hosted CI, consumer behavior, or general evaluator success.
- Do not add compatibility shims or close issues as part of this release.
- Do not publish the ignored local `.charness/quality/` receipts.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/issue/scripts/issue_closeout_rung1_floors.py:324 | action: document | note: publish as major and document the required nonempty AI-provenance carrier line plus its later truth review.
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/handoff/scripts/plan_handoff_run.py:347 | action: document | note: publish as major and document removal of --pickup-target plus ownership repair.
- F3 | bin: bundle-anyway | evidence: strong | ref: charness-artifacts/cautilus/handoff-judge-intent-2026-08-12/finding.md | action: document | note: include local-only evaluator and static-CI non-claims in release notes.
- F4 | bin: bundle-anyway | evidence: moderate | ref: skills/public/release/references/publication-boundary.md | action: document | note: state the supported recovery boundary in release notes.
- F5 | bin: over-worry | evidence: weak | ref: docs/narrative-announcement-boundary.md | action: document | note: no separate announcement is needed when the release note is the public source of truth.

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: fork_turns=none, model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority.
- Host exposure state: requested_fields_sent
- Application state: host metadata does not confirm provider application.
- Delivery state: findings-received.

## Fresh-Eye Satisfaction

parent-delegated — operational, communication, operator-experience, and
counterweight reviews were received through the host reviewer channel.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/2026-08-12-release-5-0-0-critique-packet.json
- Packet path: charness-artifacts/critique/2026-08-12-release-5-0-0-critique-packet.json
- Packet SHA256: 19ecb4905dd68803da39594303745fe3c46f4bc8014c6a5833bbb8e059db6825
- Identity SHA256: d587a94eead9030a3e8df9e02c32111fbd3652752e848fd59d7a935d1d84b9e8

## Boundary Ownership

- Producer: issue and handoff command callers provide closeout/progress input.
- Consumer: the issue closeout and handoff planner verdict renderers.
- Owning surface: packaged operator command contract.
- Verdict: owned-correctly.

## Next Move

The critique packet and v5.0.0 release notes are committed. The first execute
attempt correctly rolled back on final-record evidence drift; that repair is
committed and independently reviewed. Re-run the repo-owned major-release
helper next.
