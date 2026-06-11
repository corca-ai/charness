# Release adapter preflight helper split critique
Date: 2026-06-12

Packet Consumed: charness-artifacts/critique/2026-06-11-225820-packet.md

## Decision Under Review

Extract release-adapter focused-preflight field-diff and command-runner logic
from `skills/public/release/scripts/publish_release_preflight.py` into
`skills/public/release/scripts/publish_release_adapter_preflight.py`, preserve
the existing `publish_release_preflight.release_adapter_preflight_payload` and
`publish_release_preflight.run_release_adapter_preflight` wrapper surface, and
sync the plugin mirror.

## Failure Angles

- Behavior compatibility: release tests load `publish_release_preflight.py` by
  file location rather than package import. Verdict: the wrapper loads the new
  sibling helper by `Path(__file__).with_name(...)`, and focused release tests
  pass.
- Packaging/export correctness: the preflight module imports the new helper at
  import time, so fresh checkouts fail if source or plugin helper files are
  omitted. Verdict: include both new helper files in the commit.
- Problem framing: this could be arbitrary line moving. Verdict: the extracted
  helper owns one coherent boundary: adapter candidates, adapter-field diff,
  focused command payload construction, and command execution.

## Counterweight Pass

- Act before ship: include the new source and plugin helper files in the commit.
- Bundle anyway: record the checked-in plugin export, skill-package, public-skill
  policy/dogfood, and scan-hygiene validations in the goal log.
- Over-worry: no further behavior change is required; wrappers preserve public
  callers and the focused tests cover the path.
- Valid but defer: converting release scripts to normal package imports is
  outside this slice and should wait for a broader release-script import cleanup.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_preflight.py:12 | action: fix | note: include both new source and plugin helper files in the commit.
- F2 | bin: bundle-anyway | evidence: strong | ref: charness-artifacts/critique/2026-06-11-225820-packet.md:20 | action: document | note: record packaging/export/skill validation evidence in the goal log.
- F3 | bin: over-worry | evidence: strong | ref: skills/public/release/scripts/publish_release_adapter_preflight.py:74 | action: document | note: helper split is cohesive and wrappers preserve public callers.
- F4 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/test_release_backend.py:13 | action: defer | note: package-import conversion is outside this slice.

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
