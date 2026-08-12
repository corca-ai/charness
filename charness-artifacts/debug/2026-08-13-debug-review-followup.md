# Issue 606 Boundary Ratchet Debug
Date: 2026-08-13

## Problem

The boundary-bypass ratchet tells an operator to regenerate its baseline but
offers no executable regeneration path; its loader validates only the advisory
key count while four summary counts determine the no-increase verdict.

## Correct Behavior

Given a stored ratchet baseline, when it is loaded or regenerated, then every
enforced count must agree with the canonical inventory-derived baseline and the
operator must have a guarded command that produces that baseline rather than
hand-editing JSON.

## Observed Facts

- `COUNT_FIELDS` contains candidate, convertible, internal-boundary, and
  keep-boundary counts; `load_baseline()` checks only `candidate_key_count`.
- `check_boundary_bypass_ratchet.py` accepts no write/accept argument, although
  its errors say to regenerate.
- `build_baseline()` is the canonical producer; the quality inventory is a
  second reader of the same baseline artifact.

## Reproduction

- Create a valid baseline, alter one `COUNT_FIELDS` summary value without
  changing `candidate_keys`, and call `load_baseline()`: the current loader
  accepts it although a canonical rebuild differs.

## Candidate Causes

- The loader's consistency check was scoped to the key-list verdict instead of
  all values that later feed the ratchet decision.
- The gate and builder were kept as separate developer utilities, leaving the
  operator-visible gate without a repair command.
- A write command without an explicit delta confirmation could launder a large
  undesired baseline change.

## Hypothesis

- Falsifiable claim: a stored enforced summary count can differ from
  `build_baseline()` while `load_baseline()` accepts it | disconfirmer: create
  the smallest valid payload, change each count, and load it.

## Verification

- confirmed — a minimal valid baseline with only `internal_boundary_count`
  increased loaded successfully (`2`), while `build_baseline()` returned `1`.
  This directly proves the stored count can drift through the loader.

## Root Cause

The missing ownership contract has two coupled seams: the canonical builder is
not the gate's operator repair surface, and the loader does not reject every
persisted input that later changes its verdict. A historical no-increase
baseline may legitimately exceed the current inventory after a reduction, so
the repair must verify canonical writer-produced integrity rather than demand
equality with today's inventory on every read.

## Invariant Proof

- Invariant: when the canonical builder emits a baseline, every final quality
  reader must either consume writer-integral stored verdict inputs or refuse a
  conflicting stored count before rendering a verdict.
- Producer Proof: `build_baseline()` produces `summary` and the candidate lists.
- Final-Consumer Proof: the CLI emits `check_payload()`'s ratchet verdict; the
  structural-waste inventory separately reads the baseline.
- Interface-Shape Sibling Scan: dup ratchet exposes a guarded baseline command;
  boundary bypass does not.
- Non-Claims: no consumer repository and no safe delta threshold are proven.

## Detection Gap

- `load_baseline()` | key-count-only fixture did not fire for a drifting enforced
  count | test writer-integrity failure for every `COUNT_FIELDS` mutation.

## Sibling Search

- Mental model: a prose regeneration instruction is equivalent to an owned
  executable repair path.
- same layer: dup ratchet baseline writer | decision: reuse its operator shape,
  not its policy blindly | proof: static command surface.
- abstraction up: artifact loaders with derived summaries | decision:
  diagnostic-only pending structural matching | proof: not inspected.
- cross-file: structural-waste inventory baseline reader | decision: bundle
  reader-safe regeneration proof | proof: issue's observed crash history.

## Seam Risk

- Interrupt ID: none
- Risk Class: none
- Seam: builder → stored JSON → quality gate and inventory reader.
- Disproving Observation: canonical rebuild and stored counts agree for all
  enforced fields, and CLI exposes a guarded writer.
- What Local Reasoning Cannot Prove: consumer-repo baseline workflows.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: this record.

## Prevention

Make canonical regeneration executable and make all persisted verdict inputs
refuse drift before any reader can render a green result. Do not require a
historical no-increase baseline to equal a reduced current inventory.

## Resolution Evidence

- `check_boundary_bypass_ratchet.py --write-baseline` now produces canonical
  writer state and refuses a changed existing baseline until
  `--confirm-baseline-delta` follows a structured metadata, summary, and key
  delta review.
- `load_baseline()` refuses a missing or mismatched writer-integrity digest;
  non-object JSON, malformed JSON, and an existing directory target all retain
  the CLI's JSON-refusal path without a traceback.
- Focused proof: `python3 -m pytest tests/test_boundary_bypass_ratchet.py
  tests/quality_gates/test_staged_commit_gate_plan.py
  tests/quality_gates/test_surface_obligations.py -q` passed 120 tests;
  `ruff check` on the touched Python surfaces and the live root ratchet passed.
- Two bounded fresh-eye rounds ran. Round 2 repairs are accepted-unreviewed by
  the verdict-logic two-round cap; the resolution critique records their scope.
