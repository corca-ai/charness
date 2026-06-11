# Release publish execute helper split critique
Date: 2026-06-12

Packet Consumed: charness-artifacts/critique/2026-06-11-230953-packet.md

## Decision Under Review

Extract the long `execute_publish_plan()` release execution tail from
`skills/public/release/scripts/publish_release_cli.py` into
`skills/public/release/scripts/publish_release_execute.py`, keep the CLI module
as the public command/argument boundary, and sync the checked-in plugin export.

## Failure Angles

- Behavior ordering: release publish must still run auth, issue preflight,
  adapter preflight, bump, surface verification, review gates, quality command,
  release commit, fresh-checkout probes, tag/push, GitHub release creation,
  visibility verification, final artifact commit, issue closeout, and install
  refresh in the same order. Verdict: the helper is split into prepare,
  release-commit, and publish/finalize phases without reordering the old tail.
- Loader compatibility: direct file-location loaders may not register the CLI
  module in `sys.modules`. Verdict: execute and resume paths now pass an explicit
  `_execution_context()` namespace instead of `sys.modules[__name__]`; direct
  file-loader smoke passed.
- Durable release proof: the pre-existing publish/resume flow added
  `payload["install_refresh"]` after the final release artifact commit, so the
  payload reported refresh status but the durable artifact did not. Verdict:
  install refresh now runs before the final artifact commit on verified
  publish/resume paths, and the artifact renders an `Install Refresh` section.
- Export correctness: the CLI imports the new helper at import time, so source
  and plugin helper files must both be included. Verdict: plugin sync was run and
  source/plugin helper files are part of this slice.

## Counterweight Pass

- Act before ship: include the new source/plugin helper files and the critique
  packet artifacts in the commit.
- Bundle anyway: record focused release tests, exported plugin `--help` smoke,
  direct file-loader smoke, packaging/export validators, skill validators,
  public-skill policy/dogfood validators, and gitignore scan hygiene.
- Over-worry: direct unit tests for every private helper phase would duplicate
  the existing release publish integration tests for this behavior-preserving
  split.
- Valid but defer: replacing the broad `cli` dependency object with a typed
  protocol would be cleaner but is a separate design refactor.

## Structured Findings

<!-- allowed enums (substitute only these) - bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_cli.py:34 | action: fix | note: include `publish_release_execute.py` in both source and checked-in plugin export.
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_cli.py:301 | action: fix | note: avoid `sys.modules[__name__]` for direct file-loader compatibility; fixed by `_execution_context()`.
- F3 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_execute.py:187 | action: fix | note: durable artifact must record `install_refresh`; fixed by running refresh before final artifact commit and rendering it in `publish_release_artifact.py`.
- F4 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_release_publish.py:1 | action: document | note: run focused release publish/backend/resilience tests plus exported plugin help smoke.
- F5 | bin: over-worry | evidence: strong | ref: skills/public/release/scripts/publish_release_execute.py:9 | action: document | note: the split is cohesive around release execution phases.
- F6 | bin: valid-but-defer | evidence: moderate | ref: skills/public/release/scripts/publish_release_execute.py:15 | action: defer | note: a narrower typed execution context can wait for a broader release-script API cleanup.

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: high-leverage
- Requested spawn fields: inherited parent model; no explicit model override sent
- Host exposure state: requested_fields_sent
- Application state: spawn tool accepted two bounded angle reviewer requests and
  one counterweight reviewer request; host did not confirm provider-side
  application.

## Fresh-Eye Satisfaction

Fresh-Eye Satisfaction: parent-delegated. Parent received two bounded fresh-eye
reviews, fixed the direct-loader issue they found, then requested a separate
counterweight review. No same-agent substitute was used.
