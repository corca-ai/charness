# v0.66.4 Release Critique
Date: 2026-07-12

## Execution

Three distinct release angles and one separate counterweight ran through
parent-delegated bounded reviewers. One reviewer that spawned an unauthorized
child was interrupted and quarantined; its result is not counted.

## Fresh-Eye Satisfaction

parent-delegated — valid Gawande, Minto, and Raskin angle reviewers plus a
separate counterweight completed read-only; reviewer-boundary verification
reported zero drift.

## Packet Consumed

`charness-artifacts/critique/2026-07-12-v0664-release-packet.md`

## Target

Release critique shaped by `references/release-critique.md`.

## Release Scope

Patch `0.66.4` / tag `v0.66.4`: reduce false-start verification work, emit an
exact mutation-coverage reuse handoff, refresh aggregate quality runtime
signals, and restore test-module ownership headroom.

## Capability at Stake

Maintainers need cheaper exact-bundle confidence without weakening the
independent proof at the irreversible publication boundary.

## Surface-Lock Inventory

- `.agents/surfaces.json`: the observed SLOC writer is sync-owned.
- `scripts/mutation_coverage_producer.py` and plugin mirror: resolved base,
  source path, and strict consumer command payload.
- `scripts/run-quality.sh` and plugin mirror: mode-specific aggregate runtime
  samples that cannot replace the primary exit status.
- focused quality-runner tests, release notes, manifests, and public tag.
- no public skill/prompt contract, migration, or issue lifecycle change.

## Angles

- Gawande / operational: bind the final lock to `v0.66.3`, execute the emitted
  consumer command, then prove public/install state through different channels.
- Minto / communication: lead with fewer false starts and safer handoff; keep
  lifecycle artifacts out of the user-facing value story.
- Raskin / humane interface: explain executable-root versus target-repo paths
  and how stale/mismatched coverage recovers without inventing a new public CLI.

## Findings

- The exact clean-HEAD mutation/broad proof and public/install readbacks are
  still provisional and must run after all evidence is committed.
- Release notes must preserve the narrow #436 claim and the #433 lifecycle
  nonclaim; neither issue is authorized to close.
- The adapter's broad integrations trigger exposes a nose checklist even though
  this delta changes only generic derived plugin scripts. Record it honestly as
  conservative scope, not as evidence that nose behavior changed.
- Ambient length bands and stale noncritical timing labels are already visible
  and do not justify expanding the release.

## Counterweight Triage

### Act Before Ship

- Commit this packet, critique, notes, and remaining closeout artifacts.
- Run the `v0.66.3`-anchored verification lock and its producer-emitted strict
  consumer command on clean HEAD.
- Publish without issue-close flags or close keywords; verify public HTTPS,
  fresh checkout, update/doctor installed state, then read #433/#436 OPEN.
- Explain exact-base handoff success and stale/mismatch recovery in notes.

### Bundle Anyway

- State that the real-host nose checklist is a conservative trigger whose
  remaining items are not evidence of changed nose behavior.

### Over-Worry

- Do not add a public sync CLI, interactive mutation UI, retries, new floors,
  or speculative host abstractions.

### Valid but Defer

- Exhaustive all-writer audit (#436), tracker lifecycle (#433), ambient length
  pressure, and stale noncritical timing components remain later work.

## Operator Action Required

- Run `charness update`, restart active host sessions when instructed, and use
  `charness doctor`/version readback to confirm the published install.
- When consuming mutation coverage, run the payload's emitted command exactly.
  On stale/base/path mismatch, rerun the producer for the current committed
  bundle rather than editing the consumer arguments by memory.

## Upgrade Path

Normal patch update via `charness update`; no migration or configuration change.
Rollback is reinstalling `v0.66.3` if needed.

## Deliberately Not Doing

No #433/#436 closure, generic verifier-writer detector, public sync command,
automatic second mutation collection, or new blocking quality floor.

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: `model=gpt-5.5`, `reasoning_effort=medium`,
  `service_tier=priority` for primary angles/counterweight.
- Host exposure state: requested_fields_sent
- Application state: the host accepted the requested fields but did not expose
  provider-side confirmation; valid reviewers completed read-only.

## Boundary Ownership

- Producer: the mutation producer emits exact committed-bundle facts; the
  release helper produces version, tag, publication, and install-refresh state.
- Consumers: the existing strict coverage checker judges mutation evidence;
  public HTTPS, fresh-checkout, doctor, and issue reads judge release state.
- Owning surface: manifest/producer/consumer and release-helper boundaries,
  rather than prose reconstruction in a session.
- Verdict: owned-correctly

## Next Move

Commit the release proof inputs, run the final clean verification lock, then
dry-run and execute the repo release helper with public/install/issue readback.
