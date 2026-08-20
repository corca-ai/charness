# Issue 679: Idempotent impl bootstrap for an existing adapter

Status: active contract
Date: 2026-08-20
Source: `charness-artifacts/issues/reads/679.raw.yaml`

## Problem

The documented `impl` bootstrap runs `resolve_adapter`, `init_adapter`, and
`resolve_adapter` in sequence. In a consuming repository with a valid existing
`.agents/impl-adapter.yaml`, the middle command exits 1 with “Adapter already
exists”, even though the adapter is valid and no mutation is needed. That false
red teaches callers to ignore failures or reach for destructive `--force`.

## Capability Contract

An operator can follow the documented `impl` bootstrap in a repository with a
valid existing adapter and receive success from every step without changing the
adapter bytes or metadata. Missing adapters remain initialized; invalid or
conflicting adapters remain explicit failures and are never silently replaced.

## Current Slice

Repair the init boundary and its focused regression so the valid-existing case
is an idempotent success while preserving the missing, invalid, and explicit
force contracts. Verify both the source skill path and its installed mirror
after integration.

## Fixed Decisions

- A valid existing adapter is already configured state, not a request to
  overwrite; init returns success without writing it.
- Missing adapters still receive the generated portable scaffold.
- Invalid adapters remain visible and are not repaired implicitly by init.
- `--force` remains an explicit overwrite request and stays outside the normal
  bootstrap sequence.
- The acceptance boundary includes bytes and file metadata: the existing valid
  adapter must be unchanged.

## Probe Questions

- Does the init helper own the existence decision, or does the skill entrypoint
  need to conditionally skip it based on the resolver payload?
- Does the installed plugin mirror exercise the same helper path as the source
  skill, or does parity require a separate entrypoint smoke?
- Which conflict state is the smallest invalid fixture that proves fail-closed
  behavior without broadening the adapter schema?

## Deferred Decisions

- Do not add adapter migration or schema repair to this issue; a separate
  contract is required if invalid adapters need assisted recovery.
- Do not change adapter warning text unless a focused acceptance check depends
  on it.
- Do not infer consumer-host behavior from this repo-local fixture; retain an
  explicit host/install non-claim until the release readback stage.

## Non-Goals

- No destructive overwrite of consumer-owned configuration.
- No new adapter fields, presets, or version policy.
- No change to unrelated skill bootstrap sequences.

## Deliberately Not Doing

- Do not make every existing file a success: invalid, unreadable, or
  incompatible adapters must remain failures.
- Do not solve the symptom by documenting `|| true` or telling agents to ignore
  exit codes.
- Do not use `--force` as routine initialization.

## Constraints

- Allowed implementation paths are the ledger's `p0-679` budget:
  `skills/public/impl/SKILL.md`,
  `skills/public/impl/scripts/init_adapter.py`, and
  `tests/test_impl_bootstrap.py`.
- The shared `scripts/adapter_init_lib.py` dependency is parent-owned and
  serialized by the operating contract. If diagnosis confirms that the
  reusable classification boundary is the owner, the parent may repair that
  path during integration under a separately recorded shared-lane change; the
  p0 writer must not widen its worktree budget silently.
- Source and generated plugin mirrors must be synchronized by the parent
  integration lane.
- The regression must prove unchanged bytes and metadata for a valid adapter,
  not only exit code 0.
- Any failure is treated as a smell: repair the shared decision pattern and
  add the cheapest negative case that prevents the same false-green class.

## Success Criteria

- Verification type: unit — valid existing adapter: init exits 0, emits an
  explicit idempotent result, and leaves bytes/stat unchanged.
- Verification type: unit — missing adapter: init still creates the scaffold
  and the following resolve succeeds.
- Verification type: unit — invalid or conflicting adapter: init remains
  nonzero and does not overwrite the file.
- Verification type: integration — the documented three-command sequence is
  green in a consuming-repo-shaped fixture with a valid adapter.
- Verification type: specdown — source/plugin entrypoints remain in parity and
  no destructive default or exit-code suppression is introduced.

## Acceptance Checks

- Verification type: unit — `python3 -m pytest -q tests/test_impl_bootstrap.py`
- Verification type: unit — capture SHA-256, byte count, and stat before/after
  valid-existing init.
- Verification type: integration — execute resolve → init → resolve in the
  valid, missing, and invalid fixtures and record each exit code.
- Verification type: specdown — run the source/export parity and standalone
  entrypoint checks selected by the quality planner.

## Boundary Ownership

`init_adapter.py` owns the public existing-file decision and write boundary;
`adapter_init_lib.py` owns the reusable idempotent classification and is a
parent-owned serialized shared dependency; the resolver owns reporting adapter
validity; the parent integration lane owns generated plugin parity and release
proof. A host consumer remains outside local proof.

## Critique

- Interrupt Source: lesson-presentation-compaction-2026-08-14
- Seam Summary: lesson-session rendered output to repo-owned retro verdict
- Chosen Next Step: impl
- Impl Status: allowed
- Impl Status Reason: the forced interrupt's original disproving observation is
  resolved by the checked-in durable bundle contract; this issue is a separate
  adapter boundary and carries its own explicit host/install non-claims.
- What Disproving Observation Is Resolved: the original lesson-session output
  loss is resolved and must not be silently reopened while diagnosing #679.
- Causal critique: the false red is a control-flow ownership smell, not a
  caller inconvenience. The init owner must classify configured-valid state
  before the write refusal; the regression must preserve invalid-state refusal.

## Canonical Artifact

This file is the current implementation contract for #679. The issue read and
reproduction receipts remain the source-bound evidence; the goal ledger owns
admission and release disposition.

## First Implementation Slice

Trace the existing-file branch from `init_adapter.py` to its helper, prove the
valid/missing/invalid states, implement the smallest idempotent decision, add
focused regression coverage, and stop before parent export or release mutation.
