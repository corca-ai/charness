# v0.37.0 release critique
Date: 2026-06-10

## Decision Under Review

Cut charness v0.37.0 (minor) from pushed main @ 158d3673: #342
adapter-vs-integration-schema validation at every validate-adapters timing,
#343 host-hook liveness/posture/registry, #344 new-pool-module closeout
advisory, plus goal-closeout artifacts. All version surfaces at 0.36.0 with
zero drift; tree clean.

## Failure Angles

- The stricter validate-adapters gate could break consumer repos silently
  after `charness update` (vendored schema + out-of-contract adapter keys).
- The `session-capture status` exit-code change (dangling → exit 1) could
  break operator wrappers or install/update flows.
- Minor could under-state a compatibility break (should it be major?).
- Tagging before the in-progress quality-core run on the release SHA
  completes would treat tag push as verified publication.
- Release notes could omit the operator-visible behavior changes.

## Counterweight Pass

- Real and folded: release notes must name (a) the stricter adapter gate
  including the t-events gate-stricter-than-runtime asymmetry and (b) the
  status exit-1-on-dangling change; the release waits for the quality-core
  run on 158d3673 (completed success before publish).
- Over-worry: update-path breakage (the charness CLI never invokes
  validate_adapters; init/update use reconcile mode which always exits 0 and
  self-heals moved-checkout hooks); status JSON shape (additive key, CLI
  consumer reads preserved keys); major-bump pressure (no invocation,
  install, or CLI surface change — the integration schema contract was
  already published; enforcement timing moved).

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: strong | ref: release notes for v0.37.0 | action: document | note: name both operator-visible changes in the notes — the stricter adapter gate (with the t-events asymmetry) and the status exit-1-on-dangling drift cause. Folded into the release notes passed to the publish helper.
- F2 | bin: act-before-ship | evidence: moderate | ref: quality-core run 27254155402 | action: document | note: wait for the in-progress run on the release SHA before tagging (prudence — the workflow is a local-gate-subset mirror and the broad gate passed 73/0 on the same tree). Run completed success before publish.
- F3 | bin: over-worry | evidence: strong | ref: charness CLI reconcile call sites | action: defer | note: init/update invoke --mode reconcile only (allow_failure, always exit 0); the status exit-code change cannot reach install/update flows.
- F4 | bin: valid-but-defer | evidence: weak | ref: reconcile_usage_episodes_host_hooks.py human-readable status output | action: defer | note: hook_liveness details surface via merged DRIFT lines / --json only; cosmetic follow-up, not a release change.

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: bounded fresh-eye subagent reviewer (separate agent context, read-only).
- Requested spawn fields: subagent_type=general-purpose, name=release-critique-v037, bounded release packet (scope commits, bump rationale, operator-visible changes, green checks, reviewer questions).
- Host exposure state: applied
- Application state: host-confirmed: Agent tool returned reviewer verdict with agentId ab4c8d52d599d2dae (46 tool uses; independently verified version-surface zero-drift, mirror byte-sync via cmp, 67+84 tests green on the release tree, the degrade contracts in code, and the CLI update-path isolation).

## Fresh-Eye Satisfaction

Verdict: SHIP-WITH-NITS, no blockers (reviewer agentId ab4c8d52d599d2dae).
Minor bump confirmed right per the repo version policy (major only on
compatibility/invocation breaks); no silent update-path breakage found; the
wait-for-CI nit honored (run 27254155402 completed success before tagging);
the release-notes nit folded into the notes content. Cosmetic nits (scope
count off by docs-only commits; human-readable liveness rendering) recorded,
not release-blocking.
