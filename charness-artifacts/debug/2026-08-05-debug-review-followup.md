# Issue #507 Quality Adapter Bootstrap Debug
Date: 2026-08-05

## Problem

`bootstrap_adapter.py` rewrites an existing consumer-owned quality adapter when
its normalized generated output conflicts with the adapter's current intent,
dropping comments and adding inferred/default surfaces.

## Correct Behavior

Given an existing adapter, a normalized-equivalent bootstrap is a silent no-op.
Given a conflict, bootstrap preserves the adapter and comments, reports the
exact requested change, reason, and next action, and does not add absent or
disabled surfaces. Only an explicit migration mode may rewrite, and it must
name the intended rewrites while retaining comments.

## Observed Facts

- GitHub #507 is OPEN with `comments_read: true`; it reports `adapter_status:
  updated`, 14 comments dropped, and nonexistent CI/lefthook/coverage paths
  restored in a customized consumer adapter.
- GitHub #481 is CLOSED at `cec8c9b8`; its close comment says the deliberate-
  absence field prevents refilling declared fields but does not protect an
  existing adapter from a rewrite or preserve comments. #507 is the remaining
  bootstrap lifecycle contract, not a duplicate closeout.
- `quality_bootstrap_lib.py:434-455` detects and merges concept/command
  surfaces; `:512-526` writes any non-default-only difference immediately.
- `quality_bootstrap_render.py:86-93` treats only default/deferred additions as
  an unchanged plan. An inferred `concept_paths` addition is therefore a
  conflict that currently writes.
- `quality_bootstrap_absence.py:121-197` reports comment loss after the write,
  but warning after mutation is not preservation.

## Reproduction

- A temporary seeded consumer repo with two explanatory YAML comments, one
  explicit `npm run gate`, and no `concept_paths` was bootstrapped with the
  repository-owned command.
- Result: return code 0, `adapter_status: updated`, `comments_before: 2`,
  `comments_after: 0`, `changed: true`, and an inferred `concept_paths:` block.
  The JSON/stderr warning named 12 refilled defaults and the dropped comments,
  but the adapter had already changed.
- Cheapest disconfirmer for the conflict claim: run the same reproduction with
  a normalized-equivalent adapter and with an explicit migration flag once
  implemented; the first must remain byte-stable and the second must be the
  only write path.

## Candidate Causes

- The write planner has a default-only exemption but no general conflict state,
  so inferred safe additions and operator-owned customizations share one
  automatic `updated` path.
- The serializer renders from parsed data and has no comment-retention contract;
  `describe_intent_loss` can only report the loss after the write decision.
- The CLI exposes `--dry-run` but no explicit migration mode, so operators
  cannot approve a named rewrite while keeping ordinary bootstrap read/prepare.

## Hypothesis

- If the default path classifies any non-equivalent existing adapter as
  `conflict` and returns before writing, then the reproduction will preserve
  both bytes and comments while reporting the requested change. If an explicit
  migration path receives a named approval and a comment-preserving renderer,
  only that path will update. Disconfirmer: current source shows every
  `updated` plan writes at `quality_bootstrap_lib.py:520-526`; the reproduction
  confirmed that path and therefore supports the hypothesis.

## Verification

- resolved locally — ordinary bootstrap now treats every normalized semantic
  difference, including default/deferred additions, as `conflict` and preserves
  adapter bytes; normalized equality alone is `unchanged`.
- resolved locally — `--migrate` is the only conflicting write path, rejects
  output/report path aliasing and uninterpreted YAML, and retains mapping/list
  comments while preserving quoted hash values.
- focused evidence: 76 quality-bootstrap tests and 55 adapter/YAML regression
  tests passed; source/plugin parity was regenerated before review.
- delegated causal review received from unnamed bounded reviewer `019fd0b7`
  (delivery received; boundary fingerprint `/tmp/charness-reviewer-boundary-
  issue-507-causal.json` verified clean). The review independently confirmed
  the write-authorization root cause, classified `adapter_lib.plan_generated_write`
  as diagnostic-only, and required CLI byte-readback for all three lifecycle
  outcomes. It identified comment retention and normalized-equivalence
  semantics as implementation risks, not blockers to the bounded local slice.

## Root Cause

Bootstrap conflates “the generator found a difference” with “the operator
authorized a rewrite.” The default-only shortcut is a narrow historical
exception, not a lifecycle contract. Because the adapter is reserialized from
data, comments cannot survive the automatic write; the warning is post-hoc and
cannot restore the lost intent. The prevention boundary is the write planner
and CLI mode before `adapter_path.write_text`.

## Invariant Proof

- Invariant: when bootstrap emits a proposed adapter change, the final consumer
  (the adapter file read by the next quality planner) must either receive an
  explicitly approved, comment-retaining migration or receive the unchanged
  prior intent plus an actionable conflict advisory.
- Producer Proof: `quality_bootstrap_lib.py:434-455` produces inferred/default
  fields and `:512-518` computes the write plan; the temporary reproduction
  emitted the conflicting `concept_paths` addition.
- Final-Consumer Proof: the temporary adapter readback showed the producer's
  write changed the file and removed comments; this proves the local file
  consumer, not a separate consumer repository.
- Interface-Shape Sibling Scan: see Sibling Search; the matching shape is a
  generated config writer that turns a detected difference into an implicit
  mutation.
- Non-Claims: no external consumer checkout, installed plugin, provider, or
  remote issue state is claimed by this diagnosis.

## Detection Gap

- `tests/quality_gates/test_quality_bootstrap_absence.py:127-161` proves a
  warning is emitted for comment loss, but not that default bootstrap refuses
  the write | change the fixture to assert byte/comment preservation and a
  conflict status/advisory.
- `tests/quality_gates/test_quality_bootstrap.py:180-214` intentionally proves
  explicit adapter rewrites are currently allowed | split the contract into
  default conflict preservation and explicit migration behavior.
- `./scripts/run-quality.sh --read-only` and adapter validators check shape and
  output validity, not whether a consumer-owned adapter changed without an
  explicit migration decision | add end-to-end CLI fixtures for the three
  outcomes.

## Sibling Search

- Mental model: a generator treats normalized difference as permission to
  mutate operator-owned configuration.
- same layer: `scripts/markdown_preview_bootstrap_lib.py:146-151` also plans
  generated config writes | decision: same class, diagnostic-only for this
  slice | proof: static scan only; its ownership and migration contract need a
  separate review.
- abstraction up: `scripts/adapter_lib.py:504-517` centralizes the generic
  generated-write planner | decision: same class, fix now at the quality
  bootstrap caller | proof: local payload reproduction; keep generic helper
  semantics unchanged unless a separate contract is proven.
- specialization down: `scripts/quality_bootstrap_absence.py:121-197` warns
  about intent loss after mutation | decision: same bug, fix now by making the
  advisory part of pre-write conflict planning | proof: local payload proof.
- mental-model sibling: `scripts/quality_bootstrap_render.py:86-93` encodes the
  default-only exception | decision: same bug, fix now for the quality adapter
  plan; do not treat default/deferred additions as permission for inferred
  changes | proof: local reproduction.
- cross-file: `scripts/markdown_preview_bootstrap_lib.py` and
  `scripts/adapter_lib.py` are outside the subject file and are recorded as
  diagnostic-only/generalized siblings above.

## Seam Risk

- Interrupt ID: none
- Risk Class: external-seam
- Seam: generated YAML serializer to consumer-owned adapter; bootstrap planner,
  comment-bearing adapter, and next quality resolver
- Disproving Observation: none; the temporary reproduction confirms the seam
  mutates before the consumer can review it.
- What Local Reasoning Cannot Prove: behavior in the private consumer repository
  from #507 and installed plugin caches; this slice will prove the reconstructed
  local contract and checked-in source/plugin parity only.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/2026-08-05-issue-507-quality-adapter-lifecycle.md

## Prevention

Make bootstrap a three-way lifecycle: silent no-op for normalized equivalence,
conflict-preserve plus exact advisory by default, and explicit migration for
named changes. Test the actual CLI and read back the adapter bytes/comments;
keep the migration report and next-action evidence durable. Review the generic
markdown-preview writer separately rather than silently widening this issue.
