# Issue 679 Impl Bootstrap Debug Review
Date: 2026-08-20

## Problem

The documented `impl` bootstrap exits nonzero when a valid
`.agents/impl-adapter.yaml` already exists.

## Correct Behavior

Given a valid existing adapter, `resolve_adapter` → `init_adapter` →
`resolve_adapter` succeeds, and init leaves the adapter bytes and metadata
unchanged. Given no adapter, init creates the scaffold. Given an invalid or
conflicting adapter, init fails explicitly without replacing it.

## Observed Facts

- The locked reproduction resolves the valid adapter with exit 0.
- The same valid adapter makes init print `Adapter already exists ... Use
  --force to overwrite.` and exit 1.
- SHA-256, byte count, and stat evidence show the valid file was unchanged.
- Missing state initializes and resolves successfully.
- Invalid state remains invalid, is not overwritten, and init exits 1.
- `scripts/adapter_init_lib.py` is shared by the public skill init entrypoints;
  `scripts/adapter_lib.py::write_adapter_scaffold` refuses every existing file
  before validity can affect the decision.

## Reproduction

`charness-artifacts/issues/2026-08-20-679-reproduction.txt` records the
consuming-repository-shaped missing, valid, and invalid fixtures, commands,
exit codes, hashes, and stats.

## Candidate Causes

- Control flow: the generic writer treats existence as an unconditional write
  request and never asks whether configured state is valid and already usable.
- State/validation: the resolver could disagree with init about which adapter
  states are valid, causing an unsafe skip if classification is duplicated.
- Environment/install: the source skill and generated plugin mirror could load
  different helper code, hiding or reintroducing the behavior after export.

## Hypothesis

The control-flow cause is primary: if the init owner classifies an existing
adapter through the resolver's validation contract before reaching the writer,
valid init will return success without a write while invalid init will retain a
nonzero refusal. `disconfirmer: run the locked three-fixture probe and scan
every run_init_adapter consumer before changing code.`

## Verification

The probe confirms the predicted split: resolver validity is true for the
customized existing adapter, while the shared writer rejects it solely because
the path exists. Every discovered public init entrypoint imports the same
`run_init_adapter`; the behavior is therefore a shared decision-pattern bug,
not an impl-only caller typo. The source/plugin parity check remains a separate
integration proof.

## Root Cause

The reusable init boundary conflates “an adapter is present” with “the caller
requested an overwrite.” `run_init_adapter` always delegates an existing path
to a writer whose only non-force branch is refusal. Valid configured state is
therefore reported as a false failure, teaching callers to use `--force` or
ignore an error. The structural repair belongs at the shared classification
boundary and must preserve explicit invalid-state refusal.

## Invariant Proof

- Invariant: init is idempotent for valid configured state and non-destructive
  for invalid configured state.
- Producer Proof: resolver validation supplies the existing adapter's validity;
  the init decision must consume that result before any write.
- Final-Consumer Proof: the three-command bootstrap must observe success from
  init and then resolve the same bytes as valid.
- Interface-Shape Sibling Scan: missing, valid, invalid, and explicit `--force`
  states are distinct outcomes; no existing file is a generic success.
- Non-Claims: local source proof does not establish an installed cache,
  external consumer, hosted tag, or release readback.

## Detection Gap

The existing adapter tests cover parsing and the destructive writer refusal but
not the semantic init sequence. The smallest detector is a focused
`tests/test_impl_bootstrap.py` with byte/stat-preserving valid, missing, and
invalid fixtures, followed by source/plugin entrypoint parity proof.

## Sibling Search

- Mental model: “init” is a state classifier followed by a conditional writer,
  not an unconditional scaffold command.
- Shared helper axis: `run_init_adapter` | decision is currently existence-only
  | proof is the locked #679 reproduction; the repair must classify validity.
- Cross-file: every public `*/scripts/init_adapter.py` imports the helper, while
  `impl/scripts/resolve_adapter.py` already owns validity reporting. This is a
  follow-up carrier for all sibling init consumers: `init-idempotence-family`.

## Seam Risk

- Interrupt ID: lesson-presentation-compaction-2026-08-14 (resolved carry-forward)
- Risk Class: none
- Seam: source skill entrypoint → shared helper → consuming adapter file
- Disproving Observation: the old lesson-session output loss was resolved by
  the refreshed #617 handoff; #679 is a separate adapter boundary.
- What Local Reasoning Cannot Prove: installed plugin cache and external host
  behavior; source/plugin readback is still required.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: open
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: charness-artifacts/spec/2026-08-20-issue-679-impl-bootstrap-idempotence.md

## Prevention

Repair the shared state-classification pattern, add the three negative/positive
fixtures, and make the release closeout read both source and generated mirror.
Keep the helper as a serialized parent-owned path; do not hide its change in an
impl-only entrypoint or widen `--force` semantics.
