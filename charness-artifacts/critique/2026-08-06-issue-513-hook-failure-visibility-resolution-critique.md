# Issue #513 hook failure visibility resolution critique
Date: 2026-08-06

## Decision Under Review

Add a portable setup reference for Lefthook failure visibility: every covered
`pre-commit`/`pre-push` command declares actionable `fail_text`; diagnostic
gates retain stdout/stderr in a pre-provisioned stable log; output filtering and
consumer final-order verification are explicit. Route only Lefthook guidance;
leave Husky/simple-git-hooks to native guidance.

## Diff Scope

Changed surfaces are the public setup skill/reference, generated plugin mirrors,
worktree preparation documentation, and one deterministic guidance/parity test.
No consumer hook config, gate threshold, Charness runtime hook, provider, CI, or
installed-plugin behavior was changed.

## Capability at Stake

When a hook's output is truncated, the operator still sees which gate blocked
and where to read its retained diagnostics, or receives a self-contained
fallback that does not rely on hidden output.

## Failure Angles

- Problem framing initially found an output-order guarantee too strong for a
  portable setup reference. The final text makes final visible ordering a
  consumer acceptance check and does not claim Charness controls the runner.
- Portability initially found the `mkdir`-then-redirection example could point
  to a nonexistent log. The final example requires the log directory to be
  provisioned before the hook and gives an explicit fallback when provisioning
  fails.
- Operations initially found short commands could direct a truncated reader to
  normal output. The final contract permits no-log short commands only when
  `fail_text` is self-contained; diagnostic commands retain both streams.
- Routing initially covered all detected hook managers even though the syntax
  is Lefthook-specific. Setup now routes only a detected Lefthook configuration,
  while naming Husky/simple-git-hooks as separate native surfaces.
- The deterministic test now asserts equality for the new reference, setup
  skill, and bootstrap-seams source/plugin mirrors, plus the ownership boundary
  separating `prepare.commands` from Lefthook commands.

## Counterweight Pass

- Act Before Ship: none remain after the repaired-surface review, final packet
  regeneration, and focused tests.
- Bundle Anyway: keep source/plugin parity and the semantic setup/worktree
  separation in the same slice; both are cheap and directly protect the issue's
  failure mode.
- Over-Worry: do not add Charness-side runtime enforcement for arbitrary
  consumer Lefthook files, universal `.gitignore` or retention policy, or
  Husky/simple-git-hooks syntax to a Lefthook-owned reference.
- Valid but Defer: a consuming repository's intentional failing-hook run is the
  correct end-to-end proof of runner ordering and log availability; this slice
  records that non-claim rather than fabricating one locally.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: skills/public/setup/references/hook-failure-visibility.md:14-58 | action: document | note: keep actionable fail_text, pre-provisioned diagnostics, fallback wording, and consumer ordering acceptance together
- F2 | bin: over-worry | evidence: moderate | ref: skills/public/setup/references/hook-failure-visibility.md:60-70 | action: defer | note: other hook managers and consumer-side enforcement need their own native contract
- F3 | bin: valid-but-defer | evidence: strong | ref: skills/public/setup/references/hook-failure-visibility.md:67-70 | action: defer | note: no Charness-side consumer hook execution is claimed; adoption must run an intentional failure in the consumer repo

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: model=gpt-5.6-terra; reasoning_effort=medium; service_tier=priority; fork_context=false; unnamed one-shot spawn.
- Host exposure state: requested_fields_sent
- Application state: metadata-hidden (spawn returned findings but no separate host application confirmation).
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated. The initial three angle reviewers returned actionable findings,
but their boundary verifies were quarantined after the parent repaired the
surface. A repaired-surface operator reviewer and a separate final counterweight
then returned findings-received results with clean reviewer-boundary fingerprints.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/2026-08-06-issue-513-hook-failure-visibility-final-final-packet.json
- Packet path: charness-artifacts/critique/2026-08-06-issue-513-hook-failure-visibility-final-final-packet.json
- Packet SHA256: 7b5d6ad2df4e761ea5b0b7918c55462ae010e92a9c48e726086954f82c481de7
- Identity SHA256: 7dbbc644b15f00fe9a8a7411e12df8bf514baa7e057c47d0b8e550c170659ead

## Boundary Ownership

- Producer: the public `setup` skill and its hook-failure-visibility reference produce portable operator guidance; the plugin tree is generated from the public source.
- Consumer: a consumer repository's Lefthook runner and its operator consume the configured `fail_text` and retained failure log.
- Owning surface: public setup hook guidance, with generated plugin mirror and worktree documentation as synchronized render surfaces.
- Verdict: owned-correctly

## Deliberately Not Doing

No Charness-side Lefthook config scanner, universal log-retention policy, or
Husky/simple-git-hooks implementation is added. No consumer failing-hook run,
provider roundtrip, installed-plugin behavior, remote CI, release, tag, version
bump, or Cautilus result is claimed.

## Next Move

Run the issue closeout carrier validation and focused setup/worktree tests, then
carry the critique and final packet into the #513 direct-commit carrier. Keep
#513 local-only until the umbrella's one final push and remote readback.
