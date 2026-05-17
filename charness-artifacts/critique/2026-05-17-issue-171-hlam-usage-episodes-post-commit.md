# Critique: Issue #171 H-LAM/T Usage Episodes Post-Commit

Execution: completed with parent-delegated bounded fresh-eye reviewers.

Fresh-Eye Satisfaction: parent-delegated

Packet Consumed: committed packet `charness-artifacts/critique/2026-05-17-080239-packet.md`. A later generated packet
`2026-05-17-083538-packet.*` was discarded because it only described the
find-skills inventory refresh, not the `f05c779` usage-episodes substrate.

Target: code critique

Change: post-commit critique of `f05c779 Add H-LAM/T usage episode substrate`.

Diff Scope: `integrations/usage-episodes`, `scripts/validate_usage_episodes.py`,
`skills/public/setup`, plugin mirrors, tests, and the issue #171 spec artifact.

## Angles

- Problem framing: does the substrate actually support Ceal/Crill-style
  repeated context analysis for H-LAM/T, rather than only recording category
  labels?
- Diagnostic: do the schema and validator enforce the contract they advertise?
- Operational: can an operator seed, inspect, and validate records without
  ambiguous failure modes?
- Counterweight: which concerns are real blockers versus future analytics
  expansion?

## Counterweight Triage

### Act Before Ship

- Add a privacy-safe stable context reference. `context_bucket` only says what
  kind of surface was used; it cannot identify repeated use in the same
  product context. Remediation: added optional `context_ref` using the existing
  opaque reference shape and added a Ceal-shaped shared-context test.
- Return structured `invalid_adapter` for malformed adapter YAML. Remediation:
  catch `yaml.YAMLError` through the existing adapter error path and test that
  the validator does not emit a traceback.
- Harden portable path boundaries. The previous regex rejected POSIX absolute
  and traversal paths but allowed Windows drive-letter and backslash forms.
  Remediation: reject leading drive letters and backslashes for `storage_path`
  and reference `path`; add schema tests for `C:/...`, `C:\\...`, and
  `..\\...`.

### Bundle Anyway

- Require privacy posture keys when the adapter declares `privacy`, without
  requiring the whole block for every consumer.
- Remove the unreachable `event_filtered` validator status for v1, since the
  manifest schema only accepts `usage_episode`.
- Add validation guidance to the setup surface and a direct command to the
  adapter template comments.

### Valid But Defer

- Enforcing JSON Schema `format: date-time` remains deferred. The previous
  implementation critique already recorded this as a future tightening; v1
  should not imply timestamp ordering semantics yet.
- Derived metrics, cross-product aggregation, H-LAM/T inventory ingestion, and
  sibling issue linking remain future work. The substrate now carries the
  `context_ref` needed for those later summaries.
- End-to-end seed -> fixture -> validate dogfood would be useful later, but the
  current focused tests cover the seed helper and validator branches.

### Over-Worry

- Do not make Charness emit Ceal/Crill runtime episodes.
- Do not fold usage episodes into `t-events`.
- Do not add dashboards, raw transcript policy, automaticity scoring, or
  rotation enforcement in this slice.

## Pre-Merge Action

The act-before-ship and cheap bundle concerns were remediated in the follow-up
patch after this critique.
