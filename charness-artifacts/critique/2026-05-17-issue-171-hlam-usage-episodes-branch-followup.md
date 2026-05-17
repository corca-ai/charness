# Critique: Issue #171 Usage Episodes Branch Follow-Up

Execution: completed with parent-delegated bounded fresh-eye reviewers.

Fresh-Eye Satisfaction: parent-delegated

Packet Consumed:
`charness-artifacts/critique/2026-05-17-issue-171-branch-critique-packet-packet.md`

Target: code critique

Change: branch critique of `origin/main..HEAD`, covering `f05c779` and
`82e58ac`.

Diff Scope: usage episode schemas, validator, setup seed helper, plugin export,
tests, and issue #171 spec/critique artifacts.

## Angles

- Problem framing: whether the substrate now answers the Ceal/Crill repeated
  product context question instead of only validating Charness-local events.
- Diagnostic: whether schema claims match validator behavior and path/privacy
  boundaries after the first critique fixes.
- Operational: whether seeded consumer guidance and CLI behavior are usable by
  product operators.
- Counterweight: whether further requirements would overfit v1.

## Counterweight Triage

### Act Before Ship

- Require `t_link` when `t_status` is `promoted`. Candidate and rejected states
  may still omit a durable artifact, but promoted T evidence needs a link.
- Enforce `format: date-time` in the runtime validator, not only in schema
  annotations.
- Reject `--records-path` values outside `repo_root`; the CLI override should
  not bypass the repo-relative boundary hardened in the adapter schema.
- Keep or discard the generated branch critique packet explicitly before
  closeout. This run keeps it as consumed critique state.

### Bundle Anyway

- Clarify adapter template comments so consumers know the validator ships with
  Charness/plugin installs, not necessarily inside their product repo.
- Improve human `no_adapter` and `disabled` output with skipped-path context
  while preserving JSON output.

### Valid But Defer

- Adapter-level `product_id`, `vocabulary_ref`, and `instrumentation_ref` are
  plausible future adoption aids but should wait for a real consumer.
- Required `context_ref` is too strong for v1. Optional `context_ref` enables
  same-context analysis when the product has a safe stable reference, while
  still allowing lower-risk product records.

### Over-Worry

- Do not require `t_link` for all non-`none` T states.
- Do not add Ceal/Crill runtime emit hooks, dashboards, aggregation, or
  automaticity scoring in this slice.

## Pre-Merge Action

The act-before-ship and cheap bundle concerns were remediated in the follow-up
patch after this critique.
