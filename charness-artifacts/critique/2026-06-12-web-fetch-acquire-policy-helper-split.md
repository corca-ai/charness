# Web fetch acquire policy helper split critique
Date: 2026-06-12

Packet Consumed: charness-artifacts/critique/2026-06-11-224840-packet.md

## Decision Under Review

Extract fallback/direct-attempt acquisition policy helpers from
`skills/support/web-fetch/scripts/acquire_public_url.py` into
`skills/support/web-fetch/scripts/acquire_public_url_policy.py`, preserve the old
private helper aliases on `acquire_public_url.py`, and sync the plugin mirror.

## Failure Angles

- Behavior compatibility: existing tests import private helpers from
  `acquire_public_url.py`. Verdict: the entrypoint imports the moved policy
  helpers back under the old private names, and focused web-fetch/youtube tests
  pass.
- Packaging/export correctness: the entrypoint imports a new helper, so a fresh
  checkout would fail if the new source/plugin helper files were omitted.
  Verdict: include both new helper files in the commit; source and plugin copies
  are byte-identical after sync.
- Test sufficiency: direct unit tests for every moved predicate would duplicate
  existing public acquire-path coverage. Verdict: focused subprocess tests cover
  defuddle, generic browser, copied script layouts, and YouTube browser skip
  behavior.

## Counterweight Pass

- Act before ship: include the new source and plugin policy helper files in the
  commit.
- Bundle anyway: record the packaging, skill-package, and scan-hygiene
  validations in the goal log because the packet maps this change to those
  surfaces.
- Over-worry: direct predicate-only tests are unnecessary for this helper split.
- Valid but defer: standalone direct import of `acquire_public_url_policy.py`
  without script-directory path setup only matters if the policy module becomes
  a direct support API.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: strong | ref: skills/support/web-fetch/scripts/acquire_public_url.py:23 | action: fix | note: include both new source and plugin policy helper files in the commit.
- F2 | bin: bundle-anyway | evidence: strong | ref: charness-artifacts/critique/2026-06-11-224840-packet.md:22 | action: document | note: record checked-in plugin export, skill-package, and scan-hygiene validation evidence.
- F3 | bin: over-worry | evidence: strong | ref: tests/test_youtube_source.py:501 | action: document | note: old private helper aliases remain covered through existing tests.
- F4 | bin: valid-but-defer | evidence: moderate | ref: skills/support/web-fetch/scripts/acquire_public_url_policy.py:5 | action: defer | note: standalone import bootstrap only matters if this becomes a direct support API.

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: high-leverage
- Requested spawn fields: inherited parent model; no explicit model override sent
- Host exposure state: requested_fields_sent
- Application state: spawn tool accepted two bounded angle reviewer requests and one counterweight reviewer request; host did not confirm provider-side application.

## Fresh-Eye Satisfaction

Fresh-Eye Satisfaction: parent-delegated. Parent spawned two bounded angle
reviewers and one separate counterweight reviewer through `multi_agent_v1`;
all completed read-only review. No same-agent substitute was used.
